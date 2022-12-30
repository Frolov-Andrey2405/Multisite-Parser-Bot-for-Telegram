import requests
import json
from lxml import html
import re

# Set the base URL of the website
base_url = 'https://www.vfxmed.com/tag/blender/page/'

# Set the pattern for extracting the links
pattern = r'https://www.vfxmed.com/\d{4}/\d{2}/blender-'

# Initialize a counter for the page number
page_number = 1

# Initialize a flag to indicate when to stop paginating
stop_paginating = False

# Initialize a set to store the unique links
unique_links = set()

# Open a file to write the links in JSON format
with open('vfxmed/json/links.json', 'w') as f:
    while not stop_paginating:
        # Send a GET request to the current page of the website
        response = requests.get(f'{base_url}{page_number}')
        # Parse the HTML content
        soup = html.fromstring(response.text)

        # Find all the links with the "blender" tag
        links = soup.xpath('//a')

        # Extract the links matching the specified format
        for link in links:
            href = link.get('href')
            if href and re.match(pattern, href) and not href.endswith('#respond') and not href.endswith('#comments') and href not in unique_links:
                unique_links.add(href)
                # Write the link in JSON format to the file
                f.write(json.dumps({"link": href}) + '\n')

        # Increment the page number
        page_number += 1
