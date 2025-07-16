# syntax=docker/dockerfile:1

######## 1. Deps ########
FROM python:3.13-slim AS deps
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=yes
COPY **requirements.txt** .                 # ← inside backend/
RUN pip install -r requirements.txt

######## 2. Builder (lint / tests) ########
FROM python:3.13-slim AS builder
WORKDIR /app
COPY --from=deps /usr/local /usr/local
COPY **requirements-dev.txt** .             # ← inside backend/
RUN pip install -r requirements-dev.txt
COPY . .                                    
RUN flake8 && black --check . && isort --check-only .

######## 3. Runner (prod) ########
FROM python:3.13-slim AS runner
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY --from=deps /usr/local /usr/local
COPY app /app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

######## 4. Dev (hot-reload) ########
FROM python:3.13-slim AS dev
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=yes
COPY requirements.txt requirements-dev.txt ./     
RUN pip install -r requirements.txt -r requirements-dev.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
