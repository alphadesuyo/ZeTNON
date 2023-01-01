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


class AccountRegisterModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            title="登録 | Register",
            timeout=None
        )
        self.username = discord.ui.TextInput(
            label="ユーザー名 | UserName (※半角英数字で20字以内)",
            style=discord.TextStyle.short,
            placeholder="例: Tettu0530",
            max_length=20,
            required=True
        )
        self.password = discord.ui.TextInput(
            label="パスワード | PassWord (※半角英数字30字以内)",
            style=discord.TextStyle.short,
            placeholder="例: password",
            max_length=30,
            required=True
        )
        self.password_2 = discord.ui.TextInput(
            label="パスワード再確認 | Confirm PassWord (※半角英数字30字以内)",
            style=discord.TextStyle.short,
            placeholder="例: password",
            max_length=30,
            required=True
        )
        self.add_item(self.username)
        self.add_item(self.password)
        self.add_item(self.password_2)
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if self.password.value == self.password_2.value:
            if os.path.isdir(f"file/account/{self.username.value}") is False:
                os.mkdir(f"file/account/{self.username.value}")
                with open(f"file/account/{self.username.value}/info.txt", "w", encoding="utf-8") as f:
                    now = datetime.datetime.now(tz=pytz.timezone(
                        "Asia/Tokyo")).strftime("%Y-%m-%d_%H-%M-%S")
                    content = {"username": self.username.value,
                               "password": self.password.value,
                               "user_id": interaction.user.id,
                               "user_avatar": interaction.user.avatar.url,
                               "subscription": "False",
                               "regist_time": now}
                    json.dump(content, f)
                with open(f"file/account/{self.username.value}/info.txt", "r") as f:
                    content1 = json.load(f)
                    content1["password"] = self.password.value
                    embed = discord.Embed(
                        title="✅ Success - Register", description=f"ZeTNONアカウントを登録しました。\n```\nユーザー名: {content1['username']}\nパスワード: {content1['password']}\n登録日時: {content1['regist_time']}\nDiscordUserID: {str(content1['user_id'])}\n```")
                    embed.set_footer(text="Status - 200 | Made by Tettu0530New#7110",
                                     icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(
                    title="❌ Failure - Register", description="エラーが発生しました。\nそのZeTNONアカウントは既に登録されています。")
                embed.set_footer(text="Status - 400 | Made by Tettu0530New#7110",
                                 icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("再入力パスワードが違います。もう一度やり直してください。", ephemeral=True)


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
        try:
            with open(f"file/account/{self.username.value}/info.txt", "r") as f:
                content = json.load(f)
                if content["username"] == self.username.value:
                    if content["password"] == self.password.value:
                        if content["user_id"] == interaction.user.id:
                            embed = discord.Embed(
                                title=f"{content['username']}のZeTNONアカウント")
                            user = self.bot.get_user(int(content["user_id"]))
                            embed.set_thumbnail(url=content["user_avatar"])
                            embed.add_field(
                                name="ユーザー名", value=f"{content['username']}", inline=False)
                            embed.add_field(
                                name="パスワード", value=f"`機密保護のため閲覧できません`", inline=False)
                            if content["subscription"] == "True":
                                embed.add_field(
                                    name="有料プラン", value="有効(永久)", inline=False)
                            else:
                                embed.add_field(
                                    name="有料プラン", value="無効", inline=False)
                            embed.add_field(
                                name="登録ユーザー", value=f"{user.mention}", inline=False)
                            embed.set_footer(text="Status - 200 | Made by Tettu0530New#7110",
                                             icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                            await interaction.response.send_message(embed=embed, ephemeral=True)
                        else:
                            await interaction.response.send_message("このZeTNONアカウントはあなたのDiscordアカウントと連携されていません。`/account relink`を使ってアカウントを再連携してください", ephemeral=True)
                    else:
                        await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
                else:
                    await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
        except FileNotFoundError:
            await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)


class AccountChangeUserNameModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, username):
        super().__init__(
            title="ユーザー名変更 | Change UserName",
            timeout=None
        )
        self.new_username = discord.ui.TextInput(
            label="新しいユーザー名 | New UserName (※半角英数字20字以内)",
            style=discord.TextStyle.short,
            max_length=20,
            required=True
        )
        self.add_item(self.new_username)
        self.bot = bot
        self.username = username

    async def on_submit(self, interaction: discord.Interaction) -> None:
        with open(f"file/account/{self.username}/info.txt", "r") as f:
            content = json.load(f)
            content2 = {"username": self.new_username.value,
                               "password": content["password"],
                               "user_id": interaction.user.id,
                               "subscription": content["subscription"],
                               "regist_time": content["regist_time"]}
            with open(f"file/account/{self.username}/info.txt", "w", encoding="utf-8") as f2:
                json.dump(content2, f2)
        os.rename(f"file/account/{self.username}", f"file/account/{self.new_username.value}")
        await interaction.response.send_message(f"ユーザー名を変更しました。\b`UserName: {self.new_username.value}`", ephemeral=True)


class AccountChangePassWordModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, username):
        super().__init__(
            title="パスワード変更 | Change PassWord",
            timeout=None
        )
        self.new_password = discord.ui.TextInput(
            label="新しいパスワード | New PassWord (※半角英数字30文字以内)",
            style=discord.TextStyle.short,
            max_length=20,
            required=True
        )
        self.add_item(self.new_password)
        self.bot = bot
        self.username = username

    async def on_submit(self, interaction: discord.Interaction) -> None:
            with open(f"file/account/{self.username}/info.txt", "r") as f:
                content = json.load(f)
                content2 = {"username": content["username"],
                                   "password": self.new_password.value,
                                   "user_id": interaction.user.id,
                                   "subscription": content["subscription"],
                                   "regist_time": content["regist_time"]}
            with open(f"file/account/{self.username}/info.txt", "w", encoding="utf-8") as f2:
                json.dump(content2, f2)
            await interaction.response.send_message(f"パスワードを変更しました。\b`PassWord: {self.new_password.value}`", ephemeral=True)


class AccountChangeSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot, username):

        options = [
            discord.SelectOption(label="UserName", description="ユーザー名を変更できます"),
            discord.SelectOption(label="PassWord", description="パスワードを変更できます")
        ]
        super().__init__(
            placeholder="どれか一つ選択してください...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.bot = bot
        self.username = username

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "UserName":
            await interaction.response.send_modal(AccountChangeUserNameModal(bot=self.bot, username=self.username))
        elif self.values[0] == "PassWord":
            await interaction.response.send_modal(AccountChangePassWordModal(bot=self.bot, username=self.username))
        else:
            pass


class AccountChangeSelectView(discord.ui.View):
    def __init__(self, bot: commands.Bot, username):
        super().__init__(timeout=None)
        self.add_item(AccountChangeSelect(bot=bot, username=username))


class AccountLogin2Modal(discord.ui.Modal):
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
        try:
            with open(f"file/account/{self.username.value}/info.txt", "r") as f:
                content = json.load(f)
                if content["username"] == self.username.value:
                    if content["password"] == self.password.value:
                        if content["user_id"] == interaction.user.id:
                            await interaction.response.send_message(view=AccountChangeSelectView(bot=self.bot, username=self.username.value), ephemeral=True)
                        else:
                            await interaction.response.send_message("このZeTNONアカウントはあなたのDiscordアカウントと連携されていません。`/account relink`を使ってアカウントを再連携してください", ephemeral=True)
                    else:
                        await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
                else:
                    await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
        except FileNotFoundError:
            await interaction.response.send_message("そのZeTNONアカウントは登録されていません。", ephemeral=True)


class AccountSubscriptionPayPayModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, username):
        super().__init__(
            title="有料化 | Subscription",
            timeout=None
        )
        self.link = discord.ui.TextInput(
            label="1500円分のPayPayリンク | PayPayLink",
            style=discord.TextStyle.short,
            placeholder="例: https://pay.paypay.ne.jp/jQw9Kgr14lBmTr6A",
            max_length=100,
            required=True
        )
        self.password = discord.ui.TextInput(
            label="受け取りリンクのパスワード | PayLink PassWord",
            style=discord.TextStyle.short,
            placeholder="例: 1234",
            max_length=4,
            required=False
        )
        self.add_item(self.link)
        self.add_item(self.password)
        self.bot = bot
        self.username = username

    async def on_submit(self, interaction: discord.Interaction) -> None:
        with open(f"file/account/{self.username}/info.txt", "r") as f:
            content = json.load(f)
            if content["subscription"] == "True":
                await interaction.response.send_message("既にZeTNONアカウントが有料化されています。", ephemeral=True)
            else:
                await interaction.response.send_message("送信しました。数時間以内にアカウントを有料化します。", ephemeral=True)
                tuvon = self.bot.get_user(994953877625507851)
                tettu = self.bot.get_user(1044937269162823751)
                await tuvon.send(f"ZeTNONアカウント有料化\nユーザーID: {str(interaction.user.id)}\nユーザー名: {self.username}\nファイルディレクトリ: `file/account/{self.username}/info.txt`\nPayLink: {self.link.value}\nパスワード: {self.password.value}")
                await tettu.send(f"ZeTNONアカウント有料化\nユーザーID: {str(interaction.user.id)}\nユーザー名: {self.username}\nファイルディレクトリ: `file/account/{self.username}/info.txt`\nPayLink: {self.link.value}\nパスワード: {self.password.value}")


class AccountSubscriptionSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot, username):

        options = [
            discord.SelectOption(label="LifeTime", description="永久プラン"),
        ]
        super().__init__(
            placeholder="どれか一つ選択してください...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.bot = bot
        self.username = username

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "LifeTime":
            await interaction.response.send_modal(AccountSubscriptionPayPayModal(bot=self.bot, username=self.username))
        else:
            pass


class AccountSubscriptionSelectView(discord.ui.View):
    def __init__(self, bot: commands.Bot, username):
        super().__init__(timeout=None)
        self.add_item(AccountSubscriptionSelect(bot=bot, username=username))


class AccountLogin3Modal(discord.ui.Modal):
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
        try:
            with open(f"file/account/{self.username.value}/info.txt", "r") as f:
                content = json.load(f)
                if content["username"] == self.username.value:
                    if content["password"] == self.password.value:
                        if content["user_id"] == interaction.user.id:
                            await interaction.response.send_message(view=AccountSubscriptionSelectView(bot=self.bot, username=content["username"]), ephemeral=True)
                        else:
                            await interaction.response.send_message("このZeTNONアカウントはあなたのDiscordアカウントと連携されていません。`/account relink`を使ってアカウントを再連携してください", ephemeral=True)
                    else:
                        await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
                else:
                    await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
        except FileNotFoundError:
            await interaction.response.send_message("そのZeTNONアカウントは登録されていません。", ephemeral=True)


class AccountDeleteConfirmButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot, username):
        super().__init__(timeout=None)
        self.bot = bot
        self.username = username
    
    @discord.ui.button(label="消去 | Delete", style=discord.ButtonStyle.danger, custom_id="persistent_view:btn_deleteacc")
    async def callback_delete(self, button: discord.ui.Button, interaction: discord.Interaction):
        shutil.rmtree(f"file/account/{self.username}")
        await button.response.send_message("消去しました。", ephemeral=True)


class AccountLogin4Modal(discord.ui.Modal):
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
        try:
            with open(f"file/account/{self.username.value}/info.txt", "r") as f:
                content = json.load(f)
                if content["username"] == self.username.value:
                    if content["password"] == self.password.value:
                        if content["user_id"] == interaction.user.id:
                            await interaction.response.send_message("本当にアカウントを消去しますか？消去を押した後、**この操作は取り消せません**\n**__この操作に伴い、アカウントに保存されたデータ(バックアップ等)はすべて消去されます。__**", view=AccountDeleteConfirmButtonView(bot=self.bot, username=content["username"]), ephemeral=True)
                        else:
                            await interaction.response.send_message("このZeTNONアカウントはあなたのDiscordアカウントと連携されていません。`/account relink`を使ってアカウントを再連携してください", ephemeral=True)
                    else:
                        await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
                else:
                    await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
        except FileNotFoundError:
            await interaction.response.send_message("そのZeTNONアカウントは登録されていません。", ephemeral=True)


class AccountLogin5Modal(discord.ui.Modal):
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
        try:
            with open(f"file/account/{self.username.value}/info.txt", "r") as f:
                content = json.load(f)
                if content["username"] == self.username.value:
                    if content["password"] == self.password.value:
                        content2 = {"username": content["username"],
                               "password": content["password"],
                               "user_id": interaction.user.id,
                               "subscription": content["subscription"],
                               "regist_time": content["regist_time"]}
                        with open(f"file/account/{self.username.value}/info.txt", "w") as f:
                            json.dump(content2, f)
                            await interaction.response.send_message("アカウントを再連携しました。", ephemeral=True)
                    else:
                        await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
                else:
                    await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
        except FileNotFoundError:
            await interaction.response.send_message("そのZeTNONアカウントは登録されていません。", ephemeral=True)


class AccountCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("[COGS]AccountSlashCog on ready.")

    account = app_commands.Group(
        name="account", description="ZeTNONアカウント関係コマンド")

    @account.command(
        name="register",
        description="ZeTNONアカウントを登録します"
    )
    async def account_register(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AccountRegisterModal(bot=self.bot))

    @account.command(
        name="info",
        description="ZeTNONアカウントにアクセスします"
    )
    async def account_info(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AccountLoginModal(bot=self.bot))

    @account.command(
        name="change",
        description="ZeTNONアカウントの登録情報を変えます"
    )
    async def account_change(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AccountLogin2Modal(bot=self.bot))
    
    @account.command(
        name="delete",
        description="ZeTNONアカウントを削除します"
    )
    async def account_delete(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AccountLogin4Modal(bot=self.bot))

    @account.command(
        name="subscription",
        description="ZeTNONアカウントに有料プランを適応させます"
    )
    async def account_subscription(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AccountLogin3Modal(bot=self.bot))
    
    @account.command(
        name="relink",
        description="ZeTNONアカウントとDiscordアカウントとの再連携をします"
    )
    async def account_relink(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AccountLogin5Modal(bot=self.bot))


async def setup(bot: commands.Bot):
    await bot.add_cog(AccountCog(bot))