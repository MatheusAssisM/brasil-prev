.PHONY: help install test run clean format lint typecheck quality setup-dev

help:
	@echo "Brasil Prev - Monopoly Game Simulator"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install dependencies and project"
	@echo "  make setup-dev  - Setup development environment (deps + hooks)"
	@echo "  make test       - Run tests"
	@echo "  make run        - Start the API server"
	@echo "  make format     - Format code with black"
	@echo "  make lint       - Run flake8 and pylint"
	@echo "  make typecheck  - Run mypy type checking"
	@echo "  make quality    - Run all quality checks (format, lint, type, test)"
	@echo "  make clean      - Clean up cache and build files"

install:
	uv sync
	uv pip install -e .

setup-dev:
	@bash setup-dev.sh

test:
	uv run pytest -v

run:
	uv run start

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
