import asyncio
from asyncio import Semaphore
from json import loads
from bs4 import BeautifulSoup
import httpx
import json

FORBIDDEN_SYMBOLS = ('\\', '/', ':', '*', '?', '"', '<', '>', '|', ' ')


async def read_links() -> list:
    '''Reading links from a json format file'''
    with open('blendermarket/json/links.json', 'r') as f:
        links = f.readlines()
    return links


def replace_forbidden_symbols_for_file_name(string: str, symbol: str) -> str:
    '''Replaces forbidden characters in the file with symbol'''
    new_str = ''
    for symbol in string:
        new_str += '_' if symbol in FORBIDDEN_SYMBOLS else symbol
    return new_str


async def load_image(client: httpx.AsyncClient, link: str, semaphore: Semaphore, file) -> None:
    '''Downloading images from a link'''

    await semaphore.acquire()
    # Load the link as a JSON object
    link_json = loads(link)
    # Get the link value from the JSON object
    url = link_json['link']
    # Send a GET request to the link
    response = await client.get(url)
    # Parse the HTML contents
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the section with the images
    image_section = soup.find_all('img', class_='img-fluid')

    name_of_game = replace_forbidden_symbols_for_file_name(
        soup.find('title').get_text(strip=True), '_')

    url_on_image = image_section[0]['src'] if len(image_section) > 0 else None

    file.write(json.dumps({
        'off_link': url,
        'name_of_tools': name_of_game,
        'url_on_image': url_on_image,
    }) + '\n')

    semaphore.release()


async def main() -> None:
    '''Creating Tasks and Downloading Images in Asynchronous Mode'''
    semaphore = Semaphore(20)
    client = httpx.AsyncClient()
    # Iterate through the links
    with open('blendermarket\\json\\blend.json', 'w') as file:
        tasks = [asyncio.create_task(load_image(client, link, semaphore, file)) for link in await read_links()]
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
