FROM python:3.12-slim
WORKDIR /app
ENV GUARDRAILS_ASSET_ROOT=/app
ENV GUARDRAILS_PROPOSALS_PER_MINUTE=5
ENV GUARDRAILS_MAX_PROPOSALS_PER_PROCESS=100
ENV GUARDRAILS_DEMO_EXPIRES_AT=2026-08-06T23:59:59Z
COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts/verify_container_boundary.py ./scripts/verify_container_boundary.py
COPY data ./data
COPY evaluation ./evaluation
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["uvicorn", "guardrails.api:app", "--host", "0.0.0.0", "--port", "8000"]
