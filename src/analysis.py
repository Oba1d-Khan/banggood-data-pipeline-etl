import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def generate_all_plots(df):
    print("--- 3. STARTING DATA ANALYSIS ---")
    
    plot_dir = Path(__file__).parent.parent / "data" / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"   📊 Saving plots to: {plot_dir}")

    # --- Analysis 1: Price Distribution per Category (Box Plot)  ---
    # Shows the price range (min, max, median) for each category
    plt.figure(figsize=(12, 6))
    categories = df['category'].unique()
    data_to_plot = [df[df['category'] == cat]['price'] for cat in categories]
    
    plt.boxplot(data_to_plot, labels=categories)
    plt.title('Price Distribution by Category')
    plt.xlabel('Category')
    plt.ylabel('Price (USD)')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(plot_dir / '1_price_distribution.png')
    print("   ✅ Saved: 1_price_distribution.png")

    # --- Analysis 2: Rating vs. Price Correlation (Scatter Plot) ---
    plt.figure(figsize=(10, 6))
    plt.scatter(df['price'], df['rating'], alpha=0.6, color='purple')
    plt.title('Correlation: Price vs. Rating')
    plt.xlabel('Price (USD)')
    plt.ylabel('Rating (0-5)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(plot_dir / '2_rating_vs_price.png')
    print("   ✅ Saved: 2_rating_vs_price.png")

    # --- Analysis 3: Top 10 Most Reviewed Products (Bar Chart) ---
    top_reviewed = df.nlargest(10, 'reviews')
    plt.figure(figsize=(12, 6))
    plt.barh(top_reviewed['name'].str[:40] + '...', top_reviewed['reviews'], color='teal')
    plt.xlabel('Number of Reviews')
    plt.title('Top 10 Most Reviewed Products')
    plt.gca().invert_yaxis() 
    plt.tight_layout()
    plt.savefig(plot_dir / '3_top_reviews.png')
    print("   ✅ Saved: 3_top_reviews.png")

    # --- Analysis 4: Product Count per Category (Bar Chart) ---
    cat_counts = df['category'].value_counts()
    plt.figure(figsize=(10, 6))
    cat_counts.plot(kind='bar', color='salmon')
    plt.title('Inventory Count per Category')
    plt.xlabel('Category')
    plt.ylabel('Number of Products')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(plot_dir / '4_category_counts.png')
    print("   ✅ Saved: 4_category_counts.png")

    # --- Analysis 5: Price Tier Distribution (Pie Chart) ---
    if 'price_category' in df.columns:
        tier_counts = df['price_category'].value_counts()
        plt.figure(figsize=(8, 8))
        plt.pie(tier_counts, labels=tier_counts.index, autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99'])
        plt.title('Product Distribution by Price Tier')
        plt.savefig(plot_dir / '5_price_tiers.png')
        print("   ✅ Saved: 5_price_tiers.png")
    
    print("Analysis Complete!")

if __name__ == "__main__":
  
    from data_cleaning import get_clean_data
    test_csv = Path(__file__).parent.parent / "data" / "banggood_raw_data.csv"
    
    if test_csv.exists():
        df = get_clean_data(test_csv)
        generate_all_plots(df)
    else:
        print("No data found to test.")