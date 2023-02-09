# Import General Package
import typing
import configparser

# Import Discord Package
import discord
from discord.ext import commands
from discord import app_commands

conf = configparser.ConfigParser()
conf.read("file/conf/config.ini", encoding="utf-8")

TEST_GUILD = discord.Object(id=1047062918073700383)
TOKEN = conf["MAIN"]["DISCORD_BOT_TOKEN"]
TEST_TOKEN = conf["MAIN"]["TEST_TOKEN"]
MANAGE_USERS = [941871491337814056, 935563914354253924, 994953877625507851, 1044937269162823751]
PREFIX = conf["MAIN"]["BOT_PREFIX"]

class CogCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("[COGS]LoadCogSlashCog on ready.")
    
    @app_commands.command(
        name="cog",
        description="コマンドのロード・リロード(ZeTNONDeveloper専用)"
    )
    @app_commands.describe(mode="モード選択できます")
    @app_commands.describe(cog="操作するcogを選択できます")
    async def cog(self, interaction: discord.Interaction, mode: typing.Literal["load", "reload", "unload"], cog: str):
        if interaction.user.id in MANAGE_USERS:
            if mode == "load":
                try:
                    await self.bot.load_extension(cog)
                    await interaction.response.send_message("cog(`{}`)をロードしました。".format(cog), ephemeral=True)
                except discord.ext.commands.errors.ExtensionNotFound:
                    await interaction.response.send_message("指定したcog(`{}`)は見つかりませんでした\n(`discord.ext.commands.errors.ExtensionNotFound`)".format(cog), ephemeral=True)
            elif mode == "reload":
                try:
                    await self.bot.reload_extension(cog)
                    await interaction.response.send_message("cog(`{}`)をリロードしました。".format(cog), ephemeral=True)
                except discord.ext.commands.ExtensionNotLoaded:
                    await interaction.response.send_message("指定したコグ(`{}`)は見つかりませんでした。\n(`discord.ext.commands.errors.ExtensionNotLoaded`)".format(cog), ephemeral=True)
            elif mode == "unload":
                try:
                    await self.bot.unload_extension(cog)
                    await interaction.response.send_message("cog(`{}`)をアンロードしました。".format(cog), ephemeral=True)
                except discord.ext.commands.errors.extensionNotLoaded:
                    await interaction.response.send_message("指定したコグ(`{}`)は見つかりませんでした。\n(`discord.ext.commands.errors.ExtensionNotLoaded`)".format(cog), ephemeral=True)
            else:
                await interaction.response.send_message("引数modeが不正です(`{}`)".format(mode), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(CogCog(bot))