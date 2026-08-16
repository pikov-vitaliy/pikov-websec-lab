# syntax=docker/dockerfile:1.10@sha256:865e5dd094beca432e8c0a1d5e1c465db5f998dca4e439981029b3b81fb39ed5

# Pinned multi-platform digest for Python 3.12.14 slim (reviewed 2026-08-16).
FROM python:3.12.14-slim@sha256:dd29372629eeba2dd003fd9e9d35a5b8236c44727875a0364254b5127af88e65 AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /build

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
COPY requirements.lock ./requirements.lock
RUN pip install --require-hashes -r requirements.lock

FROM python:3.12.14-slim@sha256:dd29372629eeba2dd003fd9e9d35a5b8236c44727875a0364254b5127af88e65 AS runtime

LABEL org.opencontainers.image.title="Pikov WebSec Lab: Evil Sheep Trap" \
      org.opencontainers.image.description="Isolated educational lab for stored XSS in active SVG" \
      org.opencontainers.image.source="https://github.com/pikov-vitaliy/pikov-websec-lab" \
      org.opencontainers.image.url="https://github.com/nvmediagithub/evil_sheep_trap" \
      org.opencontainers.image.licenses="MIT"

ENV PATH="/venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=8080 \
    UPLOAD_DIR=/data/uploads

RUN groupadd --gid 10001 labuser \
    && useradd --uid 10001 --gid 10001 --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin labuser \
    && mkdir -p /app /data/uploads \
    && chown -R 10001:10001 /app /data

WORKDIR /app
COPY --from=builder /venv /venv
COPY --chown=10001:10001 app.py ./app.py
COPY --chown=10001:10001 src/ ./src/
COPY --chown=10001:10001 templates/ ./templates/
COPY --chown=10001:10001 static/ ./static/
COPY --chown=10001:10001 labs/ ./labs/

USER 10001:10001
EXPOSE 8080

HEALTHCHECK --interval=20s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2)"]

CMD ["python", "app.py"]
