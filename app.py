from flask import Flask, Response, g, jsonify, request
from datetime import datetime, timezone
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
import os
import socket
import time

app = Flask(__name__)

#Settings read once when the app starts
APP_NAME = "system-health-dashboard"
APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")
START_TIME = time.time()


def get_environment():
    # ENVIRONMENT wins; APP_ENV is still honoured so Mini Project 1 setups keep working
    return os.environ.get("ENVIRONMENT") or os.environ.get("APP_ENV", "development")


# Prometheus metrics. prometheus_client adds the _total suffix to counters itself.
REQUESTS = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
LATENCY = Histogram(
    "http_request_duration_seconds", "Request latency in seconds", ["endpoint"]
)


def endpoint_label():
    # Use the route pattern, not the raw path, so random URLs cannot create endless time series
    return request.url_rule.rule if request.url_rule else "unknown"


@app.before_request
def start_timer():
    g.start = time.perf_counter()


@app.after_request
def record_request(response):
    # Runs for every response, including the JSON 404 and any 500
    endpoint = endpoint_label()
    REQUESTS.labels(request.method, endpoint, str(response.status_code)).inc()
    LATENCY.labels(endpoint).observe(time.perf_counter() - g.get("start", time.perf_counter()))
    return response


@app.route("/health")
def health():
    uptime = round(time.time() - START_TIME, 1)
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": uptime
    })


@app.route("/version")
def version():
    return jsonify({
        "service": APP_NAME,
        "version": APP_VERSION
    })


@app.route("/environment")
def environment():
    return jsonify({
        "environment": get_environment(),
        "hostname": socket.gethostname()
    })


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)