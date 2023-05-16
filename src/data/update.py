import secret
import requests
from bs4 import BeautifulSoup
import os
import re
import pandas as pd
from urllib.parse import urlsplit
from urllib.parse import urljoin
import extract

BASE_DIR = os.path.join(os.path.dirname(__file__), '../database/')
BASE_URL = 'https://confluence.amlogic.com'
HEADERS = {
    'Authorization': 'Bearer ' + secret.token,
    'Content-Type': 'application/json'
}

def get_pages():
    # Define the tag to search for
    tag = 'security-chatbot'

    # Search for pages with the tag
    url = f'{BASE_URL}/rest/api/content/search?cql=label="{tag}"&limit=100'

    response = requests.get(url, headers=HEADERS)
    data = response.json()

    # Extract the page IDs and titles
    pages = []
    for result in data['results']:
        page_id = result['id']
        page_title = result['title']
        pages.append((page_id, page_title))

    return pages

def update():
    print('=== Updating START ===')
    pages = get_pages()
    print('GET ' + str(len(pages)) + ' FAQs with TAG "security-chatbot"!')
    for page_id, page_title in pages:
        file_name = page_title.replace(" ", '') + ".csv"
        file_path = os.path.join(BASE_DIR, file_name)
        question_tag = page_title.replace(' ', '')
        url = BASE_URL + '/display/SW/' + page_title.replace(' ', '+')
        print(file_name)
        print(file_path)
        print(url)
        extract.extract(url, HEADERS, file_path, question_tag)

    print('=== Updated ' + str(len(pages)) + ' FAQs ===')
    print('=== Updating DONE ===')


if __name__ == "__main__":
    update()
    pass
