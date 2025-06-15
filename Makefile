SHELL := /bin/bash

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help message
	@echo "Usage:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "  %-20s%s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: format
format: ## Format Python files using isort and black
	@echo "Formatting Python files..."
	poetry run isort --profile black .
	poetry run black .
	poetry run ruff check . --fix
	poetry run mypy tracenexus

.PHONY: run
run: ## Run the TraceNexus MCP server with both transports
	@echo "Starting TraceNexus MCP server (dual transport)..."
	poetry run tracenexus --http-port 52734 --sse-port 52735 --mount-path /mcp

.PHONY: install-dev
install-dev: lock ## Install development dependencies
	@echo "Installing development dependencies..."
	poetry install --with dev

.PHONY: test
test: install-dev ## Run tests (with coverage)
	@echo "Running tests with coverage..."
	poetry run pytest tests/ --cov=tracenexus --cov-report=term-missing

.PHONY: clean
clean: ## Clean up python cache files and build artifacts
	@echo "Cleaning up cache files and build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	rm -rf dist/ build/ 2>/dev/null || true
	rm -rf .pytest_cache/ .ruff_cache/ .coverage htmlcov/ .mypy_cache/ .tox/ 2>/dev/null || true

.PHONY: build
build: ## Build the package using poetry
	@echo "Building package..."
	poetry build

.PHONY: token-check
token-check: ## Check if PyPI token is configured
	@echo "Checking PyPI token configuration..."
	@if ! python -c "import keyring; token = keyring.get_password('pypi-token', 'pypi'); exit(0 if token else 1)"; then \
		echo "PyPI token not configured. Please run:"; \
		echo "make token-set TOKEN=your-token-here"; \
		exit 1; \
	else \
		echo "✓ PyPI token found"; \
	fi

.PHONY: token-set
token-set: ## Set PyPI token (Usage: make token-set TOKEN=your-token-here)
	@if [ -z "$(TOKEN)" ]; then \
		echo "Error: TOKEN is required. Usage: make token-set TOKEN=your-token-here"; \
		exit 1; \
	fi
	@echo "Setting PyPI token..."
	@poetry config pypi-token.pypi "$(TOKEN)"
	@python -c "import keyring; keyring.set_password('pypi-token', 'pypi', '$(TOKEN)')" 2>/dev/null || echo "Warning: Could not store in keyring"
	@echo "Token configured successfully"

.PHONY: token-remove
token-remove: ## Remove PyPI token configuration
	@echo "Removing PyPI token..."
	@poetry config --unset pypi-token.pypi 2>/dev/null || true
	@python -c "import keyring; keyring.delete_password('pypi-token', 'pypi')" 2>/dev/null || true
	@rm -f ~/.config/pypoetry/auth.toml 2>/dev/null || true
	@echo "Token removed successfully"

.PHONY: publish
publish: token-check ## Publish to PyPI
	@echo "Publishing package to PyPI..."
	poetry publish

.PHONY: all
all: format ## Run format

.PHONY: version
version: ## Display current version
	@poetry version

.PHONY: version-patch
version-patch: ## Bump patch version (0.0.X)
	@poetry version patch
	@$(MAKE) sync-version

.PHONY: version-minor
version-minor: ## Bump minor version (0.X.0)
	@poetry version minor
	@$(MAKE) sync-version

.PHONY: version-major
version-major: ## Bump major version (X.0.0)
	@poetry version major
	@$(MAKE) sync-version

.PHONY: sync-version
sync-version: ## Sync version between pyproject.toml and __init__.py
	@echo "Syncing versions..."
	@VERSION=$$(poetry version -s) && \
	echo "New version: $$VERSION" && \
	sed -i.bak "s/__version__ = .*/__version__ = \"$$VERSION\"/" tracenexus/__init__.py && \
	rm -f tracenexus/__init__.py.bak

.PHONY: lock
lock: ## Update poetry.lock to match pyproject.toml
	@echo "Updating poetry.lock file..."
	poetry lock

.PHONY: update
update: ## Update dependencies to their latest versions
	@echo "Updating dependencies..."
	poetry update 

.PHONY: show-package-contents
show-package-contents: build ## Show contents of the built package
	@echo "Package contents:"
	@tar -tvf dist/*.tar.gz || echo "No tar.gz file found"
	@echo "\nWheel contents:"
	@unzip -l dist/*.whl || echo "No wheel file found" 