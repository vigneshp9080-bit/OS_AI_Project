# 🖥️ Intelligent AI-Powered OS Monitoring System

## 📖 Project Overview
This project is a **real-time, distributed system monitoring solution** that uses **Artificial Intelligence (Isolation Forest)** to detect potential system failures before they happen. Unlike traditional monitoring tools that rely on fixed thresholds (e.g., "Alert if CPU > 90%"), this system **learns** the normal behavior of your computer and flags unusual patterns (Anomalies).

It features a **Client-Server architecture**, a **Cloud Database (MongoDB)**, and a **Professional Dashboard** with live animations and forecasting.

---

## ✨ Key Features
- **Real-Time Monitoring**: Tracks CPU, RAM, and Disk usage every 5 seconds.
- **AI Anomaly Detection**: Uses unsupervised machine learning to detect strange behavior (e.g., high disk usage at 3 AM).
- **Cloud Storage**: All data is securely stored in **MongoDB Atlas**.
- **Interactive Dashboard**: A beautiful, dark-themed Streamlit UI with:
  - Live Gauge Charts (Plotly)
  - Historical Trend Lines
  - Future Resource Forecasting (Linear Regression)
  - Correlation Heatmaps
- **Instant Alerts**: Sends **Telegram Notifications** immediately when an anomaly is detected.

---

## 🏗️ System Architecture & Workflow

The system consists of three main components running simultaneously:

```mermaid
graph LR
    A[Agent (agent.py)] -->|Sends Metrics JSON| B[Server API (server.py)]
    B -->|Predicts Anomaly| C{AI Model}
    B -->|Saves Data| D[(MongoDB Cloud)]
    E[Dashboard (dashboard.py)] -->|Reads Data| D
    B -.->|Background Thread| F[Model Retraining]
```

### 1. **The Agent (`agent.py`)** 🕵️‍♂️
- **Role**: The "Security Camera".
- **Action**: Runs on the client machine. constantly reads system resources using `psutil`.
- **Output**: Sends a JSON packet to the Server API every 5 seconds.

### 2. **The Server (`server.py`)** 🧠
- **Role**: The "Brain".
- **Action**:
  - Receives data from the Agent.
  - Validates data using **Pydantic**.
  - Uses the **AnomalyDetector** class to check if the current usage is "Normal" (1) or an "Anomaly" (-1).
  - Stores the result + timestamp in **MongoDB**.
  - **Auto-Training**: A background thread automatically fetches history from the DB to retrain the AI model on startup.

### 3. **The Dashboard (`dashboard.py`)** 📊
- **Role**: The "Visualizer".
- **Action**:
  - Connects directly to MongoDB to fetch the latest data (sorted chronologically).
  - Displays live animated gauges and historical charts.
  - Shows alerts and future predictions.

---

## 🛠️ Technology Stack
- **Language**: Python 3.9+
- **Frontend**: Streamlit, Plotly, Custom CSS
- **Backend**: Flask (REST API)
- **Database**: MongoDB Atlas (Cloud)
- **AI/ML**: Scikit-Learn (Isolation Forest, Linear Regression)
- **Utils**: Pydantic (Validation), Psutil (Metrics)

---

## 📂 Project Structure
```
OS_AI_PROJECT/
│
├── agent.py               # Client script to collect & send metrics
├── server.py              # Flask API + AI Logic Integration
├── dashboard.py           # Streamlit Visualization UI
├── anomaly_detector.py    # AI Class (Isolation Forest logic)
├── db_helper.py           # Database connection & data fetching utilities
├── config.py              # Configuration secrets (API Keys, DB URL)
├── style.css              # Custom CSS for the Dashboard
├── requirements.txt       # Project dependencies
└── README.md              # Project Documentation
```

---

## 🚀 How to Run the Project

You need to run **three separate terminals** for the full system to work.

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Start the Brain (Server)**
This must run first to accept data and connect to the database.
```bash
python server.py
# Output: Connected to MongoDB successfully!
```

### 3. **Start the Agent**
This starts collecting metrics from your computer.
```bash
python agent.py
# Output: ✅ Data Sent: {'system': 'YourPC', 'cpu': 12.5 ...}
```

### 4. **Launch the Dashboard**
This opens the web interface in your browser.
```bash
streamlit run dashboard.py
```

---

## 🔮 Future Roadmap
- [ ] **Authentication**: Add login to the dashboard and API keys for the agent.
- [ ] **Multi-Agent Support**: Enhance dashboard to toggle between dozens of servers.
- [ ] **Dockerization**: Containerize the app for easy deployment.
