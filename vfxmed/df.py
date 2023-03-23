import json
import re
from bs4 import BeautifulSoup, Tag
import asyncio
import httpx
from httpx import Response, AsyncClient, ReadTimeout
from requests import Session, get
from datetime import datetime
from database.work_with_db import create_connect, data_insert_in_db

BASE_URL = 'https://www.vfxmed.com/tag/blender/page/'
PATTERN = r'https://www.vfxmed.com/\d{4}/\d{2}/blender-'
COMMENT_PATTERN = r'#comment-\d+'
DELETE_BEFORE_VERSION_PATTERNS_FROM_TITLE = [
                                            r'Blender 3D:\s*|Blender \d+(\.\d+)?\+?|Blender \d+\.?\d*:|^Blender\b', 
                                            r'(Crack|CRACK)', r'Updated|Update|UPDATED', r'Complete', r'Download',
                                            r'v\b', r'Permalink to ',
                                            ]
DELETE_AFTER_VERSION_PATTERNS_FROM_TITLE = [
                                            r'\b(19|20)\d{2}\b', r'\b\d+(st|nd|rd|th)\b',
                                            r'\b\d{1,2}\s+(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\w*\b',
                                            r'^\s+|\s+$',

]

def delete_patterns(word: str, patterns: list) -> str:
    for sub_word in patterns:
        word = re.sub(sub_word, '', word)
    return word


def search_version_in_title(title: str) -> str:
    version = re.search(r'([vV]\d+.*|Vol.*$|\d+\.\d+)', title)

    if version:
        return version.group(1).strip()
    return ''


def title_and_version_handler(title: str) -> tuple[str]:
    title = delete_patterns(title, DELETE_BEFORE_VERSION_PATTERNS_FROM_TITLE)

    title = title.replace('\u2013', '-').replace('\u2019', "'")

    version = search_version_in_title(title)

    title = re.sub(version, '', title)

    title = delete_patterns(title, DELETE_AFTER_VERSION_PATTERNS_FROM_TITLE)

    title = re.sub(
            r'''
            \b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b''', '', title, flags=re.IGNORECASE
            )

    return title, version


def extract_information_from_link(link) -> tuple[str]:
    href = link.get('href')
    title = link.get('title')

    title, version = title_and_version_handler(title)

    return title, version, href


def extract_links(soup: BeautifulSoup) -> list[tuple[int]]:
    '''
    Extract all product's links on page
    '''
    if soup is None:
        return

    h2_elements = soup.find_all('h2', class_='entry-title')

    list_href_title_version = []

    links = list(map(lambda x: x.find('a'), h2_elements))

    if len(links) == 0:
        raise ValueError

    for link in links:
        title, version, href = extract_information_from_link(link)     

        list_href_title_version.append((href, title, version))
    return list_href_title_version


def get_download_link_from_h3_elements_or_none(elem: Tag) -> str|None:

    h3_elements = elem.find_all('h3')
    for element in h3_elements:
        if ('Filename:' in element.text) and (element.a):
            return element.a.get('href')
    return None


def get_download_link_from_h1_elements_or_none(elem: Tag) -> str|None:
    h1_elements = elem.find_all('h1')
    for element in h1_elements:

        if  element.a \
                and (element.a['href'].startswith("https://controlc.com/") \
                or element.a['href'].startswith("https://www.file-upload.com/")):
            
            return element.a['href']


async def get_download_links(links, client):
    """
    Sends a GET request to each link in the given list of links, extracts the download links
    from the page, and writes them to the given file in JSON format.
    """

    full_data_products = []

    for href, title, version in links:

        try:
            link_response = await client.get(href)
        except ReadTimeout:
            print(href)
            continue

        link_soup = BeautifulSoup(link_response.text, 'html.parser')

        content_section = link_soup.find('div', class_='entry-content')
        if content_section is not None:

            download_link = get_download_link_from_h3_elements_or_none(content_section)

            if not download_link:
                download_link = get_download_link_from_h1_elements_or_none(content_section)

            if download_link:
                full_data_products.append(
                    {"link": href,
                    "title": title,
                    "version": version,
                    "download_link": download_link}
                )

    return full_data_products
                    


async def request_on_1_or_other_page(page_number: int, client: AsyncClient) -> Response|None:
    try:
        if page_number != 1:
            response = await client.get(BASE_URL + str(page_number) + '/')
        else:
            response = await client.get('https://www.vfxmed.com/tag/blender/')
    except httpx.ReadTimeout:
        print('ReadTimeout')
        print(BASE_URL + str(page_number) + '/')
        return None
    
    return response


def save_load_first_product(path: str) -> None:
    response = get('https://www.vfxmed.com/tag/blender/')
    soup = BeautifulSoup(response.content, 'html.parser')
    first_product = soup.find('h2', class_='entry-title').find('a')

    with open(path, 'w') as f:
        f.write(json.dumps(
            {'link': first_product.get('href'), 'begin_update': str(datetime.now())}
        ) + '\n'
    )


def read_links_from_file(file) -> list:
    links = []

    for row in file:
        links.append(json.loads(row)['link'])
    
    return links


async def parse_pages(mode_all=True) -> None:

    if not mode_all:
        with open('vfxmed/json/vfx_last_product.json', 'r') as f:
            link = read_links_from_file(f)[0]

    save_load_first_product('vfxmed/json/vfx_last_product.json')

    with create_connect() as conn:

        page_number = 1
        client = httpx.AsyncClient(timeout=10)
        tasks = []

        while True:
            response = await request_on_1_or_other_page(page_number, client)
            
            if not response:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            try:
                page_links = extract_links(soup)

                if not mode_all:
                    if link in map(lambda x: x[2], page_links):
                        break
                
            except ValueError:
                print('ValueError', tasks)
                page_links = await asyncio.gather(*tasks)
                break

            tasks.append(asyncio.create_task(
                get_download_links(page_links, client)))

            page_number += 1

            if len(tasks) >= 40:
                for data in await asyncio.gather(*tasks):
                    data_insert_in_db(data, 'vfx', conn)
                tasks.clear()
