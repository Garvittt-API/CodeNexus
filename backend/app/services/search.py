"""Search and RAG pipeline service."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from ..core.config import get_settings
from ..core.exceptions import SearchError
from ..infrastructure.database import get_db
from ..infrastructure.embedding_provider import get_embedding_provider
from ..infrastructure.llm_provider import get_llm_provider
from ..infrastructure.reranker import get_reranker
from ..infrastructure.vector_db import get_vector_db

logger = logging.getLogger(__name__)


def search_code(
    query: str,
    repo_id: Optional[str] = None,
    top_k: int = 20,
    rerank: bool = True,
) -> Dict[str, Any]:
    """Search code using semantic search with optional re-ranking."""
    settings = get_settings()
    start_time = time.time()

    embedding_provider = get_embedding_provider()
    vector_db = get_vector_db(dimension=embedding_provider.dimension)

    query_embedding = embedding_provider.embed_query(query)

    ann_top_k = min(settings.SEARCH_TOP_K, vector_db.count()) if vector_db.count() > 0 else top_k
    candidates = vector_db.search(query_embedding, top_k=ann_top_k)

    if not candidates:
        return {
            "query": query,
            "repo_id": repo_id,
            "results": [],
            "total_results": 0,
            "search_time_ms": (time.time() - start_time) * 1000,
        }

    db = get_db()
    chunk_map: Dict[str, Dict[str, Any]] = {}
    chunk_ids_to_fetch = []

    for faiss_id, score, meta in candidates:
        chunk_id = meta.get("chunk_id")
        if chunk_id:
            chunk_ids_to_fetch.append(chunk_id)

    for cid in chunk_ids_to_fetch:
        chunk = db.get_chunk(cid)
        if chunk:
            chunk_map[cid] = chunk

    results_with_scores = []
    for faiss_id, score, meta in candidates:
        chunk_id = meta.get("chunk_id")
        if chunk_id and chunk_id in chunk_map:
            chunk = chunk_map[chunk_id]
            results_with_scores.append({
                "chunk_id": chunk_id,
                "file_path": chunk["file_path"],
                "language": chunk["language"],
                "content": chunk["content"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
                "chunk_type": chunk["chunk_type"],
                "name": chunk.get("name"),
                "score": score,
            })

    if rerank and results_with_scores and len(results_with_scores) > 1:
        reranker = get_reranker()
        documents = [r["content"] for r in results_with_scores]
        reranked = reranker.rerank(query, documents, top_k=min(settings.RERANK_TOP_K, len(documents)))
        reranked_results = []
        for rank, (idx, rerank_score) in enumerate(reranked):
            result = results_with_scores[idx]
            result["score"] = rerank_score
            result["rank"] = rank + 1
            reranked_results.append(result)
        results_with_scores = reranked_results
    else:
        for i, result in enumerate(results_with_scores):
            result["rank"] = i + 1

    final_results = results_with_scores[:top_k]
    search_time_ms = (time.time() - start_time) * 1000

    return {
        "query": query,
        "repo_id": repo_id,
        "results": final_results,
        "total_results": len(final_results),
        "search_time_ms": search_time_ms,
    }


async def search_and_explain(
    query: str,
    repo_id: Optional[str] = None,
    top_k: int = 20,
) -> Dict[str, Any]:
    """Search code and generate an LLM explanation."""
    settings = get_settings()
    start_time = time.time()

    search_result = search_code(query, repo_id, top_k=settings.EXPLAIN_TOP_K + 5, rerank=True)
    top_results = search_result["results"][: settings.EXPLAIN_TOP_K]

    if not top_results:
        return {
            "query": query,
            "repo_id": repo_id,
            "results": [],
            "explanation": "No relevant code snippets found for your query.",
            "total_results": 0,
            "search_time_ms": (time.time() - start_time) * 1000,
        }

    code_context = ""
    for i, result in enumerate(top_results):
        code_context += f"\n--- Snippet {i + 1} ({result['file_path']}, lines {result['start_line']}-{result['end_line']}) ---\n"
        code_context += f"```{result['language']}\n{result['content']}\n```\n"

    prompt = f"""Based on the following code snippets from the repository, answer the user's question.

User Query: {query}

Code Snippets:
{code_context}

Please provide:
1. A clear explanation of the relevant code
2. How it relates to the user's query
3. Any important context or caveats
4. Specific file paths and line numbers for reference

Be concise but thorough."""

    llm_provider = get_llm_provider()
    try:
        explanation = await llm_provider.generate(prompt)
    except Exception as e:
        logger.error("LLM explanation failed: %s", e)
        explanation = f"Found {len(top_results)} relevant code snippets, but the LLM explanation could not be generated: {e}"

    search_time_ms = (time.time() - start_time) * 1000

    return {
        "query": query,
        "repo_id": repo_id,
        "results": top_results,
        "explanation": explanation,
        "total_results": search_result["total_results"],
        "search_time_ms": search_time_ms,
    }


async def search_and_explain_stream(
    query: str,
    repo_id: Optional[str] = None,
    top_k: int = 20,
):
    """Search code and stream the LLM explanation as SSE events."""
    import json

    search_result = search_code(query, repo_id, top_k=top_k, rerank=True)
    top_results = search_result["results"][:3]

    yield f"data: {json.dumps({'type': 'results', 'results': [dict(r) for r in top_results], 'total': search_result['total_results']})}\n\n"

    if not top_results:
        yield f"data: {json.dumps({'type': 'explanation', 'content': 'No relevant code snippets found.'})}\n\n"
        yield "data: [DONE]\n\n"
        return

    code_context = ""
    for i, result in enumerate(top_results):
        code_context += f"\n--- Snippet {i + 1} ({result['file_path']}, lines {result['start_line']}-{result['end_line']}) ---\n"
        code_context += f"```{result['language']}\n{result['content']}\n```\n"

    prompt = f"""Based on the following code snippets from the repository, answer the user's question.

User Query: {query}

Code Snippets:
{code_context}

Please provide a clear explanation of the relevant code, how it relates to the query, and reference specific file paths and line numbers. Be concise."""

    llm_provider = get_llm_provider()
    try:
        async for chunk in llm_provider.generate_stream(prompt):
            yield f"data: {json.dumps({'type': 'explanation_chunk', 'content': chunk})}\n\n"
    except Exception as e:
        logger.error("LLM stream failed: %s", e)
        yield f"data: {json.dumps({'type': 'explanation_chunk', 'content': f'\\n\\n[LLM Error: {e}]'})}\n\n"

    yield "data: [DONE]\n\n"
