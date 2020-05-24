import asyncio
import typing
import discord
import operator
import db
import helper
from discord.ext import commands
from sites import medivia

class Medivia(commands.Cog):

  def __init__(self, bot):
    self.bot = bot


  @commands.command()
  async def hunted(self, ctx, option : str = None, *, name : str = None):
    if option is not None:
      option = option.lower()
    if option is None:
      chars = db.get_hunted(ctx.guild.id)
      for c in chars:
        print(c[0])
    elif option == "add":
      await self.send_add_response(ctx, db.add_hunted(ctx.guild.id, name), name, "Hunted List")
    elif option == "remove":
      await self.send_remove_response(ctx, db.remove_hunted(ctx.guild.id, name), name, "Hunted List")

  async def send_add_response(self, ctx, added, name, title):
    e = helper.get_embed(title)
    if added is None:
      msg = f"Unexpected error adding {name}."
      desc = helper.red("Error")
    elif added:
      msg = f"{name} added."
      desc = helper.green("Success")
    elif not added:
      msg = f"{name} already added."
      desc = helper.orange("Failed")
    e.add_field(name="message:", value=msg)
    e.description = desc
    await ctx.send(embed=e)

  async def send_remove_response(self, ctx, removed, name, title):
    e = helper.get_embed(title)
    if removed is None:
      msg = f"Unexpected error removing {name}."
      desc = helper.red("Error")
    elif removed:
      msg = f"{name} removed."
      desc = helper.green("Success")
    elif not removed:
      msg = f"{name} already removed."
      desc = helper.orange("Failed")
    e.add_field(name="message:", value=msg)
    e.description = desc
    await ctx.send(embed=e)


  @commands.command()
  async def online(self, ctx, world : str = None):
    if world == None:
      worlds = await medivia.get_player_count()
      e = helper.get_embed("Online")
      for k, v in worlds.items():
        e.add_field(name=k.lower() + ":", value=v)
      await ctx.send(embed=e)
    else:
      embeds = []
      chars = await medivia.get_online(world)
      name = ""
      prof = ""
      lvl = ""
      i = 0
      for c in sorted(chars.values(), key=lambda o: int(o.level), reverse=True):
        name += f"[{c.name}]({c.url})\n"
        prof += c.profession + "\n"
        lvl += c.level + "\n"
        if i != 0 and i % 10 == 0:
          e = helper.get_embed("Online")
          e.description = world.title()
          e.add_field(name="name:", value=name)  
          e.add_field(name="profession:", value=prof)  
          e.add_field(name="level:", value=lvl)  
          embeds.append(e)
          name = ""
          prof = ""
          lvl = ""
        i += 1

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
        return reaction.message.id == msg.id and user != self.bot.user
      
      while True:
        try:
          reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=30)
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



  @commands.command(aliases=["char", "player", "profile"])
  async def character(self, ctx, *, name):
    c = await medivia.get_character(name)
    if c.errMsg is not None:
      e = helper.get_embed(name) 
      e.url = c.url
      e.add_field(name="error:", value=c.errMsg)
      await ctx.send(embed=e)
    else:
      o = helper.get_embed(c.name)
      o.url = c.url
      o.set_thumbnail(url=c.avatar)
      status = helper.green(c.status) if c.status == "Online" else helper.orange(c.status)
      o.add_field(name="status:", value=status, inline=False)
      o.add_field(name="level:", value=helper.bold(c.level))
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
      
      d = helper.get_embed(c.name)
      d.url = c.url
      d.description = "Death list"
      for key, val in c.deaths.items():
        d.add_field(name=key, value=val, inline=False)

      k = helper.get_embed(c.name)
      k.url = c.url
      k.description = "Kill list"
      for key, val in c.kills.items():
        k.add_field(name=key, value=val, inline=False)

      t = helper.get_embed(c.name)
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

      def check(reaction, user):
        return reaction.message.id == msg.id and user != self.bot.user
      
      while True:
        try:
          reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=30)
          emoji = reaction.emoji
        except asyncio.TimeoutError:
          emoji = None
          user = None
        else:
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
  bot.add_cog(Medivia(bot))
