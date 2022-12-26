# Import General Package
import asyncio

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("[COGS]HelpSlashCog on ready.")

    @app_commands.command(
        name="help",
        description="Botのヘルプを表示します"
    )
    async def help(self, interaction: discord.Interaction):
        embed0 = discord.Embed(
            title="ZeTNON help", color=0x5946f1)
        embed0.add_field(name="/help", value="このhelpを表示します", inline=False)
        embed0.add_field(
            name="/clean", value="実行したチャンネルのメッセージログを消去します(※サーバー管理者専用)", inline=False)
        embed0.add_field(
            name="/nuke", value="チャンネルの位置や権限、名前などををそのままにしてチャンネルをきれいに消して再生成します(※サーバー管理者専用)", inline=False)
        embed0.add_field(name="/ban <Mention>",
                         value="メンションしたユーザーをBAN(アクセス禁止)します(※サーバー管理者専用)", inline=False)
        embed0.add_field(name="/kick <Mention>",
                         value="メンションしたユーザーをキックします(※サーバー管理者専用)", inline=False)
        embed0.set_footer(text="Page 1/3")

        embed0_1 = discord.Embed(
            title="ZeTNON help", color=0x5946f1)
        embed0_1.add_field(
            name="/info guild", value="サーバー情報が送信されます", inline=False)
        embed0_1.add_field(
            name="/verify", value="計算認証・ワンクリック認証のどちらかで認証を行います", inline=False)
        embed0_1.add_field(
            name="/music join", value="Botをユーザーが接続中のボイスチャットに接続させます", inline=False)
        embed0_1.add_field(name="/play <YoutubeURLまたは検索ワード>",
                           value="入力されたしたYoutubeの動画名・URLから音楽をストリームで再生します", inline=False)
        embed0_1.add_field(
            name="/music leave", value="Botをユーザーが接続中のボイスチャットから切断させます", inline=False)
        embed0_1.set_footer(text="Page 2/3")

        embed0_2 = discord.Embed(
            title="ZeTNON help", color=0x5946f1)
        embed0_2.add_field(
            name="/music pause", value="再生中の音楽を一時停止ます", inline=False)
        embed0_2.add_field(
            name="/music resume", value="一時停止中の音楽を再開させます", inline=False)
        embed0_2.add_field(
            name="/music stop", value="再生中/一時停止中の音楽を停止させます", inline=False)
        embed0_2.add_field(name="/user <Mention>",
                           value="メンションしたユーザーの情報を送信します", inline=False)
        embed0_2.add_field(
            name="/ticket", value="チケットを発行できるパネルを設置します", inline=False)
        embed0_2.set_footer(text="Page 3/3")

        contents = [embed0, embed0_1, embed0_2]
        pages = 3
        cur_pages = 1
        await interaction.response.send_message(embed=contents[cur_pages - 1])
        res: discord.InteractionMessage = await interaction.original_response()

        await res.add_reaction("◀️")
        await res.add_reaction("⏹️")
        await res.add_reaction("▶️")

        def check(reaction: discord.Reaction, user: discord.User):
            return user == interaction.user and str(reaction.emoji) in ["◀️", "⏹️", "▶️"]
        
        while True:
            try:
                reactions, user= await self.bot.wait_for("reaction_add", timeout=120, check=check)
                
                if str(reactions.emoji) == "▶️" and cur_pages != pages:
                    cur_pages += 1
                    await res.edit(embed=contents[cur_pages - 1])
                    await res.remove_reaction(reactions, user)
                elif str(reactions.emoji) == "⏹️":
                    await res.clear_reactions()
                    break
                elif str(reactions.emoji) == "◀️" and cur_pages > 1:
                    cur_pages -= 1
                    await res.edit(embed=contents[cur_pages - 1])
                    await res.remove_reaction(reactions, user)
                else:
                    await res.remove_reaction(reactions, user)
            except asyncio.TimeoutError:
                await res.clear_reactions()
                break



async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))