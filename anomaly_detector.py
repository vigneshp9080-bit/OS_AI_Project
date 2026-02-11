import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import requests

class AnomalyDetector:
    """
    A reusable class for detecting system anomalies using Isolation Forest.
    """
    def __init__(self, contamination=0.1, random_state=42):
        """
        Initialize the AnomalyDetector.
        
        Args:
            contamination (float): The amount of contamination of the data set, i.e. the proportion of outliers in the data set.
            random_state (int): Controls the pseudo-randomness of the selection of the feature and split values.
        """
        self.model = IsolationForest(contamination=contamination, random_state=random_state)
        self.is_trained = False
        self.feature_cols = ['cpu', 'ram', 'disk']

    def train(self, dataframe: pd.DataFrame):
        """
        Train the Isolation Forest model on the provided dataframe.
        
        Args:
            dataframe (pd.DataFrame): Data containing 'cpu', 'ram', and 'disk' columns.
        """
        if len(dataframe) < 10:
            print("Warning: Dataset is too small for reliable training. Need at least 10 samples.")
        
        # Ensure we have the required columns
        for col in self.feature_cols:
            if col not in dataframe.columns:
                raise ValueError(f"Missing required column: {col}")
        
        X = dataframe[self.feature_cols]
        self.model.fit(X)
        self.is_trained = True

    def detect_dataset(self, dataframe: pd.DataFrame) -> pd.Series:
        """
        Detect anomalies in the provided historical dataframe.
        
        Args:
            dataframe (pd.DataFrame): Data to check.
            
        Returns:
            pd.Series: Series containing -1 (anomaly) and 1 (normal).
        """
        if not self.is_trained:
            raise RuntimeError("Model is not trained. Call train() first.")
            
        X = dataframe[self.feature_cols]
        return self.model.predict(X)

    def predict_live(self, cpu: float, ram: float, disk: float) -> int:
        """
        Predict anomaly for live incoming metrics.
        
        Args:
            cpu (float): CPU usage percentage.
            ram (float): RAM usage percentage.
            disk (float): Disk usage percentage.
            
        Returns:
            int: 1 for normal behaviour, -1 for anomaly.
        """
        if not self.is_trained:
            # If not trained, fallback or raise. 
            # For robustness in a live system starting up, we might return 1 (normal) or raise.
            # Here we'll return 1 but log a warning if possible, or just raise to enforce training.
            # Given the requirements, let's assume valid flow involves training first.
            raise RuntimeError("Model is not trained. Call train() first.")
            
        sample = pd.DataFrame([[cpu, ram, disk]], columns=self.feature_cols)
        prediction = self.model.predict(sample)
        return int(prediction[0])

# Helper function for Telegram alerts (as requested)
def send_telegram_alert(token: str, chat_id: str, message: str):
    """
    Send a Telegram alert.
    """
    if token == "YOUR_TOKEN" or chat_id == "YOUR_CHAT_ID":
        # Placeholder check to avoid API errors during testing if credentials aren't set
        print(f"Telegram Alert (Simulated): {message}")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        response = requests.post(url, data={
            "chat_id": chat_id,
            "text": message
        })
        if response.status_code != 200:
            print(f"Failed to send Telegram alert: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")
