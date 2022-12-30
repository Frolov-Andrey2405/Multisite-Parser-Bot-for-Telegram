import json
import requests
from bs4 import BeautifulSoup
import os

# Function to sanitize file names by replacing any disallowed characters with an underscore
def sanitize_file_name(file_name):
    return file_name.translate(str.maketrans('', '', '<>:"/\|?*'))


# Open the links.json file and read the links
with open('blendermarket/json/links.json', 'r') as f:
    links = f.readlines()

# Iterate through the links
for link in links:
    # Load the link as a JSON object
    link_json = json.loads(link)
    # Get the link value from the JSON object
    url = link_json['link']
    # Send a GET request to the link
    response = requests.get(url)

    # Parse the HTML contents
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the section with the images
    image_section = soup.find_all(
        'img', class_='img-fluid')

    i = 0
    for img in image_section:
        i += 1
        if i == 1:
            img = requests.get(img['src'])
            out = open(f"blendermarket\images\{i}.jpg", "wb")
            out.write(img.content)
            out.close()
        else:
            break
