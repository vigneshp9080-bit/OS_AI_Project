from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import threading
from pydantic import BaseModel, ValidationError
from anomaly_detector import AnomalyDetector
import config

app = Flask(__name__)

# -----------------------------
# Pydantic Model for Validation
# -----------------------------
class SystemData(BaseModel):
    system: str
    cpu: float
    ram: float
    disk: float

# -----------------------------
# MongoDB Connection
# -----------------------------
try:
    client = MongoClient(config.MONGO_URL)
    # Check connection
    client.admin.command('ping')
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    # In production, we might want to exit here, but for now allow running (without DB features working properly)
    client = None

db = client["os_monitoring"] if client else None
collection = db["system_data"] if db is not None else None

# -----------------------------
# Initialize Anomaly Detector
# -----------------------------
detector = AnomalyDetector()

def train_model_from_db():
    """
    Background task to train the model from DB data.
    """
    if collection is None:
        return
        
    print("Starting background training...")
    # Fetch historical data for training
    # Limit to reasonable amount for performance, e.g., last 1000 records
    try:
        cursor = collection.find({}, {"_id": 0, "cpu": 1, "ram": 1, "disk": 1}).sort("timestamp", -1).limit(1000)
        data_list = list(cursor)
        
        if len(data_list) >= 10:
            print(f"Training model with {len(data_list)} records from DB...")
            df = pd.DataFrame(data_list)
            detector.train(df)
            print("Model trained successfully via background thread.")
        else:
            print("Not enough data in DB to train model yet.")
    except Exception as e:
        print(f"Background training failed: {e}")

# Train on startup using a separate thread so it doesn't block server start
training_thread = threading.Thread(target=train_model_from_db)
training_thread.daemon = True # Daemon thread exits when main program exits
training_thread.start()

# -----------------------------
# API Route
# -----------------------------
@app.route("/data", methods=["POST"])
def receive_data():
    if collection is None:
        return jsonify({"error": "Database not connected"}), 500

    try:
        # Pydantic Validation
        try:
            input_data = SystemData(**request.json)
        except ValidationError as e:
            return jsonify({"error": e.errors()}), 400
            
        data = input_data.dict() # Convert back to dict for generic usage
        
        # Add timestamp
        data["timestamp"] = datetime.now()

        # Detect Anomaly
        # Default to 1 (normal) if model not trained
        anomaly_status = 1
        if detector.is_trained:
            try:
                anomaly_status = detector.predict_live(data["cpu"], data["ram"], data["disk"])
            except Exception as e:
                print(f"Prediction error: {e}")
        
        data["anomaly"] = anomaly_status

        # Insert into MongoDB
        collection.insert_one(data)
        
        return jsonify({
            "status": "Data Stored",
            "anomaly": int(anomaly_status),
            "timestamp": data["timestamp"].isoformat()
        })

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
