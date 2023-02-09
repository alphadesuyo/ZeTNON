# Import General Package
import json
import typing
import random
import datetime
import pytz

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands


class VerifyModal(discord.ui.Modal):
    def __init__(self, num1, num2, result):
        super().__init__(
            title="認証 | Verify",
            timeout=None
        )
        self.answer = discord.ui.TextInput(
            label=f"{str(num1)}+{str(num2)}はいくつですか?",
            style=discord.TextStyle.short,
            placeholder="例: 5",
            required=True
        )
        self.result = result
        self.add_item(self.answer)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if int(self.answer.value) == self.result:
            try:
                with open(f"file/verify/{str(interaction.guild_id)}.txt", "r") as role_file:
                    content = json.load(role_file)
                    role = interaction.guild.get_role(content["role_id"])
                    if role is None:
                        embed = discord.Embed(
                            "❌ Failure - Verify", description="エラーが発生しました。\n認証ロールが設定されていません。サーバーの管理者にお問い合わせください")
                        embed.set_footer(text="Status - 400 | Made by Tettu0530New#7110",
                                         icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                    if role in interaction.user.roles:
                        return await interaction.response.send_message("あなたは認証対象ではありません。\n既にロール{}(ID:{})を持っています".format(role.mention, role.id), ephemeral=True)
                    await interaction.user.add_roles(role)
                    return await interaction.response.send_message("認証に成功しました。", ephemeral=True)
            except FileNotFoundError:
                embed = discord.Embed(
                    "❌ Failure - Verify", description="エラーが発生しました。\n認証ロールが設定されていません。サーバーの管理者にお問い合わせください")
                embed.set_footer(text="Status - 200 | Made by Tettu0530New#7110",
                                 icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            return await interaction.response.send_message("認証に失敗しました。もう一度ボタンを押してください。", ephemeral=True)


class VerifyButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ 認証/Verify", style=discord.ButtonStyle.green, custom_id="persistent_view:btn_verify")
    async def callback_verify(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            with open(f"file/verify/{str(button.guild_id)}.txt", "r") as f:
                content = json.load(f)
                if content["type"] == "math":
                    num1 = random.randint(0, 9)
                    num2 = random.randint(0, 9)
                    result = num1 + num2
                    await button.response.send_modal(VerifyModal(num1=num1, num2=num2, result=result))
                elif content["type"] == "oneclick":
                    role = button.guild.get_role(content["role_id"])
                    if role is None:
                        embed = discord.Embed(
                            "❌ Failure - Verify", description="エラーが発生しました。\n認証ロールが設定されていません。サーバーの管理者にお問い合わせください")
                        embed.set_footer(text="Status - 400 | Made by Tettu0530New#7110",
                                         icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                        await button.response.send_message(embed=embed, ephemeral=True)
                    if role in button.user.roles:
                        return await button.response.send_message("あなたは認証対象ではありません。\n既にロール{}(ID:{})を持っています".format(role.mention, role.id), ephemeral=True)
                    await button.user.add_roles(role)
                    return await button.response.send_message("認証に成功しました。", ephemeral=True)
        except FileNotFoundError:
            embed = discord.Embed(
                "❌ Failure - Verify", description="エラーが発生しました。\n認証ロールが設定されていません。サーバーの管理者にお問い合わせください")
            embed.set_footer(text="Status - 400 | Made by Tettu0530New#7110",
                             icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            await button.response.send_message(embed=embed, ephemeral=True)
        except discord.errors.Forbidden:
            embed = discord.Embed(
                "❌ Failure - Verify", description="エラーが発生しました。\nBotに必要な権限が付与されていません。サーバーの管理者にお問い合わせください")
            embed.set_footer(text="Status - 403 | Made by Tettu0530New#7110",
                             icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")


class VerifyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(VerifyButtonView(bot=self.bot))
        print("[COGS]VerifySlashCog on ready.")

    @app_commands.command(
        name="verify",
        description="計算式認証パネルを設置します"
    )
    @app_commands.checks.cooldown(1, 10, key=lambda i:(i.guild_id, i.user.id))
    @app_commands.describe(role="認証完了後のロールを設定できます")
    @app_commands.describe(type="認証に使用するモードを選択できます(math=計算式認証 oneclick=ワンボタン認証)")
    @app_commands.describe(title="認証パネルのタイトルを設定できます")
    @app_commands.describe(description="認証パネルの説明文を設定できます")
    @app_commands.describe(picture="認証パネルの画像を添付できます")
    async def verify(self, interaction: discord.Interaction, role: discord.Role, type: typing.Literal["math", "oneclick"], title: str = None, description: str = None, picture: discord.Attachment = None):
        if interaction.user.guild_permissions.administrator:
            embed = discord.Embed(color=0x00ff00)
            if title is None:
                embed.title = "認証 | Verify"
            else:
                embed.title = title
            if description is None:
                embed.description = "認証するには以下のボタンを押してください。"
            else:
                embed.description = description
            if picture is None:
                pass
            else:
                embed.set_image(url=picture.url)
            embed.set_footer(text="Status - 200 | Made by Tettu0530New#7110",
                             icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            if type == "math":
                role_json = {
                    "role_id": role.id,
                    "guild_id": interaction.guild_id,
                    "type": "math"
                }
                embed_type = "計算式認証"
            elif type == "oneclick":
                role_json = {
                    "role_id": role.id,
                    "guild_id": interaction.guild_id,
                    "type": "oneclick"
                }
                embed_type = "ワンクリック認証"
            embed_success = discord.Embed(
                title="✅Success - Verify", description="認証パネルの設置に成功しました。\nRoleName: {} (ID:{})\nType: {}".format(role.name, str(role.id), embed_type), color=0x00ff00)
            embed_success.set_footer(text="Status - 200 | Made by Tettu0530New#7110",
                                     icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            with open(f"file/verify/{str(interaction.guild_id)}.txt", "w", encoding="utf-8") as role_file:
                json.dump(role_json, role_file)
            await interaction.response.send_message(embed=embed_success, ephemeral=True)
            await interaction.followup.send(embed=embed, view=VerifyButtonView(bot=self.bot))
            print(f"[{datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')}]{interaction.user.name}(ID:{interaction.user.id})がverifyコマンドをサーバー:{str(interaction.guild_id)}で使用しました。")
        
    @verify.error
    async def verify_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.CommandOnCooldown):
            await interaction.response.send_message("コマンドはクールダウン中です！", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(VerifyCog(bot))
