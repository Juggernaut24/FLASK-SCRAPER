import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin
import re

BASE_URL = "https://books.toscrape.com/"
OUTPUT_DIR = "outputs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "books_bs4.json")

CATEGORIES = [
    "https://books.toscrape.com/catalogue/category/books/historical_42/index.html",
    "https://books.toscrape.com/catalogue/category/books/historical_42/index.html",
    "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
    "https://books.toscrape.com/catalogue/category/books/classics_6/index.html",
    "https://books.toscrape.com/catalogue/category/books/historical-fiction_4/index.html",
]

rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

def get_soup(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'

        return BeautifulSoup(response.text, "html.parser")

    except requests.RequestException as e:
        print(f"Fejl ved hentning af {url}: {e}")
        return None

def scrape_book_details(book_url):
    soup = get_soup(book_url)
    if not soup:
        return {
            "description": None,
            "upc": None,
            "availability": None
        }
    
    description_elem = soup.select_one("#product_description ~ p")
    description = description_elem.text.strip() if description_elem else None

    upc = None
    availability = None

    table_rows = soup.select("table.table-striped tr")
    for row in table_rows:
        header_tag = row.find("th")
        value_tag = row.find("td")

        if header_tag and value_tag:
            header = header_tag.text
            value_text = value_tag.text

            if header == "UPC":
                upc = value_text
            elif header == "Availability":
                numbers = re.findall(r'\d+', value_text)

                if numbers:
                    availability = int(numbers[0])
                else:
                    availability = 0

    return {
        "description": description,
        "upc": upc,
        "availability": availability
    }

def scrape_category(category_path, seen_upcs):
    books_data = []
    current_url = category_path

    while current_url:
        print(f"Scraping listing page: {current_url}")
        soup = get_soup(current_url)
        if not soup:
            break

        articles = soup.select("article.product_pod")

        for article in articles:
            title = article.h3.a["title"]

            price = article.select_one(".price_color").text

            rating_class = article.select_one(".star-rating")["class"]
            rating_text = rating_class[1] if len(rating_class) > 1 else "Unknown"
            rating = rating_map.get(rating_text, 0)

            relative_link = article.h3.a["href"]
            detail_url = urljoin(current_url, relative_link)
            print(f" --> Navigating to details: {title[:30]}...")
            details = scrape_book_details(detail_url)

            current_upc = details["upc"]

            if current_upc in seen_upcs:
                print("Duplicate found...skipping")
                continue

            if current_upc:
                seen_upcs.add(current_upc)

            book_info = {
                "title": title,
                "price": price,
                "rating": rating,
                "detail_url": detail_url,
                "description": details["description"],
                "upc": details["upc"],
                "availability": details["availability"]
            }

            books_data.append(book_info)
            time.sleep(0.2)

        next_button = soup.select_one("li.next a")
        if next_button:
            next_page_relative = next_button["href"]

            current_url = urljoin(current_url, next_page_relative)
        else:
            current_url = None

    return books_data

def main():
    all_books = []

    seen_upcs = set()

    for category in CATEGORIES:
        print(f"--- Starting Category: {category} ---")
        books = scrape_category(category, seen_upcs)
        all_books.extend(books)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_books, f, indent=4, ensure_ascii=False)

    print(f"Done! {len(all_books)} books saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()