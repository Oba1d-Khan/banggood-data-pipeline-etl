import time
import csv
import sys
import random
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

CATEGORIES = [
    "https://www.banggood.com/Wholesale-Tops-ca-15002.html",
    "https://www.banggood.com/Wholesale-T-Shirts-ca-15003.html",
    "https://www.banggood.com/Wholesale-Shirts-ca-15006.html",
    "https://www.banggood.com/Wholesale-Hoodies-and-Sweatshirts-ca-15008.html",
    "https://www.banggood.com/Wholesale-Outwear-ca-15014.html",
    "https://www.banggood.com/Wholesale-Dresses-ca-16042.html",
    "https://www.banggood.com/Wholesale-Two-Piece-Set-ca-16057.html",
    "https://www.banggood.com/Wholesale-Womens-Accessories-ca-10018.html",
    "https://www.banggood.com/Wholesale-Shoes-and-Bags-ca-11001.html",
    "https://www.banggood.com/Wholesale-Jewelry-Watches-and-Accessories-ca-8001.html"
]

def get_driver():
    """Sets up undetected_chromedriver to bypass Banggood security"""
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-popup-blocking")
    
    print("   ...Launching Browser...")
    driver = uc.Chrome(options=options)
    return driver

def scrape_and_save(num_pages=2, output_csv='data/banggood_raw_data.csv'):
    print("--- 1. STARTING BANGGOOD SCRAPER ---")
    
    driver = get_driver()
    all_products = []

    try:
        for category_url in CATEGORIES:
            try:
                # Extract readable category name
                # e.g. Wholesale-Tops-ca-15002 -> Tops
                raw_name = category_url.split('.com/Wholesale-')[1].split('-ca-')[0]
                category_name = raw_name.replace('-', ' ')
            except:
                category_name = "Unknown Category"
            
            print(f"\n📂 Scraping: {category_name}")
            
            for page in range(1, num_pages + 1):
                # Handle pagination safely
                separator = "&" if "?" in category_url else "?"
                target_url = f"{category_url}{separator}page={page}"
                
                print(f"   📄 Page {page}...", end="", flush=True)
                
                try:
                    driver.get(target_url)
                    
                    # Randomized wait (Human behavior)
                    time.sleep(random.uniform(5, 8))
                    
                    # Scroll to trigger images
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
                    time.sleep(1)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 1.5);")
                    time.sleep(1)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)

                    # Parse
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    
                    # Selectors
                    product_cards = soup.find_all('div', class_='p-wrap')
                    
                    if not product_cards:
                        print(" ⚠️ No items found (Check browser).")
                        continue

                    count_new = 0
                    for card in product_cards:
                        item = {}
                        try:
                            # Title
                            title_tag = card.find('a', class_='title')
                            item['name'] = title_tag.text.strip() if title_tag else None
                            
                            # Price
                            price_tag = card.find('span', class_='price')
                            item['price'] = price_tag.text.strip() if price_tag else None
                            
                            # URL
                            item['url'] = title_tag['href'] if title_tag else None
                            
                            # Rating
                            rating_tag = card.find('span', class_='review-text')
                            item['rating'] = rating_tag.text.strip() if rating_tag else "0"
                                
                            # Reviews
                            review_tag = card.find('a', class_='review')
                            item['reviews'] = review_tag.text.strip() if review_tag else "0 reviews"

                            item['category'] = category_name
                            
                            if item['name'] and item['price']:
                                all_products.append(item)
                                count_new += 1
                            
                        except Exception:
                            continue 
                    print(f" -> Found {count_new} items")
                    
                except Exception as e:
                    print(f" -> Error loading page: {e}")

    except Exception as e:
        print(f"❌ Critical Error: {e}")
    finally:
        print("🔌 Closing browser...")
        driver.quit()

    if all_products:
        try:
            keys = ['name', 'price', 'rating', 'reviews', 'category', 'url']
            with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(all_products)
            print(f"\n✅ DONE! Saved {len(all_products)} products to {output_csv}")
        except Exception as e:
            print(f"Error saving CSV: {e}")
    else:
        print("⚠️ No data collected.")

if __name__ == "__main__":
    scrape_and_save(num_pages=1)