import asyncio
import discord
from discord.ext import commands
from mcstatus import MinecraftServer

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='%', help_command=None, intents=intents)

bot_permissions = {}
mc_servers = {}

server_not_set = 'A Minecraft Server Has not Been Set'
no_perm = 'Insufficient Permissions'


# status of mc server in nickname and activity
async def status_update():
    while True:
        await asyncio.sleep(3)
        for guild in bot.guilds:
            if guild in mc_servers:
                try:
                    mc_servers[guild][2].status()
                    await guild.me.edit(nick='ONLINE')
                except:
                    await guild.me.edit(nick='OFFLINE')


# on event bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    for guild in bot.guilds:
        await guild.me.edit(nick=None)
    await bot.change_presence(activity=discord.Game('%help'))
    await status_update()


# the help command
@bot.command()
async def help(ctx):
    halp = discord.Embed(title='Help Commands', color=discord.Color.blue())
    halp.add_field(name="%help`", value="Show a list of all commands", inline=False)
    halp.add_field(name="`%serverStatus <address> [port=25565]`", value="", inline=False)
    halp.add_field(name="`%status`", value="Displays the status of the default server", inline=False)
    halp.add_field(name="`%setDefaultServer <address> [port=25565]`", value="Sets the default server", inline=False)
    halp.add_field(name="`%removeDefaultServer`", value="Sets the default server to none", inline=False)
    halp.add_field(name="`%listBotPerms`", value="Lists roles that have permissions to use the bot", inline=False)
    halp.add_field(name="`%addBotPerms <role>`", value="Allows a role the permissions to use the bot",
                   inline=False)
    halp.add_field(name="`%removeBotPerms <role>`", value="Removes a permission for a role to use the bot", inline=False)
    await ctx.channel.send(embed=halp)



# status of the mc server
@bot.command()
async def status(ctx):
    if ctx.guild in mc_servers:
        try:
            status_server = mc_servers[ctx.guild][2].status()
            await ctx.channel.send('`{}` is online with {} players'.format(mc_servers[ctx.guild][0],
                                                                         status_server.players.online))
        except:
               await ctx.channel.send('`{}` is offline'.format(mc_servers[ctx.guild][0]))
    else:
        await ctx.channel.send(server_not_set)


# set the default minecraft server for the guild
@bot.command()
async def setDefaultServer(ctx, address, port='25565'):
    if ctx.author.guild_permissions.administrator \
        or not set(ctx.author.roles).isdisjoint(set(bot_permissions[ctx].guild)):

        server = MinecraftServer.lookup('{}:{}'.format(address, port))
        mc_servers[ctx.guild] = [address, port, server]
        await ctx.channel.send('Sever set to `{}`'.format(address))
    else:
        await ctx.channel.send(no_perm)


# remove the default minecraft server for the guild
@bot.command()
async def removeDefaultServer(ctx):
    if ctx.author.guild_permissions.administrator \
        or not set(ctx.author.roles).isdisjoint(set(bot_permissions[ctx].guild)):

        if ctx.guild in mc_servers:
            await ctx.guild.me.edit(nick=None)
            del mc_servers[ctx.guild]
            await ctx.channel.send('Sever set to None')
        else:
            await ctx.channel.send(server_not_set)
    else:
        await ctx.channel.send(no_perm)


# status of mc server of user choice
@bot.command()
async def serverStatus(ctx, address, port='25565'):
    server = MinecraftServer.lookup('{}:{}'.format(address, port))
    try:
        status_server = server.status()
        await ctx.channel.send('`{}` is online with {} players'.format(address, status_server.players.online))
    except:
            await ctx.channel.send('`{}` is offline'.format(address))


# add a role that can use the bot
@bot.command()
async def addBotPerms(ctx, role: discord.Role):
    if ctx.guild not in bot_permissions:
        bot_permissions[ctx.guild] = []
    if ctx.author.guild_permissions.administrator and role not in bot_permissions[ctx.guild]:
        if ctx.guild not in bot_permissions:
            bot_permissions[ctx.guild] = []
        bot_permissions[ctx.guild].append(role)
        await ctx.channel.send('Role `{}` now has bot permissions'.format(role.name))
    elif not ctx.author.guild_permissions.administrator:
        await ctx.channel.send(no_perm)
    else:
        await ctx.channel.send('Role `{}` already has bot permissions'.format(role.name))


# remove a roll that can use the bot
@bot.command()
async def removeBotPerms(ctx, role: discord.Role):
    if ctx.guild not in bot_permissions:
        bot_permissions[ctx.guild] = []
    if ctx.author.guild_permissions.administrator and role in bot_permissions[ctx.guild]:
        bot_permissions[ctx.guild].append(role)
        await ctx.channel.send('Role `{}` no longer has bot permissions'.format(role.name))
    elif not ctx.author.guild_permissions.administrator:
        await ctx.channel.send(no_perm)
    else:
        await ctx.channel.send('Role `{}` does not have bot permissions'.format(role.name))


# if a role gets deleted, delete from the list of roles that can use the bot
@bot.event
async def on_guild_role_delete(ctx, role):
    if role in bot_permissions[ctx.guild]:
        bot_permissions[ctx.guild].remove(role)


# list the roles
@bot.command()
async def listBotPerms(ctx):
    if ctx.guild not in bot_permissions:
        bot_permissions[ctx.guild] = []
    if bot_permissions[ctx.guild]:
        lRBP = discord.Embed(title='Roles With Bot Permissions', color=0x000000)
        role_str = ''
        for role in bot_permissions[ctx.guild]:
            role_str += '\n' + role.name
        lRBP.add_field(name='Roles:', value=role_str)
        await ctx.channel.send(embed=lRBP)
    else:
        await ctx.channel.send('This server does not have any roles with bot permissions')




bot.run('Nzc1NDE1Mzk4NDcxMzAzMjI4.X6l_3Q.F6GbJ8BIIBxBa2rQgyEqunGunNQ')
