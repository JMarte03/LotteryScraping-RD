import datetime
from flask import Flask, Response, request
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
import os
import json

def load_html(search_date=None):
    url1 = "https://www.conectate.com.do/loterias/"
    if search_date:
        url1 += f"?date={search_date}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    try:
        print(f"[DEBUG] Requesting URL: {url1}")
        response = requests.get(url1, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Debug: print part of the raw HTML to see what was fetched
        print("[DEBUG] Sample of HTML content fetched:")
        print(soup.prettify()[:1500])  # print only the first 1500 chars to avoid terminal overload

        blocks = soup.find_all("div", class_="game-block")
        print(f"[DEBUG] Found {len(blocks)} game-blocks")

        return blocks

    except Exception as e:
        print(f"[ERROR] Failed to load or parse HTML: {e}")
        return []

def scraping(search_date=None, search_lotery=None):
    # Load games (lottery.json)
    with open('lottery.json', 'r', encoding='utf-8') as f:
        games_data = json.load(f)

    # Load companies (companies.json)
    with open('companies.json', 'r', encoding='utf-8') as f:
        companies_data = json.load(f)
    
    # Create company_id -> name lookup
    company_lookup = {item["id"]: item["name"] for item in companies_data}

    # Optionally filter games by search term
    if search_lotery:
        games_data = [item for item in games_data if search_lotery.lower() in item["game"].lower()]

    if not games_data:
        return []

    game_blocks = load_html(search_date)
    loteries_parser = []

    for game_block in game_blocks:
        block = {}
        title = game_block.find("a", "game-title")
        if not title:
            continue
        title = title.getText().strip().lower()

        # Extract the company-block-XX class
        company_class = next((cls for cls in game_block.get("class", []) if cls.startswith("company-block-")), None)
        if not company_class:
            continue
        company_id = company_class.split("-")[-1]

        company_name = company_lookup.get(company_id)
        if not company_name:
            continue

        # Match game using name AND company_id
        matched_game = next(
            (item for item in games_data if item["game"].lower() == title and item.get("company_id") == company_id),
            None
        )
        if not matched_game:
            continue

        # Extract score and date
        scores = game_block.find_all("span", "score")
        score = "-".join(span.text.strip() for span in scores)

        date_span = game_block.find("span", "session-date")
        if not date_span:
            continue
        date_text = date_span.getText().strip()

        # Build response block
        block["id"] = matched_game["id"]
        block["game"] = matched_game["game"]
        block["date"] = date_text
        block["number"] = score
        block["lottery"] = company_name
        loteries_parser.append(block)

    return sorted(loteries_parser, key=lambda k: k["id"])

def JsonUFT8(data=None):
	json_string = json.dumps(data,ensure_ascii = False)
	return Response(json_string, content_type='application/json; charset=utf-8')

app = Flask(__name__)
CORS(app)
port = int(os.environ.get("PORT", 2121))

@app.route("/", methods=['GET'])
def search_lotery():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	data = scraping(search_date)
	return JsonUFT8(data)

app.run(host='0.0.0.0', port=port)