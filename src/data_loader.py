import sys
from pathlib import Path  
import pandas as pd
import toml
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from data_cleaning import get_clean_data


sys.path.append(str(Path(__file__).parent))

def load_data_to_sql(df):
    print("\n--- 4. STARTING DATA LOAD TO SQL ---")
    
    SECRETS_PATH = Path(__file__).parent.parent / ".streamlit" / "secrets.toml"

    try:
        config = toml.load(SECRETS_PATH)
        db = config['database'] 
        
        DRIVER = db['driver']
        SERVER = db['server']
        DATABASE = db['database']
        USERNAME = db['username']
        PASSWORD = db['password']
        
    except FileNotFoundError:
        print(f"❌ Secrets file not found at: {SECRETS_PATH}")
        sys.exit()
    except KeyError as e:
        print(f"❌ Error in secrets file: Could not find key {e}")
        sys.exit()

    TABLE_NAME = 'banggood_products'

    print(f"   Connecting to: {SERVER}/{DATABASE} as {USERNAME}")

    try:
        connection_url = URL.create(
            "mssql+pyodbc",
            username=USERNAME,
            password=PASSWORD,
            host=SERVER,
            database=DATABASE,
            query={"driver": DRIVER}
        )
        engine = create_engine(connection_url)
        with engine.connect() as conn:
            pass
        print("   ✅ Connection engine created successfully.")
            
    except Exception as e:
        print(f"❌ Failed to create engine. Error: {e}")
        sys.exit()

    # --- 3. DUMP DATAFRAME TO SQL ---
    try:
        print(f"   Attempting to write {len(df)} rows to table '{TABLE_NAME}'...")
        
        df.to_sql(
            TABLE_NAME,
            con=engine,
            if_exists='replace',
            index=False
        )
        print(f"✅ Success! Data dumped to '{TABLE_NAME}' in '{DATABASE}'.")
        
    except Exception as e:
        print(f"❌ Failed to dump data. Error: {e}")
        sys.exit()

    # --- 4. VERIFY DATA ---
    try:
        with engine.connect() as connection:
            query = f"SELECT TOP 5 * FROM {TABLE_NAME};"
            df_from_db = pd.read_sql(query, con=connection)
            print("\n✅ Verification complete. Read 5 rows back from DB:")
            print(df_from_db[['name', 'price', 'category']])
    except Exception as e:
        print(f"❌ Failed to read data back. Error: {e}")

if __name__ == '__main__':
    print("--- Running data_loader.py directly for testing... ---")
    
    csv_path = Path(__file__).parent.parent / "data" / "banggood_raw_data.csv"
    
    if csv_path.exists():
        df = get_clean_data(csv_path) 
        load_data_to_sql(df)
    else:
        print(f"❌ Error: Could not find {csv_path}")