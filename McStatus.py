import asyncio
import discord
from discord.ext import commands
from mcstatus import MinecraftServer

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='%', help_command=None, intents=intents)

mc_servers = {}

server_not_set = 'A Minecraft Server Has not Been Set'
embed_insufficient_permissions = discord.Embed(color=0x000000)
embed_insufficient_permissions.add_field(name='Insufficient Permissions',
                                         value='You do not have sufficient permissions')


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
    await bot.change_presence(activity=discord.Game('%help (coming soon)'))
    await status_update()


# status of the mc server
@bot.command()
async def status(ctx):
    if ctx.guild in mc_servers:
        try:
            status_server = mc_servers[ctx.guild][2].status()
            await ctx.channel.send('{} is online with {} players'.format(mc_servers[ctx.guild][0],
                                                                         status_server.players.online))
        except:
               await ctx.channel.send('{} is offline'.format(mc_servers[ctx.guild][0]))
    else:
        await ctx.channel.send(server_not_set)


# set the default minecraft server for the guild
@bot.command()
async def setDefaultServer(ctx, address, port='25565'):
    if ctx.author.guild_permissions.administrator:
        server = MinecraftServer.lookup('{}:{}'.format(address, port))
        mc_servers[ctx.guild] = [address, port, server]
        await ctx.channel.send('Sever set to {}'.format(address))
    else:
        await ctx.channel.send(embed=embed_insufficient_permissions)


# remove the default minecraft server for the guild
@bot.command()
async def removeDefaultServer(ctx):
    if ctx.author.guild_permissions.administrator:
        if ctx.guild in mc_servers:
            await ctx.guild.me.edit(nick=None)
            del mc_servers[ctx.guild]
            await ctx.channel.send('Sever set to None')
        else:
            await ctx.channel.send(server_not_set)
    else:
        await ctx.channel.send(embed=embed_insufficient_permissions)


# status of mc server of user choice
@bot.command()
async def serverStatus(ctx, address, port='25565'):
    server = MinecraftServer.lookup('{}:{}'.format(address, port))
    try:
        status_server = server.status()
        await ctx.channel.send('{} is online with {} players'.format(address, status_server.players.online))
    except:
            await ctx.channel.send('{} is offline'.format(address))


bot.run('Nzc1NDE1Mzk4NDcxMzAzMjI4.X6l_3Q.F6GbJ8BIIBxBa2rQgyEqunGunNQ')
