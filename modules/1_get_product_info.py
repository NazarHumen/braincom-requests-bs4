"""
Parses a single product page on brain.com.ua with requests + BeautifulSoup:
collects the main product fields, the photo links and the full characteristics
dictionary, prints the result and saves it to the Product table.
"""

from pprint import pprint

import requests
from bs4 import BeautifulSoup

from load_django import *
from parser_app.models import *

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.google.com/',
    'Sec-Ch-Ua': '"Google Chrome";v="153", "Not_A Brand";v="8", "Chromium";v="153"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36',
}

url = 'https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html'

product = {}

r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')

# Found once and reused: 'br-pr-np' / 'br-pr-op' also appear in other product variants, so prices are searched inside this block only.
price_block = soup.find('div', attrs={'class': 'main-price-block'})

# Found once and reused: rows in this block have no classes, so single fields are searched by label text inside it.
characteristics_block = soup.find('div', attrs={'class': 'br-pr-chr'})

try:
    product['title'] = soup.find('h1', attrs={'class': 'main-title'}).text.strip()
except AttributeError:
    product['title'] = None

try:
    product['color'] = characteristics_block.find('span', string=['Колір', 'Цвет']).find_next_sibling('span').text.strip()
except AttributeError:
    product['color'] = None

try:
    product['memory'] = characteristics_block.find('span', string=["Вбудована пам'ять", 'Встроенная память']).find_next_sibling('span').text.strip()
except AttributeError:
    product['memory'] = None

try:
    product['manufacturer'] = characteristics_block.find('span', string=['Виробник', 'Производитель']).find_next_sibling('span').text.strip()
except AttributeError:
    product['manufacturer'] = None

try:
    old_price = price_block.find('div', attrs={'class': 'br-pr-op'})
    current_price = price_block.find('div', attrs={'class': 'br-pr-np'}).find('span').text.strip()
    if old_price:
        product['price'] = old_price.find('span').text.strip()
        product['sale_price'] = current_price
    else:
        product['price'] = current_price
        product['sale_price'] = None
except AttributeError:
    product['price'] = None
    product['sale_price'] = None

try:
    gallery = soup.find('div', attrs={'class': 'br-image-links'})
    product['images'] = [
        link.find('img').get('src')
        for link in gallery.find_all('a', attrs={'class': 'product-modal-button'})
    ]
except AttributeError:
    product['images'] = None

try:
    product['product_code'] = soup.find('span', attrs={'class': 'br-pr-code-val'}).text.strip()
except AttributeError:
    product['product_code'] = None

try:
    product['reviews_count'] = int(soup.find('a', attrs={'class': 'reviews-count'}).find('span').text.strip())
except (AttributeError, ValueError):
    product['reviews_count'] = None

try:
    product['screen_diagonal'] = characteristics_block.find('span', string=['Діагональ екрану', 'Диагональ экрана']).find_next_sibling('span').text.strip()
except AttributeError:
    product['screen_diagonal'] = None

try:
    product['screen_resolution'] = characteristics_block.find('span', string=['Роздільна здатність екрану', 'Разрешение экрана']).find_next_sibling('span').text.strip()
except AttributeError:
    product['screen_resolution'] = None

try:
    characteristics = {}
    for item in characteristics_block.find_all('div', attrs={'class': 'br-pr-chr-item'}):
        for row in item.find('div').find_all('div', recursive=False):
            label, value = row.find_all('span', recursive=False)
            characteristics[label.text.strip()] = ' '.join(value.text.split())
    product['characteristics'] = characteristics
except (AttributeError, ValueError):
    product['characteristics'] = None

product['link'] = url

pprint(product, sort_dicts=False)

Product.objects.get_or_create(**product)
