# Import General Package
import asyncio
import json
import os
import datetime
import pytz

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands


class TicketCloseReasonModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            title="理由 | Reason",
            timeout=None
        )
        self.reason = discord.ui.TextInput(
            label="理由を記入してください",
            style=discord.TextStyle.long,
            placeholder="例: 間違えて開いたため",
            required=True
        )
        self.bot = bot
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if os.path.isfile(f"file/ticket/{str(interaction.guild_id)}.txt") is True:
            embed_closed = discord.Embed(
                title="**Ticket Closed**", color=0xff0000)
            embed_closed.add_field(
                name="🆔チケットID | Ticket ID", value=f"`{interaction.channel.name}`", inline=False)
            embed_closed.add_field(
                name="⏰閉じた時間 | Closed Time", value=f"`{str(datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'))}`", inline=False)
            embed_closed.add_field(
                name="🔐閉じたユーザー | Closed by", value=f"{interaction.user.mention} (ID:`{interaction.user.id}`)", inline=False)
            embed_closed.add_field(
                name="❔閉じた理由 | Reason", value=f"`{self.reason.value}`", inline=False)
            embed_closed.set_thumbnail(url=interaction.user.avatar.url)
            embed_closed.set_footer(text="Status - 200 | Made by Tettu0530New#7110",
                                    icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            with open(f"file/ticket/{str(interaction.guild_id)}.txt", "r") as f:
                f_name = f"log/tickets/{str(datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y_%m_%d--%H_%M_%S'))}--{interaction.channel.name}.txt"
                with open(f_name, "w", encoding="utf-8") as f2:
                    content = []
                    async for msg in interaction.channel.history(limit=1000):
                        if not msg.attachments:
                            content.append(f"{msg.author} | {msg.content}")
                        else:
                            content.append(f"{msg.author} | {msg.attachments}")
                    content.reverse()
                    for i in content:
                        f2.write(i+"\n")
                json_ticket_info = json.load(f)
                logs_channel = self.bot.get_channel(
                    json_ticket_info["logs_channel"])
                if logs_channel is None:
                    pass
                else:
                    await logs_channel.send(embed=embed_closed, file=discord.File(f_name, filename=f"{interaction.channel.name}_logs.txt"))
            await interaction.response.send_message("3秒後にチケットを消去します...")
            await asyncio.sleep(3)
            return await interaction.channel.delete()
        else:
            return await interaction.channel.delete()


class TicketCloseConfirmButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot, is_reason: bool = None):
        super().__init__(timeout=None)
        self.is_reason = is_reason
        self.bot = bot

    @discord.ui.button(label="⭕はい", style=discord.ButtonStyle.secondary, custom_id="persistent_view:btn_ticketclose_confirm")
    async def callback_closeconfirm(self, button: discord.Button, interaction: discord.Interaction):
        if self.is_reason is False:
            if os.path.isfile(f"file/ticket/{str(button.guild_id)}.txt") is True:
                embed_closed = discord.Embed(
                    title="**Ticket Closed**", color=0xff0000)
                embed_closed.add_field(
                    name="🆔チケットID | Ticket ID", value=f"`{button.channel.name}`", inline=False)
                embed_closed.add_field(
                    name="⏰閉じた時間 | Closed Time", value=f"`{str(datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'))}`", inline=False)
                embed_closed.add_field(
                    name="🔐閉じたユーザー | Closed by", value=f"{button.user.mention} (ID:`{button.user.id}`)", inline=False)
                embed_closed.add_field(
                    name="❔閉じた理由 | Reason", value=f"`理由が記入されていません`", inline=False)
                embed_closed.set_thumbnail(url=button.user.avatar.url)
                embed_closed.set_footer(text="Status - 200 | Made by Tettu0530New#7110",
                                        icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                with open(f"file/ticket/{str(button.guild_id)}.txt", "r") as f:
                    f_name = f"log/tickets/{str(datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y_%m_%d--%H_%M_%S'))}--{button.channel.name}.txt"
                    with open(f_name, "w", encoding="utf-8") as f2:
                        content = []
                        async for msg in button.channel.history(limit=1000):
                            if not msg.attachments:
                                content.append(f"{msg.author} | {msg.content}")
                            else:
                                content.append(
                                    f"{msg.author} | {msg.attachments}")
                        content.reverse()
                        for i in content:
                            f2.write(i+"\n")
                    json_ticket_info = json.load(f)
                    logs_channel = self.bot.get_channel(
                        json_ticket_info["logs_channel"])
                    if logs_channel is None:
                        pass
                    else:
                        await logs_channel.send(embed=embed_closed, file=discord.File(f_name, filename=f"{button.channel.name}_logs.txt"))
                await button.channel.delete()
            else:
                await button.channel.delete()
        else:
            await button.response.send_modal(TicketCloseReasonModal(bot=self.bot))

    @discord.ui.button(label="❌キャンセル", style=discord.ButtonStyle.secondary, custom_id="persistent_view:btn_ticketclose_deny")
    async def callback_closedeny(self, button: discord.Button, interaction: discord.Interaction):
        await button.message.delete()


class TicketCloseButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label="🔐チケットを閉じる", style=discord.ButtonStyle.danger, custom_id="persistent_view:btn_ticketclose")
    async def callback_ticketclose(self, button: discord.Button, interaction: discord.Interaction):
        await button.response.send_message("本当にチケットを閉じてよろしいですか?", view=TicketCloseConfirmButtonView(bot=self.bot, is_reason=False))

    @discord.ui.button(label="🔐理由を指定して閉じる", style=discord.ButtonStyle.danger, custom_id="persistent_view:btn_ticketclosereason")
    async def callback_ticketclose_reason(self, button: discord.Button, interaction: discord.Interaction):
        await button.response.send_message("本当にチケットを閉じてよろしいですか?", view=TicketCloseConfirmButtonView(bot=self.bot, is_reason=True))
    
    @discord.ui.button(label="🙋‍♀️このチケットを担当する", style=discord.ButtonStyle.green, custom_id="persistent_view:btn_ticketresponsible")
    async def callback_ticketresponsible(self, button: discord.Button, interaction: discord.Interaction):
        embed = discord.Embed(title="✅ Success - Ticket", description=f"このチケットは{button.user.mention}が担当します。", color=0x00ff00)
        embed.set_footer(text="Status - 200 | Made by Tettu0530New#7110",
                               icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
        await button.response.send_message(embed=embed)


class TicketButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫チケットを開く", style=discord.ButtonStyle.primary, custom_id="persistent_view:btn_ticket")
    async def callback_ticket(self, button: discord.Button, interaction: discord.Interaction):
        ch_name = f"ticket-{button.user.name}"
        overwrites = {
            button.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            button.user: discord.PermissionOverwrite(read_messages=True)
        }
        newch = await button.channel.category.create_text_channel(name=ch_name, overwrites=overwrites)
        await button.response.send_message(f"{newch.mention} を作成しました。", ephemeral=True)
        close_embed = discord.Embed(
            title="チケット", description="チケットを開きました。\n問い合わせ内容を記入し、スタッフからの対応をお待ちください。\nチケットを閉じるには下のボタンを押してください。")
        close_embed.set_footer(text="Status - 200 | Made by Tettu0530New#7110",
                               icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
        await newch.send(f"{button.user.mention}", embed=close_embed, view=TicketCloseButtonView(bot=self.bot))

        if os.path.isfile(f"file/ticket/{button.guild.id}.txt") is True:
            embed_closed = discord.Embed(
                title="**Ticket Opened**", color=0x00ff00)
            embed_closed.add_field(
                name="❔チケットパネルの場所 | Ticket location", value=f"`{button.channel.name}`", inline=False)
            embed_closed.add_field(
                name="🆔チケットID | Ticket ID", value=f"`{newch.name}`", inline=False)
            embed_closed.add_field(
                name="⏰開いた時間 | Opened Time", value=f"`{str(datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'))}`", inline=False)
            embed_closed.add_field(
                name="🔐開いたユーザー | Opened by", value=f"{button.user.mention} (ID:`{button.user.id}`)", inline=False)
            embed_closed.set_thumbnail(url=button.user.avatar.url)
            embed_closed.set_footer(text="Status - 200 | Made by Tettu0530New#7110",
                                    icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            try:
                with open(f"file/ticket/{button.guild.id}.txt", "r") as f:
                    json_ticket_info = json.load(f)
                    logs_channel = self.bot.get_channel(json_ticket_info["logs_channel"])
                    if logs_channel is None:
                        pass
                    else:
                        await logs_channel.send(embed=embed_closed)
            except FileNotFoundError:
                pass


class TicketCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        class_list = [
            TicketCloseConfirmButtonView(bot=self.bot),
            TicketCloseButtonView(bot=self.bot),
            TicketButtonView(bot=self.bot)
        ]
        for i in class_list:
            self.bot.add_view(i)
        print("[COGS]TicketSlashCog on ready.")

    ticket = app_commands.Group(name="ticket", description="チケット関係のコマンド")

    @ticket.command(
        name="set",
        description="チケットパネルを設置できます"
    )
    @app_commands.describe(title="チケットパネルのタイトルを設定できます")
    @app_commands.describe(description="チケットパネルの説明を設定できます")
    @app_commands.describe(picture="チケットパネルの写真を設定できます")
    async def ticket_Set(self, interaction: discord.Interaction, title: str = None, description: str = None, picture: discord.Attachment = None):
        panel_embed = discord.Embed(color=0xa9ceec)
        if title is None:
            panel_embed.title = "お問い合わせ"
        else:
            panel_embed.title = title
        if description is None:
            panel_embed.description = "チケットを開くには下のボタンを押してください"
        else:
            panel_embed.description = description
        if picture is None:
            pass
        else:
            panel_embed.set_image(url=picture.url)
        panel_embed.set_footer(text="Status - 200 | Made by Tettu0530New#7110",
                               icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
        embed_success = discord.Embed(
            title="✅Success - Ticket", description="チケットパネルの設置に成功しました。", color=0x00ff00)
        embed_success.set_footer(text="Status - 200 | Made by Tettu0530New#7110",
                                 icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
        await interaction.response.send_message(embed=embed_success, ephemeral=True)
        await interaction.followup.send(embed=panel_embed, view=TicketButtonView(bot=self.bot))

    @ticket.command(
        name="config",
        description="チケットパネルの設定"
    )
    @app_commands.describe(notify="チケットが開いた時に管理者をを通知するかどうか")
    @app_commands.describe(logs_channel="チケットログチャンネルを設定するかどうか")
    async def ticket_config(self, interaction: discord.Interaction, notify: discord.Role = None, logs_channel: discord.TextChannel = None):
        await interaction.response.send_message("処理中...", ephemeral=True)
        await asyncio.sleep(1)
        if notify is None:
            pass
        else:
            try:
                with open(f"file/ticket/{str(interaction.guild_id)}.txt", "r") as f:
                    content = json.load(f)
                    with open(f"file/ticket/{str(interaction.guild_id)}.txt", "w", encoding="utf-8") as f2:
                        content["notify"] = notify.id
                        json.dump(content, f2)
                await interaction.followup.send("登録しました。\nNotify: {}(RoleID: {})".format(notify.mention, str(notify.id)), ephemeral=True)
            except FileNotFoundError:
                with open(f"file/ticket/{str(interaction.guild_id)}.txt", "w", encoding="utf-8") as f3:
                    content = {
                        "guild_id": interaction.guild_id,
                        "notify": notify.id
                    }
                    json.dump(content, f3)
                await interaction.followup.send("登録しました。\nNotify: {}(RoleID: {})".format(notify.mention, str(notify.id)), ephemeral=True)
        if logs_channel is None:
            pass
        else:
            try:
                with open(f"file/ticket/{str(interaction.guild_id)}.txt", "r") as f:
                    content = json.load(f)
                    with open(f"file/ticket/{str(interaction.guild_id)}.txt", "w", encoding="utf-8") as f4:
                        content["logs_channel"] = logs_channel.id
                        json.dump(content, f4)
                await interaction.followup.send("登録しました。\nLogChannel: {}(ChannelID: {})".format(logs_channel.mention, str(logs_channel.id)), ephemeral=True)
            except FileNotFoundError:
                with open(f"file/ticket/{str(interaction.guild_id)}.txt", "w", encoding="utf-8") as f5:
                    content = {
                        "guild_id": interaction.guild_id,
                        "logs_channel": logs_channel.id
                    }
                    json.dump(content, f5)
                await interaction.followup.send("登録しました。\nLogChannel: {}(ChannelID: {})".format(logs_channel.mention, str(logs_channel.id)), ephemeral=True)
        if notify is None and logs_channel is None:
            embed = discord.Embed(title="❌ Failure - TicketConfig",
                                  description="エラーが発生しました。\n必要な引数(notifyまたはlogs_channel)を入力してください", color=0xff0000)
            embed.set_footer(text="Status - 200 | Made by Tettu0530New#7110",
                             icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(TicketCog(bot))
