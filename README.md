# cf_speedtest_exporter

This repository contains a Docker-based Prometheus exporter for the Cloudflare speed test CLI. It is designed for Synology NAS and for a Grafana + Prometheus monitoring stack.

## What this does

- Runs the Cloudflare speed test CLI in a container.
- Exposes a Prometheus-compatible endpoint at `/metrics`.
- Publishes useful values from the CLI output, including download speed, upload speed, latency, jitter, and loaded latency.
- Includes a Grafana dashboard JSON file to import.

## Files

- `exporter.py` - lightweight HTTP server that runs the CLI and serves Prometheus metrics.
- `Dockerfile` - builds the image with the Cloudflare CLI installed.
- `docker-compose.yml` - local run configuration.
- `grafana/dashboard.json` - starter dashboard for Grafana.
- `tests/test_exporter.py` - simple regression tests.

## Build locally

```bash
docker build -t cf_speedtest_exporter:latest .
```

## Run locally

```bash
docker compose up --build -d
```

Then visit:

- `http://localhost:8000/metrics`

## GitHub Codespaces

1. Open this repository in GitHub Codespaces.
2. In the terminal, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m unittest discover -s tests
```

3. To build the container locally in Codespaces:

```bash
docker build -t cf_speedtest_exporter:latest .
```

## Synology NAS usage

1. Push this repository to GitHub.
2. In Docker on Synology, create a new image from the GitHub repository or build it manually.
3. Run the container with port `8000` exposed.
4. Add a Prometheus scrape target for `http://<synology-ip>:8000/metrics`.
5. Import the Grafana dashboard from `grafana/dashboard.json`.

## Prometheus scrape config example

```yaml
scrape_configs:
  - job_name: cf_speedtest_exporter
    static_configs:
      - targets: ["<synology-ip>:8000"]
```

## Notes

The exporter currently uses the Cloudflare CLI in JSON mode. For best results on Synology, use a container with enough access to the host network and allow the CLI to run its test normally.
