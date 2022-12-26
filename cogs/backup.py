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
            label="パスワード | PassWord",
            style=discord.TextStyle.short,
            placeholder="例: password",
            max_length=20,
            required=True
        )
        self.add_item(self.password)
        self.bot = bot
        self.username = username

    async def on_submit(self, interaction: discord.Interaction) -> None:
        with open(f"file/account/{str(interaction.user.id)}/backup/user_info.txt", "w", encoding="utf-8") as f:
            content = {
                "user_id": interaction.user.id,
                "username": self.username,
                "guild_id": interaction.guild_id,
                "password": self.password.value,
                "backup_date": str(datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M:%S"))
            }
            json.dump(content)


class ServerBackupConfirmButton(discord.ui.View):
    def __init__(self, bot: commands.Bot, username: str = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.username = username

    @discord.ui.button(label="⬆バックアップ/Backup", style=discord.ButtonStyle.green, custom_id="persistent_view:btn_backupconfirm")
    async def callback_backup_confrim(self, button: discord.ui.Button, interaction: discord.Interaction):
        await button.response.send_modal()

    @discord.ui.button(label="⬆キャンセル/Cancel", style=discord.ButtonStyle.danger, custom_id="persistent_view:btn_backupcdeny")
    async def callback_backup_(self, button: discord.ui.Button, interaction: discord.Interaction):
        shutil.rmtree(f"file/account/{str(interaction.user.id)}/backup")
        await button.response.send_message("バックアップを取り消しました。", ephemeral=True)


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
        if os.path.isdir(f"file/account/{str(interaction.user.id)}"):
            try:
                with open(f"file/account/{str(interaction.user.id)}/{self.username.value}.txt", "r") as f:
                    content = json.load(f)
                    if content["username"] == self.username.value:
                        if content["password"] == self.password.value:
                            if content["subscription"] == "True":
                                await interaction.response.defer()
                                guild = interaction.guild
                                guild_name = guild.name
                                guild_id = guild.id
                                guild_description = guild.description
                                guild_verification_level = guild.verification_level
                                guild_vanity_url = guild.vanity_url_code
                                guild_category_channels = guild.categories
                                guild_text_channels = guild.text_channels
                                guild_voice_channels = guild.voice_channels
                                guild_stage_channels = guild.stage_channels
                                guild_system_channel = guild.system_channel
                                guild_rules_channel = guild.rules_channel
                                guild_updates_channel = guild.public_updates_channel
                                guild_role = guild.roles
                                if guild.icon is None:
                                    guild_icon = None
                                else:
                                    guild_icon = guild.icon.url

                                category_channels = {}
                                text_channels = {}
                                voice_channels = {}
                                stage_channels = {}
                                roles = {}

                                if len(guild_category_channels) == 0:
                                    category_channels = {}
                                else:
                                    a = 1
                                    for i in guild_category_channels:
                                        if a <= len(guild_category_channels):
                                            break
                                        else:
                                            category_channels[f"{str(a)}"] = {
                                                "channel_name": i.name,
                                                "channel_id": i.id,
                                                "position": i.position,
                                                "nsfw": str(i.nsfw)
                                            }
                                            a += 1
                                if len(guild_text_channels) == 0:
                                    text_channels = {}
                                else:
                                    b = 1
                                    for i in guild_text_channels:
                                        if a <= len(guild_text_channels):
                                            break
                                        else:
                                            if i.category is None:
                                                text_channels[f"{str(b)}"] = {
                                                    "channel_name": i.name,
                                                    "channel_id": i.id,
                                                    "position": i.position,
                                                    "nsfw": str(i.nsfw),
                                                    "news": str(i.is_news)
                                                }
                                                b += 1
                                            else:
                                                text_channels[f"{str(b)}"] = {
                                                    "channel_name": i.name,
                                                    "channel_id": i.id,
                                                    "position": i.position,
                                                    "nsfw": str(i.nsfw),
                                                    "news": str(i.is_news),
                                                    "category": str(i.category.name)
                                                }
                                                b += 1
                                if len(guild_voice_channels) == 0:
                                    voice_channels = {}
                                else:
                                    c = 1
                                    for i in guild_voice_channels:
                                        if a <= len(guild_voice_channels):
                                            break
                                        else:
                                            if i.category is None:
                                                voice_channels[f"{str(c)}"] = {
                                                    "channel_name": i.name,
                                                    "channel_id": i.id,
                                                    "position": i.position,
                                                    "nsfw": str(i.nsfw),
                                                    "bitrate": i.bitrate,
                                                    "user_limit": i.user_limit
                                                }
                                                c += 1
                                            else:
                                                voice_channels[f"{str(c)}"] = {
                                                    "channel_name": i.name,
                                                    "channel_id": i.id,
                                                    "position": i.position,
                                                    "nsfw": str(i.nsfw),
                                                    "bitrate": i.bitrate,
                                                    "user_limit": i.user_limit,
                                                    "category": str(i.category.name)
                                                }
                                                c += 1
                                if len(guild_stage_channels) == 0:
                                    stage_channels = {}
                                else:
                                    d = 1
                                    for i in guild_stage_channels:
                                        if a <= len(guild_stage_channels):
                                            break
                                        else:
                                            if i.category is None:
                                                stage_channels[f"{str(d)}"] = {
                                                    "channel_name": i.name,
                                                    "channel_id": i.id,
                                                    "position": i.position,
                                                    "nsfw": str(i.nsfw),
                                                    "topic": i.topic,
                                                    "bitrate": i.bitrate,
                                                    "user_limit": i.user_limit
                                                }
                                                d += 1
                                            else:
                                                stage_channels[f"{str(d)}"] = {
                                                    "channel_name": i.name,
                                                    "channel_id": i.id,
                                                    "position": i.position,
                                                    "nsfw": str(i.nsfw),
                                                    "topic": i.topic,
                                                    "bitrate": i.bitrate,
                                                    "user_limit": i.user_limit,
                                                    "category": str(i.category.name)
                                                }
                                                d += 1
                                if len(guild_role) <= 1:
                                    roles = {}
                                else:
                                    e = 1
                                    for i in guild_role:
                                        if a <= len(guild_role):
                                            break
                                        else:
                                            roles[f"{str(e)}"] = {
                                                "role_name": i.name,
                                                "role_id": i.id,
                                                "role_color": str(i.color),
                                                "role_permissions": {
                                                    "add_reactions": str(i.permissions.add_reactions),
                                                    "administrator": str(i.permissions.administrator),
                                                    "attach_files": str(i.permissions.attach_files),
                                                    "ban_members": str(i.permissions.ban_members),
                                                    "change_nickname": str(i.permissions.change_nickname),
                                                    "connect": str(i.permissions.connect),
                                                    "create_instant_invite": str(i.permissions.create_instant_invite),
                                                    "create_private_threads": str(i.permissions.create_private_threads),
                                                    "create_public_threads": str(i.permissions.create_public_threads),
                                                    "deafen_members": str(i.permissions.deafen_members),
                                                    "embed_links": str(i.permissions.embed_links),
                                                    "external_emojis": str(i.permissions.external_emojis),
                                                    "external_stickers": str(i.permissions.external_stickers),
                                                    "kick_members": str(i.permissions.kick_members),
                                                    "manage_channels": str(i.permissions.manage_channels),
                                                    "manage_emojis": str(i.permissions.manage_emojis),
                                                    "manage_emojis_and_stickers": str(i.permissions.manage_emojis_and_stickers),
                                                    "manage_events": str(i.permissions.manage_events),
                                                    "manage_guild": str(i.permissions.manage_guild),
                                                    "manage_messages": str(i.permissions.manage_messages),
                                                    "manage_nicknames": str(i.permissions.manage_nicknames),
                                                    "manage_permissions": str(i.permissions.manage_permissions),
                                                    "manage_roles": str(i.permissions.manage_roles),
                                                    "manage_threads": str(i.permissions.manage_threads),
                                                    "manage_webhooks": str(i.permissions.manage_webhooks),
                                                    "mention_everyone": str(i.permissions.mention_everyone),
                                                    "moderate_members": str(i.permissions.moderate_members),
                                                    "move_members": str(i.permissions.move_members),
                                                    "mute_members": str(i.permissions.mute_members),
                                                    "priority_speaker": str(i.permissions.priority_speaker),
                                                    "ready_message_history": str(i.permissions.read_message_history),
                                                    "read_messages": str(i.permissions.read_messages),
                                                    "request_to_talk": str(i.permissions.request_to_speak),
                                                    "send_messages": str(i.permissions.send_messages),
                                                    "send_messages_in_threads": str(i.permissions.send_messages_in_threads),
                                                    "send_tts_messages": str(i.permissions.send_tts_messages),
                                                    "speak": str(i.permissions.speak),
                                                    "stream": str(i.permissions.stream),
                                                    "use_application_commands": str(i.permissions.use_application_commands),
                                                    "use_embedded_activities": str(i.permissions.use_embedded_activities),
                                                    "use_external_emojis": str(i.permissions.use_external_emojis),
                                                    "use_external_stickers": str(i.permissions.use_external_stickers),
                                                    "use_voice_activation": str(i.permissions.use_voice_activation),
                                                    "view_audit_log": str(i.permissions.view_audit_log),
                                                    "view_channel": str(i.permissions.view_channel),
                                                    "view_guild_insights": str(i.permissions.view_guild_insights)
                                                }
                                            }
                                            e += 1
                                general_settings = {
                                    "guild_name": guild_name,
                                    "guild_id": guild_id,
                                    "guild_verification_level": guild_verification_level,
                                    "channel_num": len(interaction.guild.channels)
                                }

                                if guild_vanity_url is None:
                                    general_settings["guild_vanity_url"] = "None"
                                else:
                                    general_settings["guild_vanity_url"] = guild_vanity_url
                                if guild_description is None:
                                    general_settings["guild_description"] = "None"
                                else:
                                    general_settings["guild_description"] = guild_description
                                if guild_system_channel is None:
                                    general_settings["guild_system_channel"] = "None"
                                else:
                                    general_settings["guild_system_channel"] = guild_system_channel.name
                                if guild_rules_channel is None:
                                    general_settings["guild_rules_channel"] = "None"
                                else:
                                    general_settings["guild_rules_channel"] = guild_rules_channel.name
                                if guild_updates_channel is None:
                                    general_settings["guild_updates_channel"] = "None"
                                else:
                                    general_settings["guild_updates_channel"] = guild_updates_channel.name
                                if os.path.isdir(f"file/account/{str(interaction.user.id)}/backup/{str(interaction.guild.id)}"):
                                    pass
                                else:
                                    os.makedirs(
                                        f"file/account/{str(interaction.user.id)}/backup/{str(interaction.guild.id)}")
                                    with open(f"file/account/{str(interaction.user.id)}/backup/{str(interaction.guild_id)}/general.txt", "w", encoding="utf-8") as file_general:
                                        json.dump(general_settings,
                                                  file_general)
                                    with open(f"file/account/{str(interaction.user.id)}/backup/{str(interaction.guild_id)}/category_channel.txt", "w", encoding="utf-8") as file_categorych:
                                        json.dump(category_channels,
                                                  file_categorych)
                                    with open(f"file/account/{str(interaction.user.id)}/backup/{str(interaction.guild_id)}/text_channel.txt", "w", encoding="utf-8") as file_textch:
                                        json.dump(text_channels, file_textch)
                                    with open(f"file/account/{str(interaction.user.id)}/backup/{str(interaction.guild_id)}/voice_channel.txt", "w", encoding="utf-8") as file_voicech:
                                        json.dump(voice_channels, file_voicech)
                                    with open(f"file/account/{str(interaction.user.id)}/backup/{str(interaction.guild_id)}/role.txt", "w", encoding="utf-8") as file_role:
                                        json.dump(roles, file_role)
                                embed = discord.Embed(
                                    title="✅ Backup - Success", color=0x00ff00)
                                embed.add_field(
                                    name="サーバー名", value=f"{general_settings['guild_name']}", inline=False)
                                embed.add_field(
                                    name="サーバーID", value=f"{general_settings['guild_id']}", inline=True)
                                embed.add_field(
                                    name="サーバー説明", value=f"`{general_settings['guild_description']}`", inline=True)
                                embed.add_field(
                                    name="チャンネル", value=f"{str(len(interaction.guild.channels))}(C{str(len(category_channels))} V{str(len(voice_channels))} T{str(len(text_channels))} S{str(len(stage_channels))})", inline=True)
                                embed.add_field(
                                    name="ロール", value=f"{str(len(roles))}", inline=True)
                                await interaction.followup.send("この情報でサーバーをバックアップしますか?", embed=embed, view=ServerBackupConfirmButton(bot=self.bot, username=content["username"]), ephemeral=True)
                            else:
                                await interaction.response.send_message("あなたのZeTNONアカウントは有料プランを適応させていません。`/account subscription`にて契約を有効化してからこのコマンドを実行してください\n※有料プラン申請後は適応されるまで多少時間がかかります。", ephemeral=True)
                        else:
                            await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
                    else:
                        await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
            except FileNotFoundError:
                await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
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
