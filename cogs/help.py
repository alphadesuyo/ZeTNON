# Import General Package
import asyncio

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands

embed0 = discord.Embed(
    title="ZeTNON help(アカウントコマンド系)", color=0x5946f1)
embed0.add_field(name="/account register",
                 value="ZeTNONアカウントを登録します", inline=False)
embed0.add_field(name="/account setting",
                 value="ZeTNONアカウント情報を変更します", inline=False)
embed0_1 = discord.Embed(
    title="ZeTNON help(サーバー管理コマンド系)", color=0x5946f1)
embed0_1.add_field(
    name="/clean", value="コマンドを実行したチャンネルのチャンネルログを消去します", inline=False)
embed0_1.add_field(
    name="/nuke", value="コマンドを実行したチャンネルのチャンネルログを消去します(**BotやWebhookをチャンネルに紐づけている場合は/cleanを実行することをおすすめします**)", inline=False)
embed0_1.add_field(
    name="/kick", value="指定したユーザーをサーバーから追放します", inline=False)
embed0_1.add_field(
    name="/ban", value="指定したユーザーをコマンドを実行したサーバーへの参加を禁止します", inline=False)
embed0_1.add_field(
    name="/verify", value="ロールを付与する認証パネルを設置します", inline=False)
embed0_2 = discord.Embed(
    title="ZeTNON help(サーバー管理コマンド系2)", color=0x5946f1)
embed0_2.add_field(name="/ticket set",
                   value="チケットパネルを設置できます", inline=False)
embed0_2.add_field(name="/ticket config",
                   value="チケットパネルの設定を変更します", inline=False)
embed0_3 = discord.Embed(
    title="ZeTNON help(音楽コマンド系)", color=0x5946f1)
embed0_3.add_field(name="/music join",
                   value="ユーザーがいるボイスチャンネルに参加します", inline=False)
embed0_3.add_field(name="/music leave",
                   value="今参加しているボイスチャンネルから退出します", inline=False)
embed0_3.add_field(
    name="/music play", value="入力したワードまたはYouTube動画URLの音楽を再生します", inline=False)
embed0_3.add_field(name="/music pause",
                   value="再生中の音楽を一時停止します", inline=False)
embed0_3.add_field(name="/music resume",
                   value="一時停止中の音楽を再開します", inline=False)


class ChangeHelpPageSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot, res: discord.InteractionMessage):
        options = [
            discord.SelectOption(
                label="1", description="1ページ目(アカウントコマンド系)", value="1"),
            discord.SelectOption(
                label="2", description="2ページ目(サーバー管理コマンド系1)", value="2"),
            discord.SelectOption(
                label="3", description="3ページ目(サーバー管理コマンド系2)", value="3"),
            discord.SelectOption(
                label="4", description="4ページ目(音楽コマンド系)", value="4")
        ]
        super().__init__(
            placeholder="選択してください",
            max_values=1,
            options=options
        )
        self.res = res
    
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "1":
            await self.res.edit(embed=embed0)
        elif self.values[0] == "2":
            await self.res.edit(embed=embed0_1)
        elif self.values[0] == "3":
            await self.res.edit(embed=embed0_2)

class ChangeHelpPageSelectView(discord.ui.View):
    def __init__(self, bot: commands.Bot, res: discord.InteractionMessage):
        super().__init__(timeout=None)
        self.add_item(ChangeHelpPageSelect(bot=bot, res=res))


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

        contents = [embed0, embed0_1, embed0_2, embed0_3]
        pages = 4
        cur_pages = 1
        await interaction.response.send_message(embed=contents[cur_pages - 1])
        res: discord.InteractionMessage = await interaction.original_response()

        await res.add_reaction("◀️")
        await res.add_reaction("⏹️")
        await res.add_reaction("▶️")
        await res.add_reaction("🔢")

        def check(reaction: discord.Reaction, user: discord.User):
            return user == interaction.user and str(reaction.emoji) in ["◀️", "⏹️", "▶️", "🔢"]

        while True:
            try:
                reactions, user = await self.bot.wait_for("reaction_add", timeout=120, check=check)

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
                elif str(reactions.emoji) == "🔢":
                    await interaction.followup.send(view=ChangeHelpPageSelectView(bot=self.bot, res=res), ephemeral=True)
                    await res.remove_reaction(reactions, user)
                else:
                    await res.remove_reaction(reactions, user)
            except asyncio.TimeoutError:
                await res.clear_reactions()
                break


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
