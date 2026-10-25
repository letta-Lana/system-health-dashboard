from flask import Flask, jsonify, request 
from datetime import datetime 
import json
import os

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status":"healthy"})

@app.route("/version")
def version():
    return jsonify({"version":"1.0.0"})

@app.route("/environment")
def environment():
    current_env = os.environ.get("APP_ENV", "development")
    return jsonify({"environment": current_env})

if __name__ == "__main__":
    app.run(debug=True, port=5000)


