FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (git etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
 && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY src ./src

# Prepare non-root user, but DON'T switch users here
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Keep root as final image user so devcontainer "features" can build
# (Dev Containers will run as appuser because we set remoteUser in devcontainer.json)
CMD ["bash"]
