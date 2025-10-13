# Base: small, reliable
FROM python:3.12-slim

# Faster, cleaner Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir
WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt ./

# Install deps (add build tools later only if a wheel fails)
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src ./src
COPY utils.py models.py ./

# Non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Ensure data dir exists (will usually be a bind mount)
RUN mkdir -p /app/data

# Default: do nothing dangerous; override via compose or devcontainer
CMD ["python", "--version"]
