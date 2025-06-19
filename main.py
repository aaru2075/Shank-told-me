from TG.wks import Bot, worker, asyncio, Vars
from TG.auto import main_updates

from pyrogram import idle
import random, os, shutil

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

MSG = """<blockquote><b>🔥 SYSTEMS ONLINE. READY TO RUMBLE. 🔥

Sleep mode deactivated. Neural cores at 100%. Feed me tasks, and watch magic happen. Let’s. Get. Dangerous.</b></blockquote>"""

PICS = random.choice(Vars.PICS)

button = [[        
  InlineKeyboardButton('*Start Now*', url= "https://t.me/Manga_Downloaderx_bot?start=start"),
  InlineKeyboardButton("*Channel*", url = "telegram.me/Wizard_Bots")
]]

folder_path = "Process"
if os.path.exists(folder_path) and os.path.isdir(folder_path):
  shutil.rmtree(folder_path)
  
if __name__ == "__main__":
  Bot.start()
  
  loop = asyncio.get_event_loop()
  for i in range(10):
    loop.create_task(worker(i))
  for i in range(1):
    loop.create_task(main_updates())
  
  try: Bot.send_photo(-1001723894782, photo=PICS, caption=MSG, reply_markup=InlineKeyboardMarkup(button))
  except: pass
  idle()
  try: Bot.run()
  except: pass

