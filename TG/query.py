from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

from .storage import *
from bot import Bot, Vars, logger
import random

from Tools.db import *

@Bot.on_callback_query(filters.regex("^chs"))
async def ch_handler(client, query):
  """This Is Information Handler Of Callback Data"""
  try:
    webs, data = searchs[query.data]
  except:
    return await query.answer("This is an old button, please redo the search",
                              show_alert=True)

  bio_list = await webs.get_chapters(data)
  if not bio_list:
    return await query.answer("No chapters found", show_alert=True)

  if "poster" in bio_list:
    try:
      await query.edit_message_media(InputMediaPhoto(bio_list['poster']))
    except:
      pass

  c = query.data.replace("chs", "ch")
  chaptersList[c] = webs, bio_list, data
  sf = webs.sf
  if "msg" in bio_list:
    await retry_on_flood(query.edit_message_text
                         )(bio_list['msg'],
                           reply_markup=InlineKeyboardMarkup([[
                               InlineKeyboardButton("📨 Chapters 📨",
                                                    callback_data=c),
                               InlineKeyboardButton("💠 Back 💠",
                                                    callback_data=f"bk.s.{sf}")
                           ]]))
  else:
    await retry_on_flood(query.edit_message_text
                         )(f"{bio_list['title']}",
                           reply_markup=InlineKeyboardMarkup([[
                               InlineKeyboardButton("📨 Chapters 📨",
                                                    callback_data=c),
                               InlineKeyboardButton("💠 Back 💠",
                                                    callback_data=f"bk.s.{sf}")
                           ]]))



@Bot.on_callback_query(filters.regex("^ch"))
async def p_handler(client, query):
  """This Is Chapters Handler Of Callback Data"""
  if query.data in chaptersList:
    webs, data, rdata = chaptersList[query.data]
    sf = webs.sf

    try: 
      chapters = await webs.iter_chapters(data)
    except TypeError: 
      chapters = webs.iter_chapters(data)
    
    subs_bool = get_subs(str(query.from_user.id), rdata['url'])
    if not chapters:
      return await query.answer("No chapters found", show_alert=True)

    button = []
    for chapter in chapters:
      c = f"pic|{hash(chapter['url'])}"
      chaptersList[c] = (webs, chapter)
      button.append(InlineKeyboardButton(chapter['title'], callback_data=c))

    button = split_list(button[:60])
    c = f"pg:{sf}:{hash(chapters[-1]['url'])}:"
    if len(chapters) > 60 or sf == "ck":
      pagination[c] = (webs, data, rdata)
      button.append([
          InlineKeyboardButton(">>", callback_data=f"{c}1"),
          InlineKeyboardButton("2x>", callback_data=f"{c}2"),
          InlineKeyboardButton("5x>", callback_data=f"{c}5")
      ])

    c = f"subs:{hash(rdata['url'])}"
    subscribes[c] = (webs, rdata)
    if subs_bool:
      button.insert(
        0,
        [InlineKeyboardButton("🔔 Unsubscribe 🔔", callback_data=c)])
    else:
      button.insert(
        0,
        [InlineKeyboardButton("📯 Subscribe 📯", callback_data=c)])
    
    callback_data = f"full:{sf}:{hash(chapters[0]['url'])}"
    pagination[callback_data] = (chapters, webs)
    button.append([InlineKeyboardButton("📚 Full Page 📚", callback_data=callback_data)])
    
    button.append(
        [InlineKeyboardButton("💠 Back 💠", callback_data=f"bk.s.{sf}")])
    await retry_on_flood(query.edit_message_reply_markup)(InlineKeyboardMarkup(button))
  else:
    try: await query.answer("This is an old button, please redo the search", show_alert=True)
    except: pass


@Bot.on_callback_query(filters.regex("^pg"))
async def pg_handler(client, query):
  """This Is Pagination Handler Of Callback Data"""
  data = query.data.split(":")
  page = data[-1]
  data = ":".join(data[:-1])
  data = f"{data}:"
  if data in pagination:
    webs, data, rdata = pagination[data]
    sf = webs.sf
    subs_bool = get_subs(str(query.from_user.id), rdata['url'])
    if sf == "ck":
      chapters = await webs.get_chapters(rdata, int(page))
      if not chapters:
        return await query.answer("No chapters found", show_alert=True)
      
      chapters = webs.iter_chapters(chapters)
    else:
      try: 
        chapters = await webs.iter_chapters(data, int(page))
      except TypeError: 
        chapters = webs.iter_chapters(data, int(page))
      
    if not chapters:
      return await query.answer("No chapters found", show_alert=True)

    button = []
    for chapter in chapters:
      c = f"pic|{hash(chapter['url'])}"
      chaptersList[c] = (webs, chapter)
      button.append(InlineKeyboardButton(chapter['title'], callback_data=c))

    button = split_list(button[:60])
    c = f"pg:{sf}:{hash(chapters[-1]['url'])}:"
    pagination[c] = (webs, data, rdata)
    if int(page) > 1:
      button.append([
              InlineKeyboardButton("<<", callback_data=f"{c}{int(page) - 1}"),
              InlineKeyboardButton("<2x", callback_data=f"{c}{int(page) - 2}"),
              InlineKeyboardButton("<5x", callback_data=f"{c}{int(page) - 5}")
          ])

    button.append([
          InlineKeyboardButton(">>", callback_data=f"{c}{int(page) + 1}"),
          InlineKeyboardButton("2x>", callback_data=f"{c}{int(page) + 2}"),
          InlineKeyboardButton("5x>", callback_data=f"{c}{int(page) + 5}"),
    ])

    c = f"subs:{hash(rdata['url'])}"
    subscribes[c] = (webs, rdata)
    if subs_bool:
      button.insert(
        0,
        [InlineKeyboardButton("🔔 Unsubscribe 🔔", callback_data=c)])
    else:
      button.insert(
        0,
        [InlineKeyboardButton("📯 Subscribe 📯", callback_data=c)])
    
    callback_data = f"full:{sf}:{hash(chapters[0]['url'])}"
    pagination[callback_data] = (chapters, webs)
    button.append([InlineKeyboardButton("📚 Full Page 📚", callback_data=callback_data)])
    
    button.append([InlineKeyboardButton("💠 Back 💠", callback_data=f"bk.s.{sf}")])
    await retry_on_flood(query.edit_message_reply_markup)(InlineKeyboardMarkup(button))
  else:
    try: await query.answer("This is an old button, please redo the search", show_alert=True)
    except: pass


