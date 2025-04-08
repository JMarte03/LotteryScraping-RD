import datetime
from flask import Flask,jsonify, Response, request
from flask_cors import CORS, cross_origin
import re
import urllib.request
import requests
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
import os
import json

""" def load_html(search_date=None):

	url1 = "https://www.conectate.com.do/loterias/"

	# Agregar el parámetro date a la URL si existe
	if search_date:
		url1 += f"?date={search_date}"
        
	# Crea una lista para almacenar los elementos de ambos soups
	games_blocks = []

	try:
		html1 = urllib.request.urlopen(url1).read()
                
		soup1 = BeautifulSoup(html1, "html.parser")
                
		# Encuentra los elementos deseados del soup y agrégalos a la lista
		blocks1 = soup1.find_all("div", class_="game-block")
		games_blocks.extend(blocks1)
	except:
		return []

	return games_blocks
 """
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


def load_html_name(search_name,search_date=None):
	url1 = f"https://loteriasdominicanas.com/{search_name}"

	# Agregar el parámetro date a la URL si existe
	if search_date:
		url1 += f"?date={search_date}"

	
	# Crea una lista para almacenar los elementos de ambos soups
	games_blocks = []

	try:
		html1 = urllib.request.urlopen(url1).read()      
		soup1 = BeautifulSoup(html1, "html.parser")
                
		# Encuentra los elementos deseados del soup y agrégalos a la lista
		blocks1 = soup1.find_all("div", class_="game-block")
		games_blocks.extend(blocks1)
	except:
		return []

	return games_blocks

""" def scraping(search_date=None, search_lotery=None):
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
		pather_date = game_block.find("div", "session-date").getText().strip()
		score = "-".join(span.text.strip() for span in pather_score)

		block['id'] = filtered_data[0]["id"]
		block['game'] = filtered_data[0]["game"]
		block['date'] = pather_date
		block['number'] = score
		loteries_parser.append(block)

	return sorted(loteries_parser, key=lambda k:k["id"])
 """

def scraping(search_date=None, search_lotery=None):
    data = []
    loteries_parser = []

    # Load JSON
    with open('lottery.json', 'r', encoding='utf-8') as file:
        json_data = file.read()
        data = json.loads(json_data)

    if search_lotery:
        data = [item for item in data if search_lotery.lower() in item["game"].lower()]
    
    if len(data) == 0:
        return data

    # Load HTML
    games_blocks = load_html(search_date)

    # Create a mapping of company-block number to company name
    company_map = {}
    for block in games_blocks:
        classes = block.get("class", [])
        for cls in classes:
            if cls.startswith("company-block-"):
                company_number = cls.split("-")[-1]
                company_map[company_number] = None  # we'll map name later if needed

    for game_block in games_blocks:
        block = {}

        # Title of game
        title_elem = game_block.find("a", class_="game-title")
        if not title_elem:
            continue
        title = title_elem.getText().strip()

        # Find the company-block-NN class
        classes = game_block.get("class", [])
        company_class = next((cls for cls in classes if cls.startswith("company-block-")), None)
        if not company_class:
            continue

        company_number = company_class.split("-")[-1]

        # Get all JSON games with this company
        games_for_company = [
            item for item in data 
            if item["game"].lower() == title.lower()
        ]

        if not games_for_company:
            continue
        
        game_data = games_for_company[0]

        # Scores and date
        pather_score = game_block.find_all("span", class_="score")
        pather_date = game_block.find("div", class_="session-date")
        if not pather_date:
            continue

        score = "-".join(span.text.strip() for span in pather_score)
        date_text = pather_date.getText().strip()

        block['id'] = game_data["id"]
        block['game'] = game_data["game"]
        block['date'] = date_text
        block['number'] = score

        loteries_parser.append(block)

    return sorted(loteries_parser, key=lambda k: k["id"])

""" def scrapingByName(search_name,search_date=None, search_lotery=None):
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
	games_blocks = load_html_name(search_name,search_date)

	for game_block in games_blocks:
		block = {}
		title = game_block.find("a", "game-title").getText().strip().lower()

		filtered_data = [item for item in data if item["game"].lower() == title]
		if len(filtered_data) == 0:
			continue  

		pather_score = game_block.find_all("span", "score")
		pather_date = game_block.find("div", "session-date").getText().strip()
		score = "-".join(span.text.strip() for span in pather_score)

		block['id'] = filtered_data[0]["id"]
		block['game'] = filtered_data[0]["game"]
		block['date'] = pather_date
		block['number'] = score
		loteries_parser.append(block)

	return sorted(loteries_parser, key=lambda k:k["id"])
 """

def scrapingByName(search_name, search_date=None, search_lotery=None):
    data = []
    loteries_parser = []

    # Load JSON
    with open('lottery.json', 'r', encoding='utf-8') as file:
        json_data = file.read()
        data = json.loads(json_data)

    if search_lotery:
        data = [item for item in data if search_lotery.lower() in item["game"].lower()]

    if len(data) == 0:
        return data

    # Load HTML
    games_blocks = load_html_name(search_name, search_date)

    for game_block in games_blocks:
        block = {}

        # Extract title
        title_elem = game_block.find("a", class_="game-title")
        if not title_elem:
            continue
        title = title_elem.getText().strip()

        # Extract company-block-NN class
        classes = game_block.get("class", [])
        company_class = next((cls for cls in classes if cls.startswith("company-block-")), None)
        if not company_class:
            continue

        # Extract company-block number
        company_number = company_class.split("-")[-1]

        # Find all JSON entries that match the game title
        matching_entries = [
            item for item in data if item["game"].lower() == title.lower()
        ]
        if not matching_entries:
            continue

        game_data = matching_entries[0]

        # Extract scores and date
        pather_score = game_block.find_all("span", class_="score")
        pather_date = game_block.find("div", class_="session-date")
        if not pather_date:
            continue

        score = "-".join(span.text.strip() for span in pather_score)
        date_text = pather_date.getText().strip()

        block['id'] = game_data["id"]
        block['game'] = game_data["game"]
        block['date'] = date_text
        block['number'] = score

        loteries_parser.append(block)

    return sorted(loteries_parser, key=lambda k: k["id"])


