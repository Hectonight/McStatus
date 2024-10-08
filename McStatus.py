import os
import asyncio
import discord
import pickle
from discord.ext import commands
from mcstatus import MinecraftServer
from dotenv import load_dotenv

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='%', help_command=None, intents=intents)

load_dotenv()
token = os.getenv('TOKEN')


def save_obj(obj, name):
    with open('obj/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


try:
    bot_perms = load_obj('bot_perms')
except:
    bot_perms = {}

try:
    mc_servers = load_obj('mc_servers')
except:
    mc_servers = {}

try:
    toggle_nick = load_obj('toggle_nick')
except:
    toggle_nick = {}

server_not_set = 'A Minecraft Server Has not Been Set'
no_perm = 'Insufficient Permissions'

halp = discord.Embed(title='Help Commands', color=discord.Color.blue())
halp.add_field(name="`%help`", value="Show a list of all commands", inline=False)
halp.add_field(name="`%status [address=DefaultServerAddress] [port=DefaultServerPort]`",
               value="Displays the status of the default server or a specified server", inline=False)
halp.add_field(name="`%playersOnline [address=DefaultServerAddress] [port=DefaultServerPort]`",
               value="Lists the players online on the default server or a specified server", inline=False)
halp.add_field(name="`%setServer <address> [port=25565]`", value="Sets the default server", inline=False)
halp.add_field(name="`%removeServer`", value="Sets the default server to none", inline=False)
halp.add_field(name="`%toggleNick`", value="Toggles whether the nick of the bot will become online and offline",
                inline=False)
halp.add_field(name="`%listBotPerms`", value="Lists roles that have permissions to use the bot", inline=False)
halp.add_field(name="`%addBotPerms <role>`",
                value="Allows a role the permissions to use the admin commands of the bot", inline=False)
halp.add_field(name="`%removeBotPerms <role>`",
                value="Removes the permission for a role to use the admin commands of the bot ", inline=False)

# status of mc server in nickname and activity
async def status_update():
    while True:
        await asyncio.sleep(3)
        for guild in bot.guilds:
            if guild.id not in toggle_nick:
                toggle_nick[guild.id] = False
            if guild.id in mc_servers and toggle_nick[guild.id]:
                try:
                    mc_servers[guild.id][2].status()
                    await guild.me.edit(nick='ONLINE')
                except:
                    await guild.me.edit(nick='OFFLINE')

        save_obj(bot_perms, 'bot_perms')
        save_obj(mc_servers, 'mc_servers')
        save_obj(toggle_nick, 'toggle_nick')


# on event bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    for guild in bot.guilds:
        await guild.me.edit(nick=None)
    await bot.change_presence(activity=discord.Game('%help'))
    await status_update()


# the help command
@bot.command(pass_context=True, aliases=['Help'])
async def help(ctx):
    await ctx.channel.send(embed=halp)


# status of the mc server
@bot.command(pass_context=True, aliases=['Status'])
async def status(ctx, address=None, port=None):
    if ctx.guild.id in mc_servers and address is None and port is None:
        try:
            status_server = mc_servers[ctx.guild.id][2].status()
            await ctx.channel.send('`{}` is online with {}/{} players'.format(mc_servers[ctx.guild.id][0],
                                                status_server.players.online, status_server.players.max))
        except:
            await ctx.channel.send('`{}` is offline'.format(mc_servers[ctx.guild.id][0]))
    elif address is None and port is None:
        await ctx.channel.send(server_not_set)
    else:
        server = MinecraftServer.lookup('{}:{}'.format(address, port))
        try:
            status_server = server.status()
            await ctx.channel.send('`{}` is online with {}/{} players'.format(address, status_server.players.online,
                                                                                       status_server.players.max))
        except:
            await ctx.channel.send('`{}` is offline'.format(address))



# set the default minecraft server for the guild
@bot.command(pass_context=True, aliases=['setserver', 'SetServer', 'Setserver'])
async def setServer(ctx, address, port='25565'):
    if ctx.guild.id not in bot_perms:
        bot_perms[ctx.guild.id] = []
    if ctx.author.guild_permissions.administrator \
            or not set([role.id for role in ctx.author.roles]).isdisjoint(set(bot_perms[ctx.guild.id])):

        server = MinecraftServer.lookup('{}:{}'.format(address, port))
        mc_servers[ctx.guild.id] = [address, port, server]
        await ctx.channel.send('Server set to `{}`'.format(address))
    else:
        await ctx.channel.send(no_perm)


# remove the default minecraft server for the guild
@bot.command(pass_context=True, aliases=['removeserver', 'RemoveServer', 'Removeserver'])
async def removeServer(ctx):
    if ctx.author.guild_permissions.administrator \
            or not set([role.id for role in ctx.author.roles]).isdisjoint(set(bot_perms[ctx.guild.id])):

        if ctx.guild.id in mc_servers:
            await ctx.guild.me.edit(nick=None)
            del mc_servers[ctx.guild.id]
            await ctx.channel.send('Server set to None')
        else:
            await ctx.channel.send(server_not_set)
    else:
        await ctx.channel.send(no_perm)


# add a role that can use the bot
@bot.command(pass_context=True, aliases=['AddBotPerms', 'addbotperms'])
async def addBotPerms(ctx, role: discord.Role):
    if ctx.guild.id not in bot_perms:
        bot_perms[ctx.guild.id] = []
    if ctx.author.guild_permissions.administrator and role.id not in bot_perms[ctx.guild.id]:
        if ctx.guild.id not in bot_perms:
            bot_perms[ctx.guild.id] = []
        bot_perms[ctx.guild.id].append(role.id)
        await ctx.channel.send('Role `{}` now has bot permissions'.format(role.name))
    elif not ctx.author.guild_permissions.administrator:
        await ctx.channel.send(no_perm)
    else:
        await ctx.channel.send('Role `{}` already has bot permissions'.format(role.name))


# remove a roll that can use the bot
@bot.command(pass_context=True, aliases=['removebotperms', 'RemoveBotPerms', 'Removebotperms'])
async def removeBotPerms(ctx, role: discord.Role):
    if ctx.guild.id not in bot_perms:
        bot_perms[ctx.guild.id] = []
    if ctx.author.guild_permissions.administrator and role.id in bot_perms[ctx.guild.id]:
        bot_perms[ctx.guild.id].remove(role.id)
        await ctx.channel.send('Role `{}` no longer has bot permissions'.format(role.name))
    elif not ctx.author.guild_permissions.administrator:
        await ctx.channel.send(no_perm)
    else:
        await ctx.channel.send('Role `{}` does not have bot permissions'.format(role.name))


# if a role gets deleted, delete from the list of roles that can use the bot
@bot.event
async def on_guild_role_delete(ctx, role):
    if role.id in bot_perms[ctx.guild.id]:
        bot_perms[ctx.guild.id].remove(role.id)


# list the roles
@bot.command(pass_context=True, aliases=['ListBotPerms', 'listbotperms', 'Listbotperms'])
async def listBotPerms(ctx):
    if ctx.guild.id not in bot_perms:
        bot_perms[ctx.guild.id] = []
    if bot_perms[ctx.guild.id]:
        lRBP = discord.Embed(title='Roles With Bot Permissions', color=0x000000)
        role_str = ''
        for role in bot_perms[ctx.guild.id]:
            role_str += '\n' + ctx.guild.get_role(role).name
        lRBP.add_field(name='Roles:', value=role_str)
        await ctx.channel.send(embed=lRBP)
    else:
        await ctx.channel.send('This server does not have any roles with bot permissions')


# list the players online up to 30 players
@bot.command(pass_context=True, aliases=['PlayersOnline', 'playersonline', 'Playersonline'])
async def playersOnline(ctx, address=None, port=None):
    if ctx.guild.id in mc_servers and address is None and port is None:
        try:
            server_status = mc_servers[ctx.guild.id][2].status()
        except:
            await ctx.channel.send(f'{mc_servers[ctx.guild.id][0]} is offline')
            return
        if server_status.players.online > 0:
            players_online = discord.Embed(title='Players Online', color=discord.Color.blue())
            players_str = ''
            online_players = [user['name'] for user in server_status.raw['players']['sample']]
            if len(online_players) > 30:
                online_players = online_players[:29]
            for player in online_players:
                players_str += '\n' + player
            players_online.add_field(name='{}/{} Players on {}'.format(server_status.players.online,
                                    server_status.players.max, mc_servers[ctx.guild.id][0]), value=players_str)
            await ctx.channel.send(embed=players_online)
        else:
            await ctx.channel.send(f'There is nobody online on {mc_servers[ctx.guild.id][0]}')
    elif address is None and port is None:
        await ctx.channel.send(server_not_set)
    else:
        server = MinecraftServer.lookup('{}:{}'.format(address, port))
        try:
           server_status = server.status()
        except:
            await ctx.channel.send('`{}` is offline'.format(address))
            return
        if server_status.players.online > 0:
            players_online = discord.Embed(title='Players Online', color=discord.Color.blue())
            players_str = ''
            online_players = [user['name'] for user in server_status.raw['players']['sample']]
            if len(online_players) > 30:
                online_players = online_players[:29]
            for player in online_players:
                players_str += '\n' + player
            players_online.add_field(name='{}/{} Players on {}'.format(server_status.players.online,
                                    server_status.players.max, mc_servers[ctx.guild.id][0]), value=players_str)
            await ctx.channel.send(embed=players_online)
        else:
            await ctx.channel.send(f'There is nobody online on {mc_servers[ctx.guild.id][0]}')


# toggles the nick function for the guild
@bot.command(pass_context=True, aliases=['togglenick', 'ToggleNick', 'Togglenick'])
async def toggleNick(ctx):
    if ctx.author.guild_permissions.administrator \
            or not set([role.id for role in ctx.author.roles]).isdisjoint(set(bot_perms[ctx.guild.id])):
        if ctx.guild.id not in toggle_nick:
            toggle_nick[ctx.guild.id] = True
        elif toggle_nick[ctx.guild.id]:
            toggle_nick[ctx.guild.id] = False
        else:
            toggle_nick[ctx.guild.id] = True
        await ctx.channel.send('Set Toggle Nick to {}'.format(toggle_nick[ctx.guild.id]))

    else:
        await ctx.channel.send(no_perm)


bot.run(token)