@Bot.on_callback_query(filters.regex("^full"))
async def full_handler(client, query):
  """This Is Full Page Handler Of Callback Data"""
  if query.data in pagination:
    chapters, webs = pagination[query.data]
    added_item = []
    for data in list(reversed(chapters)):
      episode_num = get_episode_number(data['title'])
      if not episode_num in added_item:
        pictures = await webs.get_pictures(url=data['url'], data=data)
        if not pictures:
          await retry_on_flood(sts.edit)("No pictures found")
        
        task_id = await queue.put((data, pictures, query, None, webs), query.from_user.id)
        added_item.append(episode_num)
  else:
    try: await query.answer("This is an old button, please redo the search", show_alert=True)
    except: pass
      

@Bot.on_callback_query(filters.regex("^subs"))
async def subs_handler(client, query):
  """This Is Subscribe Handler Of Callback Data"""
  if query.data in subscribes:
    webs, data = subscribes[query.data]
    reply_markup = query.message.reply_markup
    button = reply_markup.inline_keyboard

    if get_subs(str(query.from_user.id), data['url']):
      delete_sub(str(query.from_user.id), data['url'])
      button[0] = [InlineKeyboardButton("📯 Subscribe 📯", callback_data=query.data)]
    else:
      add_sub(str(query.from_user.id), data['url'])
      button[0] = [InlineKeyboardButton("🔔 Unsubscribe 🔔", callback_data=query.data)]
    await retry_on_flood(query.edit_message_reply_markup)(InlineKeyboardMarkup(button))
  else:
    try: await query.answer("This is an old button, please redo the search", show_alert=True)
    except: pass


@Bot.on_callback_query(filters.regex("^pic"))
async def pic_handler(client, query):
  """This Is Pictures Handler Of Callback Data"""
  if query.data in chaptersList:
    webs, data = chaptersList[query.data]
    pictures = await webs.get_pictures(url=data['url'], data=data)
    if not pictures:
      return await query.answer("No pictures found", show_alert=True)

    sts = await retry_on_flood(query.message.reply_text
       )("<code>Adding...</code>")

    txt = f"Manga Name: {data['manga_title']}\nChapter: - {data['title']}"

    task_id = await queue.put((data, pictures, query, sts, webs), query.from_user.id)
    button = [[
        InlineKeyboardButton(" Cancel Your Tasks ",
                             callback_data=f"cl:{task_id}")
    ]]
    await retry_on_flood(sts.edit)(txt, reply_markup=InlineKeyboardMarkup(button))
  else:
    try: await query.answer("This is an old button, please redo the search", show_alert=True)
    except: pass


@Bot.on_callback_query(filters.regex("^cl"))
async def cl_handler(client, query):
  """This Is Cancel Handler Of Callback Data"""
  task_id = query.data.split(":")[-1]
  if await queue.delete_task(task_id):
    await retry_on_flood(query.message.edit_text)("<b>Task Cancelled !</b>")
  else:
    await retry_on_flood(query.answer)("Task Not Found", show_alert=True)


@Bot.on_callback_query(filters.regex("^bk"))
async def bk_handler(client, query):
  """This Is Back Handler Of Callback Data"""
  if query.data == "bk.p":
    try: await query.edit_message_media(InputMediaPhoto(random.choice(Vars.PICS)))
    except: pass

    await query.edit_message_reply_markup(plugins_list())
  elif query.data.startswith("bk.s"):
    data = query.data
    sf = query.data.split(".")[-1]
    webs = get_webs(sf)
    if webs:
      photo = random.choice(Vars.PICS)
      try:
        await query.edit_message_media(InputMediaPhoto(photo))
      except:
        pass

      reply_markup = query.message.reply_markup
      try:
        await query.message.edit_text("<i>Searching...</i>")
      except:
        pass
      if query.message.reply_to_message:
        results = await webs.search(query.message.reply_to_message.text)
        if results:
          button = []
          for result in results:
            c = f"chs|{data}{result['id']}" if "id" in result else f"chs|{data}{hash(result['url'])}"
            searchs[c] = (webs, result)
            button.append(
                [InlineKeyboardButton(result['title'], callback_data=c)])

          button.append(
              [InlineKeyboardButton("🪬 Back 🪬", callback_data="bk.p")])
          await retry_on_flood(query.edit_message_text
                               )("<b>Select Manga</b>",
                                 reply_markup=InlineKeyboardMarkup(button))
        else:
          await retry_on_flood(query.message.edit_text
                               )("<b>No results found</b>",
                                 reply_markup=reply_markup)


@Bot.on_callback_query(filters.regex("^plugin_"))
async def cb_handler(client, query):
  data = query.data
  data = data.split("_")[-1]
  photo = random.choice(Vars.PICS)
  for i in web_data.keys():
    if data == web_data[i].sf:
      try:
        await query.edit_message_media(InputMediaPhoto(photo))
      except:
        pass

      reply_markup = query.message.reply_markup
      try:
        await query.edit_message_text("<i>Searching...</i>")
      except:
        pass

      results = await web_data[i].search(query.message.reply_to_message.text)
      if results:
        button = []
        for result in results:
          c = f"chs|{data}{result['id']}" if "id" in result else f"chs|{data}{hash(result['url'])}"
          searchs[c] = (web_data[i], result)
          button.append(
              [InlineKeyboardButton(result['title'], callback_data=c)])

        button.append([InlineKeyboardButton("🔥 Back 🔥", callback_data="bk.p")])
        await retry_on_flood(query.edit_message_text
                             )("<b>Select Manga</b>",
                               reply_markup=InlineKeyboardMarkup(button))
      else:
        await retry_on_flood(query.edit_message_text
                             )("<b>No results found</b>",
                               reply_markup=reply_markup)

      try:
        await query.answer()
      except:
        pass
      finally:
        return

  try:
    await query.answer('This is an old button, please redo the search',
                       show_alert=True)
  except:
    pass
  finally:
    return


'''
@Bot.on_callback_query()
async def extra_handler(client, query):
  try: 
    await query.answer('This is an old button, please redo the search',
       show_alert=True)
  except:
    pass
'''

db_type = "uts"
name = Vars.DB_NAME

@Bot.on_callback_query(filters.regex("mus"))
async def main_user_panel(_, query):
  user_id = str(query.from_user.id)
  if not user_id in uts:
    uts[user_id] = {}
    sync(name, db_type)

  if not "setting" in uts[user_id]:
    uts[user_id]['setting'] = {}
    sync(name, db_type)

  thumb = uts[user_id]['setting'].get("thumb", None)
  if thumb:
    try: thumb = thumb if thumb.startswith("http") else "None"
    except: thumb = None

  txt = users_txt.format(
    id = user_id,
    file_name = uts[user_id]['setting'].get("file_name", "None"),
    caption = uts[user_id]['setting'].get("caption", "None"),
    thumb = thumb,
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
  await retry_on_flood(query.edit_message_text)(txt, reply_markup=InlineKeyboardMarkup(button))
  
  try: await query.answer()
  except: pass


@Bot.on_callback_query(filters.regex("^ufn"))
async def file_name_handler(_, query):
  user_id = str(query.from_user.id)
  if not user_id in uts:
    uts[user_id] = {}

    uts[user_id]['setting'] = {}

    sync(name, db_type)

  file_name = uts[user_id]['setting'].get("file_name", None)
  caption = uts[user_id]['setting'].get("caption", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  banner1 = uts[user_id]['setting'].get("banner1", None)
  banner2 = uts[user_id]['setting'].get("banner2", None)
  dump = uts[user_id]['setting'].get("dump", None)
  type = uts[user_id]['setting'].get("type", None)
  megre= uts[user_id]['setting'].get("megre", None)
  regex = uts[user_id]['setting'].get("regex", None)
  file_name_len = uts[user_id]['setting'].get("file_name_len", None)
  password = uts[user_id]['setting'].get("password", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  if thumb:
    thumb = "True" if not thumb.startswith("http") else thumb

  button = [
    [InlineKeyboardButton("📐 sᴇᴛ/ᴄʜᴀɴɢᴇ 📐", callback_data="ufn_change"), InlineKeyboardButton("🗑️ ᴅᴇʟᴇᴛᴇ 🗑️", callback_data="ufn_delete")],
    [InlineKeyboardButton("📐 sᴇᴛ/ᴄʜᴀɴɢᴇ ʟᴇɴ 📐", callback_data="ufn_len_change"), InlineKeyboardButton("🗑️ ᴅᴇʟᴇᴛᴇ ʟᴇɴ 🗑️", callback_data="ufn_len_delete")],
    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ 🔙", callback_data="mus")]
  ]
  if query.data == "ufn":
    txt = users_txt.format(
      id = user_id,
      file_name = file_name,
      caption = caption,
      thumb = thumb,
      banner1 = banner1,
      banner2 = banner2,
      dump = dump,
      type = type,
      megre= megre,
      regex = regex,
      len = file_name_len,
      password = password
    )
    await retry_on_flood(query.edit_message_text)(txt, reply_markup=InlineKeyboardMarkup(button))

  elif query.data == "ufn_change":
    sts = await query.message.reply("<b>📐 Send File Name 📐 \n<u><i>Params:</u></i>\n=><code>{manga_title}</code>: Manga Name \n=> <code>{chapter_num}</code>: Chapter Number</b>")
    try:
      call = await _.listen(user_id=int(user_id), timeout=60)

      uts[user_id]['setting']["file_name"] = call.text
      sync(name, db_type)

      txt = users_txt.format(
        id = user_id,
        file_name = call.text,
        caption = caption,
        thumb = thumb,
        banner1 = banner1,
        banner2 = banner2,
        dump = dump,
        type = type,
        megre= megre,
        regex = regex,
        len = file_name_len,
        password = password,
      )

      await retry_on_flood(query.edit_message_text)(txt, reply_markup=InlineKeyboardMarkup(button))
      await retry_on_flood(sts.delete)()
      await retry_on_flood(call.delete)()
    except asyncio.TimeoutError:
      await retry_on_flood(sts.edit)("📐 ᴛɪᴍᴇᴏᴜᴛ 📐")

  elif query.data == "ufn_delete":
    if file_name:
      uts[user_id]['setting']["file_name"] = None
      sync(name, db_type)

      txt = users_txt.format(
        id = user_id,
        file_name = "None",
        caption = caption,
        thumb = thumb,
        banner1 = banner1,
        banner2 = banner2,
        dump = dump,
        type = type,
        megre= megre,
        regex = regex,
        len = file_name_len,
        password = password,
      )
      await retry_on_flood(query.edit_message_text)(txt, reply_markup=InlineKeyboardMarkup(button))
    else:
      await retry_on_flood(query.answer)("📐 𝒀𝒐𝒖 𝒉𝒂𝒔 𝒏𝒐𝒕 𝑺𝒆𝒕 𝑰𝒕 ! 📐", show_alert=True)

  elif query.data == "ufn_len_change":
    sts = await query.message.reply("<b>📐 Send File Name Len 📐\n Example: 15, 20, 50</b>")
    try:
      call = await _.listen(int(user_id), timeout=60)
      try:
        len_ch = int(call.text)
        uts[user_id]['setting']["file_name_len"] = call.text
        sync(name, db_type)

        txt = users_txt.format(
          id = user_id,
          file_name = file_name,
          caption = caption,
          thumb = thumb,
          banner1 = banner1,
          banner2 = banner2,
          dump = dump,
          type = type,
          megre= megre,
          regex = regex,
          len = call.text,
          password = password,
        )

        await retry_on_flood(query.edit_message_text)(txt, reply_markup=InlineKeyboardMarkup(button))
        await retry_on_flood(sts.delete)()

      except ValueError:
        await retry_on_flood(sts.edit)("📐 ᴛʜɪs ɪs ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ɪɴᴛᴇɢᴇʀ 📐")

    except asyncio.TimeoutError:
      await retry_on_flood(sts.edit)("📐 ᴛɪᴍᴇᴏᴜᴛ 📐")

  elif query.data == "ufn_len_delete":
    if file_name_len:
      uts[user_id]['setting']["file_name_len"] = None
      sync(name, db_type)

      txt = users_txt.format(
        id = user_id,
        file_name = file_name,
        caption = caption,
        thumb = thumb,
        banner1 = banner1,
        banner2 = banner2,
        dump = dump,
        type = type,
        megre= megre,
        regex = regex,
        len = "None",
        password = password,
      )
      await retry_on_flood(query.edit_message_text)(txt, reply_markup=InlineKeyboardMarkup(button))
    else:
      await retry_on_flood(query.answer)("📐 𝒀𝒐𝒖 𝒉𝒂𝒔 𝒏𝒐𝒕 𝑺𝒆𝒕 𝑰𝒕 ! 📐", show_alert=True)
  
  try: await query.answer()
  except: pass


@Bot.on_callback_query(filters.regex("^ucp"))
async def caption_handler(_, query):
  user_id = str(query.from_user.id)
  if not user_id in uts:
    uts[user_id] = {}
    sync(name, db_type)

    uts[user_id]['setting'] = {}
    sync(name, db_type)

  file_name = uts[user_id]['setting'].get("file_name", None)
  caption = uts[user_id]['setting'].get("caption", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  banner1 = uts[user_id]['setting'].get("banner1", None)
  banner2 = uts[user_id]['setting'].get("banner2", None)
  dump = uts[user_id]['setting'].get("dump", None)
  type = uts[user_id]['setting'].get("type", None)
  megre= uts[user_id]['setting'].get("megre", None)
  regex = uts[user_id]['setting'].get("regex", None)
  file_name_len = uts[user_id]['setting'].get("file_name_len", None)
  password = uts[user_id]['setting'].get("password", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  if thumb:
    thumb = "True" if not thumb.startswith("http") else thumb

  button = [
    [InlineKeyboardButton("📐 sᴇᴛ/ᴄʜᴀɴɢᴇ 📐", callback_data="ucp_change"), InlineKeyboardButton("🗑️ ᴅᴇʟᴇᴛᴇ 🗑️", callback_data="ucp_delete")],
    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ 🔙", callback_data="mus")]
  ]

  if query.data == "ucp":
    await retry_on_flood(query.edit_message_reply_markup)(InlineKeyboardMarkup(button))

  elif query.data == "ucp_change":
    button = [
      [InlineKeyboardButton("📐 sᴇᴛ/ᴄʜᴀɴɢᴇ 📐", callback_data="ucp_change"), InlineKeyboardButton("🗑️ ᴅᴇʟᴇᴛᴇ 🗑️", callback_data="ucp_delete")],
      [InlineKeyboardButton("🔙 ʙᴀᴄᴋ 🔙", callback_data="mus")]
    ]

    sts = await query.message.reply("<b>📐 Send Caption 📐 \n<u>Note:</u> <blockquote>Use HTML Tags For Bold, Italic,etc</blockquote>\n<u>Params:</u>\n=><code>{manga_title}</code>: Manga Name \n=> <code>{chapter_num}</code>: Chapter Number\n<code>{file_name}</code>: File Name</b>")
    try:
      call = await _.listen(user_id=int(user_id), timeout=60)

      uts[user_id]['setting']["caption"] = call.text
      sync(name, db_type)

      txt = users_txt.format(
        id=user_id,
        file_name=file_name,
        caption=call.text,
        thumb=thumb,
        banner1=banner1,
        banner2=banner2,
        dump=dump,
        type=type,
        megre=megre,
        regex=regex,
        len=file_name_len,
        password=password,
      )

      if not thumb:
        try: await query.edit_message_media(InputMediaPhoto(random.choice(Vars.PICS)))
        except: pass

      await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))
      await retry_on_flood(sts.delete)()
      await retry_on_flood(call.delete)()

    except asyncio.TimeoutError:
      await retry_on_flood(sts.edit)("📐 ᴛɪᴍᴇᴏᴜᴛ 📐")

    except Exception as err:
      await retry_on_flood(sts.edit)(f"📐 {err} 📐")

  elif query.data == "ucp_delete":
    if caption:
      uts[user_id]['setting']["caption"] = None
      sync(name, db_type)

      txt = users_txt.format(
        id = user_id,
        file_name = file_name,
        caption = "None",
        thumb = thumb,
        banner1 = banner1,
        banner2 = banner2,
        dump = dump,
        type = type,
        megre= megre,
        regex = regex,
        len = file_name_len,
        password = password,
      )

      try: await query.edit_message_media(InputMediaPhoto(random.choice(Vars.PICS)))
      except: pass

      await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))
    else:
      await retry_on_flood(query.answer)("📐 𝒀𝒐𝒖 𝒉𝒂𝒔 𝒏𝒐𝒕 𝑺𝒆𝒕 𝑰𝒕 ! 📐", show_alert=True)
  
  try: await query.answer()
  except: pass


@Bot.on_callback_query(filters.regex("^uth"))
async def thumb_handler(_, query):
  user_id = str(query.from_user.id)
  if not user_id in uts:
    uts[user_id] = {}
    sync(name, db_type)

    uts[user_id]['setting'] = {}
    sync(name, db_type)

  file_name = uts[user_id]['setting'].get("file_name", None)
  caption = uts[user_id]['setting'].get("caption", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  banner1 = uts[user_id]['setting'].get("banner1", None)
  banner2 = uts[user_id]['setting'].get("banner2", None)
  dump = uts[user_id]['setting'].get("dump", None)
  type = uts[user_id]['setting'].get("type", None)
  megre= uts[user_id]['setting'].get("megre", None)
  regex = uts[user_id]['setting'].get("regex", None)
  file_name_len = uts[user_id]['setting'].get("file_name_len", None)
  password = uts[user_id]['setting'].get("password", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  if thumb:
    thumb = "True" if not thumb.startswith("http") else thumb

  button = [
    [InlineKeyboardButton("📐 sᴇᴛ/ᴄʜᴀɴɢᴇ 📐", callback_data="uth_change"), InlineKeyboardButton("🗑️ ᴅᴇʟᴇᴛᴇ 🗑️", callback_data="uth_delete")],
    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ 🔙", callback_data="mus")]
  ]
  if query.data == "uth":
    txt = users_txt.format(
      id = user_id,
      file_name = file_name,
      caption = caption,
      thumb = thumb,
      banner1 = banner1,
      banner2 = banner2,
      dump = dump,
      type = type,
      megre= megre,
      regex = regex,
      len = file_name_len,
      password = password,
    )
    if thumb:
      try: await query.edit_message_media(InputMediaPhoto(thumb))
      except: pass

    await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))

  elif query.data == "uth_change":
    button = [
      [InlineKeyboardButton("📐 sᴇᴛ/ᴄʜᴀɴɢᴇ 📐", callback_data="uth_change"), InlineKeyboardButton("🗑️ ᴅᴇʟᴇᴛᴇ 🗑️", callback_data="uth_delete")],
      [InlineKeyboardButton("🔙 ʙᴀᴄᴋ 🔙", callback_data="mus")]
    ]
    sts = await query.message.reply("<b>📐 Send Thumbnail 📐 \n<u>Note:</u> <blockquote>You Can Send Links or Images Docs.. </blockquote></b>")
    try:
      call = await _.listen(user_id=int(user_id), timeout=60)
      call_type = call.photo or call.document or None
      if call_type:
        call_type = call_type.file_id
        uts[user_id]['setting']["thumb"] = call_type
        sync(name, db_type)

      elif not call_type:
        call_type = call.text
        uts[user_id]['setting']["thumb"] = call_type
        sync(name, db_type)

      else:
        await retry_on_flood(sts.edit)("📐 ᴛʜɪs ɪs ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ᴛʜᴜᴍʙɴᴀɪʟ 📐")
        return

      thumb = "True" if not str(call_type).startswith("http") else call_type

      txt = users_txt.format(
        id = user_id,
        file_name = file_name,
        caption = caption,
        thumb = thumb,
        banner1 = banner1,
        banner2 = banner2,
        dump = dump,
        type = type,
        megre= megre,
        regex = regex,
        len = file_name_len,
        password = password,
      )
      if thumb:
        try: await query.edit_message_media(InputMediaPhoto(thumb))
        except: pass

      await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))
      await retry_on_flood(sts.delete)()
      await retry_on_flood(call.delete)()
    except asyncio.TimeoutError:
      await retry_on_flood(sts.edit)("📐 ᴛɪᴍᴇᴏᴜᴛ 📐")
    except Exception as err:
      await retry_on_flood(sts.edit)(f"📐 {err} 📐")

  elif query.data == "uth_delete":
    button = [
      [InlineKeyboardButton("📐 sᴇᴛ/ᴄʜᴀɴɢᴇ 📐", callback_data="uth_change"), InlineKeyboardButton("🗑️ ᴅᴇʟᴇᴛᴇ 🗑️", callback_data="uth_delete")],
      [InlineKeyboardButton("🔙 ʙᴀᴄᴋ 🔙", callback_data="mus")]
    ]
    if thumb:
      uts[user_id]['setting']["thumb"] = None
      sync(name, db_type)

      txt = users_txt.format(
        id=user_id,
        file_name=file_name,
        caption=caption,
        thumb="None",
        banner1=banner1,
        banner2=banner2,
        dump=dump,
        type=type,
        megre=megre,
        regex=regex,
        len=file_name_len,
        password=password,
      )
      try: await query.edit_message_media(InputMediaPhoto(random.choice(Vars.PICS)))
      except: pass
      await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))
    else:
      await retry_on_flood(query.answer)("📐 𝒀𝒐𝒖 𝒉𝒂𝒔 𝒏𝒐𝒕 𝑺𝒆𝒕 𝑰𝒕 ! 📐", show_alert=True)
  
  try: await query.answer()
  except: pass


