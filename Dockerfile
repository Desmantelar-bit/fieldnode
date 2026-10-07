# =============================================================================
# FieldNode — Dockerfile multi-stage
#
# Estágio builder: instala dependências nativas e compila wheels (mysqlclient
# precisa de build-essential + default-libmysqlclient-dev para compilar).
#
# Estágio final: copia apenas os pacotes instalados, sem ferramentas de build.
#
# Python 3.12 escolhido por compatibilidade com Django 5.2, scikit-learn 1.8,
# mysqlclient 2.2.8 e demais dependências declaradas em requirements.txt.
# =============================================================================

# ── builder ──────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Dependências nativas necessárias para compilar mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
        pkg-config \
        default-libmysqlclient-dev \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── final ─────────────────────────────────────────────────────────────────────
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=setup.settings

# Runtime: libmysqlclient.so é necessário em tempo de execução (não só build)
RUN apt-get update && apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas os pacotes instalados pelo builder
COPY --from=builder /install /usr/local

WORKDIR /app

# Copia o código do projeto
COPY . /app/

# Diretórios que serão montados como volumes ou gerados em runtime
RUN mkdir -p /app/staticfiles /app/media/models

EXPOSE 8000
