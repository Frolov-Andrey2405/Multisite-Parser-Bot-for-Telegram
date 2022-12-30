import json
import requests
from bs4 import BeautifulSoup
import os

# Function to sanitize file names by replacing any disallowed characters with an underscore
def sanitize_file_name(file_name):
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
                file_name = element.a.text
                # Use the sanitize_file_name function to clean up the file name
                file_name = sanitize_file_name(file_name)
                # Save the link and file name to the downloads.json file
                with open('vfxmed/json/downloads.json', 'a') as f:
                    f.write(json.dumps(
                        {'link': download_link, 'file_name': file_name}))
                    f.write('\n')
