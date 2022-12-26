# Import General Package
import typing

# Import Discord Package
import discord
from discord.ext import commands
from discord import app_commands

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