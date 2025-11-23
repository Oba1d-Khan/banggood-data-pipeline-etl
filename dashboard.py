import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from pathlib import Path
import plotly.express as px 

st.set_page_config(
    page_title="Banggood Analytics", 
    page_icon="🛍️",
    layout="wide"
)

st.title("Banggood Product Analytics Dashboard")

TABLE_NAME = 'banggood_products'
CSV_PATH = Path("data") / "banggood_clean_data.csv"

@st.cache_resource
def get_database_connection():
    try:
        db = st.secrets["database"]
        connection_url = URL.create(
            "mssql+pyodbc",
            username=db["username"],
            password=db["password"],
            host=db["server"],
            database=db["database"],
            query={"driver": db["driver"]}
        )
        return create_engine(connection_url).connect()
    except:
        return None

@st.cache_data
def load_data():
    #  Try SQL
    conn = get_database_connection()
    if conn:
        try:
            df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
            st.toast("Live SQL Data Loaded", icon="🗄️")
            return df
        except:
            pass
    
    if CSV_PATH.exists():
        st.toast("SQL Offline. Using CSV Backup.", icon="⚠️")
        return pd.read_csv(CSV_PATH)
    
    return pd.DataFrame()

df = load_data()

if not df.empty:
    
    st.sidebar.header("🔍 Filter Data")
    categories = ["All"] + sorted(df['category'].unique().tolist())
    cat_filter = st.sidebar.selectbox("Category", categories)
    
    # Apply Filter
    if cat_filter != "All":
        df_filtered = df[df['category'] == cat_filter]
    else:
        df_filtered = df

    # --- KPI ROW ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total Stock", f"{len(df_filtered)}")
    col2.metric("💲 Avg Price", f"${df_filtered['price'].mean():.2f}")
    col3.metric("⭐ Avg Rating", f"{df_filtered['rating'].mean():.1f}")
    col4.metric("💬 Total Reviews", f"{df_filtered['reviews'].sum():,}")
    
    st.divider()

    # --- ROW 1: STOCK & PRICE DISTRIBUTION ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("🔰 Stock Availability (Count per Category)")
        # Analysis 5: Stock availability analysis
        stock_counts = df_filtered['category'].value_counts().reset_index()
        stock_counts.columns = ['Category', 'Count']
        fig_stock = px.pie(stock_counts, values='Count', names='Category', hole=0.4)
        st.plotly_chart(fig_stock, use_container_width=True)

    with c2:
        st.subheader("🔰 Price Distribution per Category")
        # Analysis 1: Price distribution per category
        fig_box = px.box(df_filtered, x="category", y="price", color="category")
        st.plotly_chart(fig_box, use_container_width=True)

    # --- ROW 2: CORRELATION & VIRAL PRODUCTS ---
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("🔰 Rating vs. Price Correlation")
        # Analysis 2: Rating vs Price correlation
        fig_scatter = px.scatter(
            df_filtered, x="price", y="rating", 
            size="reviews", color="category", 
            hover_name="name", log_x=True
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with c4:
        st.subheader("🔰 Top 10 Reviewed Products")
        # Analysis 3: Top reviewed products
        top_items = df_filtered.nlargest(10, 'reviews')
        fig_bar = px.bar(
            top_items, y="name", x="reviews", 
            orientation='h', color="price",
            hover_data=["category", "price"]
        )
        fig_bar.update_layout(yaxis={'visible': False, 'showticklabels': False}) 
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- ROW 3: VALUE ANALYSIS ---
    st.subheader("🔰 Best Value Metric per Category")
    # Analysis 4: Best value metric (Rating / Price)
    
    # 1. Group by category
    cat_stats = df.groupby('category')[['rating', 'price']].mean().reset_index()
    # 2. Create Value Metric
    cat_stats['Value Score'] = (cat_stats['rating'] / cat_stats['price']) * 10
    
    fig_value = px.scatter(
        cat_stats, x="price", y="rating", 
        size="Value Score", color="category", 
        text="category", 
        title="Category Sweet Spot: High Rating + Low Price = Best Value",
        labels={"price": "Average Price ($)", "rating": "Average Rating (0-5)"}
    )
    fig_value.update_traces(textposition='top center')
    st.plotly_chart(fig_value, use_container_width=True)

    # --- RAW DATA ---
    with st.expander("📂 View Detailed Data"):
        st.dataframe(df_filtered)

else:
    st.error("No data found. Please run the pipeline first!")

