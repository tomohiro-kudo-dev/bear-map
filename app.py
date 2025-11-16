from flask import Flask, jsonify, render_template
import pandas as pd
import os

app = Flask(__name__)

# --- CSV のパス ---
CSV_PATH = os.path.join("data", "2025sapporobearappearance.csv")


def load_points():
    """CSV を読み込み、日本語列名に対応して API 用データへ変換"""
    df = pd.read_csv(CSV_PATH)

    # 日本語 → 英語 のマッピング
    column_map = {
        "日付": "date",
        "時刻": "time",
        "区": "ward",
        "出没場所": "place",
        "緯度": "lat",
        "経度": "lng",
        "状況": "status"
    }

    # 英語名の列を作成
    for jp, en in column_map.items():
        if jp in df.columns:
            df[en] = df[jp]
        else:
            df[en] = ""

    points = []
    for _, row in df.iterrows():
        try:
            lat = float(row["lat"])
            lng = float(row["lng"])
        except:
            continue  # 緯度経度がない行はスキップ

        points.append({
            "date": str(row["date"]),
            "time": str(row["time"]),
            "ward": str(row["ward"]),
            "place": str(row["place"]),
            "status": str(row["status"]),
            "lat": lat,
            "lng": lng
        })

    return points



# ----------------------------------------------------------
# ルート: index.html を返す
# ----------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ----------------------------------------------------------
# API: クマ出没地点データを返す
# ----------------------------------------------------------
@app.route("/api/points")
def api_points():
    points = load_points()
    return jsonify({"points": points})


# ----------------------------------------------------------
# ローカル実行用
# ----------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
