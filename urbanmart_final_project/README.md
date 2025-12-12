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

- `generate_dummy_data.py`  
  Helper script that generates a synthetic `urbanmart_sales.csv` file if real data is not available.

- `urbanmart_sales.csv`  
  Sample dataset created with `generate_dummy_data.py`.

- `reflections.md`  
  Answers to the reflection questions based on insights from the dataset and the dashboard.

- `requirements.txt`  
  Python dependencies needed to run the project.

## How to Run (Locally)

1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Regenerate sample data:

   ```bash
   python generate_dummy_data.py
   ```

4. Run the console analysis script:

   ```bash
   python urbanmart_analysis.py
   ```

5. Run the Streamlit dashboard:

   ```bash
   streamlit run app.py
   ```

## How to Deploy on Streamlit Cloud

1. Push this folder to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your GitHub account.
3. Select the repository and choose `app.py` as the **main file**.
4. Make sure `requirements.txt` is present (it is included here).
5. Deploy – Streamlit Cloud will install dependencies and start the app.

## Python Version

The project is compatible with **Python 3.10+**.
