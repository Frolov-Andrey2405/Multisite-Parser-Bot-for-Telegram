import json
import requests
from bs4 import BeautifulSoup
import os


def sanitize_file_name(file_name):
    '''Function to sanitize file names by replacing any disallowed characters with an underscore'''
    return file_name.translate(str.maketrans('', '', '<>:"/|?*'))


# Open the links.json file and read the links
with open('vfxmed/json/links.json', 'r') as f:
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

    # Find the section with the links
    content_section = soup.find('div', class_='entry-content')
    # Find the links in the section
    if content_section is not None:
        links = content_section.find_all('h3')
        # Iterate through the links
        for element in links:
            if 'Filename:' in element.text:
                download_link = element.a['href']

                # Save the link and file name to the download_link.json file
                with open('vfxmed/json/download_link.json', 'a') as f:
                    f.write(json.dumps(
                        {'download_link': download_link}))
                    f.write('\n')
