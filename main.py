# Import General Package
import os
import time
import datetime
import textwrap
import io
import traceback
import contextlib
import configparser
import asyncio

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
MANAGE_USERS = eval(conf["MAIN"]["MANAGE_USER"])
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
]


class ZeTNONClient(commands.Bot):
    def __init__(self, command_prefix, help_command, description, intents: discord.Intents):
        super().__init__(
            command_prefix=command_prefix,
            help_command=help_command,
            description=description,
            intents=intents,
        )

    async def setup_hook(self):
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
    await bot.change_presence(activity=discord.Game(name="起動中..."))
    for i in range(len(INITAL_EXTENSIONS)):
        await asyncio.sleep(1)
    await bot.change_presence(activity=discord.Game(name="{} servers | {} members".format(str(len(bot.guilds)), str(t_member))))
    print("[Success] Successfully sync the slashcommand.\n")


@bot.event
async def on_voice_state_update(member, before, after):
    try:
        if after.channel is None:
            if member.id != bot.user.id:
                if member.guild.voice_client.channel is before.channel:
                    if len(member.guild.voice_client.channel.members) == 1:
                        await member.guild.voice_client.disconnect()
    except:
        pass


@bot.event
async def on_message(message):
    if message.content.startswith("z!eval"):
        code = message.content.split[1]
        if message.user.id in MANAGE_USERS:
            global result1, result2
            code_eval = str(code)
            env = {
                "bot": bot,
                "message": message,
            }
            env.update(globals())
            stdout = io.StringIO()
            to_compile = f"async def func():\n{textwrap.indent(code_eval, '  ')}"
            try:
                exec(to_compile, env)
            except Exception as e:
                return await message.channel.send(f"```py\n{e.__class__.__name__}: {e}\n```")
            func = env["func"]
            try:
                with contextlib.redirect_stdout(stdout):
                    ret = await func()
            except Exception as e:
                value = stdout.getvalue()
                await message.channel.send(f"```py\n{value}{traceback.format_exc()}\n```")
            else:
                value = stdout.getvalue()
                if ret is None:
                    if value:
                        await message.channel.send(f"```py\n{value}\n```")
                else:
                    result = ret
                    await message.channel.send(f"```py\n{value}{ret}\n```")

if __name__ == "__main__":
    async def boot_bot():
        for cogs in INITAL_EXTENSIONS:
            await bot.load_extension(cogs)
            await asyncio.sleep(1)
    asyncio.run(boot_bot())
    bot.run(TEST_TOKEN)
