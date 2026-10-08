import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Retail Sales Analytics", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("data/retail_sales.csv", parse_dates=["order_date"])
    df["revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)
    return df

df = load_data()

st.title("📊 Retail Sales Analytics Dashboard")
st.caption("Interactive analysis of a synthetic 2025 retail sales dataset.")

st.sidebar.header("Filters")
regions = st.sidebar.multiselect("Region", sorted(df["region"].unique()), default=sorted(df["region"].unique()))
categories = st.sidebar.multiselect("Category", sorted(df["category"].unique()), default=sorted(df["category"].unique()))
filtered = df[df["region"].isin(regions) & df["category"].isin(categories)].copy()

revenue = filtered["revenue"].sum()
orders = filtered["order_id"].nunique()
units = filtered["quantity"].sum()
aov = revenue / orders if orders else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue", f"₹{revenue:,.0f}")
c2.metric("Orders", f"{orders:,}")
c3.metric("Units Sold", f"{units:,}")
c4.metric("Average Order Value", f"₹{aov:,.0f}")

monthly = filtered.set_index("order_date").resample("MS")["revenue"].sum().reset_index()
st.plotly_chart(px.line(monthly, x="order_date", y="revenue", markers=True, title="Monthly Revenue"), use_container_width=True)

left, right = st.columns(2)
with left:
    category = filtered.groupby("category", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    st.plotly_chart(px.bar(category, x="category", y="revenue", title="Revenue by Category"), use_container_width=True)
with right:
    region = filtered.groupby("region", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    st.plotly_chart(px.bar(region, x="region", y="revenue", title="Revenue by Region"), use_container_width=True)

st.subheader("Top Products")
top_products = filtered.groupby("product", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False).head(10)
st.dataframe(top_products, use_container_width=True, hide_index=True)

st.subheader("Customer Segmentation")
today = filtered["order_date"].max() + pd.Timedelta(days=1)
rfm = filtered.groupby("customer_id").agg(
    recency=("order_date", lambda x: (today - x.max()).days),
    frequency=("order_id", "nunique"),
    monetary=("revenue", "sum")
).reset_index()

rfm["segment"] = np.select(
    [
        (rfm["monetary"] >= rfm["monetary"].quantile(.75)) & (rfm["frequency"] >= rfm["frequency"].median()),
        rfm["recency"] <= rfm["recency"].quantile(.25),
        rfm["monetary"] <= rfm["monetary"].quantile(.25)
    ],
    ["High Value", "Loyal/Recent", "Low Value"],
    default="Regular"
)
seg = rfm["segment"].value_counts().reset_index()
seg.columns = ["segment", "customers"]
st.plotly_chart(px.pie(seg, names="segment", values="customers", title="Customer Segments"), use_container_width=True)

st.subheader("Next-Month Revenue Forecast")
if len(monthly) >= 3:
    monthly["month_number"] = np.arange(len(monthly))
    model = LinearRegression()
    model.fit(monthly[["month_number"]], monthly["revenue"])
    forecast = model.predict(np.array([[len(monthly)]]))[0]
    st.metric("Estimated Next-Month Revenue", f"₹{max(0, forecast):,.0f}")
    st.caption("A simple linear trend is used for learning purposes.")
