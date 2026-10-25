from flask import Flask, jsonify
import os

app = Flask(__name__)


@app.route("/environment")
def environment():
    current_env = os.environ.get("APP_ENV", "development")
    return jsonify({"environment": current_env})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
