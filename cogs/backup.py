# Import General Package
import asyncio
import json
import os
import datetime
import pytz
import shutil

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands


class BackupPasswordModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, username: str):
        super().__init__(
            title="バックアップ | Backup",
            timeout=None
        )
        self.password = discord.ui.TextInput(
            label="復元パスワード | Restore PassWord",
            style=discord.TextStyle.short,
            placeholder="例: password",
            max_length=20,
            required=True
        )
        self.add_item(self.password)
        self.bot = bot
        self.username = username

    async def on_submit(self, interaction: discord.Interaction) -> None:
        server = interaction.guild
        channels = server.channels
        roles = server.roles
        emojis = server.emojis

        backup_data = {
            "user_id": interaction.user.id,
            "username": self.username,
            "guild_id": interaction.guild_id,
            "password": self.password.value,
            "backup_date": str(datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M:%S")),
            "name": server.name,
            "description": server.description,
            "channels": [],
            "roles": [],
            "emojis": [],
        }

        categories = server.categories

        for category in categories:
            category_data = {
                "name": category.name,
                "text_channels": [],
                "voice_channels": [],
                "stage_channels": [],
            }

            channels = category.channels

            for channel in channels:
                if isinstance(channel, discord.TextChannel):
                    channel_data = {
                        "name": channel.name,
                        "topic": channel.topic,
                        "position": channel.position
                    }
                    category_data["text_channels"].append(channel_data)

                elif isinstance(channel, discord.VoiceChannel):
                    channel_data = {
                        "name": channel.name,
                        "bitrate": channel.bitrate,
                        "user_limit": channel.user_limit,
                        "position": channel.position
                    }
                    category_data["voice_channels"].append(channel_data)

                elif isinstance(channel, discord.StageChannel):
                    channel_data = {
                        "name": channel.name,
                        "bitrate": channel.bitrate,
                        "user_limit": channel.user_limit,
                        "position": channel.position
                    }
                    category_data["stage_channels"].append(channel_data)
            backup_data["channels"].append(category_data)
        
        for role in roles:
            role_data = {
                "name": role.name,
                "permissions": role.permissions.value,
                "color": role.color.value,
                "hoist": role.hoist
            }
            backup_data["roles"].append(role_data)
        
        for emoji in emojis:
            emoji_data = {
                "name": emoji.name,
                "url": emoji.url,
            }
            backup_data["emojis"].append(emoji_data)
        
        if os.path.isdir(f"file/account/{self.username}/backup"):
            with open(f"file/account/{self.username}/backup/{str(interaction.guild_id)}", "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2)
        else:
            os.mkdir(f"file/account/{self.username}/backup")
            with open(f"file/account/{self.username}/backup/{str(interaction.guild_id)}", "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2)
        
        await interaction.response.send_message(f"バックアップが完了しました。以下の情報は**必ずメモ**してください(復元時に使用します)\nサーバーID: {str(interaction.guild_id)}", ephemeral=True)


class ServerBackupConfirmButton(discord.ui.View):
    def __init__(self, bot: commands.Bot, username: str = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.username = username

    @discord.ui.button(label="⬆バックアップ/Backup", style=discord.ButtonStyle.green, custom_id="persistent_view:btn_backupconfirm")
    async def callback_backup_confrim(self, button: discord.ui.Button, interaction: discord.Interaction):
        await button.response.send_modal(BackupPasswordModal(bot=self.bot, username=self.username))


class AccountLoginModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            title="ログイン | Login",
            timeout=None
        )
        self.username = discord.ui.TextInput(
            label="ユーザー名 | UserName",
            style=discord.TextStyle.short,
            placeholder="例: Tettu0530",
            max_length=20,
            required=True
        )
        self.password = discord.ui.TextInput(
            label="パスワード | PassWord",
            style=discord.TextStyle.short,
            placeholder="例: password",
            max_length=30,
            required=True
        )
        self.add_item(self.username)
        self.add_item(self.password)
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if os.path.isdir(f"file/account/{self.username.value}"):
            try:
                with open(f"file/account/{self.username.value}/info.txt", "r") as f:
                    content = json.load(f)
                    if content["username"] == self.username.value:
                        if content["password"] == self.password.value:
                            if content["subscription"] == "True":
                                if content["user_id"] == interaction.user.id:
                                    embed = discord.Embed(
                                        title="✅ BackupConfirm - Success", color=0x00ff00)
                                    embed.add_field(
                                        name="サーバー名", value=f"{interaction.guild.name}", inline=False)
                                    embed.add_field(
                                        name="サーバーID", value=f"{str(interaction.guild_id)}", inline=True)
                                    embed.add_field(
                                        name="サーバー説明", value=f"`{interaction.guild.description}`", inline=True)
                                    embed.add_field(
                                        name="チャンネル", value=f"{str(len(interaction.guild.channels))}(C{str(len(interaction.guild.categories))} V{str(len(interaction.guild.voice_channels))} T{str(len(interaction.guild.text_channels))} S{str(len(interaction.guild.stage_channels))})", inline=True)
                                    embed.add_field(
                                        name="ロール", value=f"{str(len(interaction.guild.roles))}", inline=True)
                                    await interaction.response.send_message("この情報でサーバーをバックアップしますか?", embed=embed, view=ServerBackupConfirmButton(bot=self.bot, username=content["username"]), ephemeral=True)
                                else:
                                    await interaction.response.send_message("このZeTNONアカウントはあなたのDiscordアカウントと連携されていません。`/account relink`を使ってアカウントを再連携してください", ephemeral=True)
                            else:
                                await interaction.response.send_message("あなたのZeTNONアカウントは有料プランを適応させていません。`/account subscription`にて契約を有効化してからこのコマンドを実行してください\n※有料プラン申請後は適応されるまで多少時間がかかります。", ephemeral=True)
                        else:
                            await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
                    else:
                        await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
            except FileNotFoundError:
                await interaction.response.send_message("そのZeTNONアカウントは登録されていません。", ephemeral=True)
        else:
            await interaction.response.send_message("ZeTNONアカウントを登録していません。`/account register`のあとにこのコマンドを実行してください", ephemeral=True)


class BuckupCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        class_list = [
            ServerBackupConfirmButton(bot=self.bot, username=None)
        ]
        print("[COGS]BackupSlashCog on ready.")
        for i in class_list:
            self.bot.add_view(i)

    backup = app_commands.Group(name="backup", description="バックアップ関係のコマンド")

    @backup.command(
        name="create",
        description="サーバーをバックアップします(サーバー・チャンネル・ロールがバックアップされます)"
    )
    async def backup_create(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AccountLoginModal(bot=self.bot))


async def setup(bot: commands.Bot):
    await bot.add_cog(BuckupCog(bot))
