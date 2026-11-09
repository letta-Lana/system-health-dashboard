from flask import Flask, jsonify
from datetime import datetime, timezone
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


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)