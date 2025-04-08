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
	data = []
	loteries_parser = []
  # Cargar JSON en un Archivo
	with open('lottery.json', 'r', encoding='utf-8') as file:
		json_data = file.read()
		data = json.loads(json_data)

	if search_lotery:
		data = [item for item in data if  search_lotery.lower() in item["game"].lower()]
	
	if len(data) == 0:
		return data

	# Load HTML 
	games_blocks = load_html(search_date)

	for game_block in games_blocks:
		block = {}
		title = game_block.find("a", "game-title").getText().strip().lower()
		 
		filtered_data = [item for item in data if item["game"].lower() == title]
		if len(filtered_data) == 0:
			continue  

		pather_score = game_block.find_all("span", "score")
		pather_date = game_block.find("span", "session-date").getText().strip()
		score = "-".join(span.text.strip() for span in pather_score)

		block['id'] = filtered_data[0]["id"]
		block['game'] = filtered_data[0]["game"]
		block['date'] = pather_date
		block['number'] = score		
		block['lottery'] = filtered_data[0]["lottery"]
		loteries_parser.append(block)

	return sorted(loteries_parser, key=lambda k:k["id"])

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