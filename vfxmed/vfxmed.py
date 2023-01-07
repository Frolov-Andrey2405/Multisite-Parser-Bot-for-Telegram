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
    """
    Extracts links from the given BeautifulSoup object that match the specified pattern and
    do not match the comment pattern. Returns a set of unique links.
    """

    # Check if the soup object is None
    if soup is None:
        return

    # Find all the links with the "blender" tag
    links = soup.find_all('a')  # Use find_all() instead of xpath()

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
    """
    Sends a GET request to each link in the given list of links, extracts the download links
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

                    # Check if the download link is a repetition
                    if check_repetition(download_link):
                        continue  # Skip writing the link to the file if it is a repetition

                    # Write the link in JSON format to the file
                    file.write(json.dumps({
                        "link": href,
                        "title": title,
                        "download_link": download_link}) + '\n')


def check_repetition(download_link):
    """
    Checks if the given download link is already present in the vfxmed.json file. 
    Returns True if it's a repeat, False otherwise.
    """

    # Open the vfxmed.json file in read mode
    with open('vfxmed/json/vfxmed.json', 'r') as file:
        # Iterate through the lines in the file
        for line in file:
            # Load the line as a JSON object
            data = json.loads(line)
            # Check if the download link is already present in the file
            if data['download_link'] == download_link:
                return True

    # If the download link is not found in the file, return False
    return False


async def main() -> None:
    '''Create a Semaphore to limit the number of concurrent tasks'''

    sem = asyncio.Semaphore(20)

    # Open a file to write the links in JSON format
    with open('vfxmed/json/vfxmed.json', 'w') as f:
        # Initialize a counter for the page number
        page_number = 1

        while not stop_paginating:
            # Acquire a lock from the semaphore
            async with sem:
                # Send a GET request to the page
                response = requests.get(base_url + str(page_number))

                # Parse the HTML content of the page
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract the links from the page
                page_links = extract_links(soup, unique_links)

                # Create a task to get the download links for each page
                task = asyncio.create_task(get_download_links(page_links, f))

                # Increment the page number
                page_number += 1

            # Wait for the tasks to complete
            await task

if __name__ == '__main__':
    asyncio.run(main())

'''
Documentation: 

This code is a web scraper designed to extract download links for 
software from the website www.vfxmed.com. 
It begins by setting the base URL for the website and two patterns 
for extracting links and for matching links that contain the string 
"#comment-". It also initializes a flag to indicate when pagination 
should stop and a set to store unique links.

The extract_links function takes in a BeautifulSoup object and a set of 
unique links, and extracts links from the soup object that match the 
specified pattern and do not match the comment_pattern. It then modifies 
the titles of the links to remove unwanted words, and yields a tuple of the 
link and the modified title.

The get_download_links function is an async function that takes in a list of 
links and a file object. It iterates through the links, sending a GET request 
to each one and parsing the HTML content with BeautifulSoup. It then finds the 
content section of the page and extracts the download links from it. 
It checks if each download link is a repetition using the check_repetition function, 
and if it is not, writes it to the file in JSON format.

The check_repetition function takes in a download link and checks if it 
is already present in the unique_links set. If it is not, it adds it to 
the set and returns False. If it is, it returns True.

The main loop of the code begins by making a GET request to the base URL and 
parsing the HTML content with BeautifulSoup. It then calls the extract_links 
function to extract the links from the content and the get_download_links 
function to write the download links to a file. It also checks the value of 
the stop_paginating flag and the nav-previous element to determine when to 
stop paginating and end the loop.

'''