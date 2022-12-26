# Import General Package
import asyncio

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands


class NukeConfirmButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="💥消去 | NUKE", style=discord.ButtonStyle.danger, custom_id="persistent_view:btn_nukeallow")
    async def callback_nukeallow(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            newch = await button.channel.category.create_text_channel(name=button.channel.name, position=button.channel.position, overwrites=button.channel.overwrites)
            await button.channel.delete()
            embed_cleaned = discord.Embed(
                title="✅ Success - Nuke", description="正常にチャンネルログを消去しました。\nこのメッセージは10秒後に消去されます", color=0x00ff00)
            embed_cleaned.set_footer(text="Status - 200 | Made by Tettu0530#0530",
                                     icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            i = await newch.send(embed=embed_cleaned)
            await asyncio.sleep(10)
            await i.delete()
        except:
            newch = await button.guild.create_text_channel(name=button.channel.name, position=button.channel.position, overwrites=button.channel.overwrites)
            await button.channel.delete()
            embed_cleaned = discord.Embed(
                title="✅ Success - Nuke", description="正常にチャンネルログを消去しました。\nこのメッセージは10秒後に消去されます", color=0x00ff00)
            embed_cleaned.set_footer(text="Status - 200 | Made by Tettu0530#0530",
                                     icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            i = await newch.send(embed=embed_cleaned)
            await asyncio.sleep(10)
            await i.delete()

    @discord.ui.button(label="❌キャンセル | CANCEL", style=discord.ButtonStyle.primary, custom_id="persistent_view:btn_nukedeny")
    async def callback_nukedeny(self, button: discord.ui.Button, interaction: discord.Interaction):
        await button.message.delete()


class NukeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("[COGS]NukeSlashCog on ready.")

    @app_commands.command(
        name="nuke",
        description="チャンネルログを全消去します(Botなどをチャンネルに登録している場合は/cleanを使用してください)"
    )
    async def nuke(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            embed = discord.Embed(title="✅ 確認 | Confirm", description="本当にチャンネルログを消去しますか？\n**消去を押した後操作は取り消せません**\n(**BotやWebHookなどを登録している場合は`/clean`を使うことを強く推奨します**)", color=0xffff00)
            embed.set_footer(text="Status - 200 | Made by Tettu0530#0530",
                                     icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            await interaction.response.send_message(embed=embed, view=NukeConfirmButtonView(bot=self.bot))

async def setup(bot: commands.Bot):
    await bot.add_cog(NukeCog(bot))