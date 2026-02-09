from time import sleep
import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin

os.makedirs('outputs', exist_ok = True)

base_url = "https://books.toscrape.com/"
current_url = base_url
all_books = []

while current_url:
    response = requests.get(current_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    book_elements = soup.find_all('article', class_ = 'product_pod')

    for book in book_elements:
        name = book.h3.a['title']
        price = book.find("p", class_ = "price_color").get_text()
        stock_text = book.find("p", class_ = "instock availability").get_text()

        is_in_stock = "In stock" in stock_text

        all_books.append({
            "book_name": name,
            "price" : price,
            "in_stock" : is_in_stock
        })
    print(current_url)
    next_btn = soup.find('li', class_ = 'next')
    sleep(0.20)
    if next_btn:
        next_page_path = next_btn.find('a')['href']
        current_url = urljoin(current_url, next_page_path)
    else:
        current_url = None

with open('outputs/books_bs4.json', 'w', encoding='utf-8') as f:
    json.dump(all_books, f, ensure_ascii=False, indent=4)

print(f"Scraping complete! Total books found: {len(all_books)}")