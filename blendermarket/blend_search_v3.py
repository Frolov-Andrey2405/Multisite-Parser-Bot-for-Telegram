from requests import Session
from bs4 import BeautifulSoup
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


def title_compare_vfx_and_blend(title_blend: str, title_vfx) -> str:
    word_distance = Levenshtein.distance(title_blend, title_vfx)
    if word_distance <= THRESHOLD:
        return True
    return False


def search_vfx_title_on_blend(title_vfx: str, session: Session) -> str:
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

    product_title = product_div.find('h5').get_text().strip()
    product_link = 'https://blendermarket.com' + product_div.find('a')['href']

    if title_compare_vfx_and_blend(product_title, title_vfx):
        print(product_title)
        print(product_link)


def main(vfx_titles: list[str]) -> None:
    with Session() as s:
        for title in vfx_titles:
            search_vfx_title_on_blend(title, s)


if __name__ == '__main__':
    vfx_titles = give_titles_from_vfx_file()
    main(vfx_titles)
