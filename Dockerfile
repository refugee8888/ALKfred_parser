FROM python:3.12-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# System deps (git etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libpq-dev \
    gcc \
    build-essential \
    postgresql-client \
 && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY src ./src

# dbt project
COPY dbt_project.yml .
COPY models ./models

# dbt profiles (uses env vars, no hardcoded credentials)
COPY profiles.yml /root/.dbt/profiles.yml



FROM mcr.microsoft.com/devcontainers/python:3.12

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    git \
 && rm -rf /var/lib/apt/lists/*

# Prepare non-root user, but DON'T switch users here
RUN useradd -m -u 1001 appuser
USER appuser

# Keep root as final image user so devcontainer "features" can build
# (Dev Containers will run as appuser because we set remoteUser in devcontainer.json)
CMD ["bash"]
