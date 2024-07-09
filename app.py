import copy
import random
import time

import requests
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

HEROES_API_URL = 'https://api.opendota.com/api/heroes'
HEROES_CACHE_TIME_S = 60 * 60


heroes_cache = []
last_fetched_time_s = 0

def get_heroes_from_url():
    global heroes_cache
    global last_fetched_time_s
    cur_time = time.time()
    if cur_time - last_fetched_time_s > HEROES_CACHE_TIME_S:
        heroes_json = requests.get(HEROES_API_URL).json()
        heroes_cache = copy.deepcopy(heroes_json)
        last_fetched_time_s = cur_time
    else:
        heroes_json = copy.deepcopy(heroes_cache)
    return [hero['localized_name'] for hero in heroes_json]


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.post("/get_heroes")
async def get_heroes(request: Request):
    body = await request.json()

    heroes = sorted(get_heroes_from_url())
    bans = {hero.strip().replace(' ', '').lower() for hero in body['bans'].split('\n')}
    allowed_heroes = [hero for hero in heroes if hero.strip().replace(' ', '').lower() not in bans]
    selected_heroes = random.sample(allowed_heroes, k=int(body['n_players']))
    return {
        'selected_heroes': selected_heroes,
        'n_omitted_heroes': len(heroes) - len(allowed_heroes),
    }
