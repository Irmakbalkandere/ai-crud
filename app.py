from flask import Flask
import os

app = Flask(__name__)

@app.get("/")
def home():
    return "Hello from Flask + MySQL (dockerized) 👋"

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
