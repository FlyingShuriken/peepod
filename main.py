import discord
from discord.ext import commands, tasks
import json
from radio import Radio
from time import time

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
sett = json.load(open("settings.json", "r"))
channel_id = sett["channel_id"]
radio_controller = sett["radio_controller"]

@tasks.loop(seconds=0.5)
async def check_if_song_end():
    lRadio = bot.base_radio
    if time() > lRadio.end_time:
        lRadio.stop(path=lRadio.radio_path)
        check_if_song_end.stop()

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    pass

@bot.event
async def on_raw_reaction_add(payload):
    if payload.channel_id == channel_id and payload.member.bot == False:
        message = payload.message_id
        if sett["base_msg"][str(message)] == "playlist":
            reaction = payload.emoji
            reaction_ = {"1️⃣": "\u0031", "2️⃣": "\u0032", "3️⃣": "\u0033", "4️⃣": "\u0034"}
            playlist_name = sett["reaction"][reaction_[reaction.name]]
            bot.base_radio = Radio(playlist_name)
            check_if_song_end.start()

@bot.event
async def on_raw_reaction_remove(payload):
    member = bot.get_user(payload.user_id)
    if payload.channel_id == channel_id and member.bot == False:
        message = payload.message_id
        if sett["base_msg"][str(message)] == "playlist":
            bot.base_radio.status = "Stop"
            bot.base_radio.stop(bot.base_radio.radio_path)
            check_if_song_end.stop()

@bot.command()
async def send(ctx):
    embed = discord.Embed(title="Radio",description="Pick a Playlist",colour=discord.Color.red())
    embed.add_field(name="", value="1. ",inline=False)
    embed.add_field(name="", value="2. ",inline=False)
    embed.add_field(name="", value="3. ",inline=False)
    embed.add_field(name="", value="4. ",inline=False)
    msg = await ctx.send(embed=embed)

@bot.command()
async def add(ctx):
    message = await ctx.channel.fetch_message(radio_controller)
    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")
    await message.add_reaction("3️⃣")
    await message.add_reaction("4️⃣")


bot.run(sett["token"])

