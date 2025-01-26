# Price Tracker Project

POETRY = poetry
VENV_DIR = .venv

all: check-poetry check-venv install run

check-poetry:
	@which poetry > /dev/null || (echo "Poetry not found. Installing..."; curl -sSL https://install.python-poetry.org | python3 -)

check-venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment not found. Creating..."; \
		$(POETRY) env use python3; \
		$(POETRY) install; \
	fi

# Dependencies from pyproject.toml
install:
	$(POETRY) install

run:
	$(POETRY) run python src/scraper.py

lint:
	@which flake8 > /dev/null || (echo "flake8 not found. Installing..."; $(POETRY) add flake8)
	$(POETRY) run flake8 .

format:
	@which black > /dev/null || (echo "black not found. Installing..."; $(POETRY) add black)
	$(POETRY) run black .

tests:
	@which pytest > /dev/null || (echo "pytest not found. Installing..."; $(POETRY) add pytest)
	$(POETRY) run pytest

# Clean up: first lint & format, then remove venv
clean:
	@echo "Running linting & formatting before cleaning..."
	$(MAKE) lint
	$(MAKE) format
	rm -rf $(VENV_DIR)
	@echo "Cleaned up venv and finished linting/formatting."


