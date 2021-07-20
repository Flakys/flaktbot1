import discord
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import youtube_dl
import asyncio
from random import choice
import os

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


client = commands.Bot(command_prefix='F ')

status = ['Happy Tree Frends']

@client.event
async def on_ready():
    change_status.start()
    print('Флэки онлайн!')

@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'Добро Пожаловать! {member.mention}!  Готов? Подробнее в команде F help')

@client.command(name='ping', help='Эта команда поазывает мой пинг')
async def ping(ctx):
    await ctx.send(f'**Понг!** Пинг: {round(client.latency * 1000)}ms')

@client.command(name='hello', help='Эта команда показывет случайное приветственное сообщение')
async def hello(ctx):
    responses = ['***Кусь***  Зачем ты меня разбудил?', 'Лучшее утро для тебя, чел!', 'Привет, как ты?', 'Приветик', '**Утро начинается с новой серии HTF, да?**']
    await ctx.send(choice(responses))

@client.command(name='die', help='Эта команда показывает случайные выражения')
async def die(ctx):
    responses = ['почему ты положил конец моей короткой жизни?', 'я бы могла быть с тобой, но но я занята', 'у меня есть семья, убей их вместо этого']
    await ctx.send(choice(responses))

@client.command(name='credits', help='Эта команда показывает что то там')
async def credits(ctx):
    await ctx.send('Сделано `Flaky#9564`')
    await ctx.send('Спасибо моему мозгу за эту идею в 3 ночи')
    await ctx.send('Помощников еще нет(')

@client.command(name='creditz', help='Эта команда показывает всех кто делал меня')
async def creditz(ctx):
    await ctx.send('**Один я делал Флэки, долбоеб**')
    await ctx.send('Пошутила')
    await ctx.send('Шутка хуйня, знаю(')

@client.command(name='play', help='Эта команда для проигрывания музыки) Просто вставь ссылку на видео')
async def play(ctx, url):
    if not ctx.message.author.voice:
        await ctx.send("***Ой*** Похоже вы не подключены к голосовому каналу")
        return

    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**Now playing:** {}'.format(player.title))

@client.command(name='stop', help='Эта команда для остановки музыки и выхода Флэки из чата')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))


@client.command(name='TC', help='Терхподдержка если чето не работает')
async def lolzsait(ctx):
    embed = discord.Embed(
        title="***Тык*** для перехода",
        description="Мой ВК, типа техподдержка",
        url='https://vk.com/flaky1',
    )
    await ctx.send(embed=embed)

token = os.environ.get('BOT_TOKEN')

client.run(str(token))



