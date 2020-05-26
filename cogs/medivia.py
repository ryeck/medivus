import asyncio
import typing
import discord
import operator
import db
import helper
import datetime
from discord.ext import commands, tasks
from sites import medivia

class Medivia(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.channels = {}
    self.online = {}
    self.get_channels.start()
    self.check_lists.start()

  # task loops
  @tasks.loop(seconds=30)
  async def get_channels(self):
    for g in self.bot.guilds:
      found = False
      for c in g.text_channels:
        if c.name == "medivia":
          self.channels[g.id] = c
          found = True
      if not found:
        chan = await g.create_text_channel("medivia")
        self.channels[g.id] = chan

  @tasks.loop(seconds=30)
  async def check_lists(self):
    new_online = await medivia.get_all_online()
    for g in self.bot.guilds:
      await self.scan(g.id, db.get_hunted(g.id), new_online, "Hunted List", helper.red("Logged On"))
      await self.scan(g.id, db.get_team(g.id), new_online, "Team List", helper.green("Logged On"))
      await self.scan(g.id, db.get_noob(g.id), new_online, "Noob List", helper.orange("Logged On"))
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    for k in new_online.keys():
      if len(self.online) > 0 and k not in self.online:
        db.add_login(k, dt)
    for k in self.online.keys():
      if len(new_online) > 0 and k not in new_online:
        db.add_logoff(k, dt)
    self.online = await medivia.get_all_online()
    print("check lists")

  async def scan(self, gid, chars, new_online, title, desc):
    logon = []
    for c in chars:
      name = c[0].lower()
      if len(self.online) > 0 and name not in self.online:
        if name in new_online:
          logon.append(name) 
    if len(logon) > 0:
      if gid in self.channels:
        e = helper.get_embed(title)
        e.description = desc 
        for nm in logon:
          char = new_online[nm]
          url = medivia.get_char_url(nm)
          e.add_field(name="name:", value=f"[{char.name}]({url})")
          e.add_field(name="profession:", value=char.profession)
          e.add_field(name="level:", value=char.level)
        await self.channels[gid].send(embed=e)


  @commands.command()
  async def hunted(self, ctx, option : str = None, *, name : str = None):
    title = "Hunted List"
    if option is not None:
      option = option.lower()
    if option is None:
      await self.send_list(ctx, db.get_hunted(ctx.guild.id), title)
    elif option in [ "add", "update" ]:
      await self.send_add_response(ctx, db.add_hunted(ctx.guild.id, name), name, title)
    elif option in [ "remove", "rm", "del", "delete" ]:
      await self.send_remove_response(ctx, db.remove_hunted(ctx.guild.id, name), name, title)
    elif option == "online":
      await self.send_online_list(ctx, db.get_hunted(ctx.guild.id), title, helper.red("Online"))
    else:
      await self.send_error(ctx, option, title)

  @commands.command()
  async def noob(self, ctx, option : str = None, *, name : str = None):
    title = "Noob List"
    if option is not None:
      option = option.lower()
    if option is None:
      await self.send_list(ctx, db.get_noob(ctx.guild.id), title)
    elif option in [ "add", "update" ]:
      await self.send_add_response(ctx, db.add_noob(ctx.guild.id, name), name, title)
    elif option in [ "remove", "rm", "del", "delete" ]:
      await self.send_remove_response(ctx, db.remove_noob(ctx.guild.id, name), name, title)
    elif option == "online":
      await self.send_online_list(ctx, db.get_noob(ctx.guild.id), title, helper.orange("Online"))
    else:
      await self.send_error(ctx, option, title)

  @commands.command()
  async def team(self, ctx, option : str = None, *, name : str = None):
    title = "Team List"
    if option is not None:
      option = option.lower()
    if option is None:
      await self.send_list(ctx, db.get_team(ctx.guild.id), title)
    elif option in [ "add", "update" ]:
      await self.send_add_response(ctx, db.add_team(ctx.guild.id, name), name, title)
    elif option in [ "remove", "rm", "del", "delete" ]:
      await self.send_remove_response(ctx, db.remove_team(ctx.guild.id, name), name, title)
    elif option == "online":
      await self.send_online_list(ctx, db.get_team(ctx.guild.id), title, helper.team("Online"))
    else:
      await self.send_error(ctx, option, title)

  async def send_online_list(self, ctx, rows, title, desc):
    l = len(rows)
    if l == 0:
      e = helper.get_embed(title)
      e.description = helper.orange("Failed")
      e.add_field(name="message:", value="No entries found.")
      await ctx.send(embed=e)
    else:
      embeds = []
      name = ""
      prof = ""
      lvl = ""
      i = 0
      for r in rows:
        nm = r[0]
        if nm in self.online:
          c = self.online[nm]
          name += f"[{c.name}]({c.url})\n"
          prof += c.profession + "\n"
          lvl += c.level + "\n"
          if i != 0 and i % 10 == 0 or i == l - 1:
            e = helper.get_embed(title)
            e.description = desc 
            e.add_field(name="name:", value=name)  
            e.add_field(name="profession:", value=prof)  
            e.add_field(name="level:", value=lvl)  
            embeds.append(e)
            name = ""
            prof = ""
            lvl = ""
          i += 1
    await helper.paginate(ctx, embeds) 


  
  async def send_list(self, ctx, rows, title):
    l = len(rows)
    if l == 0:
      e = helper.get_embed(title)
      e.description = helper.orange("Failed")
      e.add_field(name="message:", value="No entries found.")
      await ctx.send(embed=e)
    else:
      name = ""
      embeds = []
      i = 0
      for r in rows:
        nm = r[0]
        url = medivia.get_char_url(nm)
        name += f"[{nm}]({url})\n"
        if (i != 0 and i % 10 == 0) or i == l - 1:
          e = helper.get_embed(title)
          e.add_field(name="name:", value=name)  
          embeds.append(e)
          name = ""
        i += 1
      await helper.paginate(ctx, embeds) 

  async def send_error(self, ctx, option, title):
    e = helper.get_embed(title)
    e.description = helper.red("Error")
    e.add_field(name="message:", value=f"'{option}' is not a valid command.")
    await ctx.send(embed=e)

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
      await helper.paginate(ctx, embeds) 


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
