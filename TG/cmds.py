from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .storage import web_data, split_list, plugins_list, users_txt, retry_on_flood, queue
from bot import Bot, Vars

import random
from Tools.db import users, sync, uts


HELP_MSG = """
<b>To download a manga just type the name of the manga you want to keep up to date.</b>

For example:
`One Piece`

<blockquote expandable><i>Then you will have to choose the language of the manga. Depending on this language, you will be able to choose the website where you could download the manga. Here you will have the option to subscribe, or to choose a chapter to download. The chapters are sorted according to the website.</i></blockquote>

<blockquote><b>Updates Channel : @Wizard_bots</b></blockquote>
"""

@Bot.on_message(filters.command("queue"))
async def queue_msg_handler(client, message):
  if Vars.IS_PRIVATE:
    if message.chat.id not in Vars.ADMINS:
      return await message.reply("<code>You cannot use me baby </code>")

  await message.reply(f"Queue Size: {queue.qsize()}")

@Bot.on_message(filters.command("start"))
async def start(client, message):
  if Vars.IS_PRIVATE:
    if message.chat.id not in Vars.ADMINS:
      return await message.reply("<code>You cannot use me baby </code>")

  photo = random.choice(Vars.PICS)
  await message.reply_photo(
    photo,
    caption=("<b><i>Welcome to the best manga pdf bot in telegram!!</i></b>\n"
     "\n"
     "<b><i>How to use? Just type the name of some manga you want to keep up to date.</i></b>\n"
     "\n"
     "<b><i>For example:</i></b>\n"
     "<i><code>One Piece</i></code>\n"
     "\n"
     "<b><i>Check /help for more information.</i></b>"),
    reply_markup=InlineKeyboardMarkup([[        
                                         InlineKeyboardButton('* Repo *', url = "https://github.com/Dra-Sama/mangabot"),
                                         InlineKeyboardButton("* Support *", url = "https://t.me/WizardBotHelper")
                                     ]]))


@Bot.on_message(filters.command("help"))
async def help(client, message):
  if Vars.IS_PRIVATE:
    if message.chat.id not in Vars.ADMINS:
      return await message.reply("<code>You cannot use me baby </code>")

  return await message.reply(HELP_MSG)


@Bot.on_message(filters.command(["deltask", "cleantasks", "del_tasks", "clean_tasks"]))
async def deltask(client, message):
  if Vars.IS_PRIVATE:
    if message.chat.id not in Vars.ADMINS:
      return await message.reply("<code>You cannot use me baby </code>")

  user_id = message.from_user.id
  numb = 0
  if user_id in queue._user_data:
    for task_id in queue._user_data[user_id]:
      await queue.delete_task(task_id)
      numb += 1
    await message.reply(f"All tasks deleted:- {numb}")
  else:
    await message.reply("No tasks found")


@Bot.on_message(filters.command("search"))
async def search_group(client, message):
  if Vars.IS_PRIVATE:
    if message.chat.id not in Vars.ADMINS:
      return await message.reply("<code>You cannot use me baby </code>")

  try: txt = message.text.split(" ")[1]
  except: return await message.reply("<code>Format:- /search Manga </code>")
  photo = random.choice(Vars.PICS)

  try: 
    await message.reply_photo(photo, caption="Select search Webs .", reply_markup=plugins_list(), quote=True)
  except ValueError: 
    await message.reply_photo(photo, caption="Select search Webs .", reply_markup=plugins_list(), quote=True)


type = "uts"
name = Vars.DB_NAME

@Bot.on_message(filters.command(['user_panel','us', 'users_settings']))
async def _user_panel(_, msg):
  if Vars.IS_PRIVATE:
    if msg.chat.id not in Vars.ADMINS:
      return await msg.reply("<code>You cannot use me baby </code>")

  try:
    user_id = str(msg.from_user.id)

    if not user_id in uts:
      uts[user_id] = {}
      sync(name, type)

    if not "setting" in uts[user_id]:
      uts[user_id]["setting"] = {}
      sync(name, type)

    txt = users_txt.format(
      id = user_id,
      file_name = uts[user_id]['setting'].get("file_name", "None"),
      caption = uts[user_id]['setting'].get("caption", "None"),
      thumb = uts[user_id]['setting'].get("thumb", "None"),
      banner1 = uts[user_id]['setting'].get("banner1", "None"),
      banner2 = uts[user_id]['setting'].get("banner2", "None"),
      dump = uts[user_id]['setting'].get("dump", "None"),
      type = uts[user_id]['setting'].get("type", "None"),
      megre= uts[user_id]['setting'].get("megre", "None"),
      regex = uts[user_id]['setting'].get("regex", "None"),
      len = uts[user_id]['setting'].get("file_name_len", "None"),
      password = uts[user_id]['setting'].get("password", "None")
    )

    BANNEER_BUTTON = "⚙️ Banner {} ⚙️"
    BANNEER_DATA = "ubn{}"

    button = [
      [
        InlineKeyboardButton("🪦 File Name 🪦", callback_data="ufn"),
        InlineKeyboardButton("🪦 Caption‌ 🪦", callback_data="ucp")
      ],
      [
        InlineKeyboardButton("🪦 Thumbnali 🪦", callback_data="uth"),
        InlineKeyboardButton("🪦 Regex 🪦", callback_data="uregex")
      ],
      [
        InlineKeyboardButton("⚒ Banner ⚒", callback_data="ubn"),
      ],
      [
        InlineKeyboardButton("⚙️ Password ⚙️", callback_data="upass"),
        InlineKeyboardButton("⚙️ Megre Size ⚙️", callback_data="umegre")
      ],
      [
      ],
    ]
    if not Vars.CONSTANT_DUMP_CHANNEL:
      button[-1].append(InlineKeyboardButton("⚒ Dump Channel ⚒", callback_data="udc"))

    button[-1].append(InlineKeyboardButton("⚒ File Type ⚒", callback_data="u_file_type"))
    
    if uts[user_id].get("thumb", None):
      photo = uts[user_id].get("thumb")
    else:
      photo = random.choice(Vars.PICS)

    await retry_on_flood(msg.reply_photo)(photo, caption=txt, reply_markup=InlineKeyboardMarkup(button))
  except Exception as e:
    await msg.reply_text(f"Error: {e}")


@Bot.on_message(filters.text & filters.private)
async def search(client, message):
  if Vars.IS_PRIVATE:
    if message.chat.id not in Vars.ADMINS:
      return await message.reply("<code>You cannot use me baby </code>")

  txt = message.text
  photo = random.choice(Vars.PICS)
  button = []
  if not txt.startswith("/"):
    try: await message.reply_photo(photo, caption="Select search Webs .", reply_markup=plugins_list(), quote=True)
    except ValueError: await message.reply_photo(photo, caption="Select search Webs .", reply_markup=plugins_list(), quote=True)
