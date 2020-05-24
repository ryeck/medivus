#!/usr/bin/env python3

import os
import discord
import db
from discord.ext import commands, tasks
from sites import medivia

TOKEN = os.getenv("DISCORD_TOKEN")

channels = {}
online = {}

bot = commands.Bot(command_prefix=".m ")

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


@tasks.loop(seconds=30)
async def check_lists():
  global online
  global channels
  new_online = await medivia.get_all_online()
  for g in bot.guilds:
    hunted = db.get_hunted(g.id) 
    for c in hunted:
      name = c[0].lower()
      if len(online) > 0 and name not in online:
        if name in new_online:
          if g.id in channels:
            await channels[g.id].send(f"{name} is online!")
  online = await medivia.get_all_online()
  print("check lists")

for f in os.listdir("./cogs"):
  if f.endswith(".py"):
    bot.load_extension(f"cogs.{f[:-3]}")

bot.run(TOKEN)
