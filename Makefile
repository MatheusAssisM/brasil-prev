.PHONY: help install test-unit test-integration clean format lint typecheck quality setup-dev coverage docker-build docker-up docker-down docker-logs docker-test-unit docker-test-integration

help:
	@echo "Brasil Prev - Monopoly Game Simulator"
	@echo ""
	@echo "Docker Commands (Production):"
	@echo "  make docker-build     - Build Docker image"
	@echo "  make docker-up        - Start application in Docker"
	@echo "  make docker-down      - Stop Docker containers"
	@echo "  make docker-logs      - View container logs"
	@echo ""
	@echo "Development Commands:"
	@echo "  make install          - Install dependencies locally"
	@echo "  make setup-dev        - Setup dev environment (deps + hooks + quality)"
	@echo "  make test-unit        - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make coverage         - Run unit tests with coverage"
	@echo "  make format           - Format code with black"
	@echo "  make lint             - Run flake8 and pylint"
	@echo "  make typecheck        - Run mypy type checking"
	@echo "  make quality          - Run quality checks (format + lint + typecheck)"
	@echo "  make clean            - Clean cache and build files"
	@echo ""
	@echo "Docker Testing:"
	@echo "  make docker-test-unit        - Run unit tests in Docker"
	@echo "  make docker-test-integration - Run integration tests in Docker"

install:
	uv sync && uv pip install -e .

setup-dev:
	@bash setup-dev.sh

run:
	uv run start

test-unit:
	uv run pytest -m unit -v

test-integration:
	uv run pytest -m integration -v

coverage:
	uv run pytest -m unit --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=95
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"

format:
	uv run black app/ tests/

lint:
	@echo "Running flake8..."
	uv run flake8 app/ tests/
	@echo ""
	@echo "Running pylint..."
	uv run pylint app/ --recursive=y

typecheck:
	uv run mypy app/

quality: format lint typecheck
	@echo ""
	@echo "✓ All quality checks passed!"

clean:
	rm -rf .pytest_cache __pycache__ .ruff_cache .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov

docker-build:
	docker-compose build --no-cache

docker-up:
	docker-compose up
	@echo ""
	@echo "✓ Application started at http://localhost:8000"
	@echo "  View logs: make docker-logs"
	@echo "  Stop: make docker-down"

docker-down:
	docker-compose down

