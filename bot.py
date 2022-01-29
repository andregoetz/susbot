import re
import os
import json
import datetime
import asyncio
import subprocess

import validators
import discord
from discord.ext import commands

from hypixel_api import get_hypixel_player

path = os.path.dirname(os.path.abspath(__file__))
with open(path + '/res/config.json') as conf:
    conf = json.load(conf)

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=conf['prefix'], intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord as a Bot')
    await bot.change_presence(activity=discord.Game("Suscraft"))


@bot.command(name='bwstats', aliases=['bws'], help='Get the Hypixel BedWars stats of a player')
async def get_bwstats(ctx: commands.Context, player_name: str):
    hypixel_data = get_hypixel_player(player_name)
    player = hypixel_data[0]
    achievements, stats = player['achievements'], player['stats']
    bw = stats['Bedwars']
    fk, fd = bw['final_kills_bedwars'], bw['final_deaths_bedwars']
    embed = discord.Embed(title=f"{player['displayname']}'s stats")
    if hypixel_data[1] is not None:
        embed.set_thumbnail(url=hypixel_data[1])
    embed.add_field(name='fkdr', value=round(fk / fd, 2))
    embed.add_field(name='lvl', value=achievements['bedwars_level'])
    await ctx.send(embed=embed)


@bot.command(name='join', aliases=[], help='Join a vc')
async def join(ctx: commands.Context):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        return
    channel = ctx.message.author.voice.channel
    if ctx.voice_client is None:
        return await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)
        return ctx.voice_client


@bot.command(name='leave', aliases=['l', 'disconnect', 'dc'], help='Leave a vc')
async def leave(ctx: commands.Context):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()


@bot.command(name='pause', aliases=[], help='Pause playing')
async def pause(ctx: commands.Context):
    if ctx.voice_client:
        await ctx.voice_client.pause()


@bot.command(name='resume', aliases=[], help='Resume playing')
async def resume(ctx: commands.Context):
    if ctx.voice_client:
        await ctx.voice_client.resume()


@bot.command(name='skip', aliases=['s'], help='Skip the playing song')
async def skip(ctx: commands.Context):
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.voice_client.stop()


@bot.command(name='play', aliases=['p'], help='Play a yt song')
async def play(ctx: commands.Context, *query):
    query = ' '.join(query)
    vc = await join(ctx)
    if vc is None:
        return
    song_path = f'/tmp/yt_{hash(query)}.mp3'
    await ctx.send(f'Added "{query}" to the queue')
    subprocess.run(['yt-dlp', get_ytsearch(query), '-f', 'ba', '-o', song_path])
    while vc.is_playing():
        await asyncio.sleep(1)
    vc.play(discord.FFmpegPCMAudio(song_path))
    pass


def get_ytsearch(query):
    if validators.url(query):
        return query
    else:
        return 'ytsearch:' + query


@bot.command(name='remindme', aliases=['rme'],
             help='Remind me of something after given time, allowed times are: s, min, h, d')
async def remindme(ctx: commands.Context, time):
    if time.endswith('s'):
        time = int(time[:-1])
    elif time.endswith('min'):
        time = int(time[:-3]) * 60
    elif time.endswith('h'):
        time = int(time[:-1]) * 3600
    elif time.endswith('d'):
        time = int(time[:-1]) * 86400
    else:
        time = ''.join(re.findall(r'\d+', time))
        if time == '':
            time = 60
        else:
            time = int(time)
    remind = datetime.datetime.now() + datetime.timedelta(seconds=time)
    await ctx.reply(f'I will remind you on the {remind.strftime("%d.%m.%Y")} at {remind.strftime("%H:%M:%S")}')
    await asyncio.sleep(time)
    await ctx.reply('Reminding you :D')


@bot.command(name='test', aliases=['t'], help='Test')
async def test(ctx: commands.Context):
    if ctx.author.id == conf['andiru_id']:
        await ctx.message.delete()
        guild: discord.Guild = ctx.guild
        emojis = {}
        for emoji in guild.emojis:
            emojis[emoji.name] = emoji.id
        with open('otaku_emojis.json', 'w') as out:
            out.write(json.dumps(emojis, indent=2))


if __name__ == '__main__':
    bot.run(conf['token'])
