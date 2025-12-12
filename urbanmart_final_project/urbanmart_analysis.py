"""
urbanmart_analysis.py

Console-based analysis script for UrbanMart sales data.
Covers:
- Basic Python, lists, tuples, dictionaries
- File handling and error handling
- KPI functions
- Simple CLI menu
- Data preparation for dashboard (line_revenue, day_of_week, summary tables)
"""

import csv
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


DATA_FILE = "urbanmart_sales.csv"


# -----------------------------
# Part 1 – Data Loading & Sanity Checks
# -----------------------------

def print_welcome_message() -> None:
    """Print a welcome message using variables and f-strings."""
    store_name = "UrbanMart"
    print(f"Welcome to {store_name} Sales Analysis")
    print("-" * 50)


def load_data_with_pandas(filepath: str) -> pd.DataFrame:
    """
    Load sales data using pandas with basic error handling.

    Args:
        filepath: Path to the CSV file.

    Returns:
        DataFrame with sales data.

    Raises:
        FileNotFoundError: If the file is not found.
    """
    try:
        df = pd.read_csv(filepath)
        return df
    except FileNotFoundError as e:
        print(f"[ERROR] File not found: {filepath}")
        raise e
    except Exception as e:
        print(f"[ERROR] Unexpected error while reading file: {e}")
        raise e


