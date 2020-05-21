import discord

def green(txt):
  return f"```css\n{txt}```"

def orange(txt):
  return f"```fix\n{txt}```"

def blue(txt):
  return f"```css\n.{txt}```"

def red(txt):
  return f"```diff\n-{txt}```"

def bold(txt):
  return f"**{txt}**"

def get_embed(title):
  e = discord.Embed(title=title, color=discord.Color.blue())
  e.set_footer(text="Signed, King Medivus")
  return e
