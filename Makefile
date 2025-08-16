.PHONY: install test lint format run clean

install:
	pip install -e .
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v --cov=sefas

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

lint:
	ruff check sefas/ tests/
	mypy sefas/

format:
	ruff format sefas/ tests/
	black sefas/ tests/

run:
	python scripts/run_experiment.py run

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov