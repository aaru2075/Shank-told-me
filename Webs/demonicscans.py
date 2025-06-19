
from .scraper import Scraper
import json

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, quote, quote_plus

import re
from loguru import logger

class DemonicScansWebs(Scraper):
  def __init__(self):
    super().__init__()
    self.url = "https://demonicscans.org/"
    self.bg = True
    self.sf = "ds"
    self.headers = {
      "Accept": "*/*",
      #"Accept-Encoding": "gzip, deflate, br, zstd",
      #"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
      "Connection": "keep-alive",
      #"Cookie": "subdemon=1; _ga_S2788Y508W=GS2.1.s1749292219$o1$g0$t1749292219$j60$l0$h0; _ga=GA1.1.1307025858.1749292219",
      "Host":"demonicscans.org",
      "Referer": "https://demonicscans.org/",
      "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": "Windows",
      "Sec-Fetch-Dest": "empty",
      "Sec-Fetch-Mode": "cors",
      "Sec-Fetch-Site": "same-origin",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    }

  async def search(self, query: str = ""):
    url = f"https://demonicscans.org/search.php?manga={quote_plus(query)}"
    mangas = await self.get(url, headers=self.headers)

    bs = BeautifulSoup(mangas, "html.parser")
    cards = bs.find_all("a")
    results = []
    for card in cards:
      data = {}
      data['url'] = urljoin(self.url, card.get('href').strip())
      poster = card.find_next('img').get('src').strip()
      
      parsed = urlparse(poster)
      poster = quote(parsed.path)
      poster = parsed._replace(path=poster).geturl()
      
      data['poster'] = poster
      data['title'] = card.find_next('div').find_next("div").text.strip()
      
      results.append(data)
    
    return results

  async def get_chapters(self, data, page: int=1):
    results = data
    content = await self.get(results['url'], headers=self.headers)
    if content:
      bs = BeautifulSoup(content, "html.parser")
      chap = bs.find("div", {"id": "chapters-list"})
      results['chapters'] = chap
      
      des = bs.find(class_="white-font")
      des = des.text.strip() if des else "N/A"
      
      gen = bs.find("div", {"class": "genres-list"})
      gen = " ".join([g.text.strip() for g in gen.find_all("li")]) if gen else "N/A"

      results['msg'] = f"<b>{results['title']}</b>\n\n"
      results['msg'] += f"<b>Genres:</b> <code>{gen}</code>\n"
      results['msg'] += f"<b>Description:</b> <code>{des}</code>\n"

    return results

  def iter_chapters(self, data, page: int=1):
    chapters_list = []

    cards = data['chapters'].find_all("a")
    for card in cards:
      titles = card.get("href").split("=")[-1]
      
      manga_url = data['url'].replace("manga", "title")
      url = f"{manga_url}/chapter/{titles}/1"
      
      chapters_list.append({
        "title": titles,
        "url": url,
        "manga_title": data['title'],
      })

    return chapters_list[(page - 1) * 60:page * 60] if page != 1 else chapters_list

  async def get_pictures(self, url, data=None):
    response = await self.get(url, headers=self.headers)
    bs = BeautifulSoup(response, "html.parser")

    imgs_tags = bs.find_all('img', {"style": "max-width:100%;"})
    #print(imgs_tags)
    image_links = []
    for img in imgs_tags:
      images_link = img.get('src').strip()
      if images_link != "/img/free_ads.jpg":
        if images_link == "/img/wsup.gif":
          continue
        
        try:
          parsed = urlparse(images_link)
          poster = quote(parsed.path)
          
          images_link = parsed._replace(path=poster).geturl()
          image_links.append(images_link)
        except:
          continue
      
    return image_links
    

  async def get_updates(self, page:int=1):
    output = []
    while page <= 3:
      url = f"https://demonicscans.org/lastupdates.php?list={page}"
      results = await self.get(url, headers=self.headers)

      bs = BeautifulSoup(results, "html.parser")
      container = bs.find("div", {"id": "updates-container"})
      
      cards = bs.find(class_="updates-element-info ml flex flex-col justify-space-between full-width")
      if cards:
        for card in cards:
          try:
            data = {}
            a_tag = card.find_next("h2").find_next("a")
            
            data['url'] = urljoin(self.url, a_tag.get('href').strip())
            data['manga_title'] = a_tag.text.strip()
            
            div_tag = card.find_next(class_="flex flex-row chap-date justify-space-between")
            chap = div_tag.find_next("a").get('href').strip()
            
            chap = chap.split("=")[-1]
            chap = f"{data['url']}/chapter/{chap}/1"
            
            data['chapter_url'] = chap.replace("/manga/", "/title/")
            data['title'] = div_tag.find_next("a").text.strip()
            
            output.append(data)
          except:
            continue
          
      page += 1

    return output
