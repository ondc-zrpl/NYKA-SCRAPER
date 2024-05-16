from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests

app = Flask(__name__)

PROXY_URL = 'https://proxy.scrapeops.io/v1/'
PROXY_API_KEY = '3c1fb83d-5b93-4495-b023-170775d435f7'


def get_product_details(productId, skuId):
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
    }

    print(f"Using User-Agent: {headers['User-Agent']}")
    if skuId:
        url = f'https://www.nykaa.com/product/p/{productId}?skuId={skuId}&redirectpath=slug'
    else:
        url = f'https://www.nykaa.com/product/p/{productId}?redirectpath=slug'
    print(f"Requesting URL: {url}")
    #url=f'https://www.nykaa.com/nivea-derma-skin-clear-wash-gel/p/14552850?redirectpath=slug';
    proxy_response = requests.get(
        url=PROXY_URL,
        params={
            'api_key': PROXY_API_KEY,
            'url': url, 
        },
        headers=headers
    )

    if proxy_response.status_code != 200:
        return {
            'error': f"Proxy request failed with status code {proxy_response.status_code}."
        }

    soup = BeautifulSoup(proxy_response.content, 'html.parser')
    #print(soup.prettify())
    
    notify_element = soup.find('span', {'class': 'css-1neql7s'}, text="Notify me when the product is available")

    if notify_element:
        return {'title': "",
        'price': "Not Available",
        'image_url': ""
        }
    # Product name
    product_name = soup.find('h1', {'class': 'css-1gc4x7i'}).text

    # Product Price
    price_tag = soup.find('span', {'class': 'css-1jczs19'})
    product_price = '0'
    if price_tag:
        product_price = price_tag.text.replace('₹', '').replace(',', '')
        product_price = float(product_price)

    # Image URL
    image_tag = soup.find('div').find('img')
    image_url = ''
    if image_tag and 'src' in image_tag.attrs:
        image_url = image_tag['src']

    return {
        'title': product_name,
        'price': product_price,
        'image_url': image_url
    }

@app.route('/get_nyka_product_info', methods=['GET'])
def get_product_info():
    productId = request.args.get('productId')
    skuId = request.args.get('skuId')

    if not productId:
        return jsonify(error='The "producID" parameter is required.'), 400

    # If lid is not passed, use the default lid
    if not skuId:
        skuId = " "

    product_info = get_product_details(productId, skuId)
    return jsonify(product_info)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
