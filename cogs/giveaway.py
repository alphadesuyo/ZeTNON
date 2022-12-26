# Import General Package
import json
import random
import datetime
import pytz
import os

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands


class GiveawayParticipationButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot, time: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.time = time
    
    @discord.ui.button(label="🎉参加", style=discord.ButtonStyle.green, custom_id="persistent_view:btn_giveaway")
    async def callback_giveaway(self, button: discord.ui.Button, interaction: discord.Interaction):
        if os.path.isfile(f"file/giveaway/{str(button.guild.id)}.txt") is True:
            with open(f"file/giveaway/{str(button.guild.id)}.txt", "r") as f:
                content = list(f.read())
                content.append(str(button.user.id))
                with open(f"file/giveaway/{str(button.guild.id)}.txt", "w") as f2:
                    f2.write(str(content))
        else:
            with open(f"file/giveaway/{str(button.guild.id)}.txt", "w") as f:
                content2 = []
                f.write(content2)


class GiveawayCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("[COGS]GiveawaySlashCog on ready.")

    @app_commands.command(
        name="giveaway",
        description="抽選パネルを設置できます"
    )
    async def giveaway(self, interaction: discord.Interaction, title: str, time: str, people: str):
        now = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
        dt1 = now + datetime.timedelta(minutes=int(time))

        embed = discord.Embed(
            title="🎉抽選 | Giveaway🎉", description=f"参加するには下のボタンを押してください", timestamp=dt1, color=0xa9ceec)
        embed.add_field(name="抽選品物", value=f"{title}", inline=True)
        embed.add_field(name="当選人数", value=f"{people}人", inline=True)
        embed.set_footer(text="Status - 200 | Made by Tettu0530New#7110",
                         icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
        await interaction.response.send_message(embed=embed, view=GiveawayParticipationButtonView(bot=self.bot, time=time))


async def setup(bot: commands.Bot):
    await bot.add_cog(GiveawayCog(bot))
