import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="UrbanMart Analytics Platform",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .insight-box {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .profit {
        color: #28a745;
        font-weight: bold;
    }
    .loss {
        color: #dc3545;
        font-weight: bold;
    }
    .section-header {
        background: linear-gradient(90deg, #1f77b4 0%, #667eea 100%);
        color: white;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 1.5rem 0 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# DATA LOADING FUNCTION
# ============================================

@st.cache_data
def load_data():
    """Load and prepare the data"""
    try:
        df = pd.read_csv("urbanmart_sales.csv")
        
        # Create calculated columns
        df['line_revenue'] = (df['quantity'] * df['unit_price']) - df['discount_applied']
        df['gross_revenue'] = df['quantity'] * df['unit_price']
        df['total_discount'] = df['discount_applied']
        
        # Assume 30% cost of goods sold for profit calculation
        df['cost'] = df['quantity'] * df['unit_price'] * 0.30
        df['profit'] = df['line_revenue'] - df['cost']
        df['profit_margin'] = (df['profit'] / df['line_revenue'] * 100).round(2)
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Extract time components
        df['day_of_week'] = df['date'].dt.day_name()
        df['week'] = df['date'].dt.isocalendar().week
        df['month'] = df['date'].dt.month
        df['month_name'] = df['date'].dt.strftime('%B')
        df['quarter'] = df['date'].dt.quarter
        df['year'] = df['date'].dt.year
        df['year_month'] = df['date'].dt.to_period('M').astype(str)
        df['year_quarter'] = df['date'].dt.to_period('Q').astype(str)
        
        return df
    
    except FileNotFoundError:
        st.error("❌ **Error:** urbanmart_sales.csv not found!")
        st.info("👉 Please run 'python generate_sample_data.py' first to create the dataset.")
        st.stop()
    
    except Exception as e:
        st.error(f"❌ **Error loading data:** {e}")
        st.stop()

# ============================================
# ADVANCED FILTER FUNCTION
# ============================================

def apply_filters(df, date_segment, custom_start, custom_end, stores, channel, categories, segments, payment_methods):
    """Apply all filters to the dataframe"""
    
    filtered_df = df.copy()
    
    # Date filtering based on segment
    if date_segment == "Daily":
        # Use custom date range
        filtered_df = filtered_df[
            (filtered_df['date'] >= pd.to_datetime(custom_start)) & 
            (filtered_df['date'] <= pd.to_datetime(custom_end))
        ]
    elif date_segment == "Weekly":
        # Group by week
        filtered_df = filtered_df[
            (filtered_df['date'] >= pd.to_datetime(custom_start)) & 
            (filtered_df['date'] <= pd.to_datetime(custom_end))
        ]
    elif date_segment == "Monthly":
        # Filter by selected months
        filtered_df = filtered_df[
            (filtered_df['date'] >= pd.to_datetime(custom_start)) & 
            (filtered_df['date'] <= pd.to_datetime(custom_end))
        ]
    elif date_segment == "Quarterly":
        # Filter by quarters
        filtered_df = filtered_df[
            (filtered_df['date'] >= pd.to_datetime(custom_start)) & 
            (filtered_df['date'] <= pd.to_datetime(custom_end))
        ]
    elif date_segment == "Yearly":
        # Filter by years
        filtered_df = filtered_df[
            (filtered_df['date'] >= pd.to_datetime(custom_start)) & 
            (filtered_df['date'] <= pd.to_datetime(custom_end))
        ]
    
    # Other filters
    if stores:
        filtered_df = filtered_df[filtered_df['store_location'].isin(stores)]
    
    if channel != "All":
        filtered_df = filtered_df[filtered_df['channel'] == channel]
    
    if categories:
        filtered_df = filtered_df[filtered_df['product_category'].isin(categories)]
    
    if segments:
        filtered_df = filtered_df[filtered_df['customer_segment'].isin(segments)]
    
    if payment_methods:
        filtered_df = filtered_df[filtered_df['payment_method'].isin(payment_methods)]
    
    return filtered_df

# ============================================
# LOAD DATA
# ============================================

df = load_data()

# ============================================
# SIDEBAR - NAVIGATION & FILTERS
# ============================================

st.sidebar.title("🛒 UrbanMart Analytics")
st.sidebar.markdown("---")

# Page Navigation
page = st.sidebar.radio(
    "📊 Navigate to:",
    [
        "🏠 Executive Overview",
        "📈 Sales Performance",
        "👥 Customer Insights",
        "📦 Product Analytics",
        "🏪 Store Performance",
        "🔄 Channel & Payment Analysis",
        "🎯 Profitability Analysis"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Global Filters")

# ============================================
# ADVANCED DATE FILTER
# ============================================

st.sidebar.markdown("### 📅 Date Range Selection")

# Date segment selector
date_segment = st.sidebar.selectbox(
    "Select Time Period:",
    ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"],
    help="Choose how you want to view your data"
)

# Get min and max dates
min_date = df['date'].min().date()
max_date = df['date'].max().date()

# Custom date range
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "From:",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )
with col2:
    end_date = st.date_input(
        "To:",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )

# Quick date range buttons
st.sidebar.markdown("**Quick Select:**")
quick_range_col1, quick_range_col2 = st.sidebar.columns(2)

with quick_range_col1:
    if st.button("📅 Last 7 Days"):
        start_date = max_date - timedelta(days=7)
        end_date = max_date
    if st.button("📅 Last Month"):
        start_date = max_date - timedelta(days=30)
        end_date = max_date

with quick_range_col2:
    if st.button("📅 This Month"):
        start_date = max_date.replace(day=1)
        end_date = max_date
    if st.button("📅 All Time"):
        start_date = min_date
        end_date = max_date

st.sidebar.markdown("---")

# Other Filters
st.sidebar.markdown("### 🏪 Store & Location")
all_stores = sorted(df['store_location'].unique().tolist())
selected_stores = st.sidebar.multiselect(
    "Select Store(s):",
    options=all_stores,
    default=all_stores
)

st.sidebar.markdown("### 📱 Sales Channel")
channel_filter = st.sidebar.selectbox(
    "Select Channel:",
    options=["All", "In-store", "Online"]
)

st.sidebar.markdown("### 📦 Product Category")
all_categories = sorted(df['product_category'].unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Select Category(ies):",
    options=all_categories,
    default=all_categories
)

st.sidebar.markdown("### 👥 Customer Segment")
all_segments = sorted(df['customer_segment'].unique().tolist())
selected_segments = st.sidebar.multiselect(
    "Select Segment(s):",
    options=all_segments,
    default=all_segments
)

st.sidebar.markdown("### 💳 Payment Method")
all_payment_methods = sorted(df['payment_method'].unique().tolist())
selected_payment_methods = st.sidebar.multiselect(
    "Select Payment(s):",
    options=all_payment_methods,
    default=all_payment_methods
)

st.sidebar.markdown("---")

# Apply filters
df_filtered = apply_filters(
    df, date_segment, start_date, end_date, 
    selected_stores, channel_filter, selected_categories,
    selected_segments, selected_payment_methods
)

# Check if data exists
if len(df_filtered) == 0:
    st.warning("⚠️ No data available for selected filters. Please adjust your criteria.")
    st.stop()

# ============================================
# HELPER FUNCTIONS FOR INSIGHTS
# ============================================

def calculate_growth(current, previous):
    """Calculate percentage growth"""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

def format_currency(value):
    """Format value as currency"""
    return f"${value:,.2f}"

def format_percentage(value):
    """Format value as percentage"""
    return f"{value:.1f}%"

def get_trend_indicator(value):
    """Get trend indicator emoji"""
    if value > 0:
        return "📈"
    elif value < 0:
        return "📉"
    else:
        return "➡️"

def create_insight_box(title, content, insight_type="info"):
    """Create a styled insight box"""
    colors = {
        "info": "#1f77b4",
        "success": "#28a745",
        "warning": "#ffc107",
        "danger": "#dc3545"
    }
    color = colors.get(insight_type, "#1f77b4")
    
    st.markdown(f"""
        <div style='background-color: #f8f9fa; border-left: 4px solid {color}; 
                    padding: 1rem; margin: 1rem 0; border-radius: 5px;'>
            <h4 style='margin: 0 0 0.5rem 0; color: {color};'>{title}</h4>
            <p style='margin: 0;'>{content}</p>
        </div>
    """, unsafe_allow_html=True)

# ============================================
# PAGE 1: EXECUTIVE OVERVIEW
# ============================================

if page == "🏠 Executive Overview":
    
    st.markdown('<h1 class="main-header">🏠 Executive Overview Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Period: {start_date} to {end_date} | View: {date_segment}</p>', unsafe_allow_html=True)
    
    # Key Metrics Row
    st.markdown('<div class="section-header"><h2>📊 Key Performance Indicators</h2></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_revenue = df_filtered['line_revenue'].sum()
    total_profit = df_filtered['profit'].sum()
    total_transactions = df_filtered['transaction_id'].nunique()
    unique_customers = df_filtered['customer_id'].nunique()
    avg_order_value = total_revenue / total_transactions if total_transactions > 0 else 0
    
    with col1:
        st.metric(
            label="💰 Total Revenue",
            value=format_currency(total_revenue),
            delta=None
        )
    
    with col2:
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        st.metric(
            label="💵 Total Profit",
            value=format_currency(total_profit),
            delta=format_percentage(profit_margin)
        )
    
    with col3:
        st.metric(
            label="🧾 Transactions",
            value=f"{total_transactions:,}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="👥 Customers",
            value=f"{unique_customers:,}",
            delta=None
        )
    
    with col5:
        st.metric(
            label="🛒 Avg Order Value",
            value=format_currency(avg_order_value),
            delta=None
        )
    
    st.markdown("---")
    
    # Revenue Trend
    st.markdown('<div class="section-header"><h2>📈 Revenue & Profit Trend</h2></div>', unsafe_allow_html=True)
    
    if date_segment == "Daily":
        trend_data = df_filtered.groupby('date').agg({
            'line_revenue': 'sum',
            'profit': 'sum'
        }).reset_index()
        x_axis = 'date'
        x_label = 'Date'
    elif date_segment == "Weekly":
        trend_data = df_filtered.groupby(['year', 'week']).agg({
            'line_revenue': 'sum',
            'profit': 'sum'
        }).reset_index()
        trend_data['period'] = trend_data['year'].astype(str) + '-W' + trend_data['week'].astype(str)
        x_axis = 'period'
        x_label = 'Week'
    elif date_segment == "Monthly":
        trend_data = df_filtered.groupby('year_month').agg({
            'line_revenue': 'sum',
            'profit': 'sum'
        }).reset_index()
        x_axis = 'year_month'
        x_label = 'Month'
    elif date_segment == "Quarterly":
        trend_data = df_filtered.groupby('year_quarter').agg({
            'line_revenue': 'sum',
            'profit': 'sum'
        }).reset_index()
        x_axis = 'year_quarter'
        x_label = 'Quarter'
    else:  # Yearly
        trend_data = df_filtered.groupby('year').agg({
            'line_revenue': 'sum',
            'profit': 'sum'
        }).reset_index()
        x_axis = 'year'
        x_label = 'Year'
    
    fig_trend = go.Figure()
    
    fig_trend.add_trace(go.Scatter(
        x=trend_data[x_axis],
        y=trend_data['line_revenue'],
        name='Revenue',
        mode='lines+markers',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    
    fig_trend.add_trace(go.Scatter(
        x=trend_data[x_axis],
        y=trend_data['profit'],
        name='Profit',
        mode='lines+markers',
        line=dict(color='#28a745', width=3),
        marker=dict(size=8)
    ))
    
    fig_trend.update_layout(
        title=f'Revenue & Profit Trend ({date_segment} View)',
        xaxis_title=x_label,
        yaxis_title='Amount ($)',
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Insights
    create_insight_box(
        "📊 Trend Analysis",
        f"""
        • Total Revenue: {format_currency(total_revenue)} with an average profit margin of {format_percentage(profit_margin)}<br>
        • Profitability: {'✅ Profitable' if total_profit > 0 else '❌ Loss-making'} - 
          {format_currency(abs(total_profit))} {'profit' if total_profit > 0 else 'loss'}<br>
        • Customer Base: {unique_customers:,} unique customers with {total_transactions:,} transactions<br>
        • Average Order: {format_currency(avg_order_value)} per transaction
        """,
        "success" if total_profit > 0 else "danger"
    )
    
    st.markdown("---")
    
    # Performance by Category and Store
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header"><h3>📦 Top Categories by Revenue</h3></div>', unsafe_allow_html=True)
        
        category_performance = df_filtered.groupby('product_category').agg({
            'line_revenue': 'sum',
            'profit': 'sum'
        }).sort_values('line_revenue', ascending=False).reset_index()
        
        fig_category = px.bar(
            category_performance,
            x='line_revenue',
            y='product_category',
            orientation='h',
            color='profit',
            color_continuous_scale=['red', 'yellow', 'green'],
            labels={'line_revenue': 'Revenue ($)', 'product_category': 'Category', 'profit': 'Profit ($)'},
            text='line_revenue'
        )
        fig_category.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_category.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_category, use_container_width=True)
        
        # Category insights
        top_category = category_performance.iloc[0]
        create_insight_box(
            "🏆 Top Category",
            f"{top_category['product_category']} leads with {format_currency(top_category['line_revenue'])} "
            f"revenue and {format_currency(top_category['profit'])} profit",
            "success"
        )
    
    with col2:
        st.markdown('<div class="section-header"><h3>🏪 Store Performance</h3></div>', unsafe_allow_html=True)
        
        store_performance = df_filtered.groupby('store_location').agg({
            'line_revenue': 'sum',
            'profit': 'sum'
        }).sort_values('line_revenue', ascending=False).reset_index()
        
        fig_store = px.bar(
            store_performance,
            x='store_location',
            y='line_revenue',
            color='profit',
            color_continuous_scale=['red', 'yellow', 'green'],
            labels={'line_revenue': 'Revenue ($)', 'store_location': 'Store', 'profit': 'Profit ($)'},
            text='line_revenue'
        )
        fig_store.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_store.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_store, use_container_width=True)
        
        # Store insights
        top_store = store_performance.iloc[0]
        create_insight_box(
            "🏆 Top Store",
            f"{top_store['store_location']} store generates {format_currency(top_store['line_revenue'])} "
            f"revenue with {format_currency(top_store['profit'])} profit",
            "success"
        )
    
    st.markdown("---")
    
    # Channel and Segment Analysis
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="section-header"><h3>📱 Channel Split</h3></div>', unsafe_allow_html=True)
        channel_data = df_filtered.groupby('channel')['line_revenue'].sum().reset_index()
        fig_channel = px.pie(
            channel_data,
            values='line_revenue',
            names='channel',
            hole=0.4,
            color_discrete_sequence=['#4ECDC4', '#FF6B6B']
        )
        fig_channel.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_channel, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-header"><h3>👥 Customer Segments</h3></div>', unsafe_allow_html=True)
        segment_data = df_filtered.groupby('customer_segment')['line_revenue'].sum().reset_index()
        fig_segment = px.pie(
            segment_data,
            values='line_revenue',
            names='customer_segment',
            hole=0.4,
            color_discrete_sequence=['#95E1D3', '#F38181', '#EAFFD0']
        )
        fig_segment.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_segment, use_container_width=True)
    
    with col3:
        st.markdown('<div class="section-header"><h3>💳 Payment Methods</h3></div>', unsafe_allow_html=True)
        payment_data = df_filtered.groupby('payment_method')['line_revenue'].sum().reset_index()
        fig_payment = px.pie(
            payment_data,
            values='line_revenue',
            names='payment_method',
            hole=0.4
        )
        fig_payment.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_payment, use_container_width=True)

# ============================================
# PAGE 2: SALES PERFORMANCE
# ============================================

elif page == "📈 Sales Performance":
    
    st.markdown('<h1 class="main-header">📈 Sales Performance Analysis</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Detailed sales metrics and trends | {date_segment} View</p>', unsafe_allow_html=True)
    
    # Sales Metrics
    st.markdown('<div class="section-header"><h2>💰 Sales Metrics</h2></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    gross_revenue = df_filtered['gross_revenue'].sum()
    total_discounts = df_filtered['total_discount'].sum()
    net_revenue = df_filtered['line_revenue'].sum()
    discount_rate = (total_discounts / gross_revenue * 100) if gross_revenue > 0 else 0
    
    with col1:
        st.metric("💵 Gross Revenue", format_currency(gross_revenue))
    with col2:
        st.metric("🎫 Total Discounts", format_currency(total_discounts), delta=f"-{format_percentage(discount_rate)}")
    with col3:
        st.metric("💰 Net Revenue", format_currency(net_revenue))
    with col4:
        avg_discount = df_filtered['total_discount'].mean()
        st.metric("📊 Avg Discount", format_currency(avg_discount))
    
    create_insight_box(
        "💡 Sales Insight",
        f"""
        Discount Impact: {format_percentage(discount_rate)} of gross revenue was given as discounts 
        ({format_currency(total_discounts)}). This resulted in net revenue of {format_currency(net_revenue)}.<br>
        Recommendation: {'✅ Discount strategy is effective' if discount_rate < 15 else '⚠️ Consider optimizing discount strategy to improve margins'}
        """,
        "success" if discount_rate < 15 else "warning"
    )
    
    st.markdown("---")
    
    # Sales by Day of Week
    st.markdown('<div class="section-header"><h2>📅 Sales by Day of Week</h2></div>', unsafe_allow_html=True)
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_sales = df_filtered.groupby('day_of_week').agg({
        'line_revenue': 'sum',
        'transaction_id': 'nunique'
    }).reindex(day_order).reset_index()
    day_sales.columns = ['Day', 'Revenue', 'Transactions']
    
    fig_day = go.Figure()
    fig_day.add_trace(go.Bar(
        x=day_sales['Day'],
        y=day_sales['Revenue'],
        name='Revenue',
        marker_color='#1f77b4',
        text=day_sales['Revenue'],
        texttemplate='$%{text:,.0f}',
        textposition='outside'
    ))
    
    fig_day.update_layout(
        title='Revenue Distribution by Day of Week',
        xaxis_title='Day',
        yaxis_title='Revenue ($)',
        height=400
    )
    
    st.plotly_chart(fig_day, use_container_width=True)
    
    # Day insights
    best_day = day_sales.loc[day_sales['Revenue'].idxmax()]
    worst_day = day_sales.loc[day_sales['Revenue'].idxmin()]
    
    create_insight_box(
        "📊 Weekly Pattern",
        f"""
        • Best Day: {best_day['Day']} with {format_currency(best_day['Revenue'])} revenue<br>
        • Slowest Day: {worst_day['Day']} with {format_currency(worst_day['Revenue'])} revenue<br>
        • Recommendation: Increase staffing and inventory on {best_day['Day']}, 
          consider promotions on {worst_day['Day']} to boost sales
        """,
        "info"
    )
    
    st.markdown("---")
    
    # Product Performance
    st.markdown('<div class="section-header"><h2>🏆 Top & Bottom Performing Products</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🥇 Top 10 Products by Revenue")
        top_products = df_filtered.groupby('product_name').agg({
            'line_revenue': 'sum',
            'quantity': 'sum',
            'profit': 'sum'
        }).sort_values('line_revenue', ascending=False).head(10).reset_index()
        
        top_products['Revenue'] = top_products['line_revenue'].apply(format_currency)
        top_products['Profit'] = top_products['profit'].apply(format_currency)
        top_products['Units Sold'] = top_products['quantity']
        
        st.dataframe(
            top_products[['product_name', 'Revenue', 'Profit', 'Units Sold']],
            hide_index=True,
            use_container_width=True
        )
    
    with col2:
        st.subheader("📉 Bottom 10 Products by Revenue")
        bottom_products = df_filtered.groupby('product_name').agg({
            'line_revenue': 'sum',
            'quantity': 'sum',
            'profit': 'sum'
        }).sort_values('line_revenue', ascending=True).head(10).reset_index()
        
        bottom_products['Revenue'] = bottom_products['line_revenue'].apply(format_currency)
        bottom_products['Profit'] = bottom_products['profit'].apply(format_currency)
        bottom_products['Units Sold'] = bottom_products['quantity']
        
        st.dataframe(
            bottom_products[['product_name', 'Revenue', 'Profit', 'Units Sold']],
            hide_index=True,
            use_container_width=True
        )
    
    create_insight_box(
        "🎯 Product Strategy",
        f"""
        • Star Product: {top_products.iloc[0]['product_name']} generates 
          {top_products.iloc[0]['Revenue']} revenue<br>
        • Action Required: Review bottom performers for potential discontinuation or promotional opportunities<br>
        • Focus: Increase inventory and marketing for top 10 products
        """,
        "success"
    )

# ============================================
# PAGE 3: CUSTOMER INSIGHTS
# ============================================

elif page == "👥 Customer Insights":
    
    st.markdown('<h1 class="main-header">👥 Customer Insights & Behavior</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Understanding customer patterns and value</p>', unsafe_allow_html=True)
    
    # Customer Metrics
    st.markdown('<div class="section-header"><h2>📊 Customer Metrics</h2></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_customers = df_filtered['customer_id'].nunique()
    total_transactions = df_filtered['transaction_id'].nunique()
    avg_transactions_per_customer = total_transactions / total_customers if total_customers > 0 else 0
    customer_lifetime_value = df_filtered.groupby('customer_id')['line_revenue'].sum().mean()
    
    with col1:
        st.metric("👥 Total Customers", f"{total_customers:,}")
    with col2:
        st.metric("🔄 Avg Transactions/Customer", f"{avg_transactions_per_customer:.2f}")
    with col3:
        st.metric("💎 Avg Customer Value", format_currency(customer_lifetime_value))
    with col4:
        repeat_customers = df_filtered.groupby('customer_id').size()
        repeat_rate = (repeat_customers > 1).sum() / total_customers * 100 if total_customers > 0 else 0
        st.metric("🔁 Repeat Customer Rate", format_percentage(repeat_rate))
    
    st.markdown("---")
    
    # Customer Segmentation
    st.markdown('<div class="section-header"><h2>🎯 Customer Segmentation Analysis</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        segment_analysis = df_filtered.groupby('customer_segment').agg({
            'customer_id': 'nunique',
            'line_revenue': 'sum',
            'profit': 'sum',
            'transaction_id': 'nunique'
        }).reset_index()
        segment_analysis.columns = ['Segment', 'Customers', 'Revenue', 'Profit', 'Transactions']
        
        fig_segment_revenue = px.bar(
            segment_analysis,
            x='Segment',
            y='Revenue',
            color='Profit',
            color_continuous_scale=['red', 'yellow', 'green'],
            text='Revenue',
            title='Revenue by Customer Segment'
        )
        fig_segment_revenue.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig_segment_revenue, use_container_width=True)
    
    with col2:
        fig_segment_customers = px.pie(
            segment_analysis,
            values='Customers',
            names='Segment',
            title='Customer Distribution by Segment',
            hole=0.4,
            color_discrete_sequence=['#95E1D3', '#F38181', '#EAFFD0']
        )
        fig_segment_customers.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_segment_customers, use_container_width=True)
    
    # Segment insights
    best_segment = segment_analysis.loc[segment_analysis['Revenue'].idxmax()]
    create_insight_box(
        "🎯 Segment Performance",
        f"""
        • Most Valuable Segment: {best_segment['Segment']} with {format_currency(best_segment['Revenue'])} revenue<br>
        • Customer Count: {best_segment['Customers']:,} customers in this segment<br>
        • Avg Revenue per Customer: {format_currency(best_segment['Revenue'] / best_segment['Customers'])}<br>
        • Strategy: Focus retention efforts on {best_segment['Segment']} customers
        """,
        "success"
    )
    
    st.markdown("---")
    
    # Top Customers
    st.markdown('<div class="section-header"><h2>🏆 Top 20 Customers by Value</h2></div>', unsafe_allow_html=True)
    
    top_customers = df_filtered.groupby('customer_id').agg({
        'line_revenue': 'sum',
        'profit': 'sum',
        'transaction_id': 'nunique',
        'customer_segment': 'first'
    }).sort_values('line_revenue', ascending=False).head(20).reset_index()
    
    top_customers.columns = ['Customer ID', 'Total Revenue', 'Total Profit', 'Transactions', 'Segment']
    top_customers['Rank'] = range(1, len(top_customers) + 1)
    top_customers['Avg Order Value'] = top_customers['Total Revenue'] / top_customers['Transactions']
    
    # Format for display
    display_customers = top_customers.copy()
    display_customers['Total Revenue'] = display_customers['Total Revenue'].apply(format_currency)
    display_customers['Total Profit'] = display_customers['Total Profit'].apply(format_currency)
    display_customers['Avg Order Value'] = display_customers['Avg Order Value'].apply(format_currency)
    
    st.dataframe(
        display_customers[['Rank', 'Customer ID', 'Segment', 'Total Revenue', 'Total Profit', 'Transactions', 'Avg Order Value']],
        hide_index=True,
        use_container_width=True,
        height=400
    )
    
    create_insight_box(
        "💎 VIP Customer Program",
        f"""
        • Top Customer: {top_customers.iloc[0]['Customer ID']} has spent 
          {format_currency(top_customers.iloc[0]['Total Revenue'])}<br>
        • Recommendation: Create VIP loyalty program for top 20 customers<br>
        • Potential: These 20 customers represent 
          {format_percentage((top_customers['Total Revenue'].sum() / df_filtered['line_revenue'].sum()) * 100)} 
          of total revenue
        """,
        "success"
    )
    
    st.markdown("---")
    
    # Customer Purchase Patterns
    st.markdown('<div class="section-header"><h2>🛒 Purchase Patterns</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average basket size by segment
        basket_analysis = df_filtered.groupby(['customer_segment', 'bill_id']).agg({
            'line_revenue': 'sum'
        }).reset_index()
        avg_basket = basket_analysis.groupby('customer_segment')['line_revenue'].mean().reset_index()
        avg_basket.columns = ['Segment', 'Avg Basket Value']
        
        fig_basket = px.bar(
            avg_basket,
            x='Segment',
            y='Avg Basket Value',
            title='Average Basket Value by Segment',
            color='Avg Basket Value',
            color_continuous_scale='Blues',
            text='Avg Basket Value'
        )
        fig_basket.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
        st.plotly_chart(fig_basket, use_container_width=True)
    
    with col2:
        # Products per transaction by segment
        products_per_transaction = df_filtered.groupby(['customer_segment', 'transaction_id']).size().reset_index(name='products')
        avg_products = products_per_transaction.groupby('customer_segment')['products'].mean().reset_index()
        avg_products.columns = ['Segment', 'Avg Products']
        
        fig_products = px.bar(
            avg_products,
            x='Segment',
            y='Avg Products',
            title='Average Products per Transaction',
            color='Avg Products',
            color_continuous_scale='Greens',
            text='Avg Products'
        )
        fig_products.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        st.plotly_chart(fig_products, use_container_width=True)

# ============================================
# PAGE 4: PRODUCT ANALYTICS
# ============================================

elif page == "📦 Product Analytics":
    
    st.markdown('<h1 class="main-header">📦 Product Performance Analytics</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Deep dive into product performance and profitability</p>', unsafe_allow_html=True)
    
    # Product Metrics
    st.markdown('<div class="section-header"><h2>📊 Product Metrics</h2></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_products = df_filtered['product_id'].nunique()
    total_units_sold = df_filtered['quantity'].sum()
    avg_unit_price = df_filtered['unit_price'].mean()
    avg_units_per_transaction = df_filtered.groupby('transaction_id')['quantity'].sum().mean()
    
    with col1:
        st.metric("📦 Total Products", f"{total_products:,}")
    with col2:
        st.metric("📊 Units Sold", f"{total_units_sold:,}")
    with col3:
        st.metric("💵 Avg Unit Price", format_currency(avg_unit_price))
    with col4:
        st.metric("🛒 Avg Units/Transaction", f"{avg_units_per_transaction:.1f}")
    
    st.markdown("---")
    
    # Category Performance Matrix
    st.markdown('<div class="section-header"><h2>📊 Category Performance Matrix</h2></div>', unsafe_allow_html=True)
    
    category_matrix = df_filtered.groupby('product_category').agg({
        'line_revenue': 'sum',
        'profit': 'sum',
        'quantity': 'sum',
        'transaction_id': 'nunique',
        'total_discount': 'sum'
    }).reset_index()
    
    category_matrix['Profit Margin %'] = (category_matrix['profit'] / category_matrix['line_revenue'] * 100).round(2)
    category_matrix['Avg Transaction Value'] = (category_matrix['line_revenue'] / category_matrix['transaction_id']).round(2)
    
    # Scatter plot: Revenue vs Profit Margin
    fig_matrix = px.scatter(
        category_matrix,
        x='line_revenue',
        y='Profit Margin %',
        size='quantity',
        color='product_category',
        hover_data=['product_category', 'line_revenue', 'profit', 'quantity'],
        title='Category Performance: Revenue vs Profit Margin (bubble size = units sold)',
        labels={'line_revenue': 'Revenue ($)', 'Profit Margin %': 'Profit Margin (%)'}
    )
    
    # Add quadrant lines
    avg_revenue = category_matrix['line_revenue'].mean()
    avg_margin = category_matrix['Profit Margin %'].mean()
    
    fig_matrix.add_hline(y=avg_margin, line_dash="dash", line_color="gray", annotation_text="Avg Margin")
    fig_matrix.add_vline(x=avg_revenue, line_dash="dash", line_color="gray", annotation_text="Avg Revenue")
    
    fig_matrix.update_layout(height=500)
    st.plotly_chart(fig_matrix, use_container_width=True)
    
    # Quadrant analysis
    create_insight_box(
        "📊 Category Quadrant Analysis",
        f"""
        Stars (High Revenue, High Margin): Categories in top-right quadrant - Invest and grow<br>
        Cash Cows (High Revenue, Low Margin): Bottom-right - Optimize costs<br>
        Question Marks (Low Revenue, High Margin): Top-left - Consider expansion<br>
        Dogs (Low Revenue, Low Margin): Bottom-left - Review or discontinue
        """,
        "info"
    )
    
    st.markdown("---")
    
    # Detailed Category Table
    st.markdown('<div class="section-header"><h2>📋 Detailed Category Performance</h2></div>', unsafe_allow_html=True)
    
    category_table = category_matrix.copy()
    category_table['Revenue'] = category_table['line_revenue'].apply(format_currency)
    category_table['Profit'] = category_table['profit'].apply(format_currency)
    category_table['Discounts'] = category_table['total_discount'].apply(format_currency)
    category_table['Avg Transaction'] = category_table['Avg Transaction Value'].apply(format_currency)
    
    st.dataframe(
        category_table[['product_category', 'Revenue', 'Profit', 'Profit Margin %', 
                       'quantity', 'transaction_id', 'Discounts', 'Avg Transaction']].rename(columns={
            'product_category': 'Category',
            'quantity': 'Units Sold',
            'transaction_id': 'Transactions'
        }),
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Product Profitability Analysis
    st.markdown('<div class="section-header"><h2>💰 Product Profitability Analysis</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🟢 Most Profitable Products")
        profitable_products = df_filtered.groupby('product_name').agg({
            'profit': 'sum',
            'line_revenue': 'sum',
            'quantity': 'sum'
        }).reset_index()
        profitable_products['Profit Margin %'] = (profitable_products['profit'] / profitable_products['line_revenue'] * 100).round(2)
        profitable_products = profitable_products.sort_values('profit', ascending=False).head(10)
        
        profitable_products['Profit'] = profitable_products['profit'].apply(format_currency)
        profitable_products['Revenue'] = profitable_products['line_revenue'].apply(format_currency)
        
        st.dataframe(
            profitable_products[['product_name', 'Revenue', 'Profit', 'Profit Margin %', 'quantity']].rename(columns={
                'product_name': 'Product',
                'quantity': 'Units'
            }),
            hide_index=True,
            use_container_width=True
        )
    
    with col2:
        st.subheader("🔴 Least Profitable Products")
        unprofitable_products = df_filtered.groupby('product_name').agg({
            'profit': 'sum',
            'line_revenue': 'sum',
            'quantity': 'sum'
        }).reset_index()
        unprofitable_products['Profit Margin %'] = (unprofitable_products['profit'] / unprofitable_products['line_revenue'] * 100).round(2)
        unprofitable_products = unprofitable_products.sort_values('profit', ascending=True).head(10)
        
        unprofitable_products['Profit'] = unprofitable_products['profit'].apply(format_currency)
        unprofitable_products['Revenue'] = unprofitable_products['line_revenue'].apply(format_currency)
        
        st.dataframe(
            unprofitable_products[['product_name', 'Revenue', 'Profit', 'Profit Margin %', 'quantity']].rename(columns={
                'product_name': 'Product',
                'quantity': 'Units'
            }),
            hide_index=True,
            use_container_width=True
        )
    
    create_insight_box(
        "💡 Product Strategy Recommendations",
        f"""
        • Focus: Promote and stock more of high-profit products<br>
        • Review: Analyze pricing and costs for low-profit items<br>
        • Action: Consider bundling low-profit items with high-margin products<br>
        • Optimize: Reduce discounts on already profitable products
        """,
        "success"
    )

# ============================================
# PAGE 5: STORE PERFORMANCE
# ============================================

elif page == "🏪 Store Performance":
    
    st.markdown('<h1 class="main-header">🏪 Store Performance Analysis</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Compare and analyze store-level performance</p>', unsafe_allow_html=True)
    
    # Store Metrics
    st.markdown('<div class="section-header"><h2>📊 Store Comparison</h2></div>', unsafe_allow_html=True)
    
    store_metrics = df_filtered.groupby('store_location').agg({
        'line_revenue': 'sum',
        'profit': 'sum',
        'transaction_id': 'nunique',
        'customer_id': 'nunique',
        'quantity': 'sum'
    }).reset_index()
    
    store_metrics['Profit Margin %'] = (store_metrics['profit'] / store_metrics['line_revenue'] * 100).round(2)
    store_metrics['Avg Transaction Value'] = (store_metrics['line_revenue'] / store_metrics['transaction_id']).round(2)
    store_metrics['Avg Items per Transaction'] = (store_metrics['quantity'] / store_metrics['transaction_id']).round(2)
    
    # Display metrics
    for idx, row in store_metrics.iterrows():
        with st.expander(f"🏪 {row['store_location']} Store - Click to expand", expanded=True):
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("💰 Revenue", format_currency(row['line_revenue']))
            with col2:
                st.metric("💵 Profit", format_currency(row['profit']), 
                         delta=format_percentage(row['Profit Margin %']))
            with col3:
                st.metric("🧾 Transactions", f"{row['transaction_id']:,}")
            with col4:
                st.metric("👥 Customers", f"{row['customer_id']:,}")
            with col5:
                st.metric("🛒 Avg Order", format_currency(row['Avg Transaction Value']))
    
    st.markdown("---")
    
    # Store Comparison Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig_store_revenue = px.bar(
            store_metrics,
            x='store_location',
            y='line_revenue',
            color='Profit Margin %',
            color_continuous_scale=['red', 'yellow', 'green'],
            title='Revenue by Store (colored by profit margin)',
            text='line_revenue'
        )
        fig_store_revenue.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig_store_revenue, use_container_width=True)
    
    with col2:
        fig_store_customers = px.bar(
            store_metrics,
            x='store_location',
            y='customer_id',
            title='Unique Customers by Store',
            color='customer_id',
            color_continuous_scale='Blues',
            text='customer_id'
        )
        fig_store_customers.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig_store_customers.update_layout(showlegend=False)
        st.plotly_chart(fig_store_customers, use_container_width=True)
    
    st.markdown("---")
    
    # Store Performance Table
    st.markdown('<div class="section-header"><h2>📋 Detailed Store Metrics</h2></div>', unsafe_allow_html=True)
    
    store_table = store_metrics.copy()
    store_table['Revenue'] = store_table['line_revenue'].apply(format_currency)
    store_table['Profit'] = store_table['profit'].apply(format_currency)
    store_table['Avg Transaction'] = store_table['Avg Transaction Value'].apply(format_currency)
    
    st.dataframe(
        store_table[['store_location', 'Revenue', 'Profit', 'Profit Margin %', 
                    'transaction_id', 'customer_id', 'Avg Transaction', 'Avg Items per Transaction']].rename(columns={
            'store_location': 'Store',
            'transaction_id': 'Transactions',
            'customer_id': 'Customers'
        }),
        hide_index=True,
        use_container_width=True
    )
    
    # Store insights
    best_store = store_metrics.loc[store_metrics['line_revenue'].idxmax()]
    best_margin_store = store_metrics.loc[store_metrics['Profit Margin %'].idxmax()]
    
    create_insight_box(
        "🏆 Store Performance Insights",
        f"""
        • Highest Revenue: {best_store['store_location']} with {format_currency(best_store['line_revenue'])}<br>
        • **Best Profit Margin: {best_margin_store['store_location']} with {format_percentage(best_margin_store['Profit Margin %'])} margin<br>
        • Recommendation: Share best practices from top-performing stores with others<br>
        • Action: Investigate why certain stores have lower margins and address issues
        """,
        "success"
    )
    
    st.markdown("---")
    
    # Category Performance by Store
    st.markdown('<div class="section-header"><h2>📦 Category Performance by Store</h2></div>', unsafe_allow_html=True)
    
    store_category = df_filtered.groupby(['store_location', 'product_category'])['line_revenue'].sum().reset_index()
    
    fig_store_category = px.bar(
        store_category,
        x='store_location',
        y='line_revenue',
        color='product_category',
        title='Revenue by Category across Stores',
        labels={'line_revenue': 'Revenue ($)', 'store_location': 'Store'},
        barmode='group'
    )
    fig_store_category.update_layout(height=400)
    st.plotly_chart(fig_store_category, use_container_width=True)
    
    create_insight_box(
        "📊 Category Mix Insights",
        """
        • Different stores may have different category strengths<br>
        • Optimize inventory based on store-specific category performance<br>
        • Consider local demographics when planning product mix
        """,
        "info"
    )

# ============================================
# PAGE 6: CHANNEL & PAYMENT ANALYSIS
# ============================================

elif page == "🔄 Channel & Payment Analysis":
    
    st.markdown('<h1 class="main-header">🔄 Channel & Payment Analysis</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Analyze sales channels and payment preferences</p>', unsafe_allow_html=True)
    
    # Channel Metrics
    st.markdown('<div class="section-header"><h2>📱 Channel Performance</h2></div>', unsafe_allow_html=True)
    
    channel_metrics = df_filtered.groupby('channel').agg({
        'line_revenue': 'sum',
        'profit': 'sum',
        'transaction_id': 'nunique',
        'customer_id': 'nunique'
    }).reset_index()
    
    channel_metrics['Profit Margin %'] = (channel_metrics['profit'] / channel_metrics['line_revenue'] * 100).round(2)
    channel_metrics['Avg Transaction Value'] = (channel_metrics['line_revenue'] / channel_metrics['transaction_id']).round(2)
    
    col1, col2 = st.columns(2)
    
    with col1:
        for idx, row in channel_metrics.iterrows():
            st.markdown(f"### {row['channel']}")
            subcol1, subcol2, subcol3 = st.columns(3)
            with subcol1:
                st.metric("💰 Revenue", format_currency(row['line_revenue']))
            with subcol2:
                st.metric("💵 Profit", format_currency(row['profit']))
            with subcol3:
                st.metric("📊 Margin", format_percentage(row['Profit Margin %']))
    
    with col2:
        fig_channel_split = px.pie(
            channel_metrics,
            values='line_revenue',
            names='channel',
            title='Revenue Split by Channel',
            hole=0.4,
            color_discrete_sequence=['#4ECDC4', '#FF6B6B']
        )
        fig_channel_split.update_traces(textposition='inside', textinfo='percent+label+value')
        st.plotly_chart(fig_channel_split, use_container_width=True)
    
    # Channel insights
    dominant_channel = channel_metrics.loc[channel_metrics['line_revenue'].idxmax()]
    create_insight_box(
        "📱 Channel Insights",
        f"""
        • **Dominant Channel**: {dominant_channel['channel']} generates 
          {format_percentage((dominant_channel['line_revenue'] / channel_metrics['line_revenue'].sum()) * 100)} of revenue<br>
        • **Profit Margin**: {dominant_channel['channel']} has {format_percentage(dominant_channel['Profit Margin %'])} margin<br>
        • **Strategy**: {'Invest in online infrastructure' if dominant_channel['channel'] == 'Online' else 'Enhance in-store experience'}
        """,
        "success"
    )
    
    st.markdown("---")
    
    # Payment Method Analysis
    st.markdown('<div class="section-header"><h2>💳 Payment Method Analysis</h2></div>', unsafe_allow_html=True)
    
    payment_metrics = df_filtered.groupby('payment_method').agg({
        'line_revenue': 'sum',
        'transaction_id': 'nunique',
        'customer_id': 'nunique'
    }).reset_index()
    
    payment_metrics['Avg Transaction Value'] = (payment_metrics['line_revenue'] / payment_metrics['transaction_id']).round(2)
    payment_metrics = payment_metrics.sort_values('line_revenue', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_payment_revenue = px.bar(
            payment_metrics,
            x='payment_method',
            y='line_revenue',
            title='Revenue by Payment Method',
            color='line_revenue',
            color_continuous_scale='Greens',
            text='line_revenue'
        )
        fig_payment_revenue.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_payment_revenue.update_layout(showlegend=False)
        st.plotly_chart(fig_payment_revenue, use_container_width=True)
    
    with col2:
        fig_payment_transactions = px.pie(
            payment_metrics,
            values='transaction_id',
            names='payment_method',
            title='Transaction Count by Payment Method',
            hole=0.4
        )
        fig_payment_transactions.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_payment_transactions, use_container_width=True)
    
    st.markdown("---")
    
    # Payment Method Table
    st.markdown('<div class="section-header"><h2>📋 Payment Method Details</h2></div>', unsafe_allow_html=True)
    
    payment_table = payment_metrics.copy()
    payment_table['Revenue'] = payment_table['line_revenue'].apply(format_currency)
    payment_table['Avg Transaction'] = payment_table['Avg Transaction Value'].apply(format_currency)
    
    st.dataframe(
        payment_table[['payment_method', 'Revenue', 'transaction_id', 'customer_id', 'Avg Transaction']].rename(columns={
            'payment_method': 'Payment Method',
            'transaction_id': 'Transactions',
            'customer_id': 'Customers'
        }),
        hide_index=True,
        use_container_width=True
    )
    
    # Payment insights
    top_payment = payment_metrics.iloc[0]
    create_insight_box(
        "💳 Payment Insights",
        f"""
        • **Most Popular**: {top_payment['payment_method']} with {top_payment['transaction_id']:,} transactions<br>
        • **Highest Value**: {top_payment['payment_method']} has average transaction of 
          {format_currency(top_payment['Avg Transaction Value'])}<br>
        • **Recommendation**: Ensure all payment methods are well-supported and consider incentives for digital payments
        """,
        "info"
    )
    
    st.markdown("---")
    
    # Channel x Payment Cross-Analysis
    st.markdown('<div class="section-header"><h2>🔀 Channel × Payment Cross-Analysis</h2></div>', unsafe_allow_html=True)
    
    channel_payment = df_filtered.groupby(['channel', 'payment_method'])['line_revenue'].sum().reset_index()
    
    fig_heatmap = px.density_heatmap(
        channel_payment,
        x='channel',
        y='payment_method',
        z='line_revenue',
        title='Revenue Heatmap: Channel × Payment Method',
        color_continuous_scale='YlOrRd',
        labels={'line_revenue': 'Revenue ($)'}
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    create_insight_box(
        "🔍 Cross-Analysis Insights",
        """
        • Identify which payment methods are preferred in each channel<br>
        • Online channels typically favor digital payments (UPI, Credit Card)<br>
        • In-store may have more cash transactions<br>
        • Optimize payment options based on channel preferences
        """,
        "info"
    )

# ============================================
# PAGE 7: PROFITABILITY ANALYSIS
# ============================================

elif page == "🎯 Profitability Analysis":
    
    st.markdown('<h1 class="main-header">🎯 Profitability Analysis</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Deep dive into profit margins and cost analysis</p>', unsafe_allow_html=True)
    
    # Profitability Metrics
    st.markdown('<div class="section-header"><h2>💰 Profitability Overview</h2></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_revenue = df_filtered['line_revenue'].sum()
    total_cost = df_filtered['cost'].sum()
    total_profit = df_filtered['profit'].sum()
    overall_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    total_discounts = df_filtered['total_discount'].sum()
    
    with col1:
        st.metric("💰 Revenue", format_currency(total_revenue))
    with col2:
        st.metric("💸 Cost", format_currency(total_cost))
    with col3:
        profit_color = "normal" if total_profit > 0 else "inverse"
        st.metric("💵 Profit", format_currency(total_profit), 
                 delta=format_percentage(overall_margin))
    with col4:
        st.metric("📊 Profit Margin", format_percentage(overall_margin))
    with col5:
        st.metric("🎫 Discounts", format_currency(total_discounts))
    
    # Profit/Loss indicator
    if total_profit > 0:
        st.success(f"✅ **PROFITABLE**: Business is generating {format_currency(total_profit)} in profit with {format_percentage(overall_margin)} margin")
    else:
        st.error(f"❌ **LOSS**: Business is incurring {format_currency(abs(total_profit))} in losses")
    
    st.markdown("---")
    
    # Profit Trend
    st.markdown('<div class="section-header"><h2>📈 Profit Trend Analysis</h2></div>', unsafe_allow_html=True)
    
    if date_segment == "Daily":
        profit_trend = df_filtered.groupby('date').agg({
            'line_revenue': 'sum',
            'cost': 'sum',
            'profit': 'sum'
        }).reset_index()
        x_axis = 'date'
    elif date_segment == "Monthly":
        profit_trend = df_filtered.groupby('year_month').agg({
            'line_revenue': 'sum',
            'cost': 'sum',
            'profit': 'sum'
        }).reset_index()
        x_axis = 'year_month'
    else:
        profit_trend = df_filtered.groupby('date').agg({
            'line_revenue': 'sum',
            'cost': 'sum',
            'profit': 'sum'
        }).reset_index()
        x_axis = 'date'
    
    profit_trend['Profit Margin %'] = (profit_trend['profit'] / profit_trend['line_revenue'] * 100).round(2)
    
    fig_profit_trend = go.Figure()
    
    fig_profit_trend.add_trace(go.Bar(
        x=profit_trend[x_axis],
        y=profit_trend['line_revenue'],
        name='Revenue',
        marker_color='lightblue'
    ))
    
    fig_profit_trend.add_trace(go.Bar(
        x=profit_trend[x_axis],
        y=profit_trend['cost'],
        name='Cost',
        marker_color='lightcoral'
    ))
    
    fig_profit_trend.add_trace(go.Scatter(
        x=profit_trend[x_axis],
        y=profit_trend['profit'],
        name='Profit',
        mode='lines+markers',
        line=dict(color='green', width=3),
        marker=dict(size=8),
        yaxis='y2'
    ))
    
    fig_profit_trend.update_layout(
        title='Revenue, Cost & Profit Trend',
        xaxis_title='Period',
        yaxis_title='Revenue & Cost ($)',
        yaxis2=dict(
            title='Profit ($)',
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        height=450,
        barmode='group'
    )
    
    st.plotly_chart(fig_profit_trend, use_container_width=True)
    
    st.markdown("---")
    
    # Profitability by Dimension
    st.markdown('<div class="section-header"><h2>📊 Profitability by Dimension</h2></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📦 By Category", "🏪 By Store", "📱 By Channel", "👥 By Segment"])
    
    with tab1:
        category_profit = df_filtered.groupby('product_category').agg({
            'line_revenue': 'sum',
            'cost': 'sum',
            'profit': 'sum'
        }).reset_index()
        category_profit['Profit Margin %'] = (category_profit['profit'] / category_profit['line_revenue'] * 100).round(2)
        category_profit = category_profit.sort_values('profit', ascending=False)
        
        fig_cat_profit = go.Figure()
        fig_cat_profit.add_trace(go.Bar(
            y=category_profit['product_category'],
            x=category_profit['line_revenue'],
            name='Revenue',
            orientation='h',
            marker_color='lightblue'
        ))
        fig_cat_profit.add_trace(go.Bar(
            y=category_profit['product_category'],
            x=category_profit['profit'],
            name='Profit',
            orientation='h',
            marker_color='lightgreen'
        ))
        fig_cat_profit.update_layout(title='Revenue vs Profit by Category', barmode='group', height=400)
        st.plotly_chart(fig_cat_profit, use_container_width=True)
        
        # Table
        cat_table = category_profit.copy()
        cat_table['Revenue'] = cat_table['line_revenue'].apply(format_currency)
        cat_table['Cost'] = cat_table['cost'].apply(format_currency)
        cat_table['Profit'] = cat_table['profit'].apply(format_currency)
        st.dataframe(cat_table[['product_category', 'Revenue', 'Cost', 'Profit', 'Profit Margin %']], 
                    hide_index=True, use_container_width=True)
    
    with tab2:
        store_profit = df_filtered.groupby('store_location').agg({
            'line_revenue': 'sum',
            'cost': 'sum',
            'profit': 'sum'
        }).reset_index()
        store_profit['Profit Margin %'] = (store_profit['profit'] / store_profit['line_revenue'] * 100).round(2)
        
        fig_store_profit = px.bar(
            store_profit,
            x='store_location',
            y=['line_revenue', 'cost', 'profit'],
            title='Revenue, Cost & Profit by Store',
            barmode='group',
            labels={'value': 'Amount ($)', 'store_location': 'Store'}
        )
        st.plotly_chart(fig_store_profit, use_container_width=True)
        
        # Table
        store_table = store_profit.copy()
        store_table['Revenue'] = store_table['line_revenue'].apply(format_currency)
        store_table['Cost'] = store_table['cost'].apply(format_currency)
        store_table['Profit'] = store_table['profit'].apply(format_currency)
        st.dataframe(store_table[['store_location', 'Revenue', 'Cost', 'Profit', 'Profit Margin %']], 
                    hide_index=True, use_container_width=True)
    
    with tab3:
        channel_profit = df_filtered.groupby('channel').agg({
            'line_revenue': 'sum',
            'cost': 'sum',
            'profit': 'sum'
        }).reset_index()
        channel_profit['Profit Margin %'] = (channel_profit['profit'] / channel_profit['line_revenue'] * 100).round(2)
        
        fig_channel_profit = px.bar(
            channel_profit,
            x='channel',
            y=['line_revenue', 'cost', 'profit'],
            title='Revenue, Cost & Profit by Channel',
            barmode='group'
        )
        st.plotly_chart(fig_channel_profit, use_container_width=True)
        
        # Table
        channel_table = channel_profit.copy()
        channel_table['Revenue'] = channel_table['line_revenue'].apply(format_currency)
        channel_table['Cost'] = channel_table['cost'].apply(format_currency)
        channel_table['Profit'] = channel_table['profit'].apply(format_currency)
        st.dataframe(channel_table[['channel', 'Revenue', 'Cost', 'Profit', 'Profit Margin %']], 
                    hide_index=True, use_container_width=True)
    
    with tab4:
        segment_profit = df_filtered.groupby('customer_segment').agg({
            'line_revenue': 'sum',
            'cost': 'sum',
            'profit': 'sum'
        }).reset_index()
        segment_profit['Profit Margin %'] = (segment_profit['profit'] / segment_profit['line_revenue'] * 100).round(2)
        
        fig_segment_profit = px.bar(
            segment_profit,
            x='customer_segment',
            y=['line_revenue', 'cost', 'profit'],
            title='Revenue, Cost & Profit by Customer Segment',
            barmode='group'
        )
        st.plotly_chart(fig_segment_profit, use_container_width=True)
        
        # Table
        segment_table = segment_profit.copy()
        segment_table['Revenue'] = segment_table['line_revenue'].apply(format_currency)
        segment_table['Cost'] = segment_table['cost'].apply(format_currency)
        segment_table['Profit'] = segment_table['profit'].apply(format_currency)
        st.dataframe(segment_table[['customer_segment', 'Revenue', 'Cost', 'Profit', 'Profit Margin %']], 
                    hide_index=True, use_container_width=True)
    
    st.markdown("---")
    
    # Key Recommendations
    st.markdown('<div class="section-header"><h2>💡 Profitability Recommendations</h2></div>', unsafe_allow_html=True)
    
    recommendations = []
    
    if overall_margin < 20:
        recommendations.append("⚠️ **Low Profit Margin**: Overall margin is below 20%. Consider reviewing pricing strategy and cost structure.")
    
    if total_discounts / total_revenue > 0.15:
        recommendations.append("⚠️ **High Discount Rate**: Discounts exceed 15% of revenue. Review discount policies to improve profitability.")
    
    # Find loss-making categories
    loss_categories = category_profit[category_profit['profit'] < 0]
    if len(loss_categories) > 0:
        recommendations.append(f"❌ **Loss-Making Categories**: {', '.join(loss_categories['product_category'].tolist())} are generating losses. Consider discontinuing or repricing.")
    
    # Find low-margin categories
    low_margin_categories = category_profit[category_profit['Profit Margin %'] < 10]
    if len(low_margin_categories) > 0:
        recommendations.append(f"📉 **Low Margin Categories**: {', '.join(low_margin_categories['product_category'].tolist())} have margins below 10%. Review pricing and costs.")
    
    if len(recommendations) > 0:
        for rec in recommendations:
            st.warning(rec)
    else:
        st.success("✅ **Healthy Profitability**: All metrics are within acceptable ranges. Continue monitoring and optimizing.")

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; color: white;'>
        <h3>🛒 UrbanMart Analytics Platform</h3>
        <p>Powered by Python, Streamlit & Plotly</p>
        <p><strong>MAIB Students Project 2025 By Neel,Tanishk and Harsh</strong></p>
        <p style='font-size: 0.9rem;'>
            📊 Data-Driven Insights | 🎯 Strategic Decision Making | 📈 Business Intelligence
        </p>
    </div>
""", unsafe_allow_html=True)