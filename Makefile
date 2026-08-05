# ==============================================================================
# Makefile - Telegram Channel Auto-Curator Bot
# ==============================================================================

PYTHON ?= python3
VENV ?= .venv
PIP ?= $(VENV)/bin/pip
PYTEST ?= $(VENV)/bin/pytest

.PHONY: help venv install test run clean docker-build docker-up docker-down

help:
	@echo "Available Targets:"
	@echo "  make venv          - Create a local virtual environment (.venv)"
	@echo "  make install       - Install Python requirements in virtual environment"
	@echo "  make test          - Run automated pytest unit tests"
	@echo "  make run           - Run the Channel Auto-Curator Bot"
	@echo "  make clean         - Remove cache, bytecode, and temporary files"
	@echo "  make docker-build  - Build Docker image for the Curator Bot"
	@echo "  make docker-up     - Start the Curator Bot using Docker Compose"
	@echo "  make docker-down   - Stop and remove Docker containers"

venv:
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created at $(VENV)"

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Dependencies installed successfully."

test:
	$(PYTEST) -v tests/
	@echo "Test suite completed."

run:
	$(PYTHON) src/main.py

clean:
	rm -rf __pycache__/ src/__pycache__/ src/*/__pycache__/ src/*/*/__pycache__/ tests/__pycache__/
	rm -rf .pytest_cache/ *.pyc *.pyo *.db *.session-journal
	@echo "Workspace cleaned."

docker-build:
	docker build -t telegram-channel-curator:latest .

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down
