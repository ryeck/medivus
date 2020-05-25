#!/usr/bin/env python3

import os
import discord
import db
import datetime
from discord.ext import commands, tasks
from sites import medivia

TOKEN = os.getenv("DISCORD_TOKEN")

channels = {}
online = {}

bot = commands.Bot(command_prefix=[".m ", "!m "])

@bot.event
async def on_ready():
  get_channels.start()
  check_lists.start()
  print(f"{bot.user.name} has connected.")

@bot.command(hidden=True)
async def load(ctx, extension):
  bot.load_extension(f"cogs.{extension}")

@bot.command(hidden=True)
async def unload(ctx, extension):
  bot.unload_extension(f"cogs.{extension}")

@bot.command(hidden=True)
async def reload(ctx, extension):
  bot.unload_extension(f"cogs.{extension}")
  bot.load_extension(f"cogs.{extension}")


# task loops

@tasks.loop(minutes=5)
async def get_channels():
  global channels
  for g in bot.guilds:
    found = False
    for c in g.text_channels:
      if c.name == "medivia":
        channels[g.id] = c
        found = True
    if not found:
      chan = await g.create_text_channel("medivia")
      channels[g.id] = chan


@tasks.loop(seconds=60)
async def check_lists():
  global online
  new_online = await medivia.get_all_online()
  for g in bot.guilds:
    await scan(g.id, db.get_hunted(g.id), new_online, "Hunted List")
    await scan(g.id, db.get_team(g.id), new_online, "Team List")
    await scan(g.id, db.get_noob(g.id), new_online, "Noob List")
  dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
  for k in new_online.keys():
    if len(online) > 0 and k not in online:
      db.add_login(k, dt)
  for k in online.keys():
    if len(new_online) > 0 and k not in new_online:
      db.add_logoff(k, dt)
  online = await medivia.get_all_online()
  print("check lists")

async def scan(gid, chars, new_online, title):
  global online
  global channels
  for c in chars:
    name = c[0].lower()
    if len(online) > 0 and name not in online:
      if name in new_online:
        if gid in channels:
          await channels[gid].send(f"{name} is online!")


for f in os.listdir("./cogs"):
  if f.endswith(".py"):
    bot.load_extension(f"cogs.{f[:-3]}")

bot.run(TOKEN)
