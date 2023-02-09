# Import General Package
import json

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands

class AntiTokenCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("[COGS]AntiTokenSlashCog on ready.")
        
    @app_commands.command(
        name="antitoken",
        description="DiscordTokenが投稿されたら自動で削除する機能の管理ができます"
    )
    @app_commands.describe(switch="機能をONにするかOFFにするか設定できます(デフォルトはOFF)")
    async def antitoken(self, interaction: discord.Interaction, switch: bool):
        with open(f"file/antitoken/{str(interaction.guild_id)}.txt", "w", encoding="utf-8") as f:
            content = {"guild_id": interaction.guild_id, "switch": switch}
            json.dump(content, f)
        if switch == True:
            swith_s = "有効"
        else:
            swith_s = "無効"
        await interaction.response.send_message("設定が完了しました。\n{}".format(swith_s), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AntiTokenCog(bot))