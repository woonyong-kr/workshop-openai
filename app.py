from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# 공개 환경변수 먼저, 민감 환경변수 덮어쓰기
load_dotenv(".env.public")
load_dotenv(".env.secret")

app = Flask(__name__)

# MongoDB 연결
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/mydb")
client = MongoClient(mongo_uri)
db = client.get_default_database()


@app.route("/")
def index():
    r = os.getenv("BG_R", 255)
    g = os.getenv("BG_G", 255)
    b = os.getenv("BG_B", 255)
    return render_template("index.html", r=r, g=g, b=b)


@app.route("/health")
def health():
    try:
        client.admin.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return jsonify({
        "status": "ok",
        "db": db_status,
        "bg_color": {
            "r": os.getenv("BG_R", 255),
            "g": os.getenv("BG_G", 255),
            "b": os.getenv("BG_B", 255),
        }
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
