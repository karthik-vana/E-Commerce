# ─────────────────────────────────────────────────────────────────────
# ShopMind AI — Dockerfile
# Multi-stage: keeps final image lean
# ─────────────────────────────────────────────────────────────────────

# ── Stage 1: Build deps ────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# ── Stage 2: Runtime image ─────────────────────────────────────────────
FROM python:3.11-slim

# Non-root user for security
RUN useradd -m -u 1000 shopmind
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/shopmind/.local
ENV PATH=/home/shopmind/.local/bin:$PATH

# Copy application code
COPY --chown=shopmind:shopmind . .

# Create logs directory
RUN mkdir -p logs && chown shopmind:shopmind logs

USER shopmind

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0", \
            "--server.headless=true", \
            "--browser.gatherUsageStats=false"]
