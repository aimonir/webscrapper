import requests
import json
import random
import csv
import time
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin  # For handling relative URLs

# List of different User-Agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/537.36"
]

# Load target URLs from config.json
def load_config():
    with open("config.json", "r") as file:
        return json.load(file)

# Function to fetch webpage with retries
def fetch_page(url, retries=3):
    for attempt in range(retries):
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.text
        elif response.status_code == 403:
            print(f"❌ Access Denied (403). Retrying {attempt+1}/{retries} in 5 seconds...")
            time.sleep(5)
        else:
            print(f"⚠️ Failed to retrieve data (Status: {response.status_code})")
            return None
    return None

# Function to scrape job listings
def scrape_jobs(url):
    html = fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    for job_card in soup.select("div.card-outline"):  # Modify based on actual site structure
        title = job_card.select_one("h2 a").text.strip() if job_card.select_one("h2 a") else "N/A"
        company = job_card.select_one(".company").text.strip() if job_card.select_one(".company") else "N/A"
        location = job_card.select_one(".location").text.strip() if job_card.select_one(".location") else "N/A"
        link = job_card.select_one("h2 a")["href"] if job_card.select_one("h2 a") else "N/A"
        
        jobs.append({"Category": "Job Listing", "Title": title, "Company": company, "Location": location, "URL": link})
    
    return jobs

# Function to scrape news headlines
def scrape_news(url):
    html = fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    news = []

    for article in soup.select("article h2"):  # Modify based on actual site structure
        title = article.text.strip()
        link = article.find("a")["href"] if article.find("a") else "N/A"
        
        # Convert relative URL to absolute
        full_link = urljoin(url, link) if link.startswith("/") else link

        news.append({"Category": "News", "Title": title, "URL": full_link})

    return news

# Function to scrape stock data
def scrape_stocks(url):
    html = fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    stocks = []

    for row in soup.select("table tr"):  # Modify based on actual site
        cols = row.find_all("td")
        if len(cols) < 2:
            continue

        stock_name = cols[0].text.strip() if cols[0] else "N/A"
        price = cols[1].text.strip() if cols[1] else "N/A"

        stocks.append({"Category": "Stock Market", "Stock Name": stock_name, "Price": price})
    
    return stocks

# Function to save scraped data to CSV
def save_to_csv(data, filename="data.csv"):
    if not data:
        print("⚠️ No data to save.")
        return

    # Extract all possible keys dynamically
    keys = set()
    for entry in data:
        keys.update(entry.keys())

    keys = sorted(keys)

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Data saved successfully to {filename}")

# Main execution function
def main():
    config = load_config()
    all_data = []

    for category, url in config.items():
        print(f"🔍 Scraping {category} data...")

        if category == "jobs":
            all_data.extend(scrape_jobs(url))
        elif category == "news":
            all_data.extend(scrape_news(url))
        elif category == "stocks":
            all_data.extend(scrape_stocks(url))

    if all_data:
        save_to_csv(all_data)
        print(f"🎉 Scraping completed! Data saved to `data.csv`")
    else:
        print("⚠️ No data scraped.")

if __name__ == "__main__":
    main()
