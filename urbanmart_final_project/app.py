"""
app.py

Streamlit dashboard for UrbanMart Sales.

Features:
- Sidebar filters (date range, store_location, channel, product_category)
- KPIs (Total Revenue, Total Transactions, Avg Revenue/Txn, Unique Customers)
- Charts: Revenue by Category, Revenue by Store, Daily Trend
- Tables: Top Products, Top Customers, Sample Raw Data
"""

from datetime import date
from typing import List, Optional, Tuple

import pandas as pd
import streamlit as st


DATA_FILE = "urbanmart_sales.csv"


# -----------------------------
# Data Loading & Preparation
# -----------------------------

@st.cache_data
def load_data(filepath: str) -> pd.DataFrame:
    """Load data once and cache it for better performance."""
    df = pd.read_csv(filepath)

    # Convert date column
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Add line_revenue and day_of_week for analysis
    df["line_revenue"] = df["quantity"] * df["unit_price"] - df["discount_applied"]
    df["day_of_week"] = df["date"].dt.day_name()

    return df


def filter_data(
    df: pd.DataFrame,
    date_range: Tuple[date, date],
    selected_locations: List[str],
    selected_channel: str,
    selected_categories: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Filter dataframe based on:
      - date_range (start, end)
      - store_location list
      - channel ("All", "Online", "In-store")
      - product_category list (optional)
    """
    filtered = df.copy()

    # Date range filter
    start_date, end_date = date_range
    filtered = filtered[
        (filtered["date"].dt.date >= start_date)
        & (filtered["date"].dt.date <= end_date)
    ]

    # Store location filter
    if selected_locations:
        filtered = filtered[filtered["store_location"].isin(selected_locations)]

    # Channel filter
    if selected_channel != "All":
        filtered = filtered[filtered["channel"] == selected_channel]

    # Product category filter (optional)
    if selected_categories:
        filtered = filtered[filtered["product_category"].isin(selected_categories)]

    return filtered


# -----------------------------
# Streamlit Layout
# -----------------------------

def main() -> None:
    st.set_page_config(
        page_title="UrbanMart Sales Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("UrbanMart Sales Dashboard")
    st.caption("Built using Python & Streamlit for MAIB Python Mini-Project")

    # Load data
    try:
        df = load_data(DATA_FILE)
    except FileNotFoundError:
        st.error(f"File '{DATA_FILE}' not found. Please upload the CSV and reload.")
        return
    except Exception as e:
        st.error(f"Unexpected error while loading data: {e}")
        return

    # -------------------------
    # Sidebar Filters
    # -------------------------
    st.sidebar.header("Filters")

    # Date range slider: use min/max from data
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Filter transactions by date range.",
    )

    # Ensure date_range returns a tuple
    if isinstance(date_range, tuple):
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    # Store location multi-select
    all_locations = sorted(df["store_location"].dropna().unique().tolist())
    selected_locations = st.sidebar.multiselect(
        "Store Locations",
        options=all_locations,
        default=all_locations,
    )

    # Channel selectbox
    channel_options = ["All"] + sorted(df["channel"].dropna().unique().tolist())
    selected_channel = st.sidebar.selectbox(
        "Channel",
        options=channel_options,
        index=0,
    )

    # Optional product category multi-select
    all_categories = sorted(df["product_category"].dropna().unique().tolist())
    selected_categories = st.sidebar.multiselect(
        "Product Categories (optional)",
        options=all_categories,
        default=[],
        help="Leave empty to include all product categories.",
    )

    # Apply filters
    df_filtered = filter_data(
        df,
        date_range=(start_date, end_date),
        selected_locations=selected_locations,
        selected_channel=selected_channel,
        selected_categories=selected_categories,
    )

    st.sidebar.markdown("---")
    st.sidebar.write(f"Filtered rows: **{len(df_filtered):,}**")

    # -------------------------
    # KPIs
    # -------------------------
    st.subheader("Key Metrics (Filtered View)")

    if len(df_filtered) == 0:
        st.warning("No data available for the selected filters.")
        return

    total_revenue = float(df_filtered["line_revenue"].sum())
    total_transactions = int(len(df_filtered))
    avg_revenue_per_txn = total_revenue / total_transactions if total_transactions > 0 else 0.0
    unique_customers = int(df_filtered["customer_id"].nunique())

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Revenue", f"{total_revenue:,.2f}")
    col2.metric("Total Transactions", f"{total_transactions:,}")
    col3.metric("Avg Revenue / Transaction", f"{avg_revenue_per_txn:,.2f}")
    col4.metric("Unique Customers", f"{unique_customers:,}")

    st.markdown("---")

    # -------------------------
    # Revenue by Category
    # -------------------------
    st.subheader("Revenue by Product Category")

    rev_by_cat = (
        df_filtered.groupby("product_category")["line_revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(rev_by_cat)

    # -------------------------
    # Revenue by Store Location
    # -------------------------
    st.subheader("Revenue by Store Location")

    rev_by_store = (
        df_filtered.groupby("store_location")["line_revenue"]
        .sum()
        .sort_values(ascending=False)
    )
    st.bar_chart(rev_by_store)

    # -------------------------
    # Daily Revenue Trend
    # -------------------------
    st.subheader("Daily Revenue Trend")

    daily_rev = (
        df_filtered.groupby("date")["line_revenue"]
        .sum()
        .sort_index()
    )

    st.line_chart(daily_rev)

    # -------------------------
    # Top Products & Top Customers
    # -------------------------
    st.subheader("Top Products and Customers")

    # Top 5 products by revenue
    top_products = (
        df_filtered.groupby("product_name")["line_revenue"]
        .sum()
        .reset_index()
        .sort_values("line_revenue", ascending=False)
        .head(5)
    )

    # Top 5 customers by revenue
    top_customers = (
        df_filtered.groupby("customer_id")["line_revenue"]
        .sum()
        .reset_index()
        .sort_values("line_revenue", ascending=False)
        .head(5)
    )

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Top 5 Products by Revenue**")
        st.dataframe(top_products, use_container_width=True)

    with col_right:
        st.markdown("**Top 5 Customers by Revenue**")
        st.dataframe(top_customers, use_container_width=True)

    # -------------------------
    # Sample Raw Data
    # -------------------------
    st.markdown("---")
    st.subheader("Sample Raw Data (Filtered)")

    st.dataframe(df_filtered.head(20), use_container_width=True)


if __name__ == "__main__":
    main()
