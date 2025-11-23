import time
import csv
import sys
import random
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def get_driver():
    """Sets up undetected_chromedriver"""
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-popup-blocking")
    print("   ...Launching Stealth Browser...")
    driver = uc.Chrome(options=options)
    return driver

def discover_categories(driver, limit=10):
   
    print("\n🔍 DISCOVERING CATEGORIES ...")
    
    start_url = "https://www.banggood.com/all-wholesale-products.html?from=nav"
    
    try:
        driver.get(start_url)
        time.sleep(5)
        
        soup = BeautifulSoup(driver.page_source, 'lxml')
        all_links = soup.find_all('a', href=True)
        
        valid_categories = []

        for link in all_links:
            href = link['href']
            
            if "Wholesale-" in href and ".html" in href:
                
                if not href.startswith("http"):
                    href = "https://www.banggood.com" + href.strip()
                
                if ("-c-" in href or "-ca-" in href) and href not in valid_categories:
                    valid_categories.append(href)
        
        print(f"   Found {len(valid_categories)} total categories on the sitemap.")

        if not valid_categories:
            print("   ❌ Critical: No categories found. Check URL or Internet.")
            return []

        # Completely Random Selection
        if len(valid_categories) > limit:
            selected = random.sample(valid_categories, limit)
        else:
            selected = valid_categories
            
        return selected

    except Exception as e:
        print(f"   ❌ Discovery failed: {e}")
        return []

def scrape_and_save(num_pages=2, output_csv='data/banggood_raw_data3.csv'):
    print("--- 1. STARTING DYNAMIC SCRAPER ---")
    
    driver = get_driver()
    all_products = []

    try:
        # 1. Discover (Pure Random from Sitemap)
        categories_to_scrape = discover_categories(driver, limit=10)
        
        if not categories_to_scrape:
             print("❌ Exiting: No categories found.")
             return

        print(f"   Selected {len(categories_to_scrape)} random targets.")

        # 2. Scrape Loop
        for category_url in categories_to_scrape:
            try:
                # Extract name dynamically from URL
                if '-ca-' in category_url:
                    raw_name = category_url.split('Wholesale-')[1].split('-ca-')[0]
                elif '-c-' in category_url:
                    raw_name = category_url.split('Wholesale-')[1].split('-c-')[0]
                else:
                    raw_name = "Unknown"
                category_name = raw_name.replace('-', ' ')
            except:
                category_name = "Category"
            
            print(f"\n📂 Scraping: {category_name}")
            
            for page in range(1, num_pages + 1):
                separator = "&" if "?" in category_url else "?"
                target_url = f"{category_url}{separator}page={page}"
                
                print(f"   📄 Page {page}...", end="", flush=True)
                
                try:
                    driver.get(target_url)
                    time.sleep(random.uniform(3, 6))
                    
                    # Scroll to trigger lazy loading
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                    time.sleep(1)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)

                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    product_cards = soup.find_all('div', class_='p-wrap')
                    
                    if not product_cards:
                        print(" ⚠️ No items.")
                        continue

                    count_new = 0
                    for card in product_cards:
                        item = {}
                        try:
                            title_tag = card.find('a', class_='title')
                            item['name'] = title_tag.text.strip() if title_tag else None
                            
                            price_tag = card.find('span', class_='price')
                            item['price'] = price_tag.text.strip() if price_tag else None
                            
                            item['url'] = title_tag['href'] if title_tag else None
                            
                            try: item['rating'] = card.find('span', class_='review-text').text.strip()
                            except: item['rating'] = "0"
                            
                            try: item['reviews'] = card.find('a', class_='review').text.strip()
                            except: item['reviews'] = "0 reviews"

                            item['category'] = category_name
                            
                            if item['name'] and item['price']:
                                all_products.append(item)
                                count_new += 1
                        except:
                            continue 
                    print(f" -> Found {count_new} items")
                    
                except Exception as e:
                    print(f" -> Error: {e}")

    except Exception as e:
        print(f"❌ Critical Error: {e}")
    finally:
        print("🔌 Closing browser...")
        driver.quit()

    # Save Results
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