def JsonUFT8(data=None):
	json_string = json.dumps(data,ensure_ascii = False)
	return Response(json_string, content_type='application/json; charset=utf-8')

app = Flask(__name__)
CORS(app)
port = int(os.environ.get("PORT", 5000))

@app.route("/", methods=['GET'])
def search_lotery():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	data = scraping(search_date)
	return JsonUFT8(data)

app.run(host='0.0.0.0', port=port)
	 
""" @app.route("/search", methods=['GET'])
def search_lotery_by_name():
	search_query = request.args.get('game', None)
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))

	if not search_query:
		return jsonify({"error": "Missing 'game' parameter"}), 400
	
	data =  scraping(search_date, search_query) 
	return JsonUFT8(data)

@app.route("/loteria-gana-mas", methods=['GET'])
def search_lotery1():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))

	data = scrapingByName("loteria-nacional/gana-mas",search_date,"Gana Más")
	return JsonUFT8(data)

@app.route("/loteria-primera", methods=['GET'])
def search_lotery2():
	search_query = request.args.get('game', "primera")
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("la-primera",search_date, search_query) 
	return JsonUFT8(data)

@app.route("/loteria-primera-12am", methods=['GET'])
def search_lotery3():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("la-primera/quiniela-medio-dia",search_date, "la primera Día")
	return JsonUFT8(data)

@app.route("/loteria-primera-noche", methods=['GET'])
def search_lotery4():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("la-primera/quiniela-noche",search_date, "Primera Noche")
	return JsonUFT8(data)

@app.route("/loteria-la-suerte", methods=['GET'])
def search_lotery6():
	search_query = request.args.get('name', "La Suerte")
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("la-suerte-dominicana",search_date, search_query)
	return JsonUFT8(data)

@app.route("/loteria-la-suerte-12am", methods=['GET'])
def search_lotery7():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("la-suerte-dominicana/quiniela",search_date, "La Suerte 12:30")
	return JsonUFT8(data)

@app.route("/loteria-la-suerte-tarde", methods=['GET'])
def search_lotery8():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("la-suerte-dominicana/quiniela-tarde",search_date, "La Suerte 18:00")
	return JsonUFT8(data)

@app.route("/loteria-lotedom", methods=['GET'])
def search_lotery9():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("lotedom",search_date, "Quiniela LoteDom")
	return JsonUFT8(data)

@app.route("/loteria-anguila", methods=['GET'])
def search_lotery10():
	search_query = request.args.get('name', "Anguila")
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("anguila",search_date, search_query)
	return JsonUFT8(data)

@app.route("/loteria-anguila-10am", methods=['GET'])
def search_loteryAng():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("anguila/anguila-manana",search_date, "Anguila Mañana")
	return JsonUFT8(data)

@app.route("/loteria-anguila-12am", methods=['GET'])
def search_loteryAng12():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("anguila/anguila-medio-dia",search_date, "Anguila Medio Día")
	return JsonUFT8(data)

@app.route("/loteria-anguila-6pm", methods=['GET'])
def search_loteryAng6pm():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("anguila/anguila-tarde",search_date, "Anguila Tarde")
	return JsonUFT8(data)

@app.route("/loteria-anguila-9pm", methods=['GET'])
def search_loteryAng9pm():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("anguila/anguila-noche",search_date, "Anguila Noche")
	return JsonUFT8(data)

@app.route("/loterias-nacionales", methods=['GET'])
def search_lotery11():
	search_query = request.args.get('name', None)
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("loteria-nacional",search_date, search_query)	
	return JsonUFT8(data)

@app.route("/loteria-nacional", methods=['GET'])
def search_lotery12():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("loteria-nacional/quiniela",search_date, "Lotería Nacional")
	return JsonUFT8(data)

@app.route("/loteria-leidsa", methods=['GET'])
def search_lotery13():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("leidsa", search_date, "Quiniela Leidsa")
	return JsonUFT8(data)

@app.route("/loteria-real", methods=['GET'])
def search_lotery14():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("loto-real", search_date, "Quiniela Real")
	return JsonUFT8(data)

@app.route("/loteria-loteka", methods=['GET'])
def search_lotery15():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("loteka", search_date, "Quiniela Loteka")
	return JsonUFT8(data)

@app.route("/loteria-americana", methods=['GET'])
def search_lotery16():
	search_query = request.args.get('name', None)
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("americanas",search_date, search_query)
	return JsonUFT8(data)

@app.route("/loteria-florida-tarde", methods=['GET'])
def search_lotery17():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("americanas/florida-tarde",search_date, "Florida Día")
	return JsonUFT8(data)

@app.route("/loteria-florida-noche", methods=['GET'])
def search_lotery18():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("americanas/florida-noche",search_date, "Florida Noche")
	return JsonUFT8(data)	

@app.route("/loteria-new-york-12am", methods=['GET'])
def search_lotery19():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("americanas/new-york-medio-dia",search_date, "New York Tarde")
	return JsonUFT8(data)

@app.route("/loteria-new-york-noche", methods=['GET']) 
def search_lotery20():
	search_date = request.args.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
	
	data = scrapingByName("americanas/new-york-noche",search_date, "New York Noche")
	return JsonUFT8(data)
 """
