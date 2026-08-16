# =============================================================================
# Evil Sheep Trap — Educational Stored XSS Training Platform
# Multi-stage Dockerfile with security hardening
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Build — install Python dependencies
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

# Install deps in a virtual env for clean extraction
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/venv -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Runtime — minimal image, non-root user
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

# Metadata labels
LABEL org.opencontainers.image.title="Evil Sheep Trap" \
      org.opencontainers.image.description="Educational Stored XSS Training Platform" \
      org.opencontainers.image.version="2.0.0" \
      org.opencontainers.image.licenses="MIT"

# Security: run as non-root
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser \
    && mkdir -p /data/uploads /app/templates \
    && chown -R appuser:appuser /data /app

WORKDIR /app

# Copy venv from builder
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy application code
COPY app.py .
COPY templates/ templates/

# Ensure upload dir is writable
RUN chmod -R 755 /data/uploads

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Switch to non-root user
USER appuser

ENV PYTHONUNBUFFERED=1 \
    UPLOAD_DIR=/data/uploads \
    LOG_LEVEL=INFO

CMD ["python", "app.py"]
