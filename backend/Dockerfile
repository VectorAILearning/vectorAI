ARG REGISTRY=docker.io
FROM ${REGISTRY}/python:3.12.9
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --locked

COPY app /app/app

EXPOSE 8000
