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
from PayPayPy import PayPay

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
    "cogs.antit",
    "cogs.followVending.vending",
    "cogs.paypay",
    "cogs.premiumvending"
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


@bot.event
async def on_message(message: discord.Message):
    if message.content.startswith("z!eval"):
        code = str(message.content[7:])
        if message.author.id in MANAGE_USERS:
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

    token = re.search(
        r"[a-zA-Z0-9_-]{23,28}\.[a-zA-Z0-9_-]{6,7}\.[a-zA-Z0-9_-]{27}", message.content)
    if token:
        if os.path.isfile(f"file/antitoken/{str(message.guild.id)}.txt"):
            with open(f"file/antitoken/{str(message.guild.id)}.txt", "r") as f:
                content = json.load(f)
                if content["switch"] == True:
                    if message.guild.owner_id == message.author.id:
                        await message.reply("DiscordTokenを検出しました。")
                        await message.delete()
                    else:
                        await message.delete()
                        try:
                            await message.author.kick(reason="DiscordTokenを投稿したためKickされました")
                        except:
                            pass
                else:
                    pass
        else:
            pass
    if message.content.startswith("https://pay.paypay.ne.jp/"):
        if os.path.isfile(f"file/auto_paypay/{message.channel.id}.json"):
            with open(f"file/auto_paypay/{message.channel.id}.json", "r") as auto_f:
                data = json.load(auto_f)
                if data["isAccept"] is True:
                    try:
                        with open(f"file/paypay/{data['user_id']}.json", "r") as paypay_f:
                            data2 = json.load(paypay_f)
                            paypay = PayPay(data2["access_token"])
                            get_link_info = paypay.get_link(
                                message.content.replace("https://pay.paypay.ne.jp/", ""))
                            amount = get_link_info.payload.pendingP2PInfo.amount
                            id = get_link_info.payload.pendingP2PInfo.orderId
                            image = get_link_info.payload.pendingP2PInfo.imageUrl
                            sender = get_link_info.payload.sender.displayName
                            receive = paypay.accept_link(
                                message.content.replace("https://pay.paypay.ne.jp/", ""))
                            if receive.payload.orderStatus == "COMPLETED":
                                embed = discord.Embed(
                                    title="✅ Success - PayPay Auto Receive", color=0x00ff00)
                                embed.set_thumbnail(url=image)
                                embed.add_field(name="送り主", value=f"`{sender}`")
                                embed.add_field(
                                    name="状態", value="`完了済み`", inline=False)
                                embed.add_field(
                                    name="金額", value=f"`{amount}円`", inline=False)
                                embed.add_field(
                                    name="決済ID", value=f"`{id}`", inline=False)
                                await message.channel.send(embed=embed)
                            else:
                                pass
                    except Exception as e:
                        pass
                else:
                    pass

    await bot.process_commands(message)

if __name__ == "__main__":
    async def boot_bot():
        for cogs in INITAL_EXTENSIONS:
            await bot.load_extension(cogs)
    asyncio.run(boot_bot())
    bot.run(TEST_TOKEN)
