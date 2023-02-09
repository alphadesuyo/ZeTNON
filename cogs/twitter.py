# Import General Package
import asyncio
from Twitter_Frontend_API import Client

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands

api = Client()
api.generate_ct0()
api.generate_authenticity()
api.generate_token()


class TwitterCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("[COGS]TwitterSlashCog on ready.")

    @app_commands.command(name="sbcheck", description="Twitterのアカウントがシャドウバンされているか確認します")
    @app_commands.describe(id="TwitterIDを指定してください(例:Example)")
    async def sbcheck(self, interaction: discord.Interaction, id: str):
        sb = api.shadowban_check(screen_name=id)
        embed = discord.Embed()
        if sb["not_found"] == True:
            embed.title = "❌ ShadowbanCheck - Failure"
            embed.description = f"**@{id}**\n指定したユーザーは見つかりませんでした"
            embed.color = 0xff0000
        elif sb["suspend"] == True:
            embed.title = "❌ ShadowbanCheck - Failure"
            embed.description = f"**{id}**\n指定したユーザーは凍結されています"
            embed.color = 0xff0000
        elif sb["protect"] == True:
            embed.title = "❌ ShadowbanCheck - Failure"
            embed.description = f"**{id}**\n指定したユーザーは鍵垢です"
            embed.color = 0xff0000
        else:
            if sb["searchban"] == True:
                searchban = "SearchBan : Yes"
            else:
                searchban = "SearchBan : No"
            if sb["search_suggestion_ban"] == True:
                suggestion = "SearchSuggestionBan : Yes"
            else:
                suggestion = "SearchSuggestionBan : No"
            if sb["ghost_ban"] == True:
                ghost = "GhostBan : Yes"
            else:
                ghost = "GhostBan : No"
            if sb["reply_deboosting"] == True:
                reply = "ReplyDeboosting : Yes"
            else:
                reply = "ReplyDeboosting : Yes"
            embed.title = "✅ ShadowbanCheck - Success"
            embed.add_field(
                name="ステータス", value=f"{searchban}\n{suggestion}\n{ghost}\n{reply}")
            embed.color = 0x00ff00
            embed.set_footer(text="Status - 200 | Made by Tettu0530New#7110",
                             icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(TwitterCog(bot))