def manual_channel_counts_with_csv(filepath: str) -> Dict[str, int]:
    """
    Use Python's built-in csv module and a loop to count
    Online vs In-store transactions WITHOUT using pandas.

    Returns:
        Dictionary like {"Online": count, "In-store": count}
    """
    counts: Dict[str, int] = {"Online": 0, "In-store": 0}

    try:
        with open(filepath, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                channel = row.get("channel", "").strip()
                if channel in counts:
                    counts[channel] += 1
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
    except Exception as e:
        print(f"[ERROR] Unexpected error while reading with csv module: {e}")

    return counts


def run_basic_sanity_checks(df: pd.DataFrame) -> None:
    """Print total rows, unique store IDs, date range, and some list/dict usage."""
    print("\n[Basic Sanity Checks]")

    # Total number of rows
    total_rows = len(df)
    print(f"Total number of rows: {total_rows}")

    # Unique store IDs
    unique_store_ids: List[str] = sorted(df["store_id"].dropna().unique().tolist())
    print(f"Unique store IDs: {unique_store_ids}")

    # Date range
    # Convert date column to datetime for safe computation
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    min_date = df["date"].min()
    max_date = df["date"].max()
    if pd.isna(min_date) or pd.isna(max_date):
        print("Date range: not available (invalid or missing dates)")
    else:
        print(f"Date range: {min_date.date()} to {max_date.date()}")

    # Use lists and tuples: list of product categories, tuple example
    product_categories: List[str] = sorted(df["product_category"].dropna().unique().tolist())
    print(f"\nList of product categories (list):\n{product_categories}")

    categories_tuple: Tuple[str, ...] = tuple(product_categories)
    print(f"\nSame categories as an immutable tuple:\n{categories_tuple}")

    # Dictionary: store_id → store_location mapping
    store_mapping: Dict[str, str] = (
        df[["store_id", "store_location"]]
        .drop_duplicates()
        .set_index("store_id")["store_location"]
        .to_dict()
    )
    print(f"\nStore mapping (store_id → store_location):\n{store_mapping}")


# -----------------------------
# Part 2 – KPI Functions
# -----------------------------

def add_line_revenue_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a 'line_revenue' column:
    line_revenue = quantity * unit_price - discount_applied
    """
    df = df.copy()
    df["line_revenue"] = df["quantity"] * df["unit_price"] - df["discount_applied"]
    return df


def compute_total_revenue(df: pd.DataFrame) -> float:
    """
    Returns total revenue = sum((quantity * unit_price) - discount_applied).
    """
    if "line_revenue" not in df.columns:
        df = add_line_revenue_column(df)
    total = float(df["line_revenue"].sum())
    return total


def compute_revenue_by_store(df: pd.DataFrame) -> Dict[str, float]:
    """
    Returns a dictionary: store_id → revenue.
    """
    if "line_revenue" not in df.columns:
        df = add_line_revenue_column(df)
    revenue_series = df.groupby("store_id")["line_revenue"].sum()
    return revenue_series.to_dict()


def compute_top_n_products(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """
    Returns a DataFrame of top n products by revenue.
    Grouped by product_name.
    """
    if "line_revenue" not in df.columns:
        df = add_line_revenue_column(df)

    grouped = (
        df.groupby("product_name")["line_revenue"]
        .sum()
        .reset_index()
        .sort_values("line_revenue", ascending=False)
        .head(n)
    )
    return grouped


# -----------------------------
# Part 3 – Data Preparation for Dashboard
# -----------------------------

def prepare_dashboard_data(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Prepare additional columns and summary tables for dashboard use.

    Adds:
        - line_revenue
        - day_of_week

    Creates:
        - revenue_by_category
        - revenue_by_store
        - revenue_by_channel
        - top_customers
    """
    df = add_line_revenue_column(df)

    # Ensure 'date' is datetime and add day_of_week
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["day_of_week"] = df["date"].dt.day_name()

    # Summary tables
    revenue_by_category = (
        df.groupby("product_category")["line_revenue"]
        .sum()
        .reset_index()
        .sort_values("line_revenue", ascending=False)
    )

    revenue_by_store = (
        df.groupby("store_location")["line_revenue"]
        .sum()
        .reset_index()
        .sort_values("line_revenue", ascending=False)
    )

    revenue_by_channel = (
        df.groupby("channel")["line_revenue"]
        .sum()
        .reset_index()
        .sort_values("line_revenue", ascending=False)
    )

    top_customers = (
        df.groupby("customer_id")["line_revenue"]
        .sum()
        .reset_index()
        .sort_values("line_revenue", ascending=False)
        .head(10)
    )

    return {
        "df": df,
        "revenue_by_category": revenue_by_category,
        "revenue_by_store": revenue_by_store,
        "revenue_by_channel": revenue_by_channel,
        "top_customers": top_customers,
    }


def filter_data(
    df: pd.DataFrame,
    start_date=None,
    end_date=None,
    store: str | None = None,
    channel: str | None = None,
) -> pd.DataFrame:
    """
    Filter dataframe based on date range, store, and channel.

    Args:
        df: original dataframe (must have 'date', 'store_id', 'channel')
        start_date: inclusive start date (datetime or string 'YYYY-MM-DD')
        end_date: inclusive end date
        store: store_id to filter, or None for all
        channel: 'Online' or 'In-store' or None for all

    Returns:
        Filtered DataFrame.
    """
    filtered = df.copy()
    filtered["date"] = pd.to_datetime(filtered["date"], errors="coerce")

    if start_date is not None:
        filtered = filtered[filtered["date"] >= pd.to_datetime(start_date)]
    if end_date is not None:
        filtered = filtered[filtered["date"] <= pd.to_datetime(end_date)]
    if store:
        filtered = filtered[filtered["store_id"] == store]
    if channel:
        filtered = filtered[filtered["channel"] == channel]

    return filtered


# -----------------------------
# CLI Menu (Part 2 requirement)
# -----------------------------

def cli_menu(df: pd.DataFrame) -> None:
    """
    Display a simple CLI menu using while True and if/elif/else.
    """
    while True:
        print("\n===== UrbanMart CLI Menu =====")
        print("1. Show total revenue")
        print("2. Show revenue by store")
        print("3. Show top 5 products by revenue")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ").strip()

        try:
            if choice == "1":
                total_rev = compute_total_revenue(df)
                print(f"\nTotal Revenue: {total_rev:,.2f}")

            elif choice == "2":
                revenue_dict = compute_revenue_by_store(df)
                print("\nRevenue by store_id:")
                for store_id, rev in revenue_dict.items():
                    print(f"  {store_id}: {rev:,.2f}")

            elif choice == "3":
                top_products_df = compute_top_n_products(df, n=5)
                print("\nTop 5 Products by Revenue:")
                print(top_products_df.to_string(index=False))

            elif choice == "4":
                print("\nExiting CLI. Goodbye!")
                break

            else:
                print("[WARNING] Invalid menu choice. Please enter a number between 1 and 4.")

        except Exception as e:
            # Basic error handling for unexpected issues during KPI calculations
            print(f"[ERROR] Something went wrong while processing your request: {e}")


# -----------------------------
# Main Entry Point
# -----------------------------

def main() -> None:
    print_welcome_message()

    # Ensure file exists
    if not Path(DATA_FILE).exists():
        print(f"[ERROR] '{DATA_FILE}' does not exist in the current directory.")
        print("Please place urbanmart_sales.csv next to this script and try again.")
        return

    # Manual Online vs In-store counts using csv module
    channel_counts = manual_channel_counts_with_csv(DATA_FILE)
    print("\n[Manual Channel Counts (Using csv + Loops)]")
    print(f"Online transactions : {channel_counts.get('Online', 0)}")
    print(f"In-store transactions: {channel_counts.get('In-store', 0)}")

    # Load data using pandas for further analysis
    df = load_data_with_pandas(DATA_FILE)

    # Run sanity checks and show some Python collections usage
    run_basic_sanity_checks(df)

    # Prepare additional columns and summary tables (Part 3)
    prepared = prepare_dashboard_data(df)
    df_prepared = prepared["df"]

    print("\n[Sample Summary Tables]")
    print("\nRevenue by Category:")
    print(prepared["revenue_by_category"].head().to_string(index=False))

    print("\nRevenue by Store Location:")
    print(prepared["revenue_by_store"].head().to_string(index=False))

    print("\nRevenue by Channel:")
    print(prepared["revenue_by_channel"].to_string(index=False))

    print("\nTop Customers by Revenue:")
    print(prepared["top_customers"].to_string(index=False))

    # Start CLI menu for interactive analysis
    cli_menu(df_prepared)


if __name__ == "__main__":
    main()
