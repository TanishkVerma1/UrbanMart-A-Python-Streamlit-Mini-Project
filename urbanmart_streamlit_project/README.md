# UrbanMart Sales Mini Project

This repository contains my Python mini project for analyzing **UrbanMart** sales data and building an interactive dashboard.

## Contents

- `urbanmart_analysis.py`  
  Console-based analysis script that:
  - Loads the `urbanmart_sales.csv` file
  - Uses Python lists, tuples, dictionaries
  - Performs manual channel counts using the `csv` module
  - Computes KPIs (total revenue, revenue by store, top products)
  - Prepares summary tables for the dashboard
  - Exposes a CLI menu using `while` loops and `if/elif/else`

- `app.py`  
  Streamlit dashboard that:
  - Loads and caches the same CSV file
  - Adds `line_revenue` and `day_of_week`
  - Provides filters for date range, store location, channel and product category
  - Displays KPIs, charts, and tables

- `urbanmart_sales.csv`  
  Sample dataset (synthetic) with 1000 rows, generated to match the assignment structure.

- `reflections.md`  
  Answers to the reflection questions based on insights from the dataset and the dashboard.

- `requirements.txt`  
  Python dependencies needed to run the project.

## How to Run Locally

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the console analysis script:

   ```bash
   python urbanmart_analysis.py
   ```

3. Run the Streamlit dashboard:

   ```bash
   streamlit run app.py
   ```

## How to Deploy on Streamlit Cloud

1. Push this folder to a **public GitHub repository**.
2. Go to the Streamlit Cloud deployment page and connect your GitHub account.
3. Select the repository and choose `app.py` as the **main file**.
4. Make sure `requirements.txt` is present (included here).
5. Deploy – Streamlit Cloud will install dependencies and start the app.

## Python Version

This project is compatible with **Python 3.9+** (tested on 3.10 / 3.11).
