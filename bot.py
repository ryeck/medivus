#!/usr/bin/env python3

import os
import discord
from discord.ext import commands, tasks

TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix=[".m ", "!m "])

@bot.event
async def on_ready():
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

for f in os.listdir("./cogs"):
  if f.endswith(".py"):
    bot.load_extension(f"cogs.{f[:-3]}")

bot.run(TOKEN)
