# Import General Package
import asyncio
import json
import os
import datetime
import pytz
import shutil
import random
import string

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands


class marume:
    def floor(src: int, range: int):
        return (int)(src / range) * range

    def ceil(src, range):
        return ((int)(src / range) + 1) * range


def rand_gen(n: int):
    t = "".join(random.choice(string.digits) for _ in range(n))
    return t


class InstagramPaymentModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, id: int, amount: int, peoples: int, username: str):
        super().__init__(title="支払い", timeout=None)
        self.paypay = discord.ui.TextInput(label=f"PayPayリンク(`{amount}円分`)を入力してください", style=discord.TextStyle.short,
                                           min_length=1, max_length=60, placeholder="例: https://pay.paypay.ne.jp/XXXXXXXXXXXXXXXX", required=True)
        self.passcode = discord.ui.TextInput(label="パスワードがある場合はパスワードを入力してください", style=discord.TextStyle.short,
                                             min_length=1, max_length=4, placeholder="例: 1234", required=False)
        self.add_item(self.paypay)
        self.add_item(self.passcode)

        self.bot = bot
        self.amount = amount
        self.id = id
        self.peoples = peoples
        self.username = username

    async def on_submit(self, interaction: discord.Interaction) -> None:
        code = rand_gen(6)
        tuvon = self.bot.get_user(994953877625507851)
        content = f"""__**フォロ爆注文**__
発注元サーバーID : {str(interaction.guild_id)}
発注者 : {interaction.user.name} (ID:{interaction.user.id})
受注時刻 : {str(datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'))}
問い合わせID : {str(code)}

商品コード : {self.id}
人数 : {str(self.peoples)} 人
金額 : {str(self.amount)} 円
標的URL : {self.username}

PayPayリンク : {self.paypay.value}
PayPayパスワード : {self.passcode.value}
        """
        await tuvon.send(content)
        await interaction.response.send_message("購入が完了しました。\nお問い合わせID : {}\nお問い合わせ時に必要になります。必ずメモしてください".format(str(code)), ephemeral=True)


class TwitterPaymentModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, id: int, amount: int, peoples: int, username: str):
        super().__init__(title="支払い", timeout=None)
        self.paypay = discord.ui.TextInput(label=f"PayPayリンク(`{amount}円分`)を入力してください", style=discord.TextStyle.short,
                                           min_length=1, max_length=60, placeholder="例: https://pay.paypay.ne.jp/XXXXXXXXXXXXXXXX", required=True)
        self.passcode = discord.ui.TextInput(label="パスワードがある場合はパスワードを入力してください", style=discord.TextStyle.short,
                                             min_length=1, max_length=4, placeholder="例: 1234", required=False)
        self.add_item(self.paypay)
        self.add_item(self.passcode)

        self.bot = bot
        self.amount = amount
        self.id = id
        self.peoples = peoples
        self.username = username

    async def on_submit(self, interaction: discord.Interaction) -> None:
        code = rand_gen(6)
        tuvon = self.bot.get_user(994953877625507851)
        content = f"""__**フォロ爆注文**__
発注元サーバー : {interaction.guild.name} (ID:{str(interaction.guild_id)})
発注者 : {interaction.user.name} (ID:{interaction.user.id})
受注時刻 : {str(datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'))}
問い合わせID : {str(code)}

商品コード : {self.id}
人数 : {str(self.peoples)} 人
金額 : {str(self.amount)} 円
標的URL : {self.username}

PayPayリンク : {self.paypay.value}
PayPayパスワード : {self.passcode.value}
        """
        await tuvon.send(content)
        await interaction.response.send_message("購入が完了しました。\nお問い合わせID : {}\nお問い合わせ時に必要になります。必ずメモしてください".format(str(code)), ephemeral=True)


class InstagramPaymentModalButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot, id: int, amount: int, peoples: int, username: str):
        super().__init__(timeout=None)

        self.bot = bot
        self.amount = amount
        self.id = id
        self.peoples = peoples
        self.username = username

    @discord.ui.button(label="支払い/Pay", style=discord.ButtonStyle.green, custom_id="persitent_view:instagram_pay_modal_button")
    async def instagram_pay(self, button: discord.ui.Button, interaction: discord.Interaction):
        await button.response.send_modal(InstagramPaymentModal(bot=self.bot, id=self.id, amount=self.amount, peoples=self.peoples, username=self.username))


class TwitterPaymentModalButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot, id: int, amount: int, peoples: int, username: str):
        super().__init__(timeout=None)

        self.bot = bot
        self.amount = amount
        self.id = id
        self.peoples = peoples
        self.username = username

    @discord.ui.button(label="支払い/Pay", style=discord.ButtonStyle.green, custom_id="persitent_view:instagram_pay_modal_button")
    async def instagram_pay(self, button: discord.ui.Button, interaction: discord.Interaction):
        await button.response.send_modal(TwitterPaymentModal(bot=self.bot, id=self.id, amount=self.amount, peoples=self.peoples, username=self.username))


class InstagramPurchaseModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, id: int):
        super().__init__(title="Instagram爆注文", timeout=None)
        self.peoples = discord.ui.TextInput(label="注文する人数を入力してください(100人単位)", style=discord.TextStyle.short,
                                            min_length=1, max_length=20, placeholder="例: 1000", required=True)
        self.username = discord.ui.TextInput(label="対象となるユーザー名もしくはURLを入力してください", style=discord.TextStyle.short,
                                             min_length=1, max_length=50, placeholder="例: Tettu0530", required=True)
        self.add_item(self.peoples)
        self.add_item(self.username)

        self.bot = bot
        self.id = id

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if self.id == "I000S":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 14
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"I000S ⭐ 世界最安 ⭐ Instagram フォロワー爆 [MAX5K] [注:大幅遅延中]\n{str(amount)}円です", view=InstagramPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "I0001":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 15
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"I0001 ⭐ 最安 ⭐ ⚡ 超高速 ⚡ Instagram Botフォロワー爆 [MAX10K] [10K-60K/日]\n{str(amount)}円です", view=InstagramPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "I0002":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 90
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"I0002 ❄ 減少率↓ ❄ Instagram リアルユーザー爆 [MAX250K] [5K-10K/日]\n{str(amount)}円です", view=InstagramPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "I0003":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 30
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"I0003 ⭐ 最安 ⭐ Instagram フォロワー爆 [MAX50K] [30日減少保証] [5-10K/日]\n{str(amount)}円です", view=InstagramPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "I0004":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 55
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"I0004 ❄️ 減少率0%-2% ❄️ Instagram フォロワー爆 [MAX300K] [30日減少保証] [5K-10K/日]\n{str(amount)}円です", view=InstagramPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "I0005":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 35
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"I0005 Instagram フォロワー爆 [MAX1M] [60日減少保証] [5K-10K/日]\n{str(amount)}円です", view=InstagramPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "I0006":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 60
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"I0006 Instagram フォロワー爆 [MAX10M] [90日減少保証] [10K-50K/日]\n{str(amount)}円です", view=InstagramPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "I0007":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 40
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"I0007 Instagram フォロワー爆 [MAX10M] [365日減少保証] [1K-10K/日]\n{str(amount)}円です", view=InstagramPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "I0008":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 5
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"I0008 ⭐ 日本最安値 ⭐ Instagram Botいいね爆 [MAX30K] [1K-10K/日]\n{str(amount)}円です", view=InstagramPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "I0009":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 10
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"I0009 ❄️ 減少率↓ ❄️ Instagram 高品質いいね爆 [MAX400K] [5K-50K/日]\n{str(amount)}円です", view=InstagramPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "I0010":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 15
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"I0010 ❄️ 減少率ほぼ0% ❄️ Instagram リアルユーザーいいね爆 [MAX20K] [5K-10K/日]\n{str(amount)}円です", view=InstagramPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "I0011":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 0.4
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"I0011 ⭐最安⭐ Instagram 視聴爆 [MAX1000M] [500K/日]\n{str(amount)}円です", view=InstagramPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "I0012":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 0.6
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"I0012 Instagram 高速視聴爆 [MAX3M] [600K-900K/日]\n{str(amount)}円です", view=InstagramPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)


class TwitterPurchaseModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, id: int):
        super().__init__(title="Twitter爆注文", timeout=None)
        self.peoples = discord.ui.TextInput(label="注文する人数を入力してください(100人単位)", style=discord.TextStyle.short,
                                            min_length=1, max_length=20, placeholder="例: 1000", required=True)
        self.username = discord.ui.TextInput(label="対象となるユーザー名もしくはURLを入力してください", style=discord.TextStyle.short,
                                             min_length=1, max_length=50, placeholder="例: Tettu0530", required=True)
        self.add_item(self.peoples)
        self.add_item(self.username)

        self.bot = bot
        self.id = id

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if self.id == "TW00S":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 70
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"TW00S ⭐ 日本最安値 ⭐ Twitter フォロワー爆 [MAX500K] [100-200/日] [注:大幅遅延中]\n{str(amount)}円です", view=TwitterPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "TW001":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 75
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"TW001 ⭐ 最安値 ⭐ Twitter フォロワー爆 [MAX200K] [1K-2K/日]\n{str(amount)}円です", view=TwitterPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "TW002":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 100
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"TW002 Twitter フォロワー爆 [MAX500K] [30日間減少保証] [1-10K/日]\n{str(amount)}円です", view=TwitterPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "TW003":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 120
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"TW003 Twitter フォロワー爆 [MAX30K] [30日間減少保証] [15K-30K/日]\n{str(amount)}円です", view=TwitterPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "TW004":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 60
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"TW004 Twitter いいね爆[注:低速!] [MAX100K]\n{str(amount)}円です", view=TwitterPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "TW005":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 90
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"TW005 Twitter いいね爆[MAX10K] [10K/日]\n{str(amount)}円です", view=TwitterPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "TW006":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 60
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"TW006 ⭐ 最安 ⭐ Twitter RT爆 [MAX80K] [1K/日]\n{str(amount)}円です", view=TwitterPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)
        elif self.id == "TW007":
            peoples = marume.floor(int(self.peoples.value), 100)
            amount = (peoples / 1000) * 300
            if isinstance(amount, float):
                amount = round(amount)
            await interaction.response.send_message(f"TW007 ❄️  減少率ほぼ0% ❄️  Twitter リアルユーザーRT爆 [MAX50K]\n{str(amount)}円です", view=TwitterPaymentModalButtonView(bot=self.bot, id=self.id, amount=amount, peoples=peoples, username=self.username.value), ephemeral=True)


class InstagramFollowerSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot):
        options = [
            discord.SelectOption(
                label="I000S ⭐ 世界最安 ⭐ Instagram フォロワー爆 [MAX5K] [注:大幅遅延中]", description="1000人あたり 14円", value="I000S"),
            discord.SelectOption(
                label="I0001 ⭐ 最安 ⭐ ⚡ 超高速 ⚡ Instagram Botフォロワー爆 [MAX10K] [10K-60K/日]", description="1000人あたり 15円", value="I0001"),
            discord.SelectOption(
                label="I0002 ❄ 減少率↓ ❄ Instagram リアルユーザー爆 [MAX250K] [5K-10K/日]", description="1000人あたり 90円", value="I0002"),
            discord.SelectOption(
                label="I0003 ⭐ 最安 ⭐ Instagram フォロワー爆 [MAX50K] [30日減少保証] [5-10K/日]", description="1000人あたり 30円", value="I0003"),
            discord.SelectOption(
                label="I0004 ❄️ 減少率0%~2% ❄️ Instagram フォロワー爆 [MAX300K] [30日減少保証] [5K-10K/日]", description="1000人あたり 55円", value="I0004"),
            discord.SelectOption(
                label="I0005 Instagram フォロワー爆 [MAX1M] [60日減少保証] [5K-10K/日]", description="1000人あたり 35円", value="I0005"),
            discord.SelectOption(
                label="I0006 Instagram フォロワー爆 [MAX10M] [90日減少保証] [10K-50K/日]", description="1000人あたり 60円", value="I0006"),
            discord.SelectOption(
                label="I0007 Instagram フォロワー爆 [MAX10M] [365日減少保証] [1K-10K/日]", description="1000人あたり 40円", value="I0007")
        ]
        super().__init__(
            min_values=1,
            max_values=1,
            placeholder="購入するものを選択してください...",
            options=options
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(InstagramPurchaseModal(bot=self.bot, id=self.values[0]))


class InstagramFollowerSelectView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.add_item(InstagramFollowerSelect(bot=bot))


class InstagramLikesSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot):
        options = [
            discord.SelectOption(
                label="I0008 ⭐ 日本最安値 ⭐ Instagram Botいいね爆 [MAX30K] [1K-10K/日]", description="1000人あたり 5円", value="I0008"),
            discord.SelectOption(
                label="I0009 ❄️ 減少率↓ ❄️ Instagram 高品質いいね爆 [MAX400K] [5K-50K/日]", description="1000人あたり 10円", value="I0009"),
            discord.SelectOption(
                label="I0010 ❄️ 減少率ほぼ0% ❄️ Instagram リアルユーザーいいね爆 [MAX20K] [5K-10K/日]", description="1000人あたり 15円", value="I0010"),
        ]
        super().__init__(
            min_values=1,
            max_values=1,
            placeholder="購入するものを選択してください...",
            options=options
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(InstagramPurchaseModal(bot=self.bot, id=self.values[0]))


class InstagramLikesSelectView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.add_item(InstagramLikesSelect(bot=bot))


class InstagramViewsSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot):
        options = [
            discord.SelectOption(
                label="I0011 ⭐ 最安 ⭐ Instagram 視聴爆 [MAX1000M] [500K/日]", description="1000人あたり 0.4円", value="I0011"),
            discord.SelectOption(
                label="I0012 Instagram 高速視聴爆 [MAX3M] [600K-900K/日]", description="1000人あたり 0.5円", value="I0012")
        ]
        super().__init__(
            min_values=1,
            max_values=1,
            placeholder="購入するものを選択してください...",
            options=options
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(InstagramPurchaseModal(bot=self.bot, id=self.values[0]))


class InstagramViewsSelectView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.add_item(InstagramFollowerSelect(bot=bot))


class TwitterFollowerSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot):
        options = [
            discord.SelectOption(
                label="TW00S ⭐ 日本最安値 ⭐ Twitter フォロワー爆 [MAX500K] [100-200/日] [注:大幅遅延中]", description="1000人あたり 70円", value="TW00S"),
            discord.SelectOption(
                label="TW001 ⭐ 最安値 ⭐ Twitter フォロワー爆 [MAX200K] [1K-2K/日]", description="1000人あたり 75円", value="TW001"),
            discord.SelectOption(
                label="TW002 Twitter フォロワー爆 [MAX500K] [30日間減少保証] [1-10K/日]", description="1000人あたり 100円", value="TW002"),
            discord.SelectOption(
                label="TW003 Twitter フォロワー爆 [MAX30K] [30日間減少保証] [15K-30K/日]", description="1000人あたり 120円", value="TW003")
        ]
        super().__init__(
            min_values=1,
            max_values=1,
            placeholder="購入するものを選択してください...",
            options=options
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TwitterPurchaseModal(bot=self.bot, id=self.values[0]))


class TwitterFollowerSelectView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.add_item(TwitterFollowerSelect(bot=bot))


class TwitterLikesSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot):
        options = [
            discord.SelectOption(
                label="TW004 Twitter いいね爆[注:低速!] [MAX100K]", description="1000人あたり 60円", value="TW004"),
            discord.SelectOption(
                label="TW005 Twitter いいね爆[MAX10K] [10K/日]", description="1000人あたり 90円", value="TW005")
        ]
        super().__init__(
            min_values=1,
            max_values=1,
            placeholder="購入するものを選択してください...",
            options=options
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TwitterPurchaseModal(bot=self.bot, id=self.values[0]))


class TwitterLikesSelectView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.add_item(TwitterLikesSelect(bot=bot))


class TwitterRTSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot):
        options = [
            discord.SelectOption(
                label="TW006 ⭐ 最安 ⭐ Twitter RT爆 [MAX80K] [1K/日]", description="1000人あたり 60円", value="TW006"),
            discord.SelectOption(
                label="TW007 ❄️  減少率ほぼ0% ❄️  Twitter リアルユーザーRT爆 [MAX50K]", description="1000人あたり 300円", value="TW007")
        ]
        super().__init__(
            min_values=1,
            max_values=1,
            placeholder="購入するものを選択してください...",
            options=options
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TwitterPurchaseModal(bot=self.bot, id=self.values[0]))


class TwitterRTSelectView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.add_item(TwitterRTSelect(bot=bot))


class InstagramFollowerButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="🎫購入/Purchase", style=discord.ButtonStyle.green, custom_id="persistent_view:instagram_follower_button")
    async def instagram_callback(self, button: discord.Button, interaction: discord.Interaction):
        await button.response.send_message(view=InstagramFollowerSelectView(bot=self.bot), ephemeral=True)


class InstagramLikesButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="🎫購入/Purchase", style=discord.ButtonStyle.green, custom_id="persistent_view:instagram_likes_button")
    async def instagram_callback(self, button: discord.Button, interaction: discord.Interaction):
        await button.response.send_message(view=InstagramLikesSelectView(bot=self.bot), ephemeral=True)


class InstagramViewsButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="🎫購入/Purchase", style=discord.ButtonStyle.green, custom_id="persistent_view:instagram_views_button")
    async def instagram_callback(self, button: discord.Button, interaction: discord.Interaction):
        await button.response.send_message(view=InstagramViewsSelectView(bot=self.bot), ephemeral=True)


class TwitterFollowerButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="🎫購入/Purchase", style=discord.ButtonStyle.green, custom_id="persistent_view:twitter_follower_button")
    async def instagram_callback(self, button: discord.Button, interaction: discord.Interaction):
        await button.response.send_message(view=TwitterFollowerSelectView(bot=self.bot), ephemeral=True)


class TwitterLikesButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="🎫購入/Purchase", style=discord.ButtonStyle.green, custom_id="persistent_view:twitter_likes_button")
    async def instagram_callback(self, button: discord.Button, interaction: discord.Interaction):
        await button.response.send_message(view=TwitterLikesSelectView(bot=self.bot), ephemeral=True)


class TwitterRTButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="🎫購入/Purchase", style=discord.ButtonStyle.green, custom_id="persistent_view:twitter_rt_button")
    async def instagram_callback(self, button: discord.Button, interaction: discord.Interaction):
        await button.response.send_message(view=TwitterRTSelectView(bot=self.bot), ephemeral=True)


class FllowerVendingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        classlist = [
            InstagramFollowerButtonView(bot=bot),
            InstagramLikesButtonView(bot=bot),
            InstagramViewsButtonView(bot=bot),
            TwitterFollowerButtonView(bot=bot)
        ]
        for i in classlist:
            bot.add_view(i)
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("[COGS]FollowerVendingSlashCog on ready.")

    @app_commands.command(
        name="set",
        description="フォロ爆自販機を設置します"
    )
    @app_commands.choices(
        type=[
            discord.app_commands.Choice(name="Instagramフォロ爆", value="1"),
            discord.app_commands.Choice(name="Instagramいいね爆", value="2"),
            discord.app_commands.Choice(name="Instagram視聴爆", value="3"),
            discord.app_commands.Choice(name="Twitterフォロ爆", value="4"),
            discord.app_commands.Choice(name="Twitterいいね爆", value="5"),
            discord.app_commands.Choice(name="TwitterRT爆", value="6"),
            discord.app_commands.Choice(name="YouTube登録爆", value="7"),
            discord.app_commands.Choice(name="YouTube登録爆", value="8")
        ]
    )
    async def set(self, interaction: discord.Interaction, type: str):
        if type == "1":
            embed = discord.Embed(
                title="Instagramフォロ爆自販機", description="購入するには下のボタンを押してください", color=0xdf346e)
            embed.add_field(
                name="I0001 ⭐ 最安 ⭐ ⚡ 超高速 ⚡ Instagram Botフォロワー爆 [MAX10K] [10K-60K/日]", value="1000人あたり 15円", inline=False)
            embed.add_field(
                name="I0002 ❄ 減少率↓ ❄ Instagram リアルユーザー爆 [MAX250K] [5K-10K/日]", value="1000人あたり 90円", inline=False)
            embed.add_field(
                name="I0003 ⭐ 最安 ⭐ Instagram フォロワー爆 [MAX50K] [30日減少保証] [5-10K/日]", value="1000人あたり 30円", inline=False)
            embed.add_field(
                name="I0004 ❄️ 減少率0%~2% ❄️ Instagram フォロワー爆 [MAX300K] [30日減少保証] [5K-10K/日]", value="1000人あたり 55円", inline=False)
            embed.add_field(
                name="I0005 Instagram フォロワー爆 [MAX1M] [60日減少保証] [5K-10K/日]", value="1000人あたり 35円", inline=False)
            embed.add_field(
                name="I0006 Instagram フォロワー爆 [MAX10M] [90日減少保証] [10K-50K/日]", value="1000人あたり 60円", inline=False)
            embed.add_field(
                name="I0007 Instagram フォロワー爆 [MAX10M] [365日減少保証] [1K-10K/日]", value="1000人あたり 40円", inline=False)
            await interaction.response.send_message(embed=embed, view=InstagramFollowerButtonView(bot=self.bot))
        elif type == "2":
            embed = discord.Embed(
                title="Instagramいいね爆自販機", description="購入するには下のボタンを押してください", color=0xdf346e)
            embed.add_field(
                name="I0008 ⭐ 日本最安値 ⭐ Instagram Botいいね爆 [MAX30K] [1K-10K/日]", value="1000人あたり 5円", inline=False)
            embed.add_field(
                name="I0009 ❄️ 減少率↓ ❄️ Instagram 高品質いいね爆 [MAX400K] [5K-50K/日]", value="1000人あたり 10円", inline=False)
            embed.add_field(
                name="I0010 ❄️ 減少率ほぼ0% ❄️ Instagram リアルユーザーいいね爆 [MAX20K] [5K-10K/日]", value="1000人あたり 15円", inline=False)
            await interaction.response.send_message(embed=embed, view=InstagramLikesButtonView(bot=self.bot))
        elif type == "3":
            embed = discord.Embed(
                title="Instagram視聴爆自販機", description="購入するには下のボタンを押してください", color=0xdf346e)
            embed.add_field(
                name="I0011 ⭐最安⭐ Instagram 視聴爆 [MAX1000M] [500K/日]", value="1000人あたり 0.4円", inline=False)
            embed.add_field(
                name="I0012 Instagram 高速視聴爆 [MAX3M] [600K-900K/日]", value="1000人あたり 0.5円", inline=False)
            await interaction.response.send_message(embed=embed, view=InstagramViewsButtonView(bot=self.bot))
        elif type == "4":
            embed = discord.Embed(
                title="Twitterフォロ爆自販機", description="購入するには下のボタンを押してください", color=0x00acee)
            embed.add_field(
                name="TW00S ⭐ 日本最安値 ⭐ Twitter フォロワー爆 [MAX500K] [100-200/日] [注:大幅遅延中]", value="1000人あたり 70円", inline=False)
            embed.add_field(
                name="TW001 ⭐ 最安値 ⭐ Twitter フォロワー爆 [MAX200K] [1K-2K/日]", value="1000人あたり 75円", inline=False)
            embed.add_field(
                name="TW002 Twitter フォロワー爆 [MAX500K] [30日間減少保証] [1-10K/日] ", value="1000人あたり 100円", inline=False)
            embed.add_field(
                name="TW003 Twitter フォロワー爆 [MAX30K] [30日間減少保証] [15K-30K/日]", value="1000人あたり 120円", inline=False)
            await interaction.response.send_message(embed=embed, view=TwitterFollowerButtonView(bot=self.bot))
        elif type == "5":
            embed = discord.Embed(
                title="Twitterいいね爆自販機", description="購入するには下のボタンを押してください", color=0x00acee)
            embed.add_field(
                name="TW004 Twitter いいね爆[注:低速!] [MAX100K]", value="1000人あたり 60円", inline=False)
            embed.add_field(
                name="TW005 Twitter いいね爆[MAX10K] [10K/日]", value="1000人あたり 90円", inline=False)
            await interaction.response.send_message(embed=embed, view=TwitterLikesButtonView(bot=self.bot))
        elif type == "6":
            embed = discord.Embed(
                title="TwitterRT爆自販機", description="購入するには下のボタンを押してください", color=0x00acee)
            embed.add_field(
                name="TW006 ⭐ 最安 ⭐ Twitter RT爆 [MAX80K] [1K/日]", value="1000人あたり 60円", inline=False)
            embed.add_field(
                name="TW007 ❄️  減少率ほぼ0% ❄️  Twitter リアルユーザーRT爆 [MAX50K]", value="1000人あたり 300円", inline=False)
            await interaction.response.send_message(embed=embed, view=TwitterRTButtonView(bot=self.bot))
        else:
            await interaction.response.send_message("`type`に不正な引数を含んでいます。(現在開発中)", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(FllowerVendingCog(bot))
