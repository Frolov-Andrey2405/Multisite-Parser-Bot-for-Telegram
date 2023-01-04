from bs4 import BeautifulSoup
import json
from time import time
import httpx
import asyncio
from asyncio import Semaphore

# Set the base URL for the site
BASE_URL = "https://blendermarket.com/products"


async def load_link(client: httpx.AsyncClient, file, page_number: int, semaphore: Semaphore) -> None:
    '''Asyncronous function that sends a GET request to a specified URL and page number'''
    await semaphore.acquire()

    # Send a GET request to the URL with the page number
    response = await client.get(f"{BASE_URL}?page={page_number}")

    # Parse the HTML contents
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the blocks with the posts
    post_blocks = soup.find_all(
        'a', class_='text-nounderline text-nocolor')

    # Iterate through the post blocks
    for block in post_blocks:
        # Find the link to the product page
        link = block['href']

        # Write the link to the links.json file
        file.write(json.dumps(
            {"link": f"https://blendermarket.com/{link}"}) + '\n')

    semaphore.release()


async def main():
    '''Semaphore to limit the number of concurrent tasks'''
    semaphore = Semaphore(20)

    # Open the official_links.json file in write mode
    with open('blendermarket/json/official_links.json', 'w') as file:

        client = httpx.AsyncClient()

        responce = await client.get('https://blendermarket.com/products')

        soup = BeautifulSoup(responce.text, 'html.parser')

        page_count = soup.find(
            'nav', class_='pagy-bootstrap-nav').find_all('li')[-2].get_text()

        tasks = [asyncio.create_task(load_link(
            client, file, page_num, semaphore)) for page_num in range(1, int(page_count)+1)]

        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
