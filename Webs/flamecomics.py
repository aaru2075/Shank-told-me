from .scraper import Scraper
import json

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, quote, quote_plus

import re
from loguru import logger

class FlameComicsWebs(Scraper):
    def __init__(self):
      super().__init__()
      self.url = "https://flamecomics.xyz"
      self.sf = "fc"
      self.thumbnail = 'https://flamecomics.xyz/_next/image?url=https%3A%2F%2Fcdn.flamecomics.xyz%2Fseries%2F{id}%2Fthumbnail.png&w=1920&q=100'
      self.manga_url = "https://flamecomics.xyz/series/{id}"

      self.manga_api_id = "https://flamecomics.xyz/_next/data/CCokIcwOARfLGc-auhM_F/series/{id}.json"
      self.page_image = "https://cdn.flamecomics.xyz/series/{id}/{token}/{name}"
      
      self.sm_data = "CCokIcwOARfLGc-auhM_F"
      
      self.bg = True
      self.headers = {
        "Accept": "*/*",
        "Host": "flamecomics.xyz",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
      }
    
    def normalize(self, text):
      return ' '.join(text.lower().strip().split())
    
    async def search(self, query: str = ""):
      url = "https://flamecomics.xyz/api/series"
      content = await self.get(url, rjson=True, headers=self.headers)

      results = []
      search_normalized = self.normalize(query)
      for data in content:
          title_normalized = self.normalize(data["label"])
          if search_normalized in title_normalized:
            data['title'] = data["label"]
            
            data['poster'] = self.thumbnail.format(id = str(data["id"]))
            data['msg'] = f"<b>{data['title']}</b>\n\n"
            data['msg'] += f"<b>Status:</b> <code>{data['status']}</code>\n"
            data['msg'] += f"<b>Chapters :</b> <code>{data['chapter_count']}</code>\n"
            
            data['url'] = self.manga_url.format(id = str(data["id"]))
            
            results.append(data)
            
      return results

    async def get_chapters(self, data, page: int=1):
      results = data
      content = await self.get(results['url'], headers=self.headers)
      if content:
        bs = BeautifulSoup(content, "html.parser")
        container = bs.find("script", {"id": "__NEXT_DATA__"})
        content = json.loads(container.text.strip()) if container else None
        if content:
          results['chapters'] = content['props']['pageProps']['chapters']
          content = content['props']['pageProps']['series']
          
          results['id'] = content['series_id']
          results['description'] = content['description']
          
          results['geners'] = " ".join([g for g in content['tags']])
        
      return results

    def iter_chapters(self, data, page: int=1):
      chapters_list = []
      
      for card in data['chapters']:
        chapters_list.append({
          "title": f"Chapter {card['chapter']}",
          "url": f"{data['url']}/{card['token']}",
          "token": card['token'],
          "images": card['images'],
          "sid": card['series_id'],
          "manga_title": data['title'],
        })
      
      return chapters_list[(page - 1) * 60:page * 60] if page != 1 else chapters_list

    async def get_pictures(self, data, url=None):
      images_url = []
      for img in data['images'].values():
        images_url.append(self.page_image.format(token=data['token'], id=data['sid'], name=str(img["name"])))
      
      return images_url

    async def get_updates(self):
        return []
