from bot import Bot, Vars, logger
from Tools.db import *
from .storage import web_data, clean, retry_on_flood, get_episode_number, queue
from .wks import send_manga_chapter

import asyncio

import os
import shutil


async def get_updates_manga():
  updates = []
  for i in web_data.keys():
    try:
      raw_data = await web_data[i].get_updates()
      for data in raw_data:
        if data['url'] in dts:
          episode_number = str(get_episode_number(data['title']))
          if 'Lastest' not in dts[data['url']] or int(
              dts[data['url']]['Lastest']) > int(episode_number):
            if "Lastest" in dts[data['url']]:
              chapters = await web_data[i].get_chapters(data)
              chapter = web_data[i].iter_chapters(chapters)
              if chapter:
                for chapter in chapters:
                  chapter_ep = get_episode_number(chapter['title'])
                  if int(dts[data['url']]['Lastest']) < int(chapter_ep):
                    pictures = await web_data[i].get_pictures(
                        url=data['chapter_url'], data=data)
                    if pictures:
                      data['pictures_list'] = pictures
                      updates.append(data)
            else:
              pictures = await web_data[i].get_pictures(
                  url=data['chapter_url'], data=data)
              if pictures:
                data['pictures_list'] = pictures
                updates.append(
                  {'data': data, 'webs': web_data[i]}
                )
    except Exception as e:
      logger.exception(e)
      continue

  return updates


async def send_updates(data, webs):
  try:
    await Bot.send_message(
        Vars.UPDATE_CHANNEL,
        f"<b><i>Updates: {data['manga_title']} - {data['title']}\n\nUrl: {data['url']}</i></b>"
    )
  except:
    pass

  episode_number = str(get_episode_number(data['title']))
  user_ids = dts[data['url']]['users']
  for user_id in user_ids:
    await send_manga_chapter(data, picturesList=data['pictures_list'], user=None, sts=None, user_id=user_id, webs=webs)
  
  # Saving Database
  dts[data['url']]["Lastest"] = str(episode_number)
  sync()


async def main_updates():
  while True:
    min = 20
    try:
      updates = await get_updates_manga()
      for data in updates:
        try:
          await send_updates(data['data'], data['webs'])
        except:
          continue
    finally:
      await asyncio.sleep(min * 60)
