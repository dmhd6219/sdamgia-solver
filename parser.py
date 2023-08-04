from pprint import pprint

import requests as requests

url = 'https://math-ege.sdamgia.ru/test?id=54424743'

session = requests.Session()
pprint(session.get(url).text)