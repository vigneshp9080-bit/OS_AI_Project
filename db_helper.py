import config
from pymongo import MongoClient
import pandas as pd
import streamlit as st

def get_data_from_mongodb(limit=1000):
    """
    Connect to MongoDB and retrieve system data as a pandas DataFrame.
    """
    
    try:
        client = MongoClient(config.MONGO_URL)
        # Quick check
        # client.admin.command('ping') 
        
        db = client["os_monitoring"]
        collection = db["system_data"]
        
        # Fetch data, exclude _id
        cursor = collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
        data = list(cursor)
        
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        
        # Ensure columns are ordered/present
        expected_cols = ["timestamp", "system", "cpu", "ram", "disk", "anomaly"]
        # Filter to keep only relevant columns if extra exist, and ensure order
        cols_to_keep = [c for c in expected_cols if c in df.columns]
        df = df[cols_to_keep]
        
        # Convert timestamp to datetime if string (pymongo returns datetime objects usually)
        if 'timestamp' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
             df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Sort by timestamp ascending (Oldest -> Newest) so tail() gets Newest
        if 'timestamp' in df.columns:
            df = df.sort_values(by="timestamp", ascending=True).reset_index(drop=True)

        return df
        
    except Exception as e:
        print(f"Error fetching from MongoDB: {e}")
        return pd.DataFrame()
