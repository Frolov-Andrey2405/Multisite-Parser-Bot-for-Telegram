import requests
import json
from lxml import html
import os

# Create a folder to store the images
image_folder = 'images'
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# Open the file with the links in JSON format
with open('json/links.json', 'r') as f:
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
        # Find all <img> elements in the class "entry-content"
        images = soup.xpath('//div[@class="entry-content"]//img')
        for image in images:
            # Get the image URL
            image_url = image.get('src')
            # Download the image
            image_data = requests.get(image_url).content
            # Get the image file name
            image_name = image_url.split('/')[-1]
            # Save the image to the image folder
            with open(os.path.join(image_folder, image_name), 'wb') as h:
                h.write(image_data)
