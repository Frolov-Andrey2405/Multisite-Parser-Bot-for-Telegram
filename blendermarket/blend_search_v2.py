import requests
from bs4 import BeautifulSoup
import Levenshtein
import json

FORBIDDEN_SYMBOLS = ('\\\\', '/', ':', '*', '?', '', '<', '>', '|', ' ')
BASE_URL = "https://blendermarket.com/products"

# Read vfxmed.json and extract the titles
with open('vfxmed/json/vfxmed.json', 'r') as f:
    titles = []
    for line in f:
        data = json.loads(line)
        titles.append(data['title'])

# Define the threshold for Levenshtein distance
threshold = 3

# Iterate through all pages on blendermarket.com
for page in range(1, 10):
    url = BASE_URL + f'?page={page}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all card-body divs and extract the title
    for div in soup.find_all('div', class_='card-body'):
        card_title = div.find('h5', class_='card-title').text.strip()

        # Calculate the Levenshtein distance between the titles
        for title in titles:
            distance = Levenshtein.distance(title, card_title)

            # If the distance is below the threshold, print the link
            if distance <= threshold:
                link = div.find('a', href=True)['href']
                link = f'https://blendermarket.com/{link}'
                print(link)
