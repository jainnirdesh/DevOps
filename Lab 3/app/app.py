"""Simple Flask app for Lab 3 — Monitoring, Logging & DevSecOps"""
import os
import logging
import json
import socket
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from flask import Flask, jsonify

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

app = Flask(__name__)
REQUESTS = Counter("lab3_http_requests_total", "Application requests", ["method", "path", "status"])


@app.after_request
def observe(response):
    from flask import request
    if request.path != "/metrics":
        REQUESTS.labels(request.method, request.path, str(response.status_code)).inc()
        event = {"service": "lab3-flask", "method": request.method, "path": request.path, "status": response.status_code}
        app.logger.info(json.dumps(event))
        try:
            with socket.create_connection((os.getenv("LOGSTASH_HOST", "host.docker.internal"), int(os.getenv("LOGSTASH_PORT", "5002"))), timeout=1) as connection:
                connection.sendall((json.dumps(event) + "\n").encode())
        except OSError:
            pass
    return response

FEATURE_FLAGS = {
    "dark_mode": os.environ.get("FLAG_DARK_MODE", "false").lower() == "true",
    "beta_ui": os.environ.get("FLAG_BETA_UI", "false").lower() == "true",
}


@app.route("/")
def index():
    app.logger.info("GET / called")
    return jsonify({
        "message": "Lab 3 Flask App",
        "feature_flags": FEATURE_FLAGS,
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
