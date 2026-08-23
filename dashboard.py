from __future__ import annotations

from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
RESULTS_FILE = BASE_DIR / "data" / "simulation_results.json"

st.set_page_config(page_title="E-Toll Analytics Dashboard", layout="wide")
st.title("Automated E-Toll Plaza Analytics")

if not RESULTS_FILE.exists():
    st.warning("Run `python run_simulation.py` first to generate analytics data.")
    st.stop()

results = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
summary = results["summary"]
manual_df = pd.DataFrame(results["manual_results"])
automated_df = pd.DataFrame(results["automated_results"])

col1, col2, col3 = st.columns(3)
col1.metric("Vehicles Simulated", summary["vehicle_count"])
col2.metric("Manual Avg (min)", summary["manual_avg_minutes"])
col3.metric("Wait Reduction", f"{summary['wait_time_reduction_pct']}%")

comparison_df = pd.DataFrame(
    {
        "Mode": ["Manual", "Automated"],
        "Average Processing Minutes": [summary["manual_avg_minutes"], summary["automated_avg_minutes"]],
    }
)
st.plotly_chart(px.bar(comparison_df, x="Mode", y="Average Processing Minutes", color="Mode"), use_container_width=True)

route_mix = automated_df["routing_mode"].value_counts().rename_axis("Routing Mode").reset_index(name="Trips")
st.plotly_chart(px.pie(route_mix, names="Routing Mode", values="Trips", hole=0.45), use_container_width=True)

manual_wait = manual_df[["vehicle_id", "total_processing_minutes"]].rename(columns={"total_processing_minutes": "Manual"})
automated_wait = automated_df[["vehicle_id", "total_processing_minutes"]].rename(columns={"total_processing_minutes": "Automated"})
joined = manual_wait.merge(automated_wait, on="vehicle_id")
joined["Minutes Saved"] = joined["Manual"] - joined["Automated"]

st.subheader("Per-Vehicle Time Saved")
st.plotly_chart(px.line(joined, x="vehicle_id", y="Minutes Saved"), use_container_width=True)

st.subheader("Automated Sample")
st.dataframe(automated_df.head(15), use_container_width=True)
