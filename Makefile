# FieldNode Makefile
# Comandos simplificados para desenvolvimento

.PHONY: help setup run migrate createsuperuser shell clean

help:  ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup:  ## Configura ambiente virtual e instala dependências
	test -d .venv || python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

run:  ## Inicia o servidor Django
	python manage.py runserver

migrate:  ## Aplica migrações do banco
	python manage.py migrate

migrations:  ## Cria migrações
	python manage.py makemigrations

createsuperuser:  ## Cria superusuário
	python manage.py createsuperuser

shell:  ## Abre shell do Django
	python manage.py shell

clean:  ## Remove arquivos de cache e __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

test:  ## Roda os testes
	python manage.py test

lint:  ## Roda verificação de código (se ruff instalado)
	ruff check .

format:  ## Formata código (se ruff instalado)
	ruff format .

docker-up:  ## Inicia serviços com Docker
	docker-compose up -d

docker-down:  ## Para serviços Docker
	docker-compose down

docker-logs:  ## Mostra logs do Docker
	docker-compose logs -f api