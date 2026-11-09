from flask import Flask, Response, g, jsonify, request
from datetime import datetime, timezone
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
import json
import logging
import os
import socket
import sys
import time

app = Flask(__name__)

#Settings read once when the app starts
APP_NAME = "system-health-dashboard"
APP_VERSION = os.environ.get("APP_VERSION", "2.0.0")
START_TIME = time.time()


def get_environment():
    # ENVIRONMENT wins; APP_ENV is still honoured so Mini Project 1 setups keep working
    return os.environ.get("ENVIRONMENT") or os.environ.get("APP_ENV", "development")


# Structured logging: one JSON object per line on stdout, so Docker and Promtail can collect it
logger = logging.getLogger("system-health")
logger.setLevel(logging.INFO)
logger.propagate = False
_stdout_handler = logging.StreamHandler(sys.stdout)
_stdout_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(_stdout_handler)
# Werkzeug's own access log is plain text; our JSON line replaces it
logging.getLogger("werkzeug").setLevel(logging.ERROR)


def log_request(endpoint, status):
    if status >= 500:
        level = "ERROR"
    elif status >= 400:
        level = "WARNING"
    else:
        level = "INFO"
    logger.log(getattr(logging, level), json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "message": g.get("log_message", "request completed"),
        "endpoint": endpoint,
        "path": request.path,
        "method": request.method,
        "status": status,
        "environment": get_environment(),
    }))


# Prometheus metrics. prometheus_client adds the _total suffix to counters itself.
REQUESTS = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
LATENCY = Histogram(
    "http_request_duration_seconds", "Request latency in seconds", ["endpoint"]
)
# Info-style gauge: the value is always 1, the information is in the labels
APP_INFO = Gauge(
    "app_info", "Running version and environment (value is always 1)", ["version", "environment"]
)
APP_INFO.labels(APP_VERSION, get_environment()).set(1)
# Custom metric: resets to 0 on every restart, so a drop shows a crash or a redeploy
UPTIME = Gauge("app_uptime_seconds", "Seconds since the app started")
UPTIME.set_function(lambda: time.time() - START_TIME)


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
    log_request(endpoint, response.status_code)
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
    # run_simple instead of app.run: app.run prints a plain-text banner that would break the JSON-only stdout
    from werkzeug.serving import run_simple

    run_simple("0.0.0.0", 5000, app, threaded=True)