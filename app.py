import os
import json
from datetime import datetime
from flask import Flask, render_template, request
from scrapers.example_quotes import scrape_quotes
from scrapers.mandag_books import scrape_books
from scrapers.tirsdag_books import scrape_books_advanced
from scrapers.country_scraper import country_scraper

app = Flask(__name__)

# Sørg for at output mappen findes
OUTPUT_FOLDER = 'outputs'
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    
    if request.method == 'POST':
        # 1. Hent input fra formen
        scraper_choice = request.form.get('scraper_choice')
        user_query = request.form.get('query')

        # 2. Kør den valgte scraper
        if scraper_choice == 'quotes':
            data = scrape_quotes(user_query)
        # Her ville du tilføje `elif scraper_choice == 'books': ...`
        elif scraper_choice == 'books':
            data = scrape_books(user_query)
        elif scraper_choice == 'books advanced':
            data = scrape_books_advanced(user_query)
        elif scraper_choice == 'country':
            data = country_scraper(user_query)
        else:
            data = {
                "source": "Ukendt", 
                "results": [], 
                "runtime_ms": 0, 
                "errors": ["Scraper ikke implementeret endnu"]
            }

        # 3. Gem resultatet som JSON fil (YYYYMMDD_HHMMSS_scrapername.json)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{scraper_choice}.json"
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)