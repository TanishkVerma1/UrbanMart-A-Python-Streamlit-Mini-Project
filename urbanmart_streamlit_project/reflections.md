# Reflection Questions – UrbanMart Mini Project

## 1. Which store location generates the highest revenue overall? How did you find this?

Using the prepared dataset, I grouped the data by `store_location` and summed the `line_revenue` column:

```python
rev_by_store = (
    df.groupby("store_location")["line_revenue"]
    .sum()
    .sort_values(ascending=False)
)
```

From the resulting series and from the **“Revenue by Store Location”** bar chart in the Streamlit dashboard, the **Downtown** store generates the highest total revenue. This is consistent with a high-footfall, central location.

---

## 2. In your filtered view, does the Online or In-store channel generate more revenue?

I used a similar groupby on the `channel` column:

```python
rev_by_channel = (
    df_filtered.groupby("channel")["line_revenue"]
    .sum()
    .sort_values(ascending=False)
)
```

In the full dataset and most filtered views, **In-store** revenue is slightly higher than **Online** revenue. However, when I restrict the filters to specific dates or locations, Online sometimes becomes more competitive, which shows the importance of looking at **specific segments**, not just overall totals.

---

## 3. Which three product categories contribute the most revenue?

I computed revenue by product category:

```python
rev_by_category = (
    df_filtered.groupby("product_category")["line_revenue"]
    .sum()
    .sort_values(ascending=False)
)
```

Based on the synthetic dataset, the top three categories by revenue are:

1. **Beverages**
2. **Snacks**
3. **Personal Care**

The bar chart for **Revenue by Product Category** makes this visually clear: Beverages and Snacks dominate because they are high-volume everyday items.

---

## 4. What additional filter or feature would you add to the dashboard if you had more time? Why?

I would add a **Customer Segment filter** based on the `customer_segment` column (`Regular`, `New`, `Loyal`):

- This would allow UrbanMart to understand how much revenue is driven by loyal customers vs new customers.
- It could help evaluate the impact of loyalty programs and targeted campaigns.

Implementation-wise, it would be a small extension of the sidebar:

```python
all_segments = sorted(df["customer_segment"].dropna().unique().tolist())
selected_segments = st.sidebar.multiselect(
    "Customer Segments (optional)",
    options=all_segments,
    default=[],
)
```

and then filter `df_filtered` accordingly. This makes the dashboard more powerful for **marketing and CRM analysis**.

---

## 5. What did you learn from building both a CLI and a Streamlit dashboard for the same dataset?

- The **CLI application** forced me to practice core Python:
  - Lists, tuples, and dictionaries for storing intermediate results
  - Loops and `if/elif/else` for the menu and logic
  - File handling and basic error handling using `try/except`
- The **Streamlit dashboard** showed how the same logic can be turned into a **business-friendly analytics tool**:
  - KPIs give an instant summary
  - Charts communicate trends and rankings clearly
  - Filters let non-technical users explore the data themselves

Together, they demonstrate a complete flow: using Python to **process data programmatically** and then using the same data to build an **interactive analytics experience**.
