PYTHON_BIN := $(PWD)/.venv/bin/python
CELERY_BIN := $(PWD)/.venv/bin/celery
UVICORN_BIN := $(PWD)/.venv/bin/uvicorn

.PHONY: backend-dev backend-worker backend-beat backend-sync-once backend-test core-test lint db-upgrade dev-all

PY_CORE := $(PWD)/packages/clipador-core/src
PY_ADAPTERS := $(PWD)/packages/clipador-adapters/src
UV_CACHE_DIR := $(PWD)/.uv-cache
PYTHONPATH_EXPORT := PYTHONPATH=$(PY_CORE):$(PY_ADAPTERS)
BACKEND_ENV := services/backend/.env

backend-dev:
	mkdir -p $(UV_CACHE_DIR)
	set -a; source $(BACKEND_ENV); set +a; \
	$(PYTHONPATH_EXPORT) $(UVICORN_BIN) clipador_backend.main:app \
		--app-dir services/backend/src --env-file $(BACKEND_ENV)

backend-worker:
	mkdir -p $(UV_CACHE_DIR)
	set -a; source $(BACKEND_ENV); set +a; \
	$(PYTHONPATH_EXPORT) $(CELERY_BIN) -A clipador_backend.celery_app worker --loglevel=info

backend-beat:
	mkdir -p $(UV_CACHE_DIR)
	set -a; source $(BACKEND_ENV); set +a; \
	$(PYTHONPATH_EXPORT) $(CELERY_BIN) -A clipador_backend.celery_app beat --loglevel=info

# Executa uma sincronização de ingestão (útil para testar sem esperar o beat)
backend-sync-once:
	# Executa no diretório do backend para que o .env seja carregado pelas settings
	mkdir -p $(UV_CACHE_DIR)
	cd services/backend && \
		set -a; source .env; set +a; \
		PYTHONPATH=../../packages/clipador-core/src:../../packages/clipador-adapters/src \
		VIRTUAL_ENV=$(PWD)/.venv \
		$(PYTHON_BIN) -c 'from clipador_backend.tasks.ingestion import run_ingestion_task; run_ingestion_task()'

backend-test:
	mkdir -p $(UV_CACHE_DIR)
	$(PYTHONPATH_EXPORT) $(PYTHON_BIN) -m pytest services/backend/tests

core-test:
	mkdir -p $(UV_CACHE_DIR)
	$(PYTHONPATH_EXPORT) $(PYTHON_BIN) -m pytest packages/clipador-core/tests

lint:
	$(PYTHON_BIN) -m ruff check services/backend/src packages/clipador-core/src packages/clipador-adapters/src packages/clip-editor/src

db-upgrade:
	mkdir -p $(UV_CACHE_DIR)
	$(PYTHONPATH_EXPORT) $(PYTHON_BIN) -m alembic -c services/backend/alembic.ini upgrade head

# Inicia API, worker e beat em paralelo no mesmo shell.
.PHONY: dev-all
dev-all:
	bash scripts/dev-all.sh
