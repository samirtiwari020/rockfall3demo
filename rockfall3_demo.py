import streamlit as st
import pandas as pd
import plotly.express as px
import time

# Page config
st.set_page_config(page_title="Rockfall Prediction Demo", layout="wide")
st.title("🪨 Rockfall Prediction Dashboard (Stable Demo)")

# Sidebar - inputs
st.sidebar.header("Simulated Inputs")
rainfall = st.sidebar.slider("Rainfall (mm)", 0, 200, 50)
displacement = st.sidebar.slider("Displacement (mm)", 0, 50, 10)
strain = st.sidebar.slider("Strain (mm/m)", 0.0, 5.0, 1.0, step=0.1)
auto_refresh = st.sidebar.checkbox("Auto-refresh (simulate live)", value=False)
update_btn = st.sidebar.button("Update Risk Now")

# Zones and optional sensitivity to make some zones naturally riskier
zone_coords = {
    "Zone 1": (28.500, 77.000),
    "Zone 2": (28.510, 77.010),
    "Zone 3": (28.520, 77.020),
    "Zone 4": (28.530, 77.030),
}
zone_sensitivity = {"Zone 1": 1.0, "Zone 2": 1.2, "Zone 3": 1.5, "Zone 4": 0.9}

# Initialize session state
if "df_risk" not in st.session_state:
    st.session_state.df_risk = None
if "last_update" not in st.session_state:
    st.session_state.last_update = None

# Risk calculation function
def calculate_risk(rain, disp, strn):
    rows = []
    for zone, (lat, lon) in zone_coords.items():
        sens = zone_sensitivity.get(zone, 1.0)
        base = 15  # baseline risk
        # Weighted formula (tweak weights to taste)
        prob = base + int(rain * 0.25 * sens) + int(disp * 2 * sens) + int(strn * 6 * sens)
        prob = max(0, min(prob, 100))
        if prob > 70:
            level = "High"
        elif prob > 40:
            level = "Medium"
        else:
            level = "Low"
        rows.append({
            "Zone": zone,
            "lat": lat,
            "lon": lon,
            "Probability": prob,
            "Risk Level": level
        })
    return pd.DataFrame(rows)

# Decide when to update
should_update = False
if update_btn:
    should_update = True
elif st.session_state.df_risk is None:
    should_update = True
elif auto_refresh:
    should_update = True

if should_update:
    st.session_state.df_risk = calculate_risk(rainfall, displacement, strain)
    st.session_state.last_update = time.strftime("%Y-%m-%d %H:%M:%S")

# Layout
col_map, col_right = st.columns([2, 1])

with col_map:
    st.subheader("📍 Risk Map")
    df = st.session_state.df_risk.copy() if st.session_state.df_risk is not None else pd.DataFrame(columns=["Zone","lat","lon","Probability","Risk Level"])
    if not df.empty:
        # Plotly mapbox (open-street-map style does not need token)
        fig = px.scatter_mapbox(
            df,
            lat="lat", lon="lon",
            color="Risk Level",
            size="Probability",
            hover_name="Zone",
            hover_data={"Probability": True, "lat": False, "lon": False},
            color_discrete_map={"Low":"green", "Medium":"orange", "High":"red"},
            size_max=30,
            zoom=14,
            center={"lat": df["lat"].mean(), "lon": df["lon"].mean()}
        )
        fig.update_layout(mapbox_style="open-street-map", margin={"l":0,"r":0,"t":0,"b":0})
        st.plotly_chart(fig, use_container_width=True, height=600)
    else:
        st.info("No risk data yet. Press 'Update Risk Now'.")

with col_right:
    st.subheader("🚨 Alerts")
    df = st.session_state.df_risk
    if df is not None:
        for _, r in df.sort_values(by="Probability", ascending=False).iterrows():
            zone = r["Zone"]
            prob = int(r["Probability"])
            level = r["Risk Level"]
            if level == "High":
                st.markdown(f"<div style='background:#ffebeb;padding:10px;border-radius:6px'><b style='color:#d03333'>⚠️ {zone} — HIGH RISK ({prob}%)</b><br><small>Immediate action recommended</small></div>", unsafe_allow_html=True)
            elif level == "Medium":
                st.markdown(f"<div style='background:#fff7eb;padding:10px;border-radius:6px'><b style='color:#d97706'>⚠️ {zone} — Medium Risk ({prob}%)</b><br><small>Monitor closely & inspect</small></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background:#e9ffec;padding:8px;border-radius:6px'><b style='color:#2d9a37'>✅ {zone} — Low Risk ({prob}%)</b></div>", unsafe_allow_html=True)
    else:
        st.write("No alerts yet. Press 'Update Risk Now'.")

    st.markdown("---")
    st.subheader("📊 Current Sensor Stats")
    st.metric("Rainfall (mm)", rainfall)
    st.metric("Displacement (mm)", displacement)
    st.metric("Strain (mm/m)", f"{strain:.2f}")
    st.markdown(f"**Last update:** {st.session_state.last_update}")

    st.markdown("---")
    st.subheader("📈 Risk Probabilities")
    if st.session_state.df_risk is not None:
        fig2 = px.bar(
            st.session_state.df_risk,
            x="Zone", y="Probability", color="Risk Level",
            color_discrete_map={"Low":"green", "Medium":"orange", "High":"red"}


