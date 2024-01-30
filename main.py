# Import General Package
import asyncio
import configparser
import contextlib
import datetime
import io
import textwrap
import time
import traceback
import json
import re
import os

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands

start = time.perf_counter()
conf = configparser.ConfigParser()
conf.read("file/conf/config.ini", encoding="utf-8")

TEST_GUILD = discord.Object(id=1047062918073700383)
TOKEN = conf["MAIN"]["DISCORD_BOT_TOKEN"]
TEST_TOKEN = conf["MAIN"]["TEST_TOKEN"]
MANAGE_USERS = [941871491337814056, 935563914354253924,
                994953877625507851, 1044937269162823751]
PREFIX = conf["MAIN"]["BOT_PREFIX"]

INITAL_EXTENSIONS = [
    "cogs.cog",
    "cogs.verify",
    "cogs.ticket",
    "cogs.eval",
    "cogs.music",
    "cogs.nuke",
    "cogs.clean",
    "cogs.account",
    "cogs.info",
    "cogs.help",
    "cogs.backup",
    "cogs.antit"
]


class ZeTNONClient(commands.Bot):
    def __init__(self, command_prefix, help_command, description, intents: discord.Intents):
        super().__init__(
            command_prefix=command_prefix,
            help_command=help_command,
            description=description,
            intents=intents,
        )

    async def setup_hook(self) -> None:
        self.tree.copy_global_to(guild=TEST_GUILD)
        await self.tree.sync(guild=TEST_GUILD)
        return await super().setup_hook()


intents = discord.Intents.all()
bot = ZeTNONClient(command_prefix=PREFIX, help_command=None,
                   description=None, intents=intents)
end = time.perf_counter()


@bot.event
async def on_ready():
    print(f"""
[Success] Successfully logged to discord API.
Client Token : {"*"*len(TOKEN)}
Client User Name : {bot.user.name}
Client User ID : {bot.user.id}
Logged Time : {str(round(end - start, ndigits=4))} seconds

Discord.py Version : {discord.__version__} | VersionInfo : {discord.version_info.releaselevel}
Discord.py Author : {discord.__author__}
    """)
    t_member = 0
    for i in bot.guilds:
        t_member += len(i.members)
    await bot.change_presence(activity=discord.Game(name="{} servers | {} members".format(str(len(bot.guilds)), str(t_member))))
    print("[Success] Successfully sync the slashcommand.\n")


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceChannel, after: discord.VoiceChannel):
    try:
        if after.channel is None:
            if member.id != bot.user.id:
                if member.guild.voice_client.channel is before.channel:
                    if len(member.guild.voice_client.channel.members) == 1:
                        await member.guild.voice_client.disconnect()
    except:
        pass

if __name__ == "__main__":
    async def boot_bot():
        for cogs in INITAL_EXTENSIONS:
            await bot.load_extension(cogs)
    asyncio.run(boot_bot())
    bot.run(TEST_TOKEN)
