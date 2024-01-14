import os
import asyncio
import argparse

import discord
from discord.ext import commands

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--ffmpeg', help='path to ffmpeg', default="C:/ffmpeg/bin/ffmpeg.exe")
parser.add_argument('-m', '--music', help='path to directory with music', default="music/")
args = parser.parse_args()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def get_token():
    with open("token.txt", "r") as f:
        return f.read()


def get_music_dir():
    return args.music


VOICE_CLIENT = None


async def get_voice_client(channel):
    global VOICE_CLIENT
    if VOICE_CLIENT is None:
        VOICE_CLIENT = await channel.connect()
    return VOICE_CLIENT


async def wait_for_song(channel):
    vc = await get_voice_client(channel)
    while vc.is_playing():
        await asyncio.sleep(0.5)


async def play_song(channel, path):
    voice = await get_voice_client(channel)
    if voice.is_playing():
        voice.stop()
    voice.play(discord.FFmpegPCMAudio(executable=args.ffmpeg, source=f"{get_music_dir()}/{path}"))


@bot.command()
async def play(ctx, path):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await play_song(channel, path)
    else:
        ctx.send("I can't join your channel")


@bot.command()
async def playlist(ctx, path):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        files = os.listdir(get_music_dir() + "/" + path)
        for file in sorted(files):
            await play_song(channel, path + "/" + file)
            await wait_for_song(channel)

    else:
        ctx.send("I can't join your channel")


@bot.command()
async def repeat(ctx, path):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        while True:
            await play_song(channel, path)
            await wait_for_song(channel)
    else:
        ctx.send("I can't join your channel")

token = get_token()
bot.run(token)
