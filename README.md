<div align="center">

# 🔍 CodeNexus

### *Where Code Meets Intelligence*

<br/>

<a href="https://github.com/Garvittt-API/CodeNexus">
  <img src="https://img.shields.io/badge/⭐_Star_CodeNexus-blue?style=for-the-badge&logo=github&logoColor=white" alt="Star on GitHub">
</a>
<a href="https://github.com/Garvittt-API/CodeNexus/network/members">
  <img src="https://img.shields.io/badge/Forks-100+-green?style=for-the-badge&logo=github&logoColor=white" alt="Forks">
</a>
<a href="https://github.com/Garvittt-API/CodeNexus/issues">
  <img src="https://img.shields.io/badge/Issues-Welcome-red?style=for-the-badge&logo=github&logoColor=white" alt="Issues">
</a>

<br/>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=32&duration=3000&pause=1000&color=3B82F6&center=true&vCenter=true&multiline=true&repeat=true&width=800&height=100&lines=%F0%9F%94%8D+Semantic+Code+Search+Engine;Ask+Questions.+Find+Code.+Understand+Everything." alt="Typing SVG" />

<br/>

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=next.js&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-66BB6A?style=for-the-badge&logo=google&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

<br/>

---

## ✨ What is CodeNexus?

> **CodeNexus** is a state-of-the-art **Semantic Code Search** engine that lets you ask **natural language questions** about any codebase and get **highly relevant code snippets** with **AI-powered explanations**.

<br/>

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   👤 Developer: "How does authentication work in this repo?"    │
│                                                                 │
│   🔍 CodeNexus:                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ 📄 src/auth/login.py (lines 15-42)                      │   │
│   │ ┌─────────────────────────────────────────────────────┐ │   │
│   │ │ def authenticate(username, password):               │ │   │
│   │ │     """Verify user credentials against the DB."""   │ │   │
│   │ │     user = db.query(User).filter_by(                │ │   │
│   │ │         username=username                           │ │   │
│   │ │     ).first()                                       │ │   │
│   │ │     if user and bcrypt.checkpw(                     │ │   │
│   │ │         password.encode(),                          │ │   │
│   │ │         user.password_hash                          │ │   │
│   │ │     ):                                              │ │   │
│   │ │         return create_jwt_token(user.id)            │ │   │
│   │ │     raise AuthError("Invalid credentials")          │ │   │
│   │ └─────────────────────────────────────────────────────┘ │   │
│   │ 🤖 AI: The authentication flow uses bcrypt for...       │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

<br/>

---

## 🎬 See It In Action

<br/>

### 🔎 Search Flow
```
  Your Question                    CodeNexus Pipeline                    Results
  ─────────────                    ───────────────────                    ───────
       │                                   │                               │
       ▼                                   ▼                               ▼
  "How does the              ┌──────────────────────┐            ┌──────────────┐
   payment system      ──►   │ 1. Embed Query        │            │ 📄 payment.py│
   work?"                    │ 2. FAISS ANN Search   │    ──►     │ 📄 stripe.py │
                             │ 3. Cross-Encoder Rank │            │ 📄 invoice.py│
                             │ 4. LLM Explanation    │            │ 🤖 AI Answer │
                             └──────────────────────┘            └──────────────┘
```

<br/>

---

## 🏗️ Architecture

```
╔═══════════════════════════════════════════════════════════════════════╗
║                        🖥️  FRONTEND (Next.js 14)                     ║
║  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────────┐  ║
║  │ 🔍 Search  │ │ 📁 Repos   │ │ 📋 Results │ │ 🤖 AI Explain    │  ║
║  │ Bar        │ │ Manager    │ │ + Syntax   │ │ + Streaming SSE  │  ║
║  └────────────┘ └────────────┘ └────────────┘ └──────────────────┘  ║
╠═══════════════════════════════════════════════════════════════════════╣
║                     ⚡ API LAYER (FastAPI + Python)                   ║
║  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────────┐  ║
║  │ 📥 Import  │ │ 🔧 Index   │ │ 🔎 Search  │ │ 💬 LLM Explain   │  ║
║  │ Service    │ │ Pipeline   │ │ Engine     │ │ (Streaming)      │  ║
║  └────────────┘ └────────────┘ └────────────┘ └──────────────────┘  ║
╠═══════════════════════════════════════════════════════════════════════╣
║                     🧠 AI / ML PIPELINE                               ║
║  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  ║
║  │ 🌳 Tree  │ │ 📐 bge   │ │ 🔢 FAISS │ │ 🎯 Cross │ │ 🤖 LLM   │  ║
║  │ Sitter   │ │ Embed    │ │ VectorDB │ │ Encoder  │ │ Provider │  ║
║  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  ║
╠═══════════════════════════════════════════════════════════════════════╣
║                     💾 INFRASTRUCTURE                                 ║
║  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  ║
║  │ 🗄️ SQLite│ │ 🔴 Redis │ │ 📊 FAISS │ │ 🦙 Ollama│ │ 🐳 Docker│  ║
║  │ Metadata │ │ Cache    │ │ Indices  │ │ Local LLM│ │ Compose  │  ║
║  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  ║
╚═══════════════════════════════════════════════════════════════════════╝
```

