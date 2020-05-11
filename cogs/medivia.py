import asyncio
import typing
import discord
from discord.ext import commands
from sites import medivia

def green(str):
  return f"```css\n{str}```"

def orange(str):
  return f"```fix\n{str}```"

def blue(str):
  return f"```css\n.{str}```"

def red(str):
  return f"```diff\n-{str}```"

def bold(str):
  return f"**{str}**"

def get_embed(title):
  e = discord.Embed(title=title, color=discord.Color.blue())
  e.set_footer(text="Signed, King Medivus")
  return e

class Site(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def online(self, ctx, world : str = None):
    if world == None:
      worlds = medivia.get_player_count()
      e = get_embed("Online")
      for k, v in worlds.items():
        e.add_field(name=k.lower() + ":", value=v)
      await ctx.send(embed=e)
    else:
      embeds = []
      chars = medivia.get_online(world)
      chars.sort(key=lambda c: int(c.level), reverse=True)
      name = ""
      prof = ""
      lvl = ""
      for i in range(len(chars) - 1):
        c = chars[i]
        name += f"[{c.name}]({c.url})\n"
        prof += c.profession + "\n"
        lvl += c.level + "\n"
        if i != 0 and i % 10 == 0:
          e = get_embed("Online")
          e.description = world.title()
          e.add_field(name="name:", value=name)  
          e.add_field(name="profession:", value=prof)  
          e.add_field(name="level:", value=lvl)  
          embeds.append(e)
          name = ""
          prof = ""
          lvl = ""

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
      
      while True:
        try:
          reaction, user = await self.bot.wait_for("reaction_add", timeout=30)
          emoji = reaction.emoji
        except asyncio.TimeoutError:
          emoji = None
          user = None
        if user != self.bot.user:
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



  @commands.command(aliases=["char", "player", "profile"])
  async def character(self, ctx, *, name):
    c = medivia.get_character(name)
    if c.errMsg is not None:
      e = get_embed(name) 
      e.url = c.url
      e.add_field(name="error:", value=c.errMsg)
      await ctx.send(embed=e)
    else:
      o = get_embed(c.name)
      o.url = c.url
      o.set_thumbnail(url=c.avatar)
      status = green(c.status) if c.status == "Online" else orange(c.status)
      o.add_field(name="status:", value=status, inline=False)
      o.add_field(name="level:", value=bold(c.level))
      o.add_field(name="profession:", value=c.profession)
      o.add_field(name="sex:", value=c.sex)
      o.add_field(name="world:", value=c.world)
      o.add_field(name="residence:", value=c.residence)
      o.add_field(name="last login:", value=c.last_login)
      if c.guild is not None:
        o.add_field(name="guild:", value=f"[{c.guild}]({c.guild_url})")
      if c.house is not None:
        o.add_field(name="house:", value=f"[{c.house}]({c.house_url})")
      if c.banishment is not None:
        o.add_field(name="banishment:", value=c.banishment) 
      o.add_field(name="account status:", value=c.account_status)
      
      d = get_embed(c.name)
      d.url = c.url
      d.description = "Death list"
      for key, val in c.deaths.items():
        d.add_field(name=key, value=val, inline=False)

      k = get_embed(c.name)
      k.url = c.url
      k.description = "Kill list"
      for key, val in c.kills.items():
        k.add_field(name=key, value=val, inline=False)

      t = get_embed(c.name)
      t.url = c.url
      t.description = "Task list"
      for key, val in c.tasks.items():
        t.add_field(name=key, value=val)

      msg = await ctx.send(embed=o)

      o_e = "🇴"
      d_e = "🇩"
      k_e = "🇰"
      t_e = "🇹"

      await msg.add_reaction(o_e)
      await msg.add_reaction(d_e)
      await msg.add_reaction(k_e)
      await msg.add_reaction(t_e)

      while True:
        try:
          reaction, user = await self.bot.wait_for("reaction_add", timeout=30)
          emoji = reaction.emoji
        except asyncio.TimeoutError:
          emoji = None
          user = None
        if user != self.bot.user:
          if emoji == o_e:
            await msg.remove_reaction(o_e, user)
            await msg.edit(embed=o)
          elif emoji == d_e:
            await msg.remove_reaction(d_e, user)
            await msg.edit(embed=d)
          elif emoji == k_e:
            await msg.remove_reaction(k_e, user)
            await msg.edit(embed=k)
          elif emoji == t_e:
            await msg.remove_reaction(t_e, user)
            await msg.edit(embed=t)

def setup(bot):
  bot.add_cog(Site(bot))