@Bot.on_callback_query(filters.regex("^ubn"))
async def banner_handler(_, query):
  user_id = str(query.from_user.id)

  if not user_id in uts:
    uts[user_id] = {}
    sync(name, db_type)

    uts[user_id]['setting'] = {}
    sync(name, db_type)

  file_name = uts[user_id]['setting'].get("file_name", None)
  caption = uts[user_id]['setting'].get("caption", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  banner1 = uts[user_id]['setting'].get("banner1", None)
  banner2 = uts[user_id]['setting'].get("banner2", None)
  dump = uts[user_id]['setting'].get("dump", None)
  type = uts[user_id]['setting'].get("type", None)
  megre= uts[user_id]['setting'].get("megre", None)
  regex = uts[user_id]['setting'].get("regex", None)
  file_name_len = uts[user_id]['setting'].get("file_name_len", None)
  password = uts[user_id]['setting'].get("password", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  if thumb:
    thumb = "True" if not thumb.startswith("http") else thumb

  button = [
    [InlineKeyboardButton("📐 Set/Change 1 📐", callback_data="ubn_set1"), InlineKeyboardButton("🗑️ Delete 1 🗑️", callback_data="ubn_delete1")],
    [InlineKeyboardButton("📐 Set/Change 2 📐", callback_data="ubn_set2"), InlineKeyboardButton("🗑️ Delete 2 🗑️", callback_data="ubn_delete2")],
    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ 🔙", callback_data="mus")]
  ]
  if query.data == "ubn":
    await retry_on_flood(query.edit_message_reply_markup)(InlineKeyboardMarkup(button))

  if query.data.startswith("ubn_set"):
    sts = await query.message.reply("<b>📐 Send Banner 📐 \n<u>Note:</u> <blockquote>You Can Send Links or Images Docs.. </blockquote></b>")
    try:
      call = await _.listen(user_id=int(user_id), timeout=60)
      call_type = call.photo or call.document or None
      if call_type:
        banner = call.photo.file_id
      elif not call_type:
        banner = call.text
      else:
        await retry_on_flood(sts.edit)("📐 ᴛʜɪs ɪs ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ᴛʜᴜᴍʙɴᴀɪʟ 📐")
        return

      if query.data == "ubn_set1":
        uts[user_id]['setting']["banner1"] = banner
        sync(name, db_type)

        banner = banner if banner.startswith("http") else "True"
        txt = users_txt.format(
          id=user_id,
          file_name=file_name,
          caption=caption,
          thumb=thumb,
          banner1=banner,
          banner2=banner2,
          dump=dump,
          type=type,
          megre=megre,
          regex=regex,
          len=file_name_len,
          password=password,
        )

      elif query.data == "ubn_set2":
        uts[user_id]['setting']["banner2"] = banner
        sync(name, db_type)

        banner = banner if banner.startswith("http") else "True"
        txt = users_txt.format(
          id=user_id,
          file_name=file_name,
          caption=caption,
          thumb=thumb,
          banner1=banner1,
          banner2=banner,
          dump=dump,
          type=type,
          megre=megre,
          regex=regex,
          len=file_name_len,
          password=password,
        )
        if not thumb:
          try: await query.edit_message_media(InputMediaPhoto(random.choice(Vars.PICS)))
          except: pass

        await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))
    except asyncio.TimeoutError:
      await retry_on_flood(sts.edit)("📐 ᴛɪᴍᴇᴏᴜᴛ 📐")
    except Exception as err:
      await retry_on_flood(sts.edit)(f"📐 {err} 📐")

  elif query.data == "ubn_delete1":
    if banner1:
        uts[user_id]['setting']["banner1"] = None
        sync(name, db_type)

        txt = users_txt.format(
          id=user_id,
          file_name=file_name,
          caption=caption,
          thumb=thumb,
          banner1="None",
          banner2=banner2,
          dump=dump,
          type=type,
          megre=megre,
          regex=regex,
          len=file_name_len,
          password=password,
        )
        if not thumb:
          try: await query.edit_message_media(InputMediaPhoto(random.choice(Vars.PICS)))
          except: pass

        await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))
    else:
      await retry_on_flood(query.answer)("📐 𝒀𝒐𝒖 𝒉𝒂𝒔 𝒏𝒐𝒕 𝑺𝒆𝒕 𝑰𝒕 ! 📐", show_alert=True)

  elif query.data == "ubn_delete2":
    if banner2:
      uts[user_id]['setting']["banner2"] = None
      sync(name, db_type)

      txt = users_txt.format(
        id=user_id,
        file_name=file_name,
        caption=caption,
        thumb=thumb,
        banner1=banner1,
        banner2="None",
        dump=dump,
        type=type,
        megre=megre,
        regex=regex,
        len=file_name_len,
        password=password,
      )
      if not thumb:
        try: await query.edit_message_media(InputMediaPhoto(random.choice(Vars.PICS)))
        except: pass

      await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))
    else:
      await retry_on_flood(query.answer)("📐 𝒀𝒐𝒖 𝒉𝒂𝒔 𝒏𝒐𝒕 𝑺𝒆𝒕 𝑰𝒕 ! 📐", show_alert=True)
  
  try: await query.answer()
  except: pass

