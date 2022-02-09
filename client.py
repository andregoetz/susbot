import os
import json
import random
import discord

path = os.path.dirname(os.path.abspath(__file__))
with open(path + '/res/config.json') as conf:
    conf = json.load(conf)

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord as a Client')


@client.event
async def on_message(message: discord.Message):
    if message.guild is None:
        if not message.author.id == conf['bot_id'] and not message.author.id == conf['andiru_id']:
            print(message.author.name, message.content)
            await message.channel.send('sussy baka?')
    else:
        if 'sus' in message.content.lower().replace(' ', ''):
            if random.randrange(0, 3) == 0:
                await message.channel.send('amogus')


if __name__ == '__main__':
    client.run(conf['token'])
