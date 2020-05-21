#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

url = "https://medivia.online"

class Character:

  def __init__(self):
    self.errMsg = None
    self.url = None
    self.name = None
    self.position = None
    self.sex = None
    self.profession = None
    self.level = None
    self.world = None
    self.residence = None
    self.last_login = None
    self.status = None
    self.account_status = None
    self.house = None
    self.house_url = None
    self.guild = None
    self.guild_url = None
    self.banishment = None
    self.avatar = None
    self.deaths = {}
    self.kills = {}
    self.tasks = {}

def get_character(name):
  c = Character()
  name = str(name).replace(" ", "%20")
  c.url = f"{url}/community/character/{name}"
  r = requests.get(c.url)
  s = BeautifulSoup(r.text, "html.parser")

  errMsg = "Sorry, but such character does not exist." 
  if errMsg in r.text:
    c.errMsg = errMsg
    return c 

  try:
    for d in s.find_all("div", class_="med-width-50"):
      txt = d.text.strip()
      fn = lambda : d.find_next("div").text
      if txt == "name:":
        c.name = fn()
      elif txt == "position:":
        c.position = fn()
      elif txt == "sex:":
        c.sex = fn()
      elif txt == "profession:":
        c.profession = fn()
      elif txt == "level:":
        c.level = fn()
      elif txt == "world:":
        c.world = fn()
      elif txt == "residence:":
        c.residence = fn()
      elif txt == "last login:":
        c.last_login = fn()
      elif txt == "banishment:":
        c.text = fn()
      elif txt == "status:":
        c.status = fn()
      elif txt == "account status:":
        c.account_status = fn()
      elif txt == "house:":
        c.house_url = url + d.find_next("a").get("href")
        c.house = fn()
      elif txt == "guild:":
        c.guild_url = url + d.find_next("a").get("href")
        c.guild = fn()
    
    for d in s.find_all("div", class_="med-news-image"):
      style = d.find_next("div").get("style")
      c.avatar = "https://medivia.online" + style[23:-3].strip()
      
    c.deaths = _get_dict(s, "Death list")
    c.kills = _get_dict(s, "Kill list")
    c.tasks = _get_dict(s, "Task list")

  except:
    c.errMsg = "Unexpected error retrieving charactar profile."

  return c

def _get_dict(s, title):
  dic = {}
  for divs in s.find_all("div", string=title):
    for d in divs.find_next("div").find_all("div", class_="med-width-25"):
      k = d.text.strip()
      v = d.find_next("div").text.strip()
      dic[k] = v
  return dic

def get_player_count(): 
  r = requests.get(url)
  s = BeautifulSoup(r.text, "html.parser") 
  online = {} 
  for d in s.find_all("div", class_="med-text-center"):
    txt = d.text.strip()
    if ":" in txt:
      k, v = txt.split(":", 1) 
      online[k] = v
  return online 

def get_online(world):
  r = requests.get(f"{url}/community/online/{world}")
  s = BeautifulSoup(r.text, "html.parser")
  chars = {}
  for li in s.find_all("ul")[1].find_all("li"):
    c = Character()
    div = li.find_next("div")
    c.last_login = div.text
    div = div.find_next("div")
    c.name = div.text
    div = div.find_next("div")
    c.profession = div.text
    div = div.find_next("div")
    c.level = div.text
    name = str(c.name).replace(" ", "%20")
    c.url = f"{url}/community/character/{name}"
    chars[c.name.lower()] = c
  chars.pop("name", None)
  return chars

def get_all_online():
  chars = get_online("Legacy")
  chars.update(get_online("Pendulum"))
  chars.update(get_online("Destiny"))
  chars.update(get_online("Prophecy"))
  chars.update(get_online("Unity"))
  return chars

if __name__ == "__main__":
  chars = get_online("pendulum")
  for c in chars.values():
    print(c.level)