@Bot.on_callback_query(filters.regex("^udc"))
async def dump_handler(_, query):
  user_id = str(query.from_user.id)
  if not user_id in uts:
    uts[user_id] = {}
    sync(name, db_type)

    uts[user_id]['setting'] = {}
    sync(name, db_type)

  file_name = uts[user_id]['setting'].get("file_name", None)
  caption = uts[user_id]['setting'].get("caption", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  banner1 = uts[user_id]['setting'].get("banner1", None)
  banner2 = uts[user_id]['setting'].get("banner2", None)
  dump = uts[user_id]['setting'].get("dump", None)
  type = uts[user_id]['setting'].get("type", None)
  megre= uts[user_id]['setting'].get("megre", None)
  regex = uts[user_id]['setting'].get("regex", None)
  file_name_len = uts[user_id]['setting'].get("file_name_len", None)
  password = uts[user_id]['setting'].get("password", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  if thumb:
    thumb = "True" if not thumb.startswith("http") else thumb

  button = [
    [InlineKeyboardButton("📐 sᴇᴛ/ᴄʜᴀɴɢᴇ 📐", callback_data="udc_change"), InlineKeyboardButton("🗑️ ᴅᴇʟᴇᴛᴇ 🗑️", callback_data="udc_delete")],
    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ 🔙", callback_data="mus")]
  ]
  if query.data == "udc":
    await retry_on_flood(query.edit_message_reply_markup)(InlineKeyboardMarkup(button))
  elif query.data == "udc_change":
    sts = await query.message.reply("<b>📐 Send Dump Channel 📐 \n<u>Note:</u> <blockquote>You Can Send Username(without @) or Channel Id or Forward Message from Channel.. </blockquote></b>")
    try:
      call = await _.listen(user_id=int(user_id), timeout=60)
      if call.text:
        dump = call.text
      elif call.forward_from_chat:
        dump = call.forward_from_chat.id

      uts[user_id]['setting']["dump"] = dump
      sync(name, db_type)

      txt = users_txt.format(
          id=user_id,
          file_name=file_name,
          caption=caption,
          thumb=thumb,
          banner1=banner1,
          banner2=banner2,
          dump=dump,
          type=type,
          megre=megre,
          regex=regex,
          len=file_name_len,
          password=password,
      )
      if not thumb:
        try: await query.edit_message_media(InputMediaPhoto(random.choice(Vars.PICS)))
        except: pass

      await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))
      await retry_on_flood(sts.delete)()
      await retry_on_flood(call.delete)()
    except asyncio.TimeoutError:
      await retry_on_flood(sts.edit)("📐 ᴛɪᴍᴇᴏᴜᴛ 📐")
    except Exception as err:
      await retry_on_flood(sts.edit)(f"📐 {err} 📐")
    
  try: await query.answer()
  except: pass

