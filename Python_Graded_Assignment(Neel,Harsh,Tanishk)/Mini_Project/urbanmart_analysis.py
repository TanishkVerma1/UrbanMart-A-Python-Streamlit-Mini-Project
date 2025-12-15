import pandas as pd
import csv
from datetime import datetime

# ============================================
# PART 1: Basic Python & Data Loading
# ============================================

def welcome_message():
    """Display welcome message using f-strings"""
    store_name = "UrbanMart"
    print("=" * 60)
    print(f"Welcome to {store_name} Sales Analysis")
    print("=" * 60)
    print()

def load_data_with_csv(filename):
    """Load data using built-in csv module (Option A)"""
    try:
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            data = list(reader)
        return data
    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found!")
        return None

def load_data_with_pandas(filename):
    """Load data using pandas (Option B - Preferred)"""
    try:
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found!")
        return None
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None

def basic_sanity_checks(df):
    """Print basic information about the dataset"""
    print("\n📊 BASIC SANITY CHECKS")
    print("-" * 60)
    
    # Total rows
    print(f"Total number of rows: {len(df)}")
    
    # Unique stores
    unique_stores = df['store_id'].unique().tolist()
    print(f"Unique store IDs: {unique_stores}")
    
    # Date range
    min_date = df['date'].min()
    max_date = df['date'].max()
    print(f"Date range: {min_date} to {max_date}")
    print()

def demonstrate_data_structures(df):
    """Demonstrate lists, tuples, and dictionaries"""
    print("\n📚 DATA STRUCTURES DEMONSTRATION")
    print("-" * 60)
    
    # List of all product categories
    categories_list = df['product_category'].unique().tolist()
    print(f"Product Categories (List): {categories_list}")
    
    # Dictionary mapping store_id to store_location
    store_mapping = df[['store_id', 'store_location']].drop_duplicates().set_index('store_id')['store_location'].to_dict()
    print(f"Store Mapping (Dictionary): {store_mapping}")
    
    # Count Online vs In-store manually using loop
    online_count = 0
    instore_count = 0
    
    for channel in df['channel']:
        if channel == "Online":
            online_count += 1
        elif channel == "In-store":
            instore_count += 1
    
    print(f"\nChannel Distribution (Manual Count):")
    print(f"  Online: {online_count}")
    print(f"  In-store: {instore_count}")
    print()

# ============================================
# PART 2: Functions & Simple KPIs
# ============================================

def compute_total_revenue(df):
    """
    Returns total revenue = sum((quantity * unit_price) - discount_applied)
    """
    df['line_revenue'] = (df['quantity'] * df['unit_price']) - df['discount_applied']
    total_revenue = df['line_revenue'].sum()
    return round(total_revenue, 2)

def compute_revenue_by_store(df):
    """
    Returns a dictionary of store-wise revenue
    """
    df['line_revenue'] = (df['quantity'] * df['unit_price']) - df['discount_applied']
    revenue_by_store = df.groupby('store_location')['line_revenue'].sum().to_dict()
    
    # Round values
    revenue_by_store = {k: round(v, 2) for k, v in revenue_by_store.items()}
    return revenue_by_store

def compute_top_n_products(df, n=5):
    """
    Returns top n products by revenue
    """
    df['line_revenue'] = (df['quantity'] * df['unit_price']) - df['discount_applied']
    top_products = df.groupby('product_name')['line_revenue'].sum().sort_values(ascending=False).head(n)
    return top_products.to_dict()

def display_total_revenue(df):
    """Display total revenue"""
    total = compute_total_revenue(df)
    print("\n💰 TOTAL REVENUE")
    print("-" * 60)
    print(f"Total Revenue: ${total:,.2f}")
    print()

def display_revenue_by_store(df):
    """Display revenue by store"""
    revenue_dict = compute_revenue_by_store(df)
    print("\n🏪 REVENUE BY STORE")
    print("-" * 60)
    for store, revenue in revenue_dict.items():
        print(f"{store:20s}: ${revenue:,.2f}")
    print()

def display_top_products(df, n=5):
    """Display top N products"""
    top_products = compute_top_n_products(df, n)
    print(f"\n🏆 TOP {n} PRODUCTS BY REVENUE")
    print("-" * 60)
    for i, (product, revenue) in enumerate(top_products.items(), 1):
        print(f"{i}. {product:30s}: ${revenue:,.2f}")
    print()

# ============================================
# PART 2: CLI Menu with Error Handling
# ============================================

def display_menu():
    """Display the CLI menu"""
    print("\n" + "=" * 60)
    print("URBANMART ANALYTICS MENU")
    print("=" * 60)
    print("1. Show Total Revenue")
    print("2. Show Revenue by Store")
    print("3. Show Top 5 Products")
    print("4. Exit")
    print("=" * 60)

def run_cli_menu(df):
    """Run the interactive CLI menu"""
    while True:
        display_menu()
        
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                display_total_revenue(df)
            elif choice == '2':
                display_revenue_by_store(df)
            elif choice == '3':
                display_top_products(df, 5)
            elif choice == '4':
                print("\n👋 Thank you for using UrbanMart Analytics!")
                print("=" * 60)
                break
            else:
                print("\n❌ Invalid choice! Please enter a number between 1 and 4.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Exiting... Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try again.")

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Main function to run the analysis"""
    welcome_message()
    
    # Load data
    filename = "urbanmart_sales.csv"
    print(f"📂 Loading data from {filename}...")
    
    df = load_data_with_pandas(filename)
    
    if df is None:
        print("\n❌ Cannot proceed without data. Exiting...")
        return
    
    print(f"✅ Data loaded successfully!\n")
    
    # Basic sanity checks
    basic_sanity_checks(df)
    
    # Demonstrate data structures
    demonstrate_data_structures(df)
    
    # Run CLI menu
    run_cli_menu(df)

if __name__ == "__main__":
    main()