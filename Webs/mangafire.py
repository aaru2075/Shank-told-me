
from .scraper import Scraper
import json 

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, quote, quote_plus

class MangaFireWebs(Scraper):
  def __init__(self):
    super().__init__()
    self.url = "https://mangafire.to"
    self.cs = True
    self.sf = "mf"
    self.headers = {
      "Accept": "application/json, text/javascript, */*; q=0.01",
      "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
      "Connection": "keep-alive",
      "Cookie": "usertype=guest;",
      "Host": "mangafire.to",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest",
    }

  async def search(self, query: str = ""):
    url = f"https://mangafire.to/ajax/manga/search?keyword={quote_plus(query)}"
    content = await self.get(url, rjson=True, headers=self.headers)
    
    results = []
    if content:
      bs = BeautifulSoup(content['result']['html'], "html.parser")
      cards = bs.find_all('a', class_='unit')
      for card in cards:
        data = {}
        data['title'] = card.find('h6').text.strip()
        data['url'] = urljoin(self.url, card.get('href').strip())
        
        data['poster'] = card.find('img').get('src').strip()
        data['vol'] = True if "Vol" in card.text else None
        data['id'] = data['url'].split(".")[-1]
        
        results.append(data)
      
    return results
    

  async def get_chapters(self, data, page: int=1):
    results = data
    url = f"https://mangafire.to/ajax/manga/{results['id']}/chapter/en"
    data = await self.get(url, rjson=True, headers=self.headers)
    
    results['chapters'] = data['result']
    if results['vol']:
      url = f"https://mangafire.to/ajax/manga/{results['id']}/volume/en"
      data = await self.get(url, rjson=True, headers=self.headers)
      results['volumes'] = data['result']
      
    return results

  def iter_chapters(self, data, vols=None):
    chapters_list = []
    if vols:
      bs = BeautifulSoup(data['volumes'], "html.parser")
    else:
      bs = BeautifulSoup(data['chapters'], "html.parser")
    print(bs.prettify())
    cards = bs.find_all("a")
    for card in cards:
      chapters_list.append({
        "title": card.find_next("span").text.strip(),
        "url": urljoin(self.url, card.get('href').strip()),
      })
      
    return chapters_list

  async def get_pictures(self, url, data=None):
    response = await self.get(url, cs=True, headers=self.headers)
    bs = BeautifulSoup(response, "html.parser")
    container = bs.find("script", {"id": "__NEXT_DATA__"})

    con = container.text.strip()
    con = json.loads(con)

    images = con["props"]["pageProps"]["chapter"]["md_images"]
    images_url = [f"https://meo.comick.pictures/{image['b2key']}" for image in images]

    return images_url

  async def get_updates(self):
    url = "https://api.comick.fun/chapter?page=1&device-memory=8&order=new"
    results = await self.get(url, cs=True, rjson=True, headers=self.headers)

    output = {}
    for data in results:
      url = f"https://comick.io/comic/{data['md_comics']['slug']}"
      file_key = data["md_comics"]['md_covers'][0]["b2key"]

      images = f"https://meo.comick.pictures/{file_key}"
      chapter_url = f"{url}/{data['hid']}-chapter-{data['chap']}-en"

      data['images_link'] = images
      data['chapter_url'] = chapter_url

      output[url] = data

    return output
