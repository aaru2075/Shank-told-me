from pyrogram import Client

from time import time 
from loguru import logger

class Vars:
  API_ID = "20373005"
  API_HASH = "e9bfc473049cbaeff901ca6892d559c7"
  
  BOT_TOKEN = "8012002306:AAHjjsEjx0KJPflbSALKkQFT7WHrKYiUGYc"
  plugins = dict(
    root="TG",
    #include=["TG.users"]
  )
  
  LOG_CHANNEL = None
  UPDATE_CHANNEL = None
  DB_URL = "mongodb+srv://narutouzumaki22551:narutouzumaki22551@cluster0.econe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
  
  PORT = 8080
  ADMINS = [1880221341, 1002160667730, 5543390445, 5164955785, 5891177226, 7827086839, 6975428639] # eg: [83528911,836289,9362891]
  
  IS_PRIVATE = None #True Or None  Bot is for admins only
  CONSTANT_DUMP_CHANNEL = None
  
  DB_NAME = "manhwadb"
  PING = time()
  PICS = (
    "https://ik.imagekit.io/jbxs2z512/hd-anime-prr1y1k5gqxfcgpv.jpg?updatedAt=1748487947183",
    "https://ik.imagekit.io/jbxs2z512/naruto_GxcPgSeOy.jpg?updatedAt=1748486799631",
    "https://ik.imagekit.io/jbxs2z512/dazai-osamu-sunset-rooftop-anime-wallpaper-cover.jpg?updatedAt=1748488276069",
    "https://ik.imagekit.io/jbxs2z512/thumb-1920-736461.png?updatedAt=1748488419323",
    "https://ik.imagekit.io/jbxs2z512/116847-3840x2160-desktop-4k-bleach-background-photo.jpg?updatedAt=1748488510841",
    "https://ik.imagekit.io/jbxs2z512/images_q=tbn:ANd9GcSjvt9DcrLXzGYEwwOpxwCSFXTfKEhXhVB-Zg&s?updatedAt=1748488611032",
    "https://ik.imagekit.io/jbxs2z512/thumb-1920-777955.jpg?updatedAt=1748488978230",
    "https://ik.imagekit.io/jbxs2z512/thumb-1920-1361035.jpeg?updatedAt=1748488911202",
    "https://ik.imagekit.io/jbxs2z512/akali-wallpaper-960x540_43.jpg?updatedAt=1748489275125",
    "https://ik.imagekit.io/jbxs2z512/robin-honkai-star-rail-497@1@o?updatedAt=1748490140360",
    "https://ik.imagekit.io/jbxs2z512/wallpapersden.com_tian-guan-ci-fu_1920x1080.jpg?updatedAt=17484902552770000",
    "https://ik.imagekit.io/jbxs2z512/1129176.jpg?updatedAt=1748491905419",
    "https://ik.imagekit.io/jbxs2z512/wp14288215.jpg?updatedAt=1748492348766",
    "https://ik.imagekit.io/jbxs2z512/8k-anime-girl-and-flowers-t4bj6u55nmgfdrhe.jpg?updatedAt=1748493169919",
    "https://ik.imagekit.io/jbxs2z512/anime_Fuji_Choko_princess_anime_girls_Sakura_Sakura_Woman_in_Red_mask_palace-52030.png!d?updatedAt=1748493259665",
    "https://ik.imagekit.io/jbxs2z512/1187037bb1d8aaf14a631f7b813296f1.jpg?updatedAt=1748493396756",
    "https://ik.imagekit.io/jbxs2z512/yor_forger_by_senku_07_dgifqh7-fullview.jpg_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9ODAzIiwicGF0aCI6IlwvZlwvNDAxZDdlYTYtOGEyZi00ZTFiLTkxYTAtNjA3YmRlYTgzZmE4XC9kZ2lmcWg3LWNlMjY3Mzc2LWQ4NWYtNGMzZS1iNWY1LWU0OTZhYWM3ZmUyNC5wbmciLCJ3aWR0aCI6Ijw9MTI4MCJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.FVwtt0HGKv6UQqWHkEbxmE1qkI5CFNNS5SzAYj4EVUs?updatedAt=1748493490929",
    "https://ik.imagekit.io/jbxs2z512/attack-on-titan-mikasa-cover-image-ybt96t1e1041qdt3.jpg?updatedAt=1748493720903",
    "https://ik.imagekit.io/jbxs2z512/tsunade-at-her-desk-bakoh4jeg42sjn3c.jpg?updatedAt=1748493962363",
    "https://ik.imagekit.io/jbxs2z512/9aab3a2fba4bd0117b990e4ca453cb61.jpg?updatedAt=1748494616359",
    "https://ik.imagekit.io/jbxs2z512/3bf8ed2f8f1acacd5451444ba6e7842a.jpg?updatedAt=1748494817874",
    "https://ik.imagekit.io/jbxs2z512/5f10d5eeab91c46b2b442d170998a10e.jpg?updatedAt=1748494936535",
    "https://ik.imagekit.io/jbxs2z512/18a02ef5ab71d0df7a1b4f854c214dfb.jpg?updatedAt=1748495170887",
    "https://ik.imagekit.io/jbxs2z512/3860e6e91d9cc88b4579d096e4edaaf3.jpg?updatedAt=1748495479043",
    "https://ik.imagekit.io/jbxs2z512/d367f6d6d22f4ead7c359e9f091db94e.jpg?updatedAt=1748495852427",
    "https://ik.imagekit.io/jbxs2z512/9c989e113f6ba997e417a436cde4a387.jpg?updatedAt=1748496068439",
    "https://ik.imagekit.io/jbxs2z512/8750ba474fb938b94d6b1a4093e5c104.jpg?updatedAt=1748496295001",
    "https://ik.imagekit.io/jbxs2z512/2e6937e9d7c6fb4c179c3e92684bb7f4.jpg?updatedAt=1748496479835",
    "https://ik.imagekit.io/jbxs2z512/99ce9434aed7b5785cae1d784aee3d72.jpg?updatedAt=1748497104463",
    "https://ik.imagekit.io/jbxs2z512/stycc.jpg?updatedAt=1748497475612",
    "https://ik.imagekit.io/jbxs2z512/9bba360ebd71d6086e19d5729b80a5b8.jpg?updatedAt=1748497751053",
    "https://ik.imagekit.io/jbxs2z512/94f23c5b9055846db8047565bbb8cd70.jpg?updatedAt=1748497975473",
    "https://ik.imagekit.io/jbxs2z512/eec7ff7238553179fb4236da3537d19d.jpg?updatedAt=1748498058373",
    "https://ik.imagekit.io/jbxs2z512/Fight-Break-Sphere.png?updatedAt=1750042299023",
    "https://ik.imagekit.io/jbxs2z512/doupocangqiong-medusa-queen-hd-wallpaper-preview.jpg?updatedAt=1750042397343",
    "https://ik.imagekit.io/jbxs2z512/wp5890248.jpg?updatedAt=1750042498187",
    "https://ik.imagekit.io/jbxs2z512/sacffc_uu-T1F5AC?updatedAt=1750042873876",
    "https://ik.imagekit.io/jbxs2z512/1345216.jpeg?updatedAt=1750042982858",
    "https://ik.imagekit.io/jbxs2z512/shanks-divine-departure-attack-in-one-piece-sn.jpg?updatedAt=1750043121252",
    "https://ik.imagekit.io/jbxs2z512/1a74aff1d81a1af5f3e25b9b30282e06.jpg?updatedAt=1750043251516",
    "https://ik.imagekit.io/jbxs2z512/a7241b95829a685f99a900e509e39591.jpg?updatedAt=1750043398842",
  )


Bot = Client(
    "ManhwaBot",
    api_id=Vars.API_ID,
    api_hash=Vars.API_HASH,
    bot_token=Vars.BOT_TOKEN,
    plugins=Vars.plugins,
    workers=50,
)
