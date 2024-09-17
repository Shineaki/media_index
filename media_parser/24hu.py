import requests
from bs4 import BeautifulSoup as bs

rsp = requests.get("https://24.hu/belfold")
soup = bs(rsp.content, 'html.parser')
for i in soup.find_all('a', {'class': 'm-articleWidget__link'}):
    print(i.string.strip() + " " + i["href"])