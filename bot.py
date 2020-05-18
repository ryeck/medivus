#!/usr/bin/env python3
import os
import discord
import psycopg2
from discord.ext import commands, tasks
from sites import medivia


host = "localhost"
database = "db"
user = "postgres"
password = "postgres"

conn = psycopg2.connect(host=host, database=database, user=user, password=password)
cur = conn.cursor()
cur.execute("SELECT version()")
print(cur.fetchone())


TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix=".m ")

@bot.event
async def on_ready():
  scan_characters.start()
  print(f"{bot.user.name} has connected.")

@bot.command(hidden=True)
async def load(ctx, extension):
  bot.load_extension(f"cogs.{extension}")

@bot.command()
async def unload(ctx, extension):
  bot.unload_extension(f"cogs.{extension}")

@bot.command()
async def reload(ctx, extension):
  bot.unload_extension(f"cogs.{extension}")
  bot.load_extension(f"cogs.{extension}")

@tasks.loop(seconds=60)
async def scan_characters():
  chars = medivia.get_all_online()
  for c in chars:
    print(c.name)

for f in os.listdir("./cogs"):
  if f.endswith(".py"):
    bot.load_extension(f"cogs.{f[:-3]}")

bot.run(TOKEN)
