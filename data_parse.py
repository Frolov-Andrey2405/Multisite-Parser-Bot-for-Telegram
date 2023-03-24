from bs4 import BeautifulSoup, Tag
import asyncio
import httpx
from vfxmed.vfxmed_new_version import save_load_first_product, read_links_from_file, extract_links, get_download_links, request_on_1_or_other_page
from blendermarket.blend_search_v3 import search_info_about_blend_product
from mysql.connector.errors import IntegrityError
import json
from requests import Session as RequestsSession
from database.models import ENGINE, Vfx, Version, Blend
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update , values
from sqlalchemy.exc import IntegrityError


def fill_vfx_and_version_tables(query_set: list[list[dict]], session) -> None:
    for lst in query_set:

        for data in lst:

            session.execute(
                insert(Vfx),
                {'link': data['link'], 'download_link': data['link']},
            )

            vfx_id = next(session.execute(
                            select(Vfx.id).
                            where(Vfx.link == data['link'])
                        )).id
                        
            session.execute(
                        insert(Version),
                        {'product_name': data['title'], 'addon_version': data['version'], 'vfx_id': vfx_id}
            )
                        
            session.commit()


def fill_blend_and_update_tables(blend_product_info: dict, session, version_id):            
    try:
        session.execute(
            insert(Blend),
            blend_product_info
        )
                        
    except IntegrityError:
        pass
                     
    blend_product_id = next(session.execute(
                    select(Blend.id).
                    where(Blend.off_link==blend_product_info['off_link'])
                )).id

    try:
        session.execute( 
            update(Version).
            where(Version.id == version_id).
            values(blend_id=blend_product_id)
        )
    except IntegrityError:
        pass

    session.commit()

async def parse_pages_vfx(mode_all=True) -> None:

    if not mode_all:
        with open('vfxmed/json/vfx_last_product.json', 'r') as f:
            link = read_links_from_file(f)[0]

    save_load_first_product('vfxmed\\json\\vfx_last_product.json')

    with Session(ENGINE) as session:

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
                    if link in map(lambda x: x[0], page_links):
                        
                        tasks.append(asyncio.create_task(
                            get_download_links(page_links, client)))

                        fill_vfx_and_version_tables(await asyncio.gather(*tasks), session)
                        
                        break
                
            except ValueError:
                print('ValueError', tasks)

                fill_vfx_and_version_tables(await asyncio.gather(*tasks), session)

                break

            tasks.append(asyncio.create_task(
                get_download_links(page_links, client)))

            page_number += 1

            if len(tasks) >= 5:

                fill_vfx_and_version_tables(await asyncio.gather(*tasks), session)

                tasks.clear()


def parse_blend():

    with open('vfxmed/json/vfx_last_product.json', 'r') as f:
        data_file = json.loads(next(f))
        date_update = data_file['begin_update']
        link = data_file['link']
    
    with Session(ENGINE) as session:

        version_data = session.execute(
            select(Version.product_name, Version.id)
            .where(Version.data_created >= date_update)
        ).all()

        with RequestsSession() as s:
            
            for version_row in version_data:

                blend_product_info = search_info_about_blend_product(version_row[0], s)

                if blend_product_info:
                    
                    fill_blend_and_update_tables(blend_product_info, session, version_row[1])



if __name__ == '__main__':
    pass
    asyncio.run(parse_pages_vfx(mode_all=True))
    parse_blend()
    