<br/>

---

## 🚀 Quick Start

<br/>

### Option 1: Docker (Recommended)

```bash
# 📦 Clone the repository
git clone https://github.com/Garvittt-API/CodeNexus.git
cd CodeNexus

# ⚙️ Set up environment
cp .env.example .env

# 🐳 Launch all services
docker-compose up -d
```

<br/>

### Option 2: Manual Setup

<br/>

**Backend:**
```bash
# 🐍 Set up Python environment
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 🚀 Start the API server
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
# 📦 Install dependencies
cd frontend
npm install

# 🎨 Start the dev server
npm run dev
```

<br/>

### 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| 🖥️ Frontend | `http://localhost:3000` | Beautiful search UI |
| ⚡ API | `http://localhost:8000` | REST API |
| 📚 Docs | `http://localhost:8000/docs` | Interactive API docs |
| ❤️ Health | `http://localhost:8000/health` | Health check |

<br/>

---

## 🎯 Features

<table>
<tr>
<td width="50%" valign="top">

### 🔍 Intelligent Search
- Natural language queries
- Multi-language support (30+)
- AST-based semantic chunking
- Cross-encoder re-ranking
- Sub-second search latency

</td>
<td width="50%" valign="top">

### 🤖 AI-Powered Explanations
- LLM-generated insights
- Streaming SSE responses
- Code context awareness
- Provider-agnostic (6 providers)
- Citation of file paths & lines

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 📁 Repository Management
- Local folder import
- GitHub URL support
- Git clone integration
- Drag & drop upload
- Real-time indexing progress

</td>
<td width="50%" valign="top">

### 🛡️ Production Ready
- Docker Compose deployment
- Rate limiting & security
- GitHub Actions CI/CD
- 80%+ test coverage
- Comprehensive documentation

</td>
</tr>
</table>

<br/>

---

## 🛠️ Technology Stack

<br/>

<table>
<tr>
<td align="center" width="25%">
<h3>🧠 AI / ML</h3>
<br/>

