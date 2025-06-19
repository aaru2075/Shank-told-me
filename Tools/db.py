from pymongo import MongoClient
from bot import Vars

client = MongoClient(Vars.DB_URL)
db = client[Vars.DB_NAME]

subs = db["subs"]
users = db["users"]

uts = users.find_one({"_id": Vars.DB_NAME})
dts = subs.find_one({"_id": "data"})

if not dts:
  dts = {'_id': "data"}
  subs.insert_one(dts)

if not uts:
  uts = {'_id': Vars.DB_NAME}
  users.insert_one(uts)


def sync(name="data", type="dts"):
  if type == "dts":
    subs.replace_one({'_id': name}, dts)
  elif type == "uts":
    users.replace_one({'_id': name}, uts)


def add_sub(user_id, manga_url: str, chapter=None):
  user_id = str(user_id)
  if not manga_url in dts:
    dts[manga_url] = {}
    sync()
  
  if not "users" in dts[manga_url]:
    dts[manga_url]["users"] = []
    sync()
  
  if not user_id in dts[manga_url]["users"]:
    dts[manga_url]["users"].append(user_id)
    sync()
  
  if not user_id in uts:
    uts[user_id] = {}
    sync(Vars.DB_NAME, 'uts')
  
  if not "subs" in uts[user_id]:
    uts[user_id]["subs"] = []
    sync(Vars.DB_NAME, 'uts')
  
  if not manga_url in uts[user_id]["subs"]:
    uts[user_id]["subs"].append(manga_url)
    sync(Vars.DB_NAME, 'uts')
  
  sync()
  sync(Vars.DB_NAME, 'uts')

def get_subs(user_id, manga_url: str = None):
  user_id = str(user_id)
  if not user_id in uts:
    uts[user_id] = {}
    sync(Vars.DB_NAME, 'uts')
    
  if not "subs" in uts[user_id]:
    uts[user_id]["subs"] = []
    sync(Vars.DB_NAME, 'uts')
  
  if manga_url:
    if user_id in uts:
      if manga_url in uts[user_id]["subs"]:
        return True
      else:
        return None
    
  if user_id in uts:
    return uts[user_id]["subs"]

def delete_sub(user_id, manga_url: str):
  user_id = str(user_id)
  if manga_url in dts and user_id in dts[manga_url]["users"]:
    dts[manga_url]["users"].remove(user_id)
    sync()
  
  if user_id in uts and manga_url in uts[user_id]["subs"]:
    uts[user_id]["subs"].remove(manga_url)
    sync(Vars.DB_NAME, 'uts')
  
  sync()
  sync(Vars.DB_NAME, 'uts')
