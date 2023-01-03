import requests
from bs4 import BeautifulSoup
import json
from time import time

# Set the base URL for the site
base_url = "https://blendermarket.com/products?sort_sales=desc"

# Set the initial page number to 1
page_number = 1

# Set a flag to track if there are more pages to search
more_pages = True

# Open the official_links.json file in write mode
with open('blendermarket/json/official_links.json', 'w') as f:
    time_start = time()
    while more_pages:
        # Send a GET request to the URL with the page number
        response = requests.get(f"{base_url}&page={page_number}")

        # Parse the HTML contents
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the blocks with the posts
        post_blocks = soup.find_all(
            'a', class_='text-nounderline text-nocolor')

        # Iterate through the post blocks
        for block in post_blocks:
            # Find the link to the product page
            link = block['href']

            # Write the link to the official_links.json file
            f.write(json.dumps(
                {"official_links": f"https://blendermarket.com/{link}"}) + '\n')

        # Check if there are more pages to search
        pagination = soup.find('ul', class_='pagination')
        if pagination:
            # If there are more pages, increment the page number
            page_number += 1
        else:
            # If there are no more pages, set the flag to False to stop searching
            more_pages = False
