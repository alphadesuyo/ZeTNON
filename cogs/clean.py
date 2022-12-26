# Import General Package
import asyncio

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands

class CleanConfirmButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)

    @discord.ui.button(label="💥消去 | CLEAN", style=discord.ButtonStyle.danger, custom_id="persistent_view:btn_clanallow")
    async def callback_cleanallow(self, button: discord.ui.Button, interaction: discord.Interaction):
        await button.channel.purge(limit=1000)
        embed_cleaned = discord.Embed(
            title="✅ Success - Clean", description="正常にチャンネルログを消去しました。\nこのメッセージは10秒後に消去されます", color=0x00ff00)
        embed_cleaned.set_footer(text="Status - 200 | Made by Tettu0530#0530",
                                 icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
        i = await button.response.send_message(embed=embed_cleaned)
        await asyncio.sleep(10)
        await i.delete()

    @discord.ui.button(label="❌キャンセル | CANCEL", style=discord.ButtonStyle.primary, custom_id="persistent_view:btn_cleandeny")
    async def callback_cleandeny(self, button: discord.ui.Button, interaction: discord.Interaction):
        await button.message.delete()

    
class CleanCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("[COGS]CleanSlashCog on ready.")

    @app_commands.command(
        name="clean",
        description="チャンネルログを全消去します"
    )
    async def clean(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            embed = discord.Embed(title="✅ 確認 | Confirm", description="本当にチャンネルログを消去しますか？\n**消去を押した後操作は取り消せません**", color=0xffff00)
            embed.set_footer(text="Status - 200 | Made by Tettu0530#0530",
                                     icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            await interaction.response.send_message(embed=embed, view=CleanConfirmButtonView(bot=self.bot))

async def setup(bot: commands.Bot):
    await bot.add_cog(CleanCog(bot))