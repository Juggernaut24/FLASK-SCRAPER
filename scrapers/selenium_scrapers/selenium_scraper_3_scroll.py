import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

def get_brave_driver():
    options = Options()
    options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_infinite_scroll():

    driver = get_brave_driver()
    driver.get("https://quotes.toscrape.com/scroll")

    wait = WebDriverWait(driver, 5)

    css_selector = ".quote"

    while True:
        current_items = driver.find_elements(By.CSS_SELECTOR, css_selector)
        current_count = len(current_items)
        print(f"current loaded iteams: {current_count}")

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            wait.until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, css_selector)) > current_count
            )

        except TimeoutException:
            print("Reached the end of the page. No new items loaded.")
            break

    print("Starting data extraction...")
    all_quotes = driver.find_elements(By.CSS_SELECTOR, css_selector)

    data = []
    for q in all_quotes:
        text = q.find_element(By.CSS_SELECTOR, ".text").text
        author = q.find_element(By.CSS_SELECTOR, ".author").text
        tags = [t.text for t in q.find_elements(By.CSS_SELECTOR, ".tags")]

        data.append({
            "text": text,
            "author": author,
            "tags": tags
        })

    driver.quit()
    print(f"Successfully scraped {len(data)} items.")
    
    # -- Gemmer Til Fil --
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/quotes_selenium_3.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    scrape_infinite_scroll()