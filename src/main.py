from web_scraper import scrape_and_save
from data_cleaning import get_clean_data
from analysis import generate_all_plots
from data_loader import load_data_to_sql
from utils.paths import get_data_path

# constants
RAW_DATA_PATH = get_data_path('banggood_raw_data3.csv')
PAGES_TO_SCRAPE = 4

def run_pipeline():
    # 1. Extract
    # scrape_and_save(PAGES_TO_SCRAPE, RAW_DATA_PATH)
    
    # 2. Transform
    clean_df = get_clean_data(RAW_DATA_PATH)
    
    # 3. Analyze & Visualize
    generate_all_plots(clean_df)
    
    # 4. Load
    load_data_to_sql(clean_df)
    
    print("\n --- ENTIRE PIPELINE COMPLETED --- ")

if __name__ == "__main__":
    run_pipeline()