@Bot.on_callback_query(filters.regex("^u_file_type"))
async def type_handler(_, query):
  user_id = str(query.from_user.id)
  if not user_id in uts:
    uts[user_id] = {}
    sync(name, db_type)

    uts[user_id]['setting'] = {}
    sync(name, db_type)

  file_name = uts[user_id]['setting'].get("file_name", None)
  caption = uts[user_id]['setting'].get("caption", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  banner1 = uts[user_id]['setting'].get("banner1", None)
  banner2 = uts[user_id]['setting'].get("banner2", None)
  dump = uts[user_id]['setting'].get("dump", None)
  type = uts[user_id]['setting'].get("type", None)
  megre= uts[user_id]['setting'].get("megre", None)
  regex = uts[user_id]['setting'].get("regex", None)
  file_name_len = uts[user_id]['setting'].get("file_name_len", None)
  password = uts[user_id]['setting'].get("password", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  if thumb:
    thumb = "True" if not thumb.startswith("http") else thumb

  if not "type" in uts[user_id]['setting']:
    uts[user_id]['setting']["type"] = []
    sync(name, db_type)

  type = uts[user_id].get("setting", {}).get("type", [])

  button = [[]]
  if "PDF" in type:
    button[0].append(InlineKeyboardButton("📙 PDF 📙", callback_data="u_file_type_pdf"))
  else:
    button[0].append(InlineKeyboardButton("❗PDF ❗", callback_data="u_file_type_pdf"))
  if "CBZ" in type:
    button[0].append(InlineKeyboardButton("📂 CBZ 📂", callback_data="u_file_type_cbz"))
  else:
    button[0].append(InlineKeyboardButton("❗CBZ ❗", callback_data="u_file_type_cbz"))

  button.append([InlineKeyboardButton("🔙 ʙᴀᴄᴋ 🔙", callback_data="mus")])

  if query.data == "u_file_type":
    await retry_on_flood(query.edit_message_reply_markup)(InlineKeyboardMarkup(button))

  elif query.data == "u_file_type_pdf":
    if "PDF" in type:
      uts[user_id]['setting']["type"].remove("PDF")
      sync(name, db_type)

      button[0][0] = InlineKeyboardButton("❗PDF ❗", callback_data="u_file_type_pdf")

    else:
      uts[user_id]['setting']["type"].append("PDF")
      sync(name, db_type)

      button[0][0] = InlineKeyboardButton("📙 PDF 📙", callback_data="u_file_type_pdf")

    type = uts[user_id].get("setting", {}).get("type", "None")
    txt = users_txt.format(
      id=user_id,
      file_name=file_name,
      caption=caption,
      thumb=thumb,
      banner1=banner1,
      banner2=banner2,
      dump=dump,
      type=type,
      megre=megre,
      regex=regex,
      len=file_name_len,
      password=password,
    )
    if not thumb:
      try: await query.edit_message_media(InputMediaPhoto(random.choice(Vars.PICS)))
      except: pass

    await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))

  elif query.data == "u_file_type_cbz":
    if "CBZ" in type:
      uts[user_id]['setting']["type"].remove("CBZ")
      sync(name, db_type)

      button[0][1] = InlineKeyboardButton("❗CBZ ❗", callback_data="u_file_type_cbz")

    else:
      uts[user_id]['setting']["type"].append("CBZ")
      sync(name, db_type)

      button[0][1] = InlineKeyboardButton("📂 CBZ 📂", callback_data="u_file_type_cbz")

    type = uts[user_id].get("setting", {}).get("type", "None")
    txt = users_txt.format(
      id=user_id,
      file_name=file_name,
      caption=caption,
      thumb=thumb,
      banner1=banner1,
      banner2=banner2,
      dump=dump,
      type=type,
      megre=megre,
      regex=regex,
      len=file_name_len,
      password=password,
    )
    if not thumb:
      try: await query.edit_message_media(InputMediaPhoto(random.choice(Vars.PICS)))
      except: pass

    await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))
  
  try: await query.answer()
  except: pass

