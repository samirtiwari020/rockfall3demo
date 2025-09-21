import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px

# --- Streamlit Page Config ---
st.set_page_config(page_title="Rockfall Prediction Dashboard", layout="wide")
st.title("🪨 AI-based Rockfall Prediction Dashboard")

# --- Sidebar: Simulated Inputs ---
st.sidebar.header("Sensor Inputs")
rainfall = st.sidebar.slider("Rainfall (mm)", 0, 200, 50)
displacement = st.sidebar.slider("Displacement (mm)", 0, 50, 10)
strain = st.sidebar.slider("Strain (mm/m)", 0, 5, 1)

# Update button
if st.sidebar.button("Update Risk"):
    st.session_state["update"] = True
else:
    if "update" not in st.session_state:
        st.session_state["update"] = True

# --- Initialize Zones ---
zone_coords = {
    "Zone 1": [28.5, 77.0],
    "Zone 2": [28.51, 77.01],
    "Zone 3": [28.52, 77.02],
    "Zone 4": [28.53, 77.03],
}

# --- Risk Calculation Function ---
def calculate_risk(rainfall, displacement, strain):
    risk_data = []
    for zone, coord in zone_coords.items():
        base_risk = 20  # baseline
        prob = base_risk + int(rainfall * 0.3) + int(displacement * 2) + int(strain * 5)
        prob = max(0, min(prob, 100))  # clamp 0-100

        if prob > 70:
            risk = "High"
            color = "red"
        elif prob > 40:
            risk = "Medium"
            color = "orange"
        else:
            risk = "Low"
            color = "green"

        risk_data.append({"Zone": zone, "Coord": coord, "Risk Level": risk, "Probability": prob, "Color": color})
    return pd.DataFrame(risk_data)

# --- Only Update When Needed ---
if st.session_state["update"]:
    df_risk = calculate_risk(rainfall, displacement, strain)

    # --- Layout ---
    col1, col2 = st.columns([2, 1])

    # --- Column 1: Map ---
    with col1:
        st.subheader("📍 Risk Map")

        m = folium.Map(location=[28.515, 77.015], zoom_start=14)

        for _, row in df_risk.iterrows():
            folium.CircleMarker(
                location=row["Coord"],
                radius=15,
                color=row["Color"],
                fill=True,
                fill_color=row["Color"],
                popup=f"{row['Zone']}: {row['Risk Level']} ({row['Probability']}%)"
            ).add_to(m)

               # Add Legend
        legend_html = """
        <div style="position: fixed; bottom: 50px; left: 50px; width:120px; height:90px;
        border:2px solid grey; z-index:9999; font-size:14px;
        background-color:white; padding:10px;">
        <b>Risk Legend</b><br>
        <i style="color:green">● Low</i><br>
        <i style="color:orange">● Medium</i><br>
        <i style="color:red">● High</i>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))
