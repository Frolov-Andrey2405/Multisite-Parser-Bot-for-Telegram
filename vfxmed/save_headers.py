import requests
import json
from lxml import html
import re

# Open the file with the links in JSON format
with open('json/links.json', 'r') as f:
    # Open a file to write the headers in JSON format
    with open('json/headers.json', 'w') as g:
        # Read the lines from the file
        for line in f:
            # Load the line as a JSON object
            link = json.loads(line)
            # Get the link from the object
            href = link['link']
            # Send a GET request to the page
            response = requests.get(href)
            # Parse the HTML contents
            soup = html.fromstring(response.text)
            # Find the <h1> element
            header = soup.xpath('//h1')[0]
            # Get the text from the element
            text = header.text
            # Replace the phrases with an empty string
            text = re.sub(
                r'Blender 3D:\s*|Blender \d+(\.\d+)?\+?|Blender \d+\.?\d*:|^Blender\b', '', text)

            text = re.sub(r'(Crack|CRACK)', '', text)

            text = re.sub(r'Updated|Update|UPDATED', '', text)

            text = text.replace('Complete', '')
            text = text.replace('Download', '')

            # remove the letter "v" if it occurs alone
            text = re.sub(r'v\b', '', text)

            # Removes all leading (at the beginning) and leading (at the end) spaces from the text.
            text = re.sub(r'^\s+|\s+$', '', text)

            # Replace the \u2013 with -
            text = text.replace('\u2013', '-')

            # Replace the \u2019 with '
            text = text.replace('\u2019', "'")

            # Write the header in JSON format to the file
            g.write(json.dumps({"header": text}) + '\n')
