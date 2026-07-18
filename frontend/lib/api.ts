const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new ApiError(
      errorBody.detail || `Request failed with status ${response.status}`,
      response.status
    );
  }

  return response.json();
}

export interface SearchItem {
  chunk_id: string;
  file_path: string;
  language: string;
  content: string;
  start_line: number;
  end_line: number;
  chunk_type: string;
  name?: string;
  score: number;
  rank: number;
}

export interface SearchResponse {
  query: string;
  repo_id?: string;
  results: SearchItem[];
  total_results: number;
  search_time_ms: number;
}

export interface ExplainResponse extends SearchResponse {
  explanation: string;
}

export interface Repository {
  id: string;
  name: string;
  source: string;
  source_type: string;
  status: string;
  total_files: number;
  total_lines: number;
  total_chunks: number;
  languages: Record<string, number>;
  functions: number;
  classes: number;
  created_at: string;
  updated_at: string;
  error_message?: string;
}

export interface ImportResponse {
  id: string;
  name: string;
  source: string;
  source_type: string;
  status: string;
  message: string;
}

export interface IndexingTask {
  id: string;
  repo_id: string;
  status: string;
  progress: number;
  total_files: number;
  processed_files: number;
  current_file?: string;
  error_message?: string;
}

export async function searchCode(
  query: string,
  repo_id?: string,
  top_k: number = 20,
  rerank: boolean = true
): Promise<SearchResponse> {
  return fetchApi<SearchResponse>("/api/search", {
    method: "POST",
    body: JSON.stringify({ query, repo_id, top_k, rerank }),
  });
}

export async function searchAndExplain(
  query: string,
  repo_id?: string,
  top_k: number = 20
): Promise<ExplainResponse> {
  return fetchApi<ExplainResponse>("/api/search/explain", {
    method: "POST",
    body: JSON.stringify({ query, repo_id, top_k }),
  });
}

export async function listRepos(): Promise<Repository[]> {
  return fetchApi<Repository[]>("/api/repos");
}

export async function importRepo(
  source: string,
  source_type: string = "local"
): Promise<ImportResponse> {
  return fetchApi<ImportResponse>("/api/repos/import", {
    method: "POST",
    body: JSON.stringify({ source, source_type }),
  });
}

export async function deleteRepo(repo_id: string): Promise<{ message: string }> {
  return fetchApi(`/api/repos/${repo_id}`, { method: "DELETE" });
}

export async function indexRepo(
  repo_id: string
): Promise<{ task_id: string; repo_id: string; message: string }> {
  return fetchApi(`/api/repos/${repo_id}/index`, { method: "POST" });
}

export async function getIndexingStatus(
  task_id: string
): Promise<IndexingTask> {
  return fetchApi<IndexingTask>(`/api/indexing/${task_id}/status`);
}

export async function healthCheck(): Promise<{
  status: string;
  version: string;
  embedding_model: string;
  llm_provider: string;
}> {
  return fetchApi("/health");
}