@Bot.on_callback_query(filters.regex("^umegre"))
async def megre_handler(_, query):
  user_id = str(query.from_user.id)
  if not user_id in uts:
    uts[user_id] = {}
    sync(name, db_type)
    
    uts[user_id]['setting'] = {}
    sync(name, db_type)
  
  file_name = uts[user_id]['setting'].get("file_name", None)
  caption = uts[user_id]['setting'].get("caption", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  banner1 = uts[user_id]['setting'].get("banner1", None)
  banner2 = uts[user_id]['setting'].get("banner2", None)
  dump = uts[user_id]['setting'].get("dump", None)
  type = uts[user_id]['setting'].get("type", None)
  megre= uts[user_id]['setting'].get("megre", None)
  regex = uts[user_id]['setting'].get("regex", None)
  file_name_len = uts[user_id]['setting'].get("file_name_len", None)
  password = uts[user_id]['setting'].get("password", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  if thumb:
    thumb = "True" if not thumb.startswith("http") else thumb
  button = [
    [InlineKeyboardButton("📐 sᴇᴛ/ᴄʜᴀɴɢᴇ 📐", callback_data="umegre_change"), InlineKeyboardButton("🗑️ ᴅᴇʟᴇᴛᴇ 🗑️", callback_data="umegre_delete")],
    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ 🔙", callback_data="mus")]
  ]
  if query.data == "umegre":
    await retry_on_flood(query.edit_message_reply_markup)(InlineKeyboardMarkup(button))
    
  elif query.data == "umegre_change":
    sts = await query.message.reply("<b>📐 Send Megre Size 📐 \n<u>Note:</u> <blockquote>It's Number For Megre. i.e 2, 3 ,4 ,5,etc </blockquote></b>")
    try:
      call = await _.listen(user_id=int(user_id), timeout=60)
      call_int = int(call.text)
      
      uts[user_id]['setting']["megre"] = call.text
      sync(name, db_type)
      txt = users_txt.format(
        id=user_id,
        file_name=file_name,
        caption=caption,
        thumb=thumb,
        banner1=banner1,
        banner2=banner2,
        dump=dump,
        type=type,
        megre=call.text,
        regex=regex,
        len=file_name_len,
        password=password,
      )
      if not thumb:
        try: await query.edit_message_media(InputMediaPhoto(random.choice(Vars.PICS)))
        except: pass
      
      await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))
      await retry_on_flood(sts.delete)()
      await retry_on_flood(call.delete)()
    except ValueError:
      await retry_on_flood(sts.edit)("📐 ᴛʜɪs ɪs ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ɪɴᴛᴇɢᴇʀ 📐")
    except asyncio.TimeoutError:
      await retry_on_flood(sts.edit)("📐 ᴛɪᴍᴇᴏᴜᴛ 📐")
    except Exception as err:
      await retry_on_flood(sts.edit)(f"📐 {err} 📐")
      
  elif query.data == "umegre_delete":
    if megre:
      uts[user_id]['setting']["megre"] = None
      sync(name, db_type)
      
      txt = users_txt.format(
        id=user_id,
        file_name=file_name,
        caption=caption,
        thumb=thumb,
        banner1=banner1,
        banner2=banner2,
        dump=dump,
        type=type,
        megre="None",
        regex=regex,
        len=file_name_len,
        password=password,
      )
      
      if not thumb:
        try: await query.edit_message_media(InputMediaPhoto(random.choice(Vars.PICS)))
        except: pass
      
      await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))
    else:
      await retry_on_flood(query.answer)("📐 𝒀𝒐𝒖 𝒉𝒂𝒔 𝒏𝒐𝒕 𝑺𝒆𝒕 𝑰𝒕 ! 📐", show_alert=True)
  
  try: await query.answer()
  except: pass

