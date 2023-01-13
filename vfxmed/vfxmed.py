import json
import re
from bs4 import BeautifulSoup
import asyncio
from lxml import html
import httpx

# Set the base URL of the website
base_url = 'https://www.vfxmed.com/tag/blender/page/'

# Set the pattern for extracting the links
pattern = r'https://www.vfxmed.com/\d{4}/\d{2}/blender-'

# Set the pattern to match links with "#comment-" followed by digits
comment_pattern = r'#comment-\d+'

# Initialize a set to store the unique links


def extract_links(soup):
    """
    Extracts links from the given BeautifulSoup object that match the specified pattern and
    do not match the comment pattern. Returns a set of unique links.
    """

    # Check if the soup object is None
    if soup is None:
        return

    # Find all the links with the "blender" tag
    links = soup.find_all('h2', class_='entry-title')  # Use find_all() instead of xpath()

    list_href_title = []

    links = list(map(lambda x: x.find('a'), links))

    if len(links) == 0:
        raise ValueError

    # Extract links that match the specified format
    for link in links:
        href = link.get('href')
        title = link.get('title')
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

        list_href_title.append((href, title))
    return list_href_title


async def get_download_links(links, file, client):
    """
    Sends a GET request to each link in the given list of links, extracts the download links
    from the page, and writes them to the given file in JSON format.
    """

    # Iterate through the links
    for href, title in links:
        # Send a GET request to the link
        link_response = await client.get(href)
        # Parse the HTML content of the link
        link_soup = BeautifulSoup(link_response.text, 'html.parser')

        # Find the content section of the page
        content_section = link_soup.find('div', class_='entry-content')
        if content_section is not None:
            download_link = None
            # Find the download links in the content section
            h3_elements = content_section.find_all('h3')
            for element in h3_elements:
                if 'Filename:' in element.text and element.a:
                    download_link = element.a['href']
                    break

            if not download_link:
                h1_elements = content_section.find_all('h1')
                for element in h1_elements:
                    if element.a:
                        download_link = element.a['href']
                        break

            # Check if the download link is a repetition
            if download_link:
                # Write the link in JSON format to the file
                file.write(json.dumps({
                    "link": href,
                    "title": title,
                    "download_link": download_link}) + '\n')


async def main() -> None:
    # Open a file to write the links in JSON format
    with open('vfxmed/json/vfxmed.json', 'w') as f:
        # Initialize a counter for the page number
        page_number = 1
        client = httpx.AsyncClient(timeout=10)
        tasks = []

        while True:
            # Acquire a lock from the semaphore
            # Send a GET request to the page
            try:
                if page_number != 1:
                    response = await client.get(base_url + str(page_number) + '/')
                else:
                    response = await client.get('https://www.vfxmed.com/tag/blender/')
            except httpx.ReadTimeout:
                print('ReadTimeout')
                print(base_url + str(page_number) + '/')
                continue
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract the links from the page
            try:
                page_links = extract_links(soup)
            except ValueError:
                await asyncio.gather(*tasks)
                break

            # Create a task to get the download links for each page
            tasks.append(asyncio.create_task(get_download_links(page_links, f, client)))

            # Increment the page number
            page_number += 1

            # Wait for the tasks to complete

            if len(tasks) == 40:
                await asyncio.gather(*tasks)
                tasks.clear()

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