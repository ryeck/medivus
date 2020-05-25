import discord
import asyncio

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

async def paginate(ctx, embeds):
  i = 0
  msg = await ctx.send(embed=embeds[i])

  f_e = "\u23ee"
  l_e = "\u25c0"
  r_e = "\u25b6"
  e_e = "\u23ed"

  await msg.add_reaction(f_e)
  await msg.add_reaction(l_e)
  await msg.add_reaction(r_e)
  await msg.add_reaction(e_e)

  def check(reaction, user):
    return reaction.message.id == msg.id and user != ctx.bot.user
  
  while True:
    try:
      reaction, user = await ctx.bot.wait_for("reaction_add", check=check, timeout=30)
      emoji = reaction.emoji
    except asyncio.TimeoutError:
      emoji = None
      user = None
    else:
      if emoji == f_e:
        i = 0
        await msg.remove_reaction(f_e, user)
        await msg.edit(embed=embeds[i])
      elif emoji == l_e:
        if i > 0:
          i -= 1
        await msg.remove_reaction(l_e, user)
        await msg.edit(embed=embeds[i])
      elif emoji == r_e:
        if i < len(embeds) - 1:
          i += 1
        await msg.remove_reaction(r_e, user)
        await msg.edit(embed=embeds[i])
      elif emoji == e_e:
        i = len(embeds) - 1
        await msg.remove_reaction(e_e, user)
        await msg.edit(embed=embeds[i])

