from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

FILE = "cloud_data.csv"

@app.route("/data", methods=["POST"])
def receive_data():
    data = request.json

    df = pd.DataFrame([data])

    if not os.path.exists(FILE):
        df.to_csv(FILE, index=False)
    else:
        df.to_csv(FILE, mode="a", header=False, index=False)

    return jsonify({"status": "received"})


app.run(host="0.0.0.0", port=5000)
