.PHONY: help install dev test lint format typecheck build run stop clean docker-build docker-up docker-down

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev: ## Start development servers
	docker-compose up -d redis
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
	cd frontend && npm run dev

test: ## Run all tests
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-unit: ## Run unit tests only
	cd backend && python -m pytest tests/ -v -m "not integration" --cov=app --cov-report=term

test-integration: ## Run integration tests
	cd backend && python -m pytest tests/ -v -m integration

lint: ## Run linting
	cd backend && ruff check app/ tests/
	cd frontend && npm run lint

format: ## Format code
	cd backend && ruff format app/ tests/
	cd backend && black app/ tests/
	cd frontend && npm run format

typecheck: ## Run type checking
	cd backend && mypy app/

build: ## Build Docker images
	docker-compose build

run: ## Start all services
	docker-compose up -d

stop: ## Stop all services
	docker-compose down

clean: ## Clean up generated files
	rm -rf backend/__pycache__ backend/app/__pycache__ backend/app/**/__pycache__
	rm -rf backend/.pytest_cache backend/htmlcov backend/.coverage
	rm -rf frontend/.next frontend/node_modules/.cache
	rm -rf data/*.faiss data/*.db

docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start all services via Docker
	docker-compose up -d

docker-down: ## Stop all Docker services
	docker-compose down

benchmark: ## Run benchmarks
	cd backend && python -m tests.benchmark

setup: ## Initial project setup
	cp .env.example .env
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	mkdir -p data
