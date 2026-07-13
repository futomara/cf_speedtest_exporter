import json
import os
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List


class SpeedtestExporterHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/metrics":
            self.send_response(404)
            self.end_headers()
            return

        payload = run_speedtest()
        metrics = generate_prometheus_metrics(payload)
        body = metrics.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: ARG002
        return


def resolve_cli_path() -> str:
    configured = os.environ.get("CLOUDFLARE_SPEEDCLI_BIN")
    if configured:
        return configured

    candidate_paths = [
        "/root/.local/bin/cloudflare-speed-cli",
        "/usr/local/bin/cloudflare-speed-cli",
        "/usr/bin/cloudflare-speed-cli",
        "cloudflare-speed-cli",
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            return path
    return "cloudflare-speed-cli"


def run_speedtest() -> Dict[str, Any]:
    cli = resolve_cli_path()
    command = [cli, "--json"]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=True, timeout=600)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Cloudflare CLI not found: {cli}") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Cloudflare CLI failed: {exc.stderr or exc.stdout}") from exc

    payload = json.loads(completed.stdout)
    if isinstance(payload, dict):
        return payload
    raise RuntimeError("Cloudflare CLI output is not a JSON object")


def flatten_metrics(payload: Any, prefix: str = "cf_speedtest") -> Dict[str, Any]:
    if isinstance(payload, dict):
        values: Dict[str, Any] = {}
        for key, value in payload.items():
            new_prefix = f"{prefix}_{normalize_key(key)}"
            if isinstance(value, (dict, list)):
                values.update(flatten_metrics(value, prefix=new_prefix))
            else:
                values[new_prefix] = value
        return values
    if isinstance(payload, list):
        values = {}
        for index, item in enumerate(payload):
            new_prefix = f"{prefix}_{index}"
            if isinstance(item, (dict, list)):
                values.update(flatten_metrics(item, prefix=new_prefix))
            else:
                values[new_prefix] = item
        return values
    return {prefix: payload}


def normalize_key(key: str) -> str:
    return key.strip().lower().replace("-", "_").replace(" ", "_")


def generate_prometheus_metrics(payload: Dict[str, Any]) -> str:
    metrics = flatten_metrics(payload)
    lines = ["# HELP cf_speedtest_last_run_seconds Unix timestamp of the last speed test run", "# TYPE cf_speedtest_last_run_seconds gauge"]
    lines.append(f"cf_speedtest_last_run_seconds {int(time.time())}")

    for key, value in sorted(metrics.items()):
        if isinstance(value, bool):
            numeric = 1 if value else 0
        elif isinstance(value, (int, float)):
            numeric = value
        else:
            continue
        lines.append(f"{key} {numeric}")
    return "\n".join(lines) + "\n"


def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer((host, port), SpeedtestExporterHandler)
    print(f"Serving on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
