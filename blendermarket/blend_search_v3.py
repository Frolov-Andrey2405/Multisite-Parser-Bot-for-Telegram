from requests import Session
from bs4 import BeautifulSoup, Tag
import Levenshtein
import json

FORBIDDEN_SYMBOLS = ('\\\\', '/', ':', '*', '?', '', '<', '>', '|', ' ')
BASE_URL = "https://blendermarket.com/products"
THRESHOLD = 3


def give_titles_from_vfx_file():
    with open('vfxmed/json/vfxmed.json', 'r') as f:
        titles = []
        for line in f:
            data = json.loads(line)
            titles.append(data['title'])
    return titles


def title_compare_with_blend(title_blend: str, title_vfx: str) -> str:
    word_distance = Levenshtein.distance(title_blend, title_vfx)
    if word_distance <= THRESHOLD:
        return True
    return False


def get_title_blend_product(product: Tag) -> str:
    return product.find('h5').get_text().strip()


def get_full_information_about_blend_product(title_product: str, product: Tag) -> dict:
    product_link = 'https://blendermarket.com' + product.find('a')['href']
    image_url = product.find('img')['src']

    return {
        'title': title_product, 
        'off_link': product_link,
        'url_on_image': image_url,
    }


def search_first_vfx_product_on_blend(title_vfx: str, session: Session) -> None|Tag:
    response = session.get(
        f'''
    https://blendermarket.com/search?utf8=%E2%9C%93&search%5Bq%5D={title_vfx}&button=
    '''
    )

    response_parser = BeautifulSoup(response.content, 'html.parser')
    product_div = response_parser.find(
        'div', class_="col-12 col-md-6 col-lg-3 mb-4")

    if product_div is None:
        return None

    return product_div


def search_info_about_blend_product(title: str, session: Session) -> dict|None:
    product = search_first_vfx_product_on_blend(title, session)
            
    if product is not None:
        title_blend = get_title_blend_product(product)

        flag = title_compare_with_blend(title_blend, title)

        if flag:
            return get_full_information_about_blend_product(title_blend, product)

    return None


if __name__ == '__main__':
    vfx_titles = give_titles_from_vfx_file()
    with Session() as s:
        for title in vfx_titles:
            search_info_about_blend_product(title, s)
