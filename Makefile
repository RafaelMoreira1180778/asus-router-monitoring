.PHONY: help install dev-install test lint format clean build docker-build docker-run docker-stop docker-logs

# Default target
help: ## Show this help message
	@echo "ASUS Router Prometheus Exporter v2.0 - Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install package in current environment
	pip install -r requirements.txt

dev-install: ## Install package in development mode
	pip install -e .
	pip install -r requirements.txt

# Code quality
lint: ## Run linting checks
	@echo "Running linting checks..."
	python -m py_compile asus_exporter.py
	python -m py_compile src/main.py
	find src/ -name "*.py" -exec python -m py_compile {} \;

format: ## Format code (if you have black installed)
	@if command -v black >/dev/null 2>&1; then \
		echo "Formatting code with black..."; \
		black asus_exporter.py src/; \
	else \
		echo "Black not installed, skipping formatting"; \
	fi

# Testing
test: ## Run tests (if test files exist)
	@if [ -d "tests" ]; then \
		python -m pytest tests/; \
	else \
		echo "No tests directory found"; \
	fi

# Cleanup
clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/

# Docker operations
docker-build: ## Build Docker image
	docker build -t asus-router-exporter:latest .

docker-run: ## Run Docker container (requires ASUS_PASSWORD env var)
	@if [ -z "$$ASUS_PASSWORD" ]; then \
		echo "Error: ASUS_PASSWORD environment variable is required"; \
		exit 1; \
	fi
	docker run -d --name asus-exporter \
		-p 8000:8000 \
		-e ASUS_PASSWORD=$$ASUS_PASSWORD \
		-e ASUS_HOSTNAME=$${ASUS_HOSTNAME:-192.168.1.1} \
		-e ASUS_USERNAME=$${ASUS_USERNAME:-admin} \
		asus-router-exporter:latest

docker-stop: ## Stop and remove Docker container
	docker stop asus-exporter 2>/dev/null || true
	docker rm asus-exporter 2>/dev/null || true

docker-logs: ## Show Docker container logs
	docker logs -f asus-exporter

# Docker Compose operations
compose-up: ## Start services with docker-compose
	docker-compose up -d

compose-down: ## Stop services with docker-compose
	docker-compose down

compose-logs: ## Show docker-compose logs
	docker-compose logs -f

# Development
run: ## Run the exporter locally (requires ASUS_PASSWORD env var)
	@if [ -z "$$ASUS_PASSWORD" ]; then \
		echo "Error: ASUS_PASSWORD environment variable is required"; \
		echo "Usage: ASUS_PASSWORD=your_password make run"; \
		exit 1; \
	fi
	python asus_exporter.py

# Build Python package
build: clean ## Build Python package
	python setup.py sdist bdist_wheel

# Show current project structure
tree: ## Show project structure
	@if command -v tree >/dev/null 2>&1; then \
		tree -I '__pycache__|*.pyc|.git|.venv|*.egg-info'; \
	else \
		find . -type f -not -path "./.git/*" -not -path "./.venv/*" -not -path "./__pycache__/*" | sort; \
	fi
