import asyncio
from asyncio import Semaphore
import re
from bs4 import BeautifulSoup
import httpx
import json
from time import time, sleep

FORBIDDEN_SYMBOLS = ('\\', '/', ':', '*', '?', '"', '<', '>', '|', ' ')
BASE_URL = "https://blendermarket.com/products"


async def page_count(client: httpx.AsyncClient) -> int:
    '''Count page number'''

    responce = await client.get('https://blendermarket.com/products')

    soup = BeautifulSoup(responce.text, 'html.parser')

    page_count = soup.find(
        'nav', class_='pagy-bootstrap-nav').find_all('li')[-2].get_text()

    return int(page_count)

def replace_forbidden_symbols_for_file_name(string: str, symbol_repalced: str) -> str:
    '''Replace FORBIDDEN_SYMBOLS in file on symbol'''
    new_str = ''
    for symbol in string:
        new_str += symbol_repalced if symbol in FORBIDDEN_SYMBOLS else symbol
    return new_str


async def load_data(client: httpx.AsyncClient, semaphore: Semaphore, file, page_number: int) -> None:
    '''Load data from site'''

    await semaphore.acquire()
    # Load the link as a JSON object
    sleep(0.005)
    # Send a GET request to the URL with the page number
    try:
        response = await client.get(f"{BASE_URL}?page={page_number}")
    except:
        with open('./logs/links_on_page', 'w') as file:
            file.write(f"{BASE_URL}?page={page_number}")
            return None
    # Parse the HTML contents
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the blocks with the posts
    post_blocks = soup.find_all(
        'a', class_='text-nounderline text-nocolor')

    # Iterate through the post blocks
    tasks = [asyncio.create_task(write_data_in_files(
        block, client, file)) for block in post_blocks]

    await asyncio.gather(*tasks)

    semaphore.release()


async def write_data_in_files(block: list, client: httpx.AsyncClient, file):
    link = block['href']
    # Find the link to the product page
    link = f'https://blendermarket.com/{link}'
    sleep(0.005)
    try:
        response = await client.get(link)
    except httpx.ReadTimeout:
        with open('./logs/links_on_product', 'w') as file:
            file.write(link)
            return None
    # Parse the HTML contents
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the section with the images
    image_section = soup.find_all('img', class_='img-fluid')

    try:
        name_of_tools = soup.find('title').get_text(strip=True)
        name_of_tools = name_of_tools.replace(" - Blender Market", "")
    except AttributeError:
        return None

    # Removing unwanted symbols
    name_of_tools = re.sub(
        r'\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8}', '', name_of_tools)

    for symbol in FORBIDDEN_SYMBOLS:
        name_of_tools = name_of_tools.replace(symbol, ' ')

    url_on_image = image_section[0]['src'] if len(image_section) > 0 else None

    file.write(json.dumps({
        'off_link': link,
        'name_of_tools': name_of_tools,
        'url_on_image': url_on_image,
    }) + '\n')


async def main() -> None:
    '''Create tasks and async load data'''
    semaphore = Semaphore(1)
    start_time = time()
    client = httpx.AsyncClient(timeout=25)
    client.headers['user-agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    number_of_page = await page_count(client)

    # Iterate through the links
    with open('blendermarket\\json\\blend.json', 'w') as file:

        tasks = [asyncio.create_task(load_data(
            client, semaphore, file, num_page)) for num_page in range(1, number_of_page+1)]
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())

'''
Documentation:

This code is a web scraping script that extracts data from the website 
blendermarket.com. 
The script is written in Python and utilizes the asyncio, bs4, httpx, 
json, re, and time libraries.

The script begins by defining a list of forbidden symbols that will 
be removed from the extracted data later on in the script. 
The BASE_URL variable is set to the base URL of the website that the script 
will be scraping.

The page_count() function is an asynchronous function that takes in an 
httpx.AsyncClient object as a parameter and uses it to make a GET request 
to the website's products page. The function then parses the HTML response 
using BeautifulSoup and extracts the page count from the pagination 
navigation element. This value is returned as an integer.

The replace_forbidden_symbols_for_file_name() function takes in a string 
and a replacement symbol as parameters. It then iterates through the string, 
replacing any forbidden symbols with the replacement symbol. 
The modified string is returned.

The load_data() function is an asynchronous function that takes in 
an httpx.AsyncClient object, a Semaphore object, a file object, and 
a page number as parameters. The function uses the httpx.AsyncClient 
object to make a GET request to the website using the provided page number 
as a query parameter. The function then parses the HTML response using 
BeautifulSoup and extracts the post blocks. For each post block, the function 
creates an asynchronous task that calls the write_data_in_files() function 
and passes the post block, httpx.AsyncClient object, and file object as parameters. 
The function then waits for all tasks to complete before releasing 
the semaphore and returning None.

The write_data_in_files() function is an asynchronous function that takes 
in a list, an httpx.AsyncClient object, and a file object as parameters. 
The function extracts the product page link from the provided list and uses 
the httpx.AsyncClient object to make a GET request to the product page. 
The function then parses the HTML response using BeautifulSoup and extracts 
the product name, image URL, and product link. The function removes any 
unwanted symbols from the product name using regular expressions. The function 
then writes the extracted data to the provided file object in JSON format.
'''
