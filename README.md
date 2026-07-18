<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
<div align="center">

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

</div>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Garvittt-API/CodeNexus">
    <img src="https://img.shields.io/badge/CODE-NEXUS-blueviolet?style=for-the-badge&logo=search&logoColor=white&labelColor=1A1A2E&color=6C63FF" alt="CodeNexus Logo">
  </a>

  <h3 align="center">Where Human Language Meets Code Intelligence</h3>

  <p align="center">
    Ask natural language questions about any codebase.<br/>
    Get highly relevant code snippets with AI-powered explanations.
    <br />
    <a href="https://github.com/Garvittt-API/CodeNexus"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Garvittt-API/CodeNexus#quick-start">Quick Start</a>
    &middot;
    <a href="https://github.com/Garvittt-API/CodeNexus/blob/main/docs/api.md">API Reference</a>
    &middot;
    <a href="https://github.com/Garvittt-API/CodeNexus/issues/new?labels=bug&template=bug_report.md">Report Bug</a>
    &middot;
    <a href="https://github.com/Garvittt-API/CodeNexus/issues/new?labels=enhancement&template=feature_request.md">Request Feature</a>
  </p>
</div>

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=flat-square&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-66BB6A?style=flat-square&logo=google&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

</div>

<br/>

<!-- BADGES -->
<div align="center">
<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=24&duration=2500&pause=1000&color=6C63FF&center=true&vCenter=true&multiline=true&repeat=true&width=900&height=80&lines=%F0%9F%94%8D+Semantic+Code+Search+Engine;Ask+Questions.+Find+Code.+Understand+Everything." alt="Typing SVG" />
</div>

<br/>

---

<!-- ABOUT THE PROJECT -->
## About The Project

<div align="center">
<strong>CodeNexus</strong> is a full-stack <strong>Semantic Code Search</strong> engine that bridges the gap between human language and code.<br/>
Unlike keyword search, CodeNexus understands <strong>meaning</strong> — ask <em>"How does authentication work?"</em> and get the exact functions, classes, and files that implement it.
</div>

<br/>

<div align="center">

|  |  |  |
|:---:|:---:|:---:|
| **Zero API keys** | **AST-aware chunking** | **Two-stage ranking** |
| Embeddings run locally via `sentence-transformers` | Code split at function/class boundaries | FAISS ANN + cross-encoder re-ranking |
| **6 LLM providers** | **30+ languages** | **One command deploy** |
| Ollama, OpenAI, Anthropic, Gemini, DeepSeek, Mistral | Python, JS, TS, Java, Go, Rust, C/C++, and more | `docker-compose up` and you're running |

</div>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Features

<table>
<tr>
<td width="50%">

### Intelligent Code Search
- Natural language queries
- 30+ programming languages
- AST-based semantic chunking
- Cross-encoder re-ranking
- Sub-second search latency

</td>
<td width="50%">

### AI-Powered Explanations
- LLM-generated insights
- Streaming SSE responses
- Code context awareness
- 6 LLM providers supported
- File paths & line numbers cited

</td>
</tr>
<tr>
<td width="50%">

### Repository Management
- Local folder import
- GitHub / Git URL support
- Drag & drop upload
- Real-time indexing progress
- Multi-repo support

</td>
<td width="50%">

### Production Ready
- Docker Compose deployment
- Rate limiting & security
- GitHub Actions CI/CD
- Comprehensive docs
- Pre-commit hooks

</td>
</tr>
</table>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Architecture

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                                                                             │
 │    USER QUERY                                                              │
 │    "How does the payment system work?"                                     │
 │         │                                                                   │
 │         ▼                                                                   │
 │   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
 │   │              │    │              │    │              │                  │
 │   │   EMBED      │───▶│  FAISS ANN   │───▶│ CROSS-ENCODER│                  │
 │   │   (bge)      │    │  Top-100     │    │  Re-rank     │                  │
 │   │              │    │              │    │  Top-20      │                  │
 │   └──────────────┘    └──────────────┘    └──────┬───────┘                  │
 │                                                   │                         │
 │                                    ┌──────────────┴──────────────┐          │
 │                                    │                             │          │
 │                                    ▼                             ▼          │
 │                           ┌──────────────┐             ┌──────────────┐     │
 │                           │              │             │              │     │
 │                           │   RESULTS    │             │  LLM EXPLAIN │     │
 │                           │   (JSON)     │             │  (Streaming) │     │
 │                           │              │             │              │     │
 │                           └──────────────┘             └──────────────┘     │
 │                                                                             │
 └─────────────────────────────────────────────────────────────────────────────┘
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Tech Stack

<div align="center">

| Layer | Stack |
|-------|-------|
| **Frontend** | Next.js 14, React 18, TailwindCSS 3.4, Zustand, react-syntax-highlighter |
| **Backend** | FastAPI, Python 3.11, Pydantic v2, SQLAlchemy 2.0 |
| **AI / ML** | sentence-transformers, FAISS, tree-sitter, cross-encoder |
| **LLM** | Ollama (default), OpenAI, Anthropic, Gemini, DeepSeek, Mistral |
| **Infra** | Docker, Redis, GitHub Actions, SQLite |

