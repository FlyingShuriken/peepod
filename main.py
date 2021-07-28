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
            playlist_reaction = {"1️⃣": "\u0031", "2️⃣": "\u0032", "3️⃣": "\u0033", "4️⃣": "\u0034"}
            radio_reaction = {"🔂":"loop","🔀":"shuffle","⏸":"pause","⏪":"previous","⏩":"next"}
            if reaction.name in list(playlist_reaction.keys()):
                playlist_name = sett["reaction"][playlist_reaction[reaction.name]]
                bot.base_radio = Radio(playlist_name)
                check_if_song_end.start()
            elif reaction.name in list(radio_reaction.keys()):
                if radio_reaction[reaction.name] in ["loop","pause"]:
                    if radio_reaction[reaction.name] == "loop":
                        bot.base_radio.loop()
                    elif radio_reaction[reaction.name] == "pause":
                        bot.base_radio.pause()
                else:
                    if radio_reaction[reaction.name] == "shuffle":
                        bot.base_radio.shuffle()
                    elif radio_reaction[reaction.name] == "previous":
                        bot.base_radio.previous(bot.base_radio.radio_path)
                    elif radio_reaction[reaction.name] == "next":
                        bot.base_radio.next(bot.base_radio.radio_path)
                    channel = bot.get_channel(channel_id)
                    message = await channel.fetch_message(radio_controller)
                    await message.clear_reaction("🔀")
                    await message.clear_reaction("⏪")
                    await message.clear_reaction("⏩")
                    await message.add_reaction("🔀")
                    await message.add_reaction("⏪")
                    await message.add_reaction("⏩")


@bot.event
async def on_raw_reaction_remove(payload):
    member = bot.get_user(payload.user_id)
    if payload.channel_id == channel_id and member.bot == False:
        message = payload.message_id
        reaction = payload.emoji
        if sett["base_msg"][str(message)] == "playlist":
            radio_reaction = {"🔂": "loop", "⏸": "pause"}
            if reaction.name in list(radio_reaction.keys()):
                if radio_reaction[reaction.name] == "loop":
                    bot.base_radio.unloop()
                elif radio_reaction[reaction.name] == "pause":
                    bot.base_radio.resume()
            else:
                bot.base_radio.status = "stop"
                bot.base_radio.stop(bot.base_radio.radio_path)
                check_if_song_end.stop()
                channel = bot.get_channel(payload.channel_id)
                message = await channel.fetch_message(radio_controller)
                await message.clear_reaction("🔂")
                await message.clear_reaction("⏸")
                await message.clear_reaction("🔀")
                await message.clear_reaction("⏪")
                await message.clear_reaction("⏩")

                await message.add_reaction("🔂")
                await message.add_reaction("⏸")
                await message.add_reaction("🔀")
                await message.add_reaction("⏪")
                await message.add_reaction("⏩")

@bot.command()
async def np(ctx,link):
    bot.base_radio.single_song(link)
    await ctx.message.delete()

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
    await message.clear_reaction("🔂")
    await message.clear_reaction("⏸")
    await message.clear_reaction("🔀")
    await message.clear_reaction("⏪")
    await message.clear_reaction("⏩")

    await message.add_reaction("🔂")
    await message.add_reaction("⏸")
    await message.add_reaction("🔀")
    await message.add_reaction("⏪")
    await message.add_reaction("⏩")


bot.run(sett["token"])