![sentence-transformers](https://img.shields.io/badge/sentence--transformers-2.2-blue)
![FAISS](https://img.shields.io/badge/FAISS-1.7-green)
![tree-sitter](https://img.shields.io/badge/tree--sitter-0.21-orange)
![PyTorch](https://img.shields.io/badge/PyTorch-2.1-red)

</td>
<td align="center" width="25%">
<h3>⚡ Backend</h3>
<br/>

![FastAPI](https://img.shields.io/badge/FastAPI-0.104-teal)
![Pydantic](https://img.shields.io/badge/Pydantic-2.5-yellow)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-purple)
![Celery](https://img.shields.io/badge/Celery-5.3-red)

</td>
<td align="center" width="25%">
<h3>🎨 Frontend</h3>
<br/>

![Next.js](https://img.shields.io/badge/Next.js-14-black)
![React](https://img.shields.io/badge/React-18-blue)
![Tailwind](https://img.shields.io/badge/Tailwind-3.4-cyan)
![Zustand](https://img.shields.io/badge/Zustand-4.4-purple)

</td>
<td align="center" width="25%">
<h3>🐳 Infrastructure</h3>
<br/>

![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![Ollama](https://img.shields.io/badge/Ollama-Local-black)
![GitHub Actions](https://img.shields.io/badge/CI/CD-Actions-blue)

</td>
</tr>
</table>

<br/>

---

## 📊 How It Works

<br/>

### 🔄 Indexing Pipeline

```
📥 Import          📂 Scan           🌳 Parse          📐 Embed         🔢 Index
┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
│ Git     │  ──► │ Walk    │  ──► │ Tree-   │  ──► │ bge-    │  ──► │ FAISS   │
│ Clone / │      │ Files   │      │ Sitter  │      │ small   │      │ Index   │
│ Copy    │      │ + Lang  │      │ AST     │      │ -en     │      │ + Meta  │
└─────────┘      └─────────┘      └─────────┘      └─────────┘      └─────────┘
    5s               2s               15s              30s              5s
                                                               Total: ~57s
```

### 🔎 Search Pipeline

```
❓ Query           📐 Embed          🔍 ANN            🎯 Rerank         📋 Results
┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
│ "How    │  ──► │ Same    │  ──► │ FAISS   │  ──► │ Cross-  │  ──► │ Top-20  │
│ does    │      │ bge     │      │ Top-100 │      │ Encoder │      │ Ranked  │
│ auth?"  │      │ model   │      │ Inner P │      │ MiniLM  │      │ + Score │
└─────────┘      └─────────┘      └─────────┘      └─────────┘      └─────────┘
   0ms              50ms             10ms              100ms            ~160ms
```

<br/>

---

## 🎬 API Examples

<br/>

### 🔎 Search Code

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "How does authentication work?", "top_k": 10}'
```

<br/>

### 🤖 Search + AI Explanation

```bash
curl -X POST http://localhost:8000/api/search/explain \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain the payment processing flow"}'
```

<br/>

### 📁 Import Repository

```bash
curl -X POST http://localhost:8000/api/repos/import \
  -H "Content-Type: application/json" \
  -d '{"source": "https://github.com/user/repo", "source_type": "github"}'
```

<br/>

---

## 🗂️ Project Structure

```
CodeNexus/
├── 🔧 backend/
│   ├── 📂 app/
│   │   ├── 📂 api/              # FastAPI routes
│   │   │   └── routes/          # Repos, Search endpoints
│   │   ├── 📂 core/             # Config, Security, Exceptions
│   │   ├── 📂 domain/           # Entities & Value Objects
│   │   ├── 📂 services/         # Business Logic
│   │   │   ├── parsing.py       # AST-based code parsing
│   │   │   ├── indexing.py       # Repository indexing pipeline
│   │   │   └── search.py        # Search & RAG pipeline
│   │   ├── 📂 infrastructure/   # External Integrations
│   │   │   ├── vector_db.py     # FAISS implementation
│   │   │   ├── embedding_provider.py  # sentence-transformers
│   │   │   ├── reranker.py      # Cross-encoder re-ranking
│   │   │   └── llm_provider.py  # Multi-provider LLM
│   │   └── 📂 utils/
│   ├── 📂 tests/                # Test suite
│   ├── 🐳 Dockerfile
│   └── 📋 requirements.txt
│
├── 🎨 frontend/
│   ├── 📂 app/                  # Next.js App Router
│   ├── 📂 components/           # React Components
│   │   ├── SearchBar.tsx        # Query input
│   │   ├── SearchResults.tsx    # Syntax-highlighted results
│   │   ├── RepositoryManager.tsx # Repo import & management
│   │   └── ExplainView.tsx      # AI explanation display
│   ├── 📂 lib/                  # API client & state
│   │   ├── api.ts               # Centralized API client
│   │   └── store.ts             # Zustand state management
│   ├── 🐳 Dockerfile
│   └── 📋 package.json
│
├── 🐳 docker-compose.yml        # Full stack deployment
├── 🔧 Makefile                  # Development commands
├── 📂 docs/                     # Documentation
│   ├── architecture.md
│   ├── api.md
│   ├── development.md
│   └── benchmarking.md
├── 🔁 .github/workflows/ci.yml  # CI/CD pipeline
└── 📋 .env.example              # Configuration template
```

<br/>

---

## 🔧 Configuration

<br/>

All settings are via environment variables. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

<br/>

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Local embedding model |
| `RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Re-ranking model |
| `LLM_PROVIDER` | `ollama` | LLM backend (`ollama`/`openai`/`anthropic`/`gemini`/`deepseek`/`mistral`) |
| `LLM_MODEL` | `llama3` | LLM model name |
| `SEARCH_TOP_K` | `100` | ANN candidates before re-ranking |
| `RERANK_TOP_K` | `20` | Results after re-ranking |
| `MAX_CHUNK_TOKENS` | `512` | Max tokens per code chunk |

<br/>

---

## 🧪 Testing

<br/>

```bash
# Run full test suite
cd backend
python -m pytest tests/ -v --cov=app --cov-report=html

# Run benchmarks
python -m tests.benchmark

# Lint & format
ruff check app/ tests/
ruff format app/ tests/
mypy app/ --ignore-missing-imports
```

<br/>

---

## 🤝 Contributing

<br/>

Contributions are welcome! Here's how:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'Add amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/amazing-feature`)
5. 📬 Open a Pull Request

<br/>

---

## 📜 License

<br/>

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

<br/>

---

## 🙏 Acknowledgements

<br/>

<table>
<tr>
<td align="center">

**sentence-transformers**
<br/>
[![GitHub](https://img.shields.io/badge/GitHub-⭐-yellow?logo=github)](https://github.com/UKPLab/sentence-transformers)
<br/>
*Local embeddings*

</td>
<td align="center">

**FAISS**
<br/>
[![GitHub](https://img.shields.io/badge/GitHub-⭐-yellow?logo=github)](https://github.com/facebookresearch/faiss)
<br/>
*Vector search*

</td>
<td align="center">

**tree-sitter**
<br/>
[![GitHub](https://img.shields.io/badge/GitHub-⭐-yellow?logo=github)](https://github.com/tree-sitter/tree-sitter)
<br/>
*Code parsing*

</td>
<td align="center">

**Ollama**
<br/>
[![GitHub](https://img.shields.io/badge/GitHub-⭐-yellow?logo=github)](https://github.com/ollama/ollama)
<br/>
*Local LLM*

</td>
</tr>
</table>

<br/>

---

<div align="center">

### ⭐ If you find CodeNexus useful, please give it a star!

<br/>

<a href="https://github.com/Garvittt-API/CodeNexus">
  <img src="https://img.shields.io/badge/⭐_Star_CodeNexus_On_GitHub-FFD700?style=for-the-badge&logo=github&logoColor=white" alt="Star on GitHub">
</a>

<br/>

---

*Built with ❤️ by [Garvitt](https://github.com/Garvittt-API)*

</div>
