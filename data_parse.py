from bs4 import BeautifulSoup, Tag
import asyncio
import httpx
from vfxmed.vfxmed_new_version import save_load_first_product, read_links_from_file, extract_links, get_download_links, request_on_1_or_other_page
from database.work_with_db import create_connect, data_insert_in_db, get_object
from mysql.connector.errors import IntegrityError

def insert_data_in_table(data: dict, table_name, conn) -> None:
    try:
        data_insert_in_db(data, table_name, conn)
    except IntegrityError:
        pass


def do_requests_to_db(query_set: list[list[dict]], conn) -> None:
    for lst in query_set:

        for data in lst:
            
            insert_data_in_table({'link': data['link'], 'download_link': data['link']}, 'vfx', conn)
            
            id = get_object('link', data['link'], 'vfx', conn)['id']
            
            insert_data_in_table({'product_name': data['title'], 'addon_version': data['version'], 'Vfx_id': id}, 'version', conn)


async def parse_pages(mode_all=True) -> None:

    if not mode_all:
        with open('vfxmed/json/vfx_last_product.json', 'r') as f:
            link = read_links_from_file(f)[0]

    save_load_first_product('vfxmed\\json\\vfx_last_product.json')

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
                    print(page_number, link)
                    if link in map(lambda x: x[0], page_links):
                        
                        tasks.append(asyncio.create_task(
                            get_download_links(page_links, client)))

                        do_requests_to_db(await asyncio.gather(*tasks), conn)
                        
                        break
                
            except ValueError:
                print('ValueError', tasks)

                do_requests_to_db(await asyncio.gather(*tasks), conn)

                break

            tasks.append(asyncio.create_task(
                get_download_links(page_links, client)))

            page_number += 1

            if len(tasks) >= 5:

                do_requests_to_db(await asyncio.gather(*tasks), conn)

                tasks.clear()

if __name__ == '__main__':
    asyncio.run(parse_pages(mode_all=False))
    #asyncio.run(parse_all_pages())