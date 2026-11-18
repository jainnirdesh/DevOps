import os
import socket
import redis
from flask import Flask, jsonify

app = Flask(__name__)
store = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), port=6379, decode_responses=True)

@app.get("/")
def index():
    return jsonify(message="Lab 2 Compose with Redis", hostname=socket.gethostname(), visits=store.incr("visits"))

@app.get("/health")
def health():
    store.ping()
    return jsonify(status="healthy")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
