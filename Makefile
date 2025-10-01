.PHONY: help install test run demo clean

help:
	@echo "Brasil Prev - Monopoly Game Simulator"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install dependencies and project"
	@echo "  make test       - Run tests"
	@echo "  make run        - Start the API server"
	@echo "  make demo       - Run demonstration"
	@echo "  make clean      - Clean up cache and build files"

install:
	uv sync
	uv pip install -e .

test:
	uv run pytest -v

run:
	uv run start

demo:
	uv run python demo.py

clean:
	rm -rf .pytest_cache __pycache__ .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
