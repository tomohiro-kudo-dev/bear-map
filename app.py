from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, render_template


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "2025sapporobearappearance.csv"

app = Flask(__name__)


def classify_status(status: str) -> str:
    text = str(status)
    if "負傷" in text or "けが" in text or "怪我" in text:
        return "injury"
    if "駆除" in text or "捕獲" in text:
        return "captured"
    if "足跡" in text or "ふん" in text or "痕跡" in text or "カメラ" in text:
        return "trace"
    if "親子" in text or "複数" in text or "2頭" in text or "３頭" in text or "3頭" in text:
        return "family"
    return "sighting"


def load_points() -> list[dict]:
    df = pd.read_csv(CSV_PATH)
    required = ["日付", "時刻", "区", "出没場所", "緯度", "経度", "状況"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"CSVに必要な列がありません: {', '.join(missing)}")

    points: list[dict] = []
    for index, row in df.iterrows():
        lat = pd.to_numeric(row["緯度"], errors="coerce")
        lng = pd.to_numeric(row["経度"], errors="coerce")
        if pd.isna(lat) or pd.isna(lng):
            continue

        status = "" if pd.isna(row["状況"]) else str(row["状況"])
        points.append(
            {
                "id": int(index),
                "date": "" if pd.isna(row["日付"]) else str(row["日付"]),
                "time": "" if pd.isna(row["時刻"]) else str(row["時刻"]),
                "ward": "" if pd.isna(row["区"]) else str(row["区"]),
                "place": "" if pd.isna(row["出没場所"]) else str(row["出没場所"]),
                "status": status,
                "category": classify_status(status),
                "lat": float(lat),
                "lng": float(lng),
            }
        )
    return points


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/points")
def api_points():
    points = load_points()
    return jsonify({"points": points, "count": len(points)})


if __name__ == "__main__":
    app.run(debug=True)