</div>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- GETTING STARTED -->
## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (recommended)

### One-Command Deploy

```bash
git clone https://github.com/Garvittt-API/CodeNexus.git
cd CodeNexus
cp .env.example .env
docker-compose up -d
```

> **Frontend:** http://localhost:3000 &nbsp;&nbsp;|&nbsp;&nbsp; **API:** http://localhost:8000 &nbsp;&nbsp;|&nbsp;&nbsp; **Docs:** http://localhost:8000/docs

### Manual Setup

<details>
<summary><strong>Backend</strong></summary>

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

</details>

<details>
<summary><strong>Frontend</strong></summary>

```bash
cd frontend
npm install
npm run dev
```

</details>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- USAGE EXAMPLES -->
## Usage

### Search Code

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "How does authentication work?", "top_k": 10}'
```

**Response:**
```json
{
  "query": "How does authentication work?",
  "results": [
    {
      "file_path": "src/auth/login.py",
      "content": "def authenticate(username, password):...",
      "start_line": 15,
      "end_line": 42,
      "score": 0.9234,
      "rank": 1
    }
  ],
  "search_time_ms": 156.7
}
```

### Search + AI Explanation

```bash
curl -X POST http://localhost:8000/api/search/explain \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain the payment processing flow"}'
```

### Import a Repository

```bash
curl -X POST http://localhost:8000/api/repos/import \
  -H "Content-Type: application/json" \
  -d '{"source": "https://github.com/user/repo", "source_type": "github"}'
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Project Structure

```
CodeNexus/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # REST endpoints
│   │   ├── core/                # Config, security, exceptions
│   │   ├── domain/              # Entities & value objects
│   │   ├── services/            # Business logic
│   │   │   ├── parsing.py       # AST-based code parsing
│   │   │   ├── indexing.py      # Repository indexing
│   │   │   └── search.py        # Search & RAG pipeline
│   │   └── infrastructure/      # External integrations
│   │       ├── vector_db.py     # FAISS vector database
│   │       ├── embedding_provider.py
│   │       ├── reranker.py      # Cross-encoder re-ranking
│   │       └── llm_provider.py  # Multi-provider LLM
│   └── tests/
├── frontend/
│   ├── app/                     # Next.js App Router
│   ├── components/              # React components
│   └── lib/                     # API client & state
├── docs/                        # Documentation
├── docker-compose.yml
└── .github/workflows/ci.yml
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- ROADMAP -->
## Roadmap

- [x] Repository import (local, GitHub, Git)
- [x] AST-based code chunking with tree-sitter
- [x] Local embeddings with sentence-transformers
- [x] FAISS vector search
- [x] Cross-encoder re-ranking
- [x] Multi-provider LLM integration
- [x] Streaming SSE explanations
- [x] Docker Compose deployment
- [x] GitHub Actions CI/CD
- [ ] PostgreSQL + pgvector support
- [ ] WebSocket real-time updates
- [ ] Code diff search
- [ ] Collaborative repositories
- [ ] VS Code extension

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- CONTRIBUTING -->
## Contributing

Contributions make the open source community an amazing place to learn, inspire, and create. Any contributions are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- CONTACT -->
## Contact

**Garvitt** — [GitHub Profile](https://github.com/Garvittt-API)

Project Link: [https://github.com/Garvittt-API/CodeNexus](https://github.com/Garvittt-API/CodeNexus)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [sentence-transformers](https://www.sbert.net/) — Local embedding models
* [FAISS](https://faiss.ai/) — Facebook AI Similarity Search
* [tree-sitter](https://tree-sitter.github.io/) — Incremental parser for code
* [FastAPI](https://fastapi.tiangolo.com/) — Modern Python web framework
* [Next.js](https://nextjs.org/) — The React framework for the web
* [Ollama](https://ollama.com/) — Run LLMs locally

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/Garvittt-API/CodeNexus.svg?style=for-the-badge
[contributors-url]: https://github.com/Garvittt-API/CodeNexus/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Garvittt-API/CodeNexus.svg?style=for-the-badge
[forks-url]: https://github.com/Garvittt-API/CodeNexus/network/members
[stars-shield]: https://img.shields.io/github/stars/Garvittt-API/CodeNexus.svg?style=for-the-badge
[stars-url]: https://github.com/Garvittt-API/CodeNexus/stargazers
[issues-shield]: https://img.shields.io/github/issues/Garvittt-API/CodeNexus.svg?style=for-the-badge
[issues-url]: https://github.com/Garvittt-API/CodeNexus/issues
[license-shield]: https://img.shields.io/github/license/Garvittt-API/CodeNexus.svg?style=for-the-badge
[license-url]: https://github.com/Garvittt-API/CodeNexus/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white
[linkedin-url]: https://linkedin.com/
