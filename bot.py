#!/usr/bin/env python3

import os
import discord
import db
from discord.ext import commands, tasks
from sites import medivia

TOKEN = os.getenv("DISCORD_TOKEN")

channels = {}
online = []

bot = commands.Bot(command_prefix=".m ")

@bot.event
async def on_ready():
  #scan_characters.start()
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

@tasks.loop(seconds=60)
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


@tasks.loop(seconds=30)
async def check_lists():
  global online
  global channels
  new_online = medivia.get_all_online() 
  for g in bot.guilds:
    for c in db.get_hunted(g.id):
      name = c[0].lower()
      print(name)
      if len(online) > 0 and not any(o.name.lower() == name for o in online):
        if any(o.name.lower() == name for o in new_online):
          if g.id in channels:
            await channels[g.id].send(f"{name} is online!")
  print("bye")
  online = medivia.get_all_online()


for f in os.listdir("./cogs"):
  if f.endswith(".py"):
    bot.load_extension(f"cogs.{f[:-3]}")

bot.run(TOKEN)
