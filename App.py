import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Logistics Dashboard", layout="wide")

# -------------------------------
# DARK MODE + KPI CARD STYLE
# -------------------------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
[data-testid="metric-container"] {
    background-color: #1c1f26;
    border-radius: 10px;
    padding: 15px;
    border: 1px solid #333;
}
h1, h2, h3 {
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# TITLE
# -------------------------------
st.title("📦 Logistics Performance Dashboard")

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv("APL_Logistics_small.csv", encoding='latin1')
df.columns = df.columns.str.replace(" ", "_")

# -------------------------------
# FEATURES
# -------------------------------
df['Delay_Gap'] = df['Days_for_shipping_(real)'] - df['Days_for_shipment_(scheduled)']
df['Delivery_Status'] = df['Delay_Gap'].apply(lambda x: 'Delayed' if x > 0 else 'On-Time')

# -------------------------------
# SIDEBAR NAVIGATION
# -------------------------------
st.sidebar.title("📊 Navigation")

page = st.sidebar.radio("Go to", ["Dashboard", "Analysis", "Data"])

# FILTERS
st.sidebar.header("🔍 Filters")
mode = st.sidebar.selectbox("Shipping Mode", df['Shipping_Mode'].unique())
region = st.sidebar.selectbox("Region", df['Order_Region'].unique())

df = df[(df['Shipping_Mode'] == mode) & (df['Order_Region'] == region)]

# -------------------------------
# KPI CALCULATIONS
# -------------------------------
total_orders = len(df)
on_time_pct = (df['Delivery_Status'] == 'On-Time').mean() * 100
delayed_pct = (df['Delivery_Status'] == 'Delayed').mean() * 100
avg_delay = df['Delay_Gap'].mean()
total_profit = df['Order_Profit_Per_Order'].sum()

# =========================================================
# 🏠 DASHBOARD TAB
# =========================================================
if page == "Dashboard":

    st.subheader("📊 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Orders", total_orders)
    col2.metric("✅ On-Time %", f"{round(on_time_pct,2)}%")
    col3.metric("⚠ Delayed %", f"{round(delayed_pct,2)}%")
    col4.metric("💰 Profit", f"${round(total_profit,2)}")

    # -------------------------------
    # DELIVERY OVERVIEW
    # -------------------------------
    st.markdown("---")
    st.subheader("🚚 Delivery Overview")

    col1, col2 = st.columns(2)

    fig_pie = px.pie(df, names='Delivery_Status')
    col1.plotly_chart(fig_pie, use_container_width=True)

    status_count = df['Delivery_Status'].value_counts().reset_index()
    status_count.columns = ['Status', 'Count']

    fig_bar = px.bar(status_count, x='Status', y='Count', color='Status')
    col2.plotly_chart(fig_bar, use_container_width=True)

    # -------------------------------
    # HEATMAP
    # -------------------------------
    st.markdown("---")
    st.subheader("🗺 Delivery Map")

    fig_map = px.scatter_geo(
        df.sample(min(2000, len(df))),
        lat='Latitude',
        lon='Longitude',
        color='Delay_Gap'
    )
    st.plotly_chart(fig_map, use_container_width=True)

# =========================================================
# 📊 ANALYSIS TAB
# =========================================================
elif page == "Analysis":

    st.subheader("📉 Delay Risk Analysis")

    col1, col2 = st.columns(2)

    fig1 = px.histogram(df, x='Delay_Gap', color='Delivery_Status')
    col1.plotly_chart(fig1, use_container_width=True)

    fig2 = px.histogram(df, x='Late_delivery_risk')
    col2.plotly_chart(fig2, use_container_width=True)

    # -------------------------------
    # SHIPPING MODE
    # -------------------------------
    st.markdown("---")
    st.subheader("🚚 Shipping Mode")

    col1, col2 = st.columns(2)

    mode_data = df.groupby('Shipping_Mode')['Delay_Gap'].mean().reset_index()

    fig3 = px.bar(mode_data, x='Shipping_Mode', y='Delay_Gap', color='Shipping_Mode')
    col1.plotly_chart(fig3, use_container_width=True)

    sla_data = df.groupby('Shipping_Mode')['Delivery_Status'].apply(
        lambda x: (x == 'On-Time').mean() * 100
    ).reset_index(name='On_Time_%')

    fig4 = px.bar(sla_data, x='Shipping_Mode', y='On_Time_%', color='On_Time_%')
    col2.plotly_chart(fig4, use_container_width=True)

    # -------------------------------
    # REGION
    # -------------------------------
    st.markdown("---")
    st.subheader("🌍 Region Analysis")

    region_data = df.groupby('Order_Region')['Delay_Gap'].mean().reset_index()

    fig5 = px.bar(region_data, x='Order_Region', y='Delay_Gap', color='Delay_Gap')
    st.plotly_chart(fig5, use_container_width=True)

# =========================================================
# 📄 DATA TAB
# =========================================================
elif page == "Data":

    st.subheader("📄 Dataset Preview")
    st.dataframe(df)

    st.download_button(
        "⬇ Download Data",
        df.to_csv(index=False),
        file_name="logistics_data.csv"
    )
