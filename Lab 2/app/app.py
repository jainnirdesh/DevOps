import os
import socket
from pathlib import Path
from threading import Lock
from flask import Flask, jsonify

app = Flask(__name__)
lock = Lock()
counter_path = Path(os.environ.get("DATA_DIR", "/data")) / "counter.txt"

@app.get("/")
def index():
    with lock:
        counter_path.parent.mkdir(parents=True, exist_ok=True)
        count = int(counter_path.read_text()) + 1 if counter_path.exists() else 1
        counter_path.write_text(str(count))
    return jsonify(message=os.environ.get("APP_MESSAGE", "Welcome to Lab 2 - VERSION 1.0"), hostname=socket.gethostname(), visits=count)

@app.get("/health")
def health():
    return jsonify(status="healthy")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
