import asyncio
from asyncio import Semaphore
from json import loads
from bs4 import BeautifulSoup
from time import time
import httpx

FORBIDDEN_SYMBOLS = ('\\', '/', ':', '*', '?', '"', '<', '>', '|', ' ')

async def read_links() -> list:
    '''Чтение ссылок из файла в формате json'''
    with open('blendermarket/json/links.json', 'r') as f:
        links = f.readlines()
    return links

def replace_forbidden_symbols_for_file_name(string: str, symbol: str) -> str:
    '''Заменяет запрещённые символы в файле на symbol'''
    new_str = ''
    for symbol in string:
        new_str += '_' if symbol in FORBIDDEN_SYMBOLS else symbol
    return new_str

async def load_image(client: httpx.AsyncClient, link: str, semaphore: Semaphore) -> None:
    '''Загрузка изображений с сайта по ссылке'''

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

    name_of_game = replace_forbidden_symbols_for_file_name(soup.find('title').get_text(strip=True), '_')
    img = await client.get(image_section[0]['src'])
    out = open(f"blendermarket\\images\\{name_of_game}.jpg", "wb")
    out.write(img.content)
    out.close()

    semaphore.release()

async def main() -> None:
    start_time = time()
    '''Создание тасков и загрузка изображений в асинхронном режиме'''
    semaphore = Semaphore(20)
    client = httpx.AsyncClient()
    # Iterate through the links
    tasks = [asyncio.create_task(load_image(client, link, semaphore)) for link in await read_links()]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
    