import pandas as pd
import numpy as np
import sys
from pathlib import Path

def _clean_price(price_str):
    """Cleans 'US$20.99' -> 20.99"""
    if pd.isna(price_str): return np.nan
    
    # Convert to string
    clean_str = str(price_str)
    
    # Remove 'US$', '$', ',', and whitespace
    clean_str = clean_str.replace('US$', '').replace('$', '').replace(',', '').strip()
    
    try:
        return float(clean_str)
    except ValueError:
        return np.nan

def _clean_reviews(review_str):
    """Cleans '5 reviews' -> 5"""
    if pd.isna(review_str): return 0
    
    # Remove non-digit characters 
    clean_str = ''.join(filter(str.isdigit, str(review_str)))
    
    try:
        return int(clean_str)
    except ValueError:
        return 0

def get_clean_data(raw_csv_path):
    print("\n--- 2. STARTING DATA CLEANING ---")
    
    try:
        # encoding='utf-8' is safer for web scraped text
        df = pd.read_csv(raw_csv_path, encoding='utf-8')
    except FileNotFoundError:
        print(f"❌ Error: '{raw_csv_path}' not found.")
        sys.exit()

    # 1. Clean Price
    df['price'] = df['price'].apply(_clean_price)
    
    # 2. Clean Reviews
    df['reviews'] = df['reviews'].apply(_clean_reviews)
    
    # 3. Clean Rating
    # If rating is 0 or missing, replace with NaN or keep as 0
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)

    
    # Feature 1: Price Category
    def categorize_price(p):
        if pd.isna(p): return "Unknown"
        if p < 20: return "Budget"
        elif p < 50: return "Standard"
        else: return "Premium"
    
    df['price_category'] = df['price'].apply(categorize_price)

    # Feature 2: High Engagement
    df['is_popular'] = (df['reviews'] > 0) & (df['rating'] >= 4.5)

    # Drop rows where price is completely missing (useless data)
    df.dropna(subset=['price'], inplace=True)
    
    # Fill missing names
    df['name'] = df['name'].fillna("Unknown Product")

    print("✅ Data cleaning & Feature Engineering complete.")
    print(df.info())
    return df

if __name__ == '__main__':
    test_path = Path(__file__).parent.parent / "data" / "banggood_raw_data.csv"
    df = get_clean_data(test_path)
    print("\n--- Head ---")
    print(df[['name', 'price', 'reviews', 'price_category', 'is_popular']].head())