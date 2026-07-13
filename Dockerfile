FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=9877

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://raw.githubusercontent.com/kavehtehrani/cloudflare-speed-cli/main/install.sh | sh \
    && install -m 0755 /root/.local/bin/cloudflare-speed-cli /usr/local/bin/cloudflare-speed-cli

WORKDIR /app
COPY exporter.py /app/exporter.py

EXPOSE 9877
CMD ["python", "/app/exporter.py"]
