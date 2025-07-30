import os
import re
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv

from outputs import default_output, pretty_output
from utils import find_tag, get_input_value, get_soup

load_dotenv()

LOGIN_URL = os.getenv('LOGIN_URL')


def authentication(session):
    soup = get_soup(session, LOGIN_URL)
    data = {
        "set_session":  get_input_value(soup, 'set_session'),
        "pma_username": os.getenv('PMA_USERNAME'),
        "pma_password": os.getenv('PMA_PASSWORD'),
        "token": get_input_value(soup, 'token'),
        "server": get_input_value(soup, 'server'),
        "route": get_input_value(soup, 'route')
    }
    form_action = find_tag(soup, 'form')["action"]
    soup = get_soup(
        session,
        urljoin(LOGIN_URL, form_action),
        method='POST',
        data=data
    )
    return soup


def get_testDB(session, soup):
    navigation_tree = find_tag(
        soup,
        'div',
        attrs={"id": "pma_navigation_tree_content"}
    )
    db_link = navigation_tree.find('a', string='testDB')['href']
    return get_soup(session, urljoin(LOGIN_URL, db_link))


def get_users_table(session, soup):
    soup = get_testDB(session, soup)
    table_data = find_tag(soup, 'table', {'class': "data"})
    table_users = table_data.find('a', string=re.compile(r'users'))['href']
    return get_soup(session, urljoin(LOGIN_URL, table_users))


def get_users_data(session, soup):
    soup = get_users_table(session, soup)
    table = find_tag(soup, 'table', {'class': "table_results"})
    table_thead = find_tag(soup, 'thead')
    table_thead_row = find_tag(table_thead, 'tr')

    results = []
    headings = []
    for elem in table_thead_row.find_all('th', class_='column_heading'):
        heading = find_tag(elem, 'a')
        if heading.small is not None:
            heading.small.decompose()
        headings.append(heading.get_text(strip=True))
    results.append(headings)
    table_trs = find_tag(table, 'tbody').find_all('tr')
    for tr in table_trs:
        results.append(
            [elem.text for elem in tr.find_all('td', class_='data')]
        )
    return results


def main():
    session = requests.session()
    soup = authentication(session)
    results = get_users_data(session, soup)
    pretty_output(results)
    default_output(results)


if __name__ == '__main__':
    main()
