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

From the resulting series and from the **“Revenue by Store Location”** bar chart in the Streamlit dashboard, the **Downtown** store consistently shows the highest total revenue. This is intuitive because it likely has higher footfall and a larger customer base.

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

In most filter scenarios I tested (full date range and all locations), **In-store** revenue is slightly higher than **Online** revenue. However, when I restrict the dashboard to recent dates and specific locations, Online revenue sometimes becomes more competitive. This shows how important it is to look at **filtered views**, not only overall totals.

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

This is also visible directly from the **“Revenue by Product Category”** bar chart in the dashboard. Beverages and snacks are high-volume, high-frequency items which naturally dominate revenue.

---

## 4. What additional filter or feature would you add to the dashboard if you had more time? Why?

If I had more time, I would add:

### Filter by Customer Segment

- **Filter:** `customer_segment` (Regular, New, Loyal)
- **Why:** This would allow UrbanMart to compare revenue and average spend between loyal customers vs new customers. For example, management could see whether loyalty programs are working by comparing revenue and transaction frequency for the “Loyal” segment vs others.

Implementation-wise, this would be a small extension of the current sidebar:

```python
all_segments = sorted(df["customer_segment"].dropna().unique().tolist())
selected_segments = st.sidebar.multiselect(
    "Customer Segments (optional)",
    options=all_segments,
    default=[],
)
```

and then filter `df_filtered` accordingly. This would make the dashboard more powerful for **marketing and CRM analysis**.

---

## 5. What did you learn from building both a CLI and a Streamlit dashboard for the same dataset?

- The **CLI application** helped me practice core Python concepts:
  - Lists, tuples, and dictionaries
  - Loops and `if/elif/else`
  - Functions with return values
  - File handling and basic error handling
- The **Streamlit dashboard** showed how the same logic could be made **interactive and visual** for business users:
  - KPIs provide an at-a-glance summary
  - Bar/line charts make trends and comparisons more intuitive
  - Filters allow non-technical users to explore the same dataset without writing code

Together, they demonstrate a complete flow: **Python for data processing + Python for user-facing analytics**.
