# Import General Package
import asyncio
import json
import uuid
import os
from PayPayPy import PayPay

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands


class OtpModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, phone_number: str, password: str, paypay: PayPay):
        super().__init__(title="OTP認証 | OTP Authorization")
        self.otp = discord.ui.TextInput(
            label=f"{phone_number}に届いた確認コード4桁を入力してください",
            style=discord.TextStyle.short,
            placeholder="例: 1234",
            required=True,
            max_length=4
        )
        self.add_item(self.otp)
        self.bot = bot
        self.phone_number = phone_number
        self.password = password
        self.paypay = paypay

    async def on_submit(self, interaction: discord.Interaction):
        login_otp_result = self.paypay.login_otp(str(self.otp.value))
        if login_otp_result.header.resultCode == "S0000":
            with open(f"file/paypay/{interaction.user.id}.json", "w", encoding="utf-8") as token_f:
                id = str(uuid.uuid4()).upper()
                data = {
                    "user_id": interaction.user.id,
                    "access_token": login_otp_result.payload.accessToken,
                    "paypayid": id
                }
                json.dump(data, token_f)
                paypay2 = PayPay(login_otp_result.payload.accessToken)
                embed = discord.Embed(title="✅ Success - Paypay login",
                                      description=f"**PayPay表示名**: `{paypay2.get_profile().payload.userPorfile.displayName}`\n\n**メールアドレス: `{paypay2.get_profile().payload.userProfile.mailAddress}`**\n\n**電話番号**: `{self.phone_number}`\n\n**パスワード**: `{len(self.password)*'*'}`\n\n**PayPayユーザー識別ID**: {id}")
                embed.set_footer(text="Status - 200 | Made by Tettu0530#0530",
                                 icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title="❌ Failure - Paypay login",
                                  description="OTP認証に失敗しました。確認コードが間違っている可能性があります。", color=0xff0000)
            embed.set_footer(text="Status - 403 | Made by Tettu0530#0530",
                             icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            await interaction.response.send_message(embed=embed, ephemeral=True)


class PayPayCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("[COGS]PayPaySlashCog on ready.")

    paypay = app_commands.Group(name="paypay", description="PayPay関係コマンド")

    @paypay.command(
        name="login",
        description="PayPayアカウントとお使いのDiscordアカウントを連携します"
    )
    @app_commands.describe(phone_number="PayPayアカウントで使用している電話番号(例:01234567890)")
    @app_commands.describe(password="PayPayアカウントで使用しているパスワード")
    async def paypay_login(self, interaction: discord.Interaction, phone_number: str, password: str):
        paypay = PayPay()
        login_result = paypay.login(phone_number, password)
        if login_result.header.resultCode == "S0000":
            await interaction.response.send_modal(OtpModal(bot=self.bot, phone_number=phone_number, password=password, paypay=paypay))
        else:
            embed = discord.Embed(title="❌ Failure - PayPay Login",
                                  description="電話番号またはパスワードが間違っています。", color=0xff0000)
            embed.set_footer(text="Status - 403 | Made by Tettu0530#0530",
                             icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @paypay.command(
        name="info",
        description="PayPayアカウントの情報を表示します"
    )
    async def paypay_info(self, interaction: discord.Interaction):
        try:
            with open(f"file/paypay/{interaction.user.id}.json", "r") as paypay_f:
                data = json.load(paypay_f)
                paypay = PayPay(data["access_token"])
                userProfile = paypay.get_profile().payload.userProfile
                avatar = userProfile.avatarImageUrl
                username = userProfile.displayName
                mail_addr = userProfile.mailAddress
                phone_num = userProfile.phoneNumber
                embed = discord.Embed(
                    title="✅ Success - PayPay Info", color=0x00ff00)
                embed.set_thumbnail(url=avatar)
                embed.add_field(
                    name="表示名", value=f"```\n{username}\n```", inline=False)
                embed.add_field(
                    name="メールアドレス", value=f"```\n{mail_addr}\n```", inline=False)
                embed.add_field(
                    name="電話番号", value=f"```\n{phone_num}\n```", inline=False)
                embed.set_footer(text="Status - 200 | Made by Tettu0530#0530",
                                 icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except FileNotFoundError:
            embed = discord.Embed(title="❌ Failure - PayPay Info",
                                  description="このDiscordアカウントは何もPayPayアカウントと連携されていません", color=0xff0000)
            embed.set_footer(text="Status - 400 | Made by Tettu0530#0530",
                             icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @paypay.command(
        name="balance",
        description="PayPayアカウントの残高を確認します"
    )
    async def paypay_balance(self, interaction: discord.Interaction):
        try:
            with open(f"file/paypay/{interaction.user.id}.json", "r") as paypay_f:
                data = json.load(paypay_f)
                paypay = PayPay(data["access_token"])
                print(dir(paypay.get_balance()))
                embed = discord.Embed(title="✅ Success - PayPay Balance",
                                      description=f"現在の総残高は\n```\n{str(paypay.get_balance().payload.walletSummary.allTotalBalanceInfo.balance)}円\n```です", color=0x00ff00)
                await interaction.response.send_message(embed=embed)
        except FileNotFoundError:
            embed = discord.Embed(title="❌ Failure - PayPay Balance",
                                  description="このDiscordアカウントは何もPayPayアカウントと連携されていません", color=0xff0000)
            embed.set_footer(text="Status - 400 | Made by Tettu0530#0530",
                             icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @paypay.command(
        name="accept",
        description="PayPay送金リンクの受け取りをします"
    )
    @app_commands.describe(pay_link="受け取るPayPayリンク(例: https://pay.paypay.ne.jp/QwErTyUiOpP12345)")
    @app_commands.describe(password="PayPay送金リンクにパスワードがある場合のパスワード")
    async def paypay_link(self, interaction: discord.Interaction, pay_link: str, password: str = None):
        try:
            await interaction.response.defer()
            with open(f"file/paypay/{interaction.user.id}.json", "r") as paypay_f:
                data = json.load(paypay_f)
                paypay = PayPay(data["access_token"])
                get_link_info = paypay.get_link(
                    pay_link.replace("https://pay.paypay.ne.jp/", ""))
                amount = get_link_info.payload.pendingP2PInfo.amount
                id = get_link_info.payload.pendingP2PInfo.orderId
                image = get_link_info.payload.pendingP2PInfo.imageUrl
                sender = get_link_info.payload.sender.displayName
                if password is not None:
                    get_pay = paypay.accept_link(pay_link.replace(
                        "https://pay.paypay.ne.jp/", ""), password)
                get_pay = paypay.accept_link(
                    pay_link.replace("https://pay.paypay.ne.jp/", ""))
                if get_pay.payload.orderStatus == "COMPLETED":
                    embed = discord.Embed(
                        title="✅ Success - PayPay Link", color=0x00ff00)
                    embed.set_thumbnail(url=image)
                    embed.add_field(name="送り主", value=f"`{sender}`")
                    embed.add_field(name="状態", value="`完了済み`", inline=False)
                    embed.add_field(
                        name="金額", value=f"`{amount}円`", inline=False)
                    embed.add_field(name="決済ID", value=f"`{id}`", inline=False)
                    await interaction.followup.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="❌ Failure - PayPay Link", description="不明なエラーが発生しました。もう一度お試しください", color=0xff0000)
                    embed.set_footer(text="Status - 400 | Made by Tettu0530#0530",
                                     icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                    await interaction.followup.send(embed=embed, ephemeral=True)
        except FileNotFoundError:
            embed = discord.Embed(title="❌ Failure - PayPay Link",
                                  description="このDiscordアカウントは何もPayPayアカウントと連携されていません", color=0xff0000)
            embed.set_footer(text="Status - 400 | Made by Tettu0530#0530",
                             icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @paypay.command(
        name="auto_accept",
        description="PayPay送金リンクを自動で受け取ります(チャンネル別に設定可能)"
    )
    @app_commands.choices(accept=[
        app_commands.Choice(name="ON", value="ON"),
        app_commands.Choice(name="OFF", value="OFF"),
    ])
    @app_commands.describe(channel="自動受け取りを行うチャンネルを指定できます")
    async def auto_accept(self, interaction: discord.Interaction, accept: app_commands.Choice[str], channel: discord.TextChannel = None):
        if os.path.isfile(f"file/paypay/{interaction.user.id}.json") is False:
            return await interaction.response.send_message("このDiscordアカウントはPayPayアカウントと連携されていません。先に`/paypay login`で連携してください")
        if accept.value == "ON":
            isAccept = True
        else:
            isAccept = False
        if channel is None:
            channel_id = interaction.channel.id
        else:
            channel_id = channel.id
        with open(f"file/auto_paypay/{channel_id}.json", "w", encoding="utf-8") as auto_f:
            data = {
                "user_id": interaction.user.id,
                "channel_id": channel_id,
                "isAccept": isAccept
            }
            json.dump(data, auto_f)
            await interaction.response.send_message(f"自動受け取りを設定しました。設定: {accept.name}\nチャンネル: {self.bot.get_channel(channel_id).mention}")


async def setup(bot: commands.Bot):
    await bot.add_cog(PayPayCog(bot))