@Bot.on_callback_query(filters.regex("^upass"))
async def password_handler(_, query):
  user_id = str(query.from_user.id)
  if not user_id in uts:
    uts[user_id] = {}
    sync(name, db_type)
    uts[user_id]['setting'] = {}
    sync(name, db_type)
  
  file_name = uts[user_id]['setting'].get("file_name", None)
  caption = uts[user_id]['setting'].get("caption", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  banner1 = uts[user_id]['setting'].get("banner1", None)
  banner2 = uts[user_id]['setting'].get("banner2", None)
  dump = uts[user_id]['setting'].get("dump", None)
  type = uts[user_id]['setting'].get("type", None)
  megre= uts[user_id]['setting'].get("megre", None)
  regex = uts[user_id]['setting'].get("regex", None)
  file_name_len = uts[user_id]['setting'].get("file_name_len", None)
  password = uts[user_id]['setting'].get("password", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  if thumb:
    thumb = "True" if not thumb.startswith("http") else thumb
  
  button = [
    [InlineKeyboardButton("📐 sᴇᴛ/ᴄʜᴀɴɢᴇ 📐", callback_data="upass_change"), InlineKeyboardButton("🗑️ ᴅᴇʟᴇᴛᴇ 🗑️", callback_data="upass_delete")],
    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ 🔙", callback_data="mus")]
  ]
  
  if query.data == "upass":
    await retry_on_flood(query.edit_message_reply_markup)(InlineKeyboardMarkup(button))
  elif query.data == "upass_change":
    sts = await query.message.reply("<b>📐 Send Password 📐 \n<u>Note:</u> <blockquote>It's Password For PDF.</blockquote></b>")
    try:
      call = await _.listen(user_id=int(user_id), timeout=60)
      
      uts[user_id]['setting']["password"] = call.text
      sync(name, db_type)
      
      txt = users_txt.format(
        id=user_id,
        file_name=file_name,
        caption=caption,
        thumb=thumb,
        banner1=banner1,
        banner2=banner2,
        dump=dump,
        type=type,
        megre=megre,
        regex=regex,
        len=file_name_len,
        password=call.text,
      )
      if not thumb:
        try: await query.edit_message_media(InputMediaPhoto(random.choice(Vars.PICS)))
        except: pass
      
      await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))
      await retry_on_flood(sts.delete)()
      await retry_on_flood(call.delete)()
    except asyncio.TimeoutError:
      await retry_on_flood(sts.edit)("📐 ᴛɪᴍᴇᴏᴜᴛ 📐")
    except Exception as err:
      await retry_on_flood(sts.edit)(f"📐 {err} 📐")
      
  elif query.data == "upass_delete":
    if password:
      uts[user_id]['setting']["password"] = None
      sync(name, db_type)
      
      txt = users_txt.format(
        id=user_id,
        file_name=file_name,
        caption=caption,
        thumb=thumb,
        banner1=banner1,
        banner2=banner2,
        dump=dump,
        type=type,
        megre=megre,
        regex=regex,
        len=file_name_len,
        password="None",
      )
      if not thumb:
        try: await query.edit_message_media(InputMediaPhoto(random.choice(Vars.PICS)))
        except: pass
      
      await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))
    else:
      await retry_on_flood(query.answer)("📐 𝒀𝒐𝒖 𝒉𝒂𝒔 𝒏𝒐𝒕 𝑺𝒆𝒕 𝑰𝒕 ! 📐", show_alert=True)
  
  try: await query.answer()
  except: pass

@Bot.on_callback_query(filters.regex("^uregex"))
async def regex_handler(_, query):
  user_id = str(query.from_user.id)
  if not user_id in uts:
    uts[user_id] = {}
    sync(name, db_type)
    
    uts[user_id]['setting'] = {}
    sync(name, db_type)
  
  file_name = uts[user_id]['setting'].get("file_name", None)
  caption = uts[user_id]['setting'].get("caption", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  banner1 = uts[user_id]['setting'].get("banner1", None)
  banner2 = uts[user_id]['setting'].get("banner2", None)
  dump = uts[user_id]['setting'].get("dump", None)
  type = uts[user_id]['setting'].get("type", None)
  megre= uts[user_id]['setting'].get("megre", None)
  regex = uts[user_id]['setting'].get("regex", None)
  file_name_len = uts[user_id]['setting'].get("file_name_len", None)
  password = uts[user_id]['setting'].get("password", None)
  thumb = uts[user_id]['setting'].get("thumb", None)
  if thumb:
    thumb = "True" if not thumb.startswith("http") else thumb

  button = [
    [InlineKeyboardButton(i, callback_data=f"uregex_set_{i}") for i in range(1, 5)],
    [InlineKeyboardButton("🗑️ ᴅᴇʟᴇᴛᴇ 🗑️", callback_data="uregex_delete")],
    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ 🔙", callback_data="mus")]
  ]
  if query.data == "uregex":
    await retry_on_flood(query.edit_message_reply_markup)(InlineKeyboardMarkup(button))
  elif query.data.startswith("uregex_set"):
    regex = query.data.split("_")[-1]
    
    uts[user_id]['setting'][f"regex"] = regex
    sync(name, db_type)
    
    txt = users_txt.format(
        id=user_id,
        file_name=file_name,
        caption=caption,
        thumb=thumb,
        banner1=banner1,
        banner2=banner2,
        dump=dump,
        type=type,
        megre=megre,
        regex=regex,
        len=file_name_len,
        password=password,
    )
    if not thumb:
      try: await query.edit_message_media(InputMediaPhoto(random.choice(Vars.PICS)))
      except: pass
    
    await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))
  elif query.data == "uregex_delete":
    if regex:
      uts[user_id]['setting']["regex"] = None
      sync(name, db_type)
      
      txt = users_txt.format(
        id=user_id,
        file_name=file_name,
        caption=caption,
        thumb=thumb,
        banner1=banner1,
        banner2=banner2,
        dump=dump,
        type=type,
        megre=megre,
        regex="None",
        len=file_name_len,
        password=password,
      )
      if not thumb:
        try: await query.edit_message_media(InputMediaPhoto(random.choice(Vars.PICS)))
        except: pass
      
      await retry_on_flood(query.edit_message_caption)(txt, reply_markup=InlineKeyboardMarkup(button))
    else:
      await retry_on_flood(query.answer)("📐 𝒀𝒐𝒖 𝒉𝒂𝒔 𝒏𝒐𝒕 𝑺𝒆𝒕 𝑰𝒕 ! 📐", show_alert=True)
