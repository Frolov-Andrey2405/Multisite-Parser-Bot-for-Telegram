import json
import re
from bs4 import BeautifulSoup
import asyncio
import requests
from lxml import html

# Set the base URL of the website
base_url = 'https://www.vfxmed.com/tag/blender/page/'

# Set the pattern for extracting the links
pattern = r'https://www.vfxmed.com/\d{4}/\d{2}/blender-'

# Set the pattern to match links with "#comment-" followed by digits
comment_pattern = r'#comment-\d+'

# Initialize a flag to indicate when to stop paginating
stop_paginating = False

# Initialize a set to store the unique links
unique_links = set()

def extract_links(soup, unique_links):
    """Extracts links from the given BeautifulSoup object that match the specified pattern and
    do not match the comment pattern. Returns a set of unique links.
    """
    # Find all the links with the "blender" tag
    links = soup.xpath('//a')

    # Extract links that match the specified format
    for link in links:
        href = link.get('href')
        title = link.get('title')
        if href and re.match(pattern, href) and \
            not href.endswith('#respond') and \
                not href.endswith('#comments') and \
            not re.search(comment_pattern, href) and \
            href not in unique_links:
            unique_links.add(href)

            # Remove "Permalink to" from the title
            title = re.sub(r'Permalink to ', '', title)

            # Remove other unwanted words from the title
            title = re.sub(
                r'Blender 3D:\s*|Blender \d+(\.\d+)?\+?|Blender \d+\.?\d*:|^Blender\b', '', title)
            title = re.sub(r'(Crack|CRACK)', '', title)
            title = re.sub(r'Updated|Update|UPDATED', '', title)
            title = title.replace('Complete', '')
            title = title.replace('Download', '')
            title = re.sub(r'v\b', '', title)
            title = re.sub(r'^\s+||s+$', '', title)
            title = title.replace('\u2013', '-')
            title = title.replace('\u2019', "'")

            yield (href, title)


async def get_download_links(links, file):
    """Sends a GET request to each link in the given list of links, extracts the download links
    from the page, and writes them to the given file in JSON format.
    """
    # Iterate through the links
    for href, title in links:
        # Send a GET request to the link
        link_response = requests.get(href)
        # Parse the HTML content of the link
        link_soup = BeautifulSoup(link_response.text, 'html.parser')

        # Find the content section of the page
        content_section = link_soup.find('div', class_='entry-content')
        if content_section is not None:
            # Find the download links in the content section
            download_links = content_section.find_all('h3')
            # Iterate through the download links
            for element in download_links:
                if 'Filename:' in element.text:
                    # Extract the download link
                    download_link = element.a['href']
                    # Write the link in JSON format to the file
                    file.write(json.dumps({
                        "link": href,
                        "title": title,
                        "download_link": download_link}) + '\n')


async def main():
    # Open a file to write the links in JSON format
    with open('vfxmed/json/links.json', 'w') as f:
        # Initialize a counter for the page number
        page_number = 1

        while not stop_paginating:
            # Send a GET request to the current page of the website
            response = requests.get(f'{base_url}{page_number}')
            # Parse the HTML content
            soup = html.fromstring(response.text)

            # Extract the links from the page
            links = extract_links(soup, unique_links)

            # Get the download links for the links
            await get_download_links(links, f)

            # Increment the page number
            page_number += 1

if __name__ == '__main__':
    asyncio.run(main())
