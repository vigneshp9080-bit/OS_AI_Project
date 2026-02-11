import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

import config
from anomaly_detector import AnomalyDetector, send_telegram_alert
from db_helper import get_data_from_mongodb

# ----------------------
# Helper: Inject CSS
# ----------------------
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ----------------------
# Page Config
# ----------------------
st.set_page_config(
    page_title="AI OS Monitor", 
    page_icon="🖥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    local_css("style.css")
except:
    st.warning("style.css not found, using default styles.")

# Auto-refresh
st_autorefresh(interval=3000, key="datarefresh") # Faster refresh 3s

# ----------------------
# Sidebar
# ----------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/919/919853.png", width=64)
    st.markdown("## AI Monitor Control")
    st.markdown("---")
    
    # Load Data (Once per refresh)
    raw_data = get_data_from_mongodb(limit=500)
    
    if raw_data.empty:
        st.error("❌ No Data Found")
        st.info("Check if server.py & agent.py are running.")
        st.stop()
        
    raw_data.columns = raw_data.columns.str.lower()
    
    # System Selector
    systems = raw_data["system"].unique()
    selected_system = st.selectbox("Select System", systems, index=0)
    
    st.markdown("---")
    st.markdown("### Settings")
    heatmap_on = st.toggle("Show Correlation Heatmap", False)
    forecast_on = st.toggle("Show Future Forecast", True)
    
    st.markdown("---")
    st.caption(f"Last Updated: {time.strftime('%H:%M:%S')}")

# Filter Data for Selected System
df = raw_data[raw_data["system"] == selected_system].copy()
# Sort for chronological display (Oldest -> Newest) is default from db_helper now
# But plot likes X axis sorted
df = df.sort_values("timestamp") 

# Get Latest Record
latest = df.iloc[-1]
cpu = latest["cpu"]
ram = latest["ram"]
disk = latest["disk"]

# ----------------------
# Header Section
# ----------------------
col_head_1, col_head_2 = st.columns([3, 1])

with col_head_1:
    st.markdown(f"# 🖥 {selected_system}")
    st.caption("Live AI-Powered System Monitoring Dashboard")

# ----------------------
# AI Anomaly Detection Logic
# ----------------------
detector = AnomalyDetector(contamination=0.1)
is_trained = False
anomaly_status = 1 # Normal

# Train if enough data
if len(df) >= 10:
    detector.train(df)
    is_trained = True
    try:
        anomaly_status = detector.predict_live(cpu, ram, disk)
    except:
        pass

# Status Badge
with col_head_2:
    if anomaly_status == -1:
        st.markdown("""
            <div class="metric-card" style="border-left: 4px solid #f43f5e; text-align: center;">
                <div class="metric-label" style="color: #f43f5e;">SYSTEM STATUS</div>
                <div class="metric-value" style="color: #f43f5e;">⚠️ CRITICAL</div>
                <div class="status-badge status-anomaly">Anomaly Detected</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Telegram Alert Logic
        alert_msg = f"🚨 {selected_system} ANOMALY DETECTED!\nCPU: {cpu}%\nRAM: {ram}%\nDisk: {disk}%"
        if "last_anomaly_alert" not in st.session_state:
            st.session_state.last_anomaly_alert = 0
        if time.time() - st.session_state.last_anomaly_alert > 60:
            send_telegram_alert(config.TELEGRAM_TOKEN, config.TELEGRAM_CHAT_ID, alert_msg)
            st.session_state.last_anomaly_alert = time.time()
            st.toast("🚨 Anomaly Alert Sent!", icon="🔥")
            
    else:
        st.markdown("""
            <div class="metric-card" style="border-left: 4px solid #10b981; text-align: center;">
                <div class="metric-label" style="color: #10b981;">SYSTEM STATUS</div>
                <div class="metric-value" style="color: #10b981;">✅ HEALTHY</div>
                <div class="status-badge status-normal">Running Normally</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------
# Key Metrics Row (Gauge Charts + Cards using Plotly Indicators)
# ----------------------
def make_gauge(title, value, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'size': 24, 'color': "#94a3b8"}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#334155"},
            'bar': {'color': color},
            'bgcolor': "rgba(30, 41, 59, 0.5)",
            'borderwidth': 2,
            'bordercolor': "#334155",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(16, 185, 129, 0.1)'},
                {'range': [50, 80], 'color': 'rgba(245, 158, 11, 0.1)'},
                {'range': [80, 100], 'color': 'rgba(244, 63, 94, 0.1)'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90}}))
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)", font = {'color': "#e2e8f0", 'family': "Inter"}, height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.plotly_chart(make_gauge("CPU Load", cpu, "#3b82f6"), use_container_width=True)
    st.markdown(f'<div style="text-align: center; color: #94a3b8;">{cpu}% Utilized</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.plotly_chart(make_gauge("RAM Usage", ram, "#8b5cf6"), use_container_width=True)
    st.markdown(f'<div style="text-align: center; color: #94a3b8;">{ram}% Utilized</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.plotly_chart(make_gauge("Disk Space", disk, "#f59e0b"), use_container_width=True)
    st.markdown(f'<div style="text-align: center; color: #94a3b8;">{disk}% Utilized</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------
# Charts Section
# ----------------------
st.markdown("### 📈 Performance Trends")

# Prepare Time Series Chart
fig_line = px.line(df.tail(100), x="timestamp", y=["cpu", "ram", "disk"], 
              labels={"value": "Usage (%)", "variable": "Metric"},
              color_discrete_map={"cpu": "#3b82f6", "ram": "#8b5cf6", "disk": "#f59e0b"},
              template="plotly_dark")

fig_line.update_layout(
    plot_bgcolor="rgba(30, 41, 59, 0.4)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_family="Inter",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
fig_line.update_xaxes(showgrid=False)
fig_line.update_yaxes(showgrid=True, gridcolor="rgba(148, 163, 184, 0.1)")

st.plotly_chart(fig_line, use_container_width=True)

# ----------------------
# Dual Column: Anomalies & Forecast
# ----------------------
c1, c2 = st.columns([1, 1])

with c1:
    if heatmap_on:
        st.markdown("### 🌡 Correlation Heatmap")
        corr = df[["cpu", "ram", "disk"]].corr()
        fig_heat = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", template="plotly_dark")
        fig_heat.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.markdown("### ⚠️ Recent Anomalies (Last 50)")
        if is_trained:
             # Re-detect just for display purposes on historical
            historical_check = df.tail(50).copy()
            historical_check['anomaly'] = detector.detect_dataset(historical_check)
            anomalies = historical_check[historical_check['anomaly'] == -1]
            
            if not anomalies.empty:
                st.dataframe(
                    anomalies[['timestamp', 'cpu', 'ram', 'disk']].style.format(precision=2),
                    use_container_width=True,
                    height=300
                )
            else:
                st.success("No anomalies found in recent history.")
                st.image("https://cdn-icons-png.flaticon.com/512/4413/4413985.png", width=100)
                st.caption("Clean Bill of Health")
        else:
            st.info("Gathering more data for analysis...")

with c2:
    if forecast_on:
        st.markdown("### 🔮 Future Forecast (CPU)")
        # Simple Linear Regression for Forecast
        df_forecast = df.tail(100).copy()
        df_forecast["index"] = np.arange(len(df_forecast))
        
        model = LinearRegression()
        model.fit(df_forecast[["index"]], df_forecast["cpu"])
        
        future_steps = 20
        last_idx = df_forecast["index"].iloc[-1]
        future_indices = np.arange(last_idx + 1, last_idx + future_steps + 1).reshape(-1, 1)
        future_preds = model.predict(future_indices)
        
        # Plot
        fig_fore = go.Figure()
        
        # Historical
        fig_fore.add_trace(go.Scatter(x=np.arange(len(df_forecast)), y=df_forecast["cpu"], 
                                      mode='lines', name='Actual', line=dict(color='#3b82f6', width=2)))
        
        # Forecast
        fig_fore.add_trace(go.Scatter(x=np.arange(last_idx, last_idx + future_steps), 
                                      y=future_preds, 
                                      mode='lines+markers', name='Forecast', line=dict(color='#10b981', dash='dot')))
        
        fig_fore.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               hovermode="x unified", font_family="Inter", height=300,
                               margin=dict(l=10, r=10, t=30, b=10))
        
        st.plotly_chart(fig_fore, use_container_width=True)

# ----------------------
# Threshold Alerts (Backup)
# ----------------------
# Keeping original threshold logic but silent in UI to avoid clutter, runs in background
if "last_alert_time" not in st.session_state:
    st.session_state.last_alert_time = 0
    
if time.time() - st.session_state.last_alert_time > 60:
    thresh_msg = None
    if cpu > 90: thresh_msg = f"⚠️ {selected_system} CPU Critical: {cpu}%"
    elif ram > 90: thresh_msg = f"⚠️ {selected_system} RAM Critical: {ram}%"
    elif disk > 95: thresh_msg = f"⚠️ {selected_system} Disk Full: {disk}%"
    
    if thresh_msg:
        st.toast(thresh_msg, icon="⚠️")
        try:
            send_telegram_alert(config.TELEGRAM_TOKEN, config.TELEGRAM_CHAT_ID, thresh_msg)
            st.session_state.last_alert_time = time.time()
        except:
             pass