# Import General Package
import asyncio
import json
import time
import os
import datetime
import uuid
import pytz
import random
from PayPayPy import PayPay

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands


def count_json(path):
    return len([f for f in os.listdir(path) if f.endswith(".json")])


class VendingPurcaseModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, vending_name: str, product_index: str, stock: int, access_token: str, username: str = None, quantity: int = None, much: int = None):
        super().__init__(title="購入 | Purcase", timeout=None)
        self.link = discord.ui.TextInput(label=f"{much}円分のPayPay送金リンク", style=discord.TextStyle.short,
                                         placeholder="https://www.paypay.ne.jp/yArpGfsZuoZ4VoOK", min_length=1, max_length=1000, required=True)
        self.password = discord.ui.TextInput(label="PayPay送金リンクのパスワード(必要な場合)", style=discord.TextStyle.short,
                                             placeholder="1234", min_length=4, max_length=4, required=False)
        self.add_item(self.how_many)
        self.add_item(self.link)
        self.add_item(self.password)
        self.bot = bot
        self.username = username
        self.product_index = product_index
        self.access_token = access_token
        self.vending_name = vending_name
        self.quantity = quantity
        self.stock = stock

    async def on_submit(self, interaction: discord.Interaction):
        paypay = PayPay(self.access_token)
        get_link_info = paypay.get_link(
            self.link.value.replace("https://pay.paypay.ne.jp/", ""))
        amount = get_link_info.payload.pendingP2PInfo.amount
        id = get_link_info.payload.pendingP2PInfo.orderId
        image = get_link_info.payload.pendingP2PInfo.imageUrl
        sender = get_link_info.payload.sender.displayName
        if self.password.value != "":
            get_pay = paypay.accept_link(self.link.value.replace(
                "https://pay.paypay.ne.jp/", ""), self.password.value)
        get_pay = paypay.accept_link(
            self.link.value.replace("https://pay.paypay.ne.jp/", ""))
        if get_pay.payload.orderStatus == "COMPLETED":
            embed = discord.Embed(
                title="✅ Success - PayPay Link", color=0x00ff00)
            embed.set_thumbnail(url=image)
            embed.add_field(name="送り主", value=f"`{sender}`")
            embed.add_field(name="状態", value="`完了済み`", inline=False)
            embed.add_field(
                name="金額", value=f"`{amount}円`", inline=False)
            embed.add_field(name="決済ID", value=f"`{id}`", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{interaction.channel.id}.json", "r") as f:
                data = json.load(f)
                name = data["product"][self.product_index]["name"]
                stock = data["product"][self.product_index]["stock"]
                product = str(
                    data["product"][self.product_index]["product"]).split("\n")
            with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{interaction.channel.id}.json", "w", encoding="utf-8") as f2:
                data["stock"] = data["stock"] - int(self.how_many.value)
                product = [products for products in product if product]
                send_product = product[:int(self.how_many.value)]
            if os.path.isdir(f"file/account/{self.username}/vending/order") is False:
                os.mkdir(f"file/account/{self.username}/vending/order")
            with open(f"file/account/{self.username}/vending/order/order_{interaction.user.id}.txt", "w", encoding="utf-8") as product_f:
                for line in send_product:
                    product_f.write(line + "\n")
            try:
                embed = discord.Embed(title="✅ Vending 商品", color=0x00ffff)
                embed.add_field(
                    name="注文日時", value=f"`{datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo')).strftime('%Y年%m月%d日 %H時%M分%S秒')}`", inline=False)
                embed.add_field(name="注文商品", value=f"`{name}`", inline=False)
                embed.add_field(
                    name="注文数量", value=f"`{self.how_many.value}個`", inline=False)
                embed.add_field(
                    name="支払金額", value=f"`{amount}円`", inline=False)
                await interaction.user.send(embed=embed, file=discord.File(f"file/account/{self.username}/vending/order/order_{interaction.user.id}.txt"))
                await interaction.followup.send("DMにも同じものを送信してあります。", embed=embed, file=discord.File(f"file/account/{self.username}/vending/order/order_{interaction.user.id}.txt"), ephemeral=True)
            except:
                embed = discord.Embed(title="✅ Vending 商品", color=0x00ffff)
                embed.add_field(
                    name="注文日時", value=f"`{datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo')).strftime('%Y年%m月%d日 %H時%M分%S秒')}`", inline=False)
                embed.add_field(name="注文商品", value=f"`{name}`", inline=False)
                embed.add_field(
                    name="注文数量", value=f"`{self.how_many.value}個`", inline=False)
                embed.add_field(
                    name="支払金額", value=f"`{amount}円`", inline=False)
                await interaction.followup.send(embed=embed, file=discord.File(f"file/account/{self.username}/vending/order/order_{interaction.user.id}.txt"), ephemeral=True)


class VendingPurcaseQuantitySelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot, options: str, vending_name: str, product_index: str, stock: int, price: int, access_token: str, username: str = None):
        super().__init__(
            placeholder="個数を選択してください...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="quantity_select"
        )
        self.bot = bot
        self.product_index = product_index
        self.stock = stock
        self.price = price
        self.access_token = access_token
        self.username = username
        self.vending_name = vending_name
    
    async def callback(self, interaction: discord.Interaction):
        quantity = int(self.values[0].replace("個", ""))
        much = quantity * self.price
        await interaction.response.send_modal(VendingPurcaseModal(bot=self.bot, vending_name=self.vending_name, product_index=self.product_index, stock=self.stock, access_token=self.access_token, username=self.username, quantity=quantity, much=much))


class VendingPurcaseQuantitySelectView(discord.ui.View):
    def __init__(self, bot: commands.Bot, vending_name: str = None, product_index: int = None, options: list = None, username: str = None, price: int = None, access_token: str = None):
        self.add_item(VendingPurcaseQuantitySelect(bot=bot, options=options, vending_name=vending_name, product_index=product_index, price=price, access_token=access_token, username=username))


class VendingPurcaseSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot, options: list, username: str = None, vending_name: str = None):
        super().__init__(placeholder="購入する商品を選んでください",
                         min_values=1, max_values=1, options=options, custom_id="purcase_select")
        self.bot = bot
        self.username, self.vending_name = username, vending_name

    async def callback(self, interaction: discord.Interaction):
        with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.vending_name}.json", "r") as f:
            data = json.load(f)
            for i, product in enumerate(data["products"]):
                if product["name"] == self.values[0]:
                    product_index = i
                    stock = product["stock"]
                    price = product["price"]
                    if product["stock"] == 0:
                        return await interaction.response.send_message("この商品は現在在庫切れです。入荷までお待ちください。", ephemeral=True)
                    break
            try:
                paypay_f = data["paypay_file"]
                with open(paypay_f, "r") as paypay_f:
                    data = json.load(paypay_f)
                paypay = PayPay(data["access_token"])
            except KeyError:
                await interaction.response.send_message("この自販機はPayPayアカウントが連携されていません。\nこのサーバーの管理者に連絡し、PayPayアカウントを連携してもらう必要があります。")
            except AttributeError:
                await interaction.response.send_message("この自販機のPayPayアカウントは無効です。\nこのサーバーの管理者に連絡し、PayPayアカウントを再連携してもらう必要があります。")
        products = str(data["products"][product_index]["product"]).split("\n")
        options = [discord.SelectOption(label=str(i) + "個") for i in range(1, len(products) + 1)]
        await interaction.response.send_modal(VendingPurcaseQuantitySelect(bot=self.bot, username=self.username, options=options, product_index=product_index, stock=stock, price=price, access_token=data["access_token"]))


class VendingPurcaseSelectView(discord.ui.View):
    def __init__(self, bot: commands.Bot, username: str = None, options: str = None):
        super().__init__(timeout=None)
        self.add_item(VendingPurcaseSelect(bot=bot, username=username, options=options))


class VendingPurcaseButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot, username: str = None, vending_name: str = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.username, self.vending_name = username, vending_name

    @discord.ui.button(label="🛒購入 | Purcase", style=discord.ButtonStyle.green, custom_id="vending_purcase")
    async def vending_purcase_callback(self, button: discord.Button, interaction: discord.Interaction):
        with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.vending_name}.json", "r") as f:
            data = json.load(f)
            options = [discord.SelectOption(
                name=products["name"], description=products["price"]) for products in data["products"]]
            await interaction.response.send_message("どの商品を購入しますか？", view=VendingPurcaseSelectView(bot=self.bot, username=self.username, options=options), ephemeral=True)


class VendingCreateModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, username: str = None):
        super().__init__(
            title="自販機作成 | Vending Create",
            timeout=None
        )
        self.name = discord.ui.TextInput(
            label="自販機の名前 | Vending name",
            style=discord.TextStyle.short,
            max_length=100,
            required=True
        )
        self.description = discord.ui.TextInput(
            label="自販機の説明 | Vending description",
            style=discord.TextStyle.long,
            required=True
        )
        self.add_item(self.name)
        self.add_item(self.description)
        self.bot = bot
        self.username = username

    async def on_submit(self, interaction: discord.Interaction):
        if os.path.isdir(f"file/account/{self.username}/vending/") is False:
            os.mkdir(f"file/account/{self.username}/vending/")
        if os.path.isdir(f"file/account/{self.username}/vending/{interaction.guild.id}") is False:
            os.mkdir(
                f"file/account/{self.username}/vending/{interaction.guild.id}")
        if os.path.isfile(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.name.value}.json") is False:
            with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.name.value}.json", "w", encoding="utf-8") as vending_f:
                data = {
                    "name": self.name.value,
                    "description": self.description.value,
                    "guild_id": interaction.guild.id,
                    "author_id": interaction.user.id,
                    "paypay_file": "",
                    "log_channel": "",
                    "products": []
                }
                json.dump(data, vending_f)
                embed = discord.Embed(
                    title="✅ Success - Vending Create", description="自動販売機を作成しました。", color=0x00ff00)
                embed.add_field(
                    name="自販機の名前", value=self.name.value, inline=False)
                embed.add_field(
                    name="自販機の説明", value=self.description.value, inline=False)
                embed.set_footer(text="Status - 200 | Made by Tettu0530#0530",
                                 icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title="❌ Failure - Vending Create",
                                  description="エラーが発生しました。\n指定した自販機は既に同じサーバー上に存在します", color=0xff0000)
            embed.set_footer(text="Status - 400 | Made by Tettu0530#0530",
                             icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            await interaction.response.send_message(embed=embed, ephemeral=True)


class VendingCreateButtonView(discord.ui.View):
    def __init__(self, bot: commands.Bot, username: str = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.username = username

    @discord.ui.button(label="作成 | Create", style=discord.ButtonStyle.green, custom_id="vending_create")
    async def vending_purcase_callback(self, button: discord.Button, interaction: discord.Interaction):
        await button.response.send_modal(VendingCreateModal(bot=self.bot, username=self.username))


class VendingLoginModal(discord.ui.Modal):
    def __init__(self, types: str, bot: commands.Bot, embed_title: str = None, embed_description: str = None):
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
        self.types = types
        self.embed_title = embed_title
        self.embed_description = embed_description

    async def on_submit(self, interaction: discord.Interaction):
        try:
            with open(f"file/account/{self.username.value}/info.json", "r") as f:
                data = json.load(f)
                if data["username"] == self.username.value:
                    if data["password"] == self.password.value:
                        if data["user_id"] == interaction.user.id:
                            if data["subscription"] == True:
                                if self.types == "create":
                                    await interaction.response.send_message("自販機作成に進みます。", view=VendingCreateButtonView(bot=self.bot, username=self.username.value))
                                elif self.types == "set":
                                    with open(f"file/account/{data['username']}/info.json", "r") as account_f:
                                        data = json.load(account_f)
                                        files = [f for f in os.listdir(f"file/account/{data['username']}/vending/{interaction.guild.id}") if os.path.isfile(
                                            os.path.join(f"file/account/{data['username']}/vending/{interaction.guild.id}", f))]
                                        files = [os.path.splitext(
                                            f)[0] for f in files if f.endswith(".json")]
                                        options = [discord.SelectOption(
                                            label=f) for f in files]
                                        await interaction.response.send_message(view=VendingSettingSelectView(bot=self.bot, types="set", options=options), ephemeral=True)
                                elif self.types == "log":
                                    with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.values[0]}.json", "r") as f:
                                        data = json.load(f)
                                    with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.values[0]}.json", "w", encoding="utf-8") as f2:
                                        data["log_channel"] = interaction.channel.id
                                        json.dump(data, f2)
                                        await interaction.response.send_message(f"ログを表示するチャンネルを変更しました。\n現在のログ出力チャンネル: {interaction.channel.mention}", ephemeral=True)
                                elif self.types == "paypay":
                                    if os.path.isfile(f"file/paypay/{interaction.user.id}.json") is False:
                                        embed = discord.Embed(title="❌ Failure - Vending PayPay",
                                                              description="このDiscordアカウントは何もPayPayアカウントと連携されていません", color=0xff0000)
                                        embed.set_footer(text="Status - 404 | Made by Tettu0530#0530",
                                                         icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                                    if os.path.isfile(f"file/account/{data['username']}/vending/{interaction.guild.id}/{interaction.channel.id}.json") is False:
                                        return await interaction.response.send_message("自販機が設置されていません。 `/vending create` で自販機を作成してからこのコマンドを実行してください")
                                    else:
                                        with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.values[0]}.json", "r") as f:
                                            data = json.load(f)
                                        with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.values[0]}.json", "w") as f2:
                                            data["paypay_file"] = f"file/paypay/{interaction.user.id}.json"
                                            json.dump(data, f2)
                                        await interaction.response.send_message("PayPayアカウントと自販機を連携しました。", ephemeral=True)
                                elif self.types == "restock_product":
                                    pass
                                elif self.types == "take_product":
                                    pass
                                elif self.types == "edit_product":
                                    pass
                                elif self.types == "add_product":
                                    await interaction.response.send_modal(VendingAddProductModal(bot=self.bot, username=self.username, vending_name=self.values[0]))
                                elif self.types == "set":
                                    with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.values[0]}.json", "r") as vending_f:
                                        data = json.load(vending_f)
                                        embed = discord.Embed(
                                            title=self.title, description=self.description, color=0x00ffff)
                                        for i in data["products"]:
                                            embed.add_field(
                                                name=i["name"], value=f"`{data['price']}`", inline=False)
                                        embed.set_footer(text="Status - 200 | Made by Tettu0530#0530",
                                                         icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                                        if len(data["products"]) == 0:
                                            return await interaction.response.send_message("先に`/vending setting`を使って商品を追加してください", ephemeral=True)
                                        await interaction.response.send_message(embed=embed)
                            else:
                                await interaction.response.send_message("このZeTNONアカウントは有料プランに契約していません。`/account setting`を使って有料プランに契約してください", ephemeral=True)
                        else:
                            await interaction.response.send_message("このZeTNONアカウントはあなたのDiscordアカウントと連携されていません。`/account relink`を使ってアカウントを再連携してください", ephemeral=True)
                    else:
                        await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
                else:
                    await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
        except FileNotFoundError:
            await interaction.response.send_message("そのZeTNONアカウントは登録されていません。", ephemeral=True)


class VendingPayPayModal(discord.ui.Modal):
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
            with open(f"file/account/{self.username.value}/info.json", "r") as f:
                data = json.load(f)
                if data["username"] == self.username.value:
                    if data["password"] == self.password.value:
                        if data["user_id"] == interaction.user.id:
                            if data["subscription"] == True:
                                if os.path.isfile(f"file/account/{self.username.value}/vending/{interaction.guild.id}/{interaction.channel.id}.json") is False:
                                    return await interaction.response.send_message("自販機が設置されていません。 `/vending create` で自販機を作成してからこのコマンドを実行してください")
                                else:
                                    with open(f"file/account/{self.username.value}/vending/{interaction.guild.id}/{interaction.channel.id}.json", "r") as f:
                                        data = json.load(f)
                                    with open(f"file/account/{self.username.value}/vending/{interaction.guild.id}/{interaction.channel.id}.json", "w") as f2:
                                        data["paypay_file"] = f"file/paypay/{interaction.user.id}.json"
                                        json.dump(data, f2)
                                    await interaction.response.send_message("PayPayアカウントと自販機を連携しました。")
                            else:
                                await interaction.response.send_message("このZeTNONアカウントは有料プランに契約していません。`/account setting`を使って有料プランに契約してください", ephemeral=True)
                        else:
                            await interaction.response.send_message("このZeTNONアカウントはあなたのDiscordアカウントと連携されていません。`/account relink`を使ってアカウントを再連携してください", ephemeral=True)
                    else:
                        await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
                else:
                    await interaction.response.send_message("ユーザー名またはパスワードが間違っています。間違っていないかご確認の上、再度お試しください。\nそれでもログインできない場合はTettu0530New#7110までお願いします。", ephemeral=True)
        except FileNotFoundError:
            await interaction.response.send_message("そのZeTNONアカウントは登録されていません。", ephemeral=True)


class VendingAddProductModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, vending_name: str, username: str = None):
        super().__init__(title="商品追加 | Add Product")
        self.product_name = discord.ui.TextInput(
            label="新しい商品の名前 | New Product Name",
            style=discord.TextStyle.short,
            placeholder="例: 商品1",
            min_length=1,
            required=True
        )
        self.price = discord.ui.TextInput(
            label="新しい商品の価格 | New Product Price",
            style=discord.TextStyle.short,
            placeholder="例: 100",
            min_length=1,
            required=True
        )
        self.add_item(self.product_name)
        self.add_item(self.price)
        self.bot = bot
        self.username = username
        self.vending_name = vending_name

    async def on_submit(self, interaction: discord.Interaction):
        with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.vending_name}.json", "r") as f:
            data = json.load(f)
        with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.vending_name}.json", "w", encoding="utf-8") as f2:
            if self.price.value == "offer":
                price = "offer"
            else:
                price = int(self.price.value)
            product = {
                "name": self.product_name.value,
                "price": price,
                "stock": 0,
                "product": ""
            }
            data["products"].append(product)
            json.dump(data, f2)
            embed = discord.Embed(
                title="✅ Success - Add Product", description="新しい商品を追加しました。", color=0x00ff00)
            embed.add_field(
                name="新しい商品の名前", value=self.product_name.value, inline=False)
            embed.add_field(
                name="新しい商品の値段", value=self.price.value + " 円", inline=False)
            embed.set_footer(text="Status - 200 | Made by Tettu0530#0530",
                             icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            await interaction.response.send_message(embed=embed, ephemeral=True)


class VendingSettingRestockModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, vending_name: str, product_index: int, username: str = None):
        super().__init__(title="商品在庫追加 | Restock Product")
        self.products = discord.ui.TextInput(
            label="商品を一行ずつ入力 | Input poduct (1 per line)",
            style=discord.TextStyle.long,
            placeholder="例: https://gigafile.nu/e34b2c2a22abbc54ab4bace4...",
            min_length=1,
            required=True
        )
        self.add_item(self.products)
        self.bot = bot
        self.username = username
        self.vending_name = vending_name
        self.product_index = product_index

    async def on_submit(self, interaction: discord.Interaction):
        product = ""
        with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.vending_name}.json", "r") as f:
            data = json.load(f)
        with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.vending_name}.json", "w") as f2:
            lines = self.products.value.strip().split("\n")
            count = 0
            for line in lines:
                product += line + "\n"
                count += 1
            product = [x for x in product if x.strip()]
            product = "\n".join(product)
            data["products"][self.product_index]["product"] = product
            data["products"][self.product_index]["stock"] += count
            json.dump(data, f2)
        embed = discord.Embed(title="✅ Success - Restock Product",
                              description="以下の商品を補充しました。", color=0x00ff00)
        embed.add_field(
            name="補充した商品名", value=data["products"][self.product_index]["name"], inline=False)
        embed.add_field(name="補充した個数", value=f"`{count}個`", inline=False)
        embed.add_field(
            name="現在の在庫数", value=f"`{data['products'][self.product_index]['stock']}個`", inline=False)
        embed.set_footer(text="Status - 200 | Made by Tettu0530#0530",
                         icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
        await interaction.response.send_message(embed=embed, ephemeral=True)


class VendingSettingTakeSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot, vending_name: str, products: str, product_index: int, options: list, username: str = None):
        super().__init__(
            placeholder="個数を選択してください...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="take_select"
        )
        self.bot = bot
        self.username = username
        self.products = products
        self.product_index = product_index
        self.vending_name = vending_name
    
    async def callback(self, interaction: discord.Interaction):
        selected = random.sample(self.products, int(self.values[0].replace("個", "")))
        with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.vending_name}.json", "r") as f:
            id = str(uuid.uuid4())
            data = json.load(f)
            if os.path.isdir(f"file/account/{self.username}/vending/{interaction.guild.id}/product") is False:
                os.mkdir(f"file/account/{self.username}/vending/{interaction.guild.id}/product")
            with open(f"file/account/{self.username}/vending/{interaction.guild.id}/product/product_{id}.txt", "w") as f2:
                for i in selected:
                    f2.write(i + "\n")
                new_products = [i for i in self.products if i not in selected]
                new_products = "\n".join(new_products)
                data["products"][self.product_index]["product"] = new_products
                data["products"][self.product_index]["stock"] -= len(selected)
        with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.vending_name}.json", "w") as f3:
            json.dump(data, f3)
        embed = discord.Embed(title="✅ Success - Take Product", description="以下の通りに商品の手動取り出しを行いました", color=0x00ff00)
        embed.add_field(name="取り出した商品名", value=data["products"][self.product_index]["name"], inline=False)
        embed.add_field(name="取り出した商品個数", value=f"`{len(selected)}`個", inline=False)
        embed.add_field(name="現在の商品在庫数", value=f"`{(len(self.products) - len(selected))}`個", inline=False)
        embed.set_footer(text="Status - 200 | Made by Tettu0530#0530",
                                 icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
        await interaction.response.send_message(embed=embed, file=discord.File(f"file/account/{self.username}/vending/{interaction.guild.id}/transaction/transaction_{id}.txt"))


class VendingSettingTakeSelectView(discord.ui.View):
    def __init__(self, bot: commands.Bot = None, vending_name: str = None, products: str = None, product_index: int = None, options: list = None, username: str = None):
        super().__init__(timeout=None)
        self.add_item(VendingSettingTakeSelect(
            bot=bot, username=username, vending_name=vending_name, products=products, product_index=product_index, options=options))


class VendingSettingProductDeleteView(discord.ui.View):
    def __init__(self, bot: commands.Bot = None, vending_name: str = None, product_index: int = None, username: str = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.vending_name, self.username = vending_name, username
        self.product_index = product_index
    
    @discord.ui.button(label="❌ 商品を削除 | Delete Product", style=discord.ButtonStyle.danger, custom_id="delete_product_button")
    async def delete_product_callback(self, button: discord.Button, interaction: discord.Interaction):
        with open(f"file/account/{self.username}/vending/{button.guild.id}/{self.vending_name}.json", "r") as f:
            data = json.load(f)
            name = data["products"][self.product_index]["name"]
        with open(f"file/account/{self.username}/vending/{button.guild.id}/{self.vending_name}.json", "w", encoding="utf-8") as f2:
            del data["products"][self.product_index]
            json.dump(data, f2)
        embed = discord.Embed(title="✅ Success - Delete Product", description=f"以下の商品を削除しました。\n削除した商品: {name}", color=0x00ff00)
        embed.set_footer(text="Status - 200 | Made by Tettu0530#0530",
                                 icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
        await button.response.send_message(embed=embed, ephemeral=True)


class VendingSettingProductSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot, types: str, vending_name: str, options: list, username: str = None):
        super().__init__(
            placeholder="商品を選択してください...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="product_select"
        )
        self.bot = bot
        self.username = username
        self.vending_name = vending_name
        self.types = types

    async def callback(self, interaction: discord.Interaction):
        if self.types == "restock":
            with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.vending_name}.json", "r") as f:
                data = json.load(f)
                for i, product in enumerate(data["products"]):
                    if product["name"] == self.values[0]:
                        await interaction.response.send_modal(VendingSettingRestockModal(bot=self.bot, username=self.username, vending_name=self.vending_name, product_index=int(i)))
                        break
        elif self.types == "take":
            with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.vending_name}.json", "r") as f:
                data = json.load(f)
                for i, product in enumerate(data["products"]):
                    if product["name"] == self.values[0]:
                        index = i
                        break
                products = str(data["products"][index]["product"]).split("\n")
                options = [discord.SelectOption(label=str(i) + "個") for i in range(1, len(products) + 1)]
            await interaction.response.send_message(view=VendingSettingTakeSelectView(bot=self.bot, username=self.username, vending_name=self.vending_name, products=products, product_index=index, options=options), ephemeral=True)
        elif self.types == "delete":
            with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.vending_name}.json", "r") as f:
                data = json.load(f)
                for i, product in enumerate(data["products"]):
                    if product["name"] == self.values[0]:
                        index = i
                        break
            embed = discord.Embed(title="⚠ Warning - Delete Product", description=f"本当に以下の商品を削除しますか？ 削除するとその商品の在庫・価格等のデータがすべて消去されます\n削除する商品:`{self.values[0]}`", color=0xffff00)
            embed.set_footer(text="Status - 199 | Made by Tettu0530#0530",
                                 icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            await interaction.response.send_message(embed=embed, view=VendingSettingProductDeleteView(bot=self.bot, vending_name=self.vending_name, product_index=index, username=self.username), ephemeral=True)


class VendingSettingProductSelectView(discord.ui.View):
    def __init__(self, bot: commands.Bot = None, types: str = None, vending_name: str = None, options: list = None, username: str = None):
        super().__init__(timeout=None)
        self.add_item(VendingSettingProductSelect(
            bot=bot, types=types, username=username, vending_name=vending_name, options=options))


class VendingSettingSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot, types: str, options: list, username: str = None, title: str = None, description: str = None):
        super().__init__(
            options=options,
            placeholder="自販機を選択してください...",
            min_values=1,
            max_values=1,
            custom_id="setting_select"
        )
        self.bot = bot
        self.types = types
        self.username = username
        self.title, self.description = title, description

    async def callback(self, interaction: discord.Interaction):
        if self.types == "log":
            with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.values[0]}.json", "r") as f:
                data = json.load(f)
            with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.values[0]}.json", "w", encoding="utf-8") as f2:
                data["log_channel"] = interaction.channel.id
                json.dump(data, f2)
                await interaction.response.send_message(f"ログを表示するチャンネルを変更しました。\n現在のログ出力チャンネル: {interaction.channel.mention}", ephemeral=True)
        elif self.types == "paypay":
            if os.path.isfile(f"file/paypay/{interaction.user.id}.json") is False:
                embed = discord.Embed(title="❌ Failure - Vending PayPay",
                                      description="このDiscordアカウントは何もPayPayアカウントと連携されていません", color=0xff0000)
                embed.set_footer(text="Status - 404 | Made by Tettu0530#0530",
                                 icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            if os.path.isfile(f"file/account/{data['username']}/vending/{interaction.guild.id}/{interaction.channel.id}.json") is False:
                return await interaction.response.send_message("自販機が設置されていません。 `/vending create` で自販機を作成してからこのコマンドを実行してください")
            else:
                with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.values[0]}.json", "r") as f:
                    data = json.load(f)
                with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.values[0]}.json", "w") as f2:
                    data["paypay_file"] = f"file/paypay/{interaction.user.id}.json"
                    json.dump(data, f2)
                await interaction.response.send_message("PayPayアカウントと自販機を連携しました。")
        elif self.types == "restock_product":
            try:
                with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.values[0]}.json", "r") as restock_f:
                    data = json.load(restock_f)
                    options = [discord.SelectOption(
                        label=product["name"]) for product in data["products"]]
                await interaction.response.send_message(view=VendingSettingProductSelectView(bot=self.bot, username=self.username, types="restock", vending_name=self.values[0], options=options), ephemeral=True)
            except discord.errors.HTTPException:
                embed = discord.Embed(title="❌ Failure - Restock Poduct", description="エラーが発生しました。\nこの自販機にはなにも商品がありません。", color=0xff0000)
                await interaction.response.send_message(embed=embed, ephemeral=True)
        elif self.types == "take_product":
            try:
                with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.values[0]}.json", "r") as take_f:
                    data = json.load(take_f)
                    options = [discord.SelectOption(
                        label=product["name"]) for product in data["products"]]
                await interaction.response.send_message(view=VendingSettingProductSelectView(bot=self.bot, username=self.username, types="take", vending_name=self.values[0], options=options), ephemeral=True)
            except discord.errors.HTTPException:
                embed = discord.Embed(title="❌ Failure - Restock Poduct", description="エラーが発生しました。\nこの自販機にはなにも商品がありません。", color=0xff0000)
                await interaction.response.send_message(embed=embed, ephemeral=True)
        elif self.types == "edit_product":
            with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.values[0]}.json", "r") as edit_f:
                data = json.load(edit_f)
                options = [discord.SelectOption(
                    label=product["name"]) for product in data["products"]]
            await interaction.response.send_message(view=VendingSettingProductSelectView(bot=self.bot, username=self.username, types="edit", vending_name=self.values[0], options=options), ephemeral=True)
        elif self.types == "delete_product":
            with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.values[0]}.json", "r") as delete_f:
                data = json.load(delete_f)
                options = [discord.SelectOption(
                    label=product["name"]) for product in data["products"]]
            await interaction.response.send_message(view=VendingSettingProductSelectView(bot=self.bot, username=self.username, types="delete", vending_name=self.values[0], options=options), ephemeral=True)
        elif self.types == "add_product":
            await interaction.response.send_modal(VendingAddProductModal(bot=self.bot, username=self.username, vending_name=self.values[0]))
        elif self.types == "set":
            with open(f"file/account/{self.username}/vending/{interaction.guild.id}/{self.values[0]}.json", "r") as vending_f:
                data = json.load(vending_f)
                embed = discord.Embed(
                    title=self.title, description=self.description, color=0x00ffff)
                for i in data["products"]:
                    embed.add_field(
                        name=i["name"], value=f"`価格: {i['price']}円`", inline=False)
                embed.set_footer(text="Status - 200 | Made by Tettu0530#0530",
                                 icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                if len(data["products"]) == 0:
                    return await interaction.response.send_message("先に`/vending setting`を使って商品を追加してください", ephemeral=True)
                await interaction.response.send_message(embed=embed, view=VendingPurcaseButtonView(bot=self.bot, username=self.username, vending_name=self.values[0]))


class VendingSettingSelectView(discord.ui.View):
    def __init__(self, types: str = None, bot: commands.Bot = None, options: list = None, title: str = None, description: str = None, username: str = None):
        super().__init__(timeout=None)
        self.add_item(VendingSettingSelect(
            types=types, bot=bot, options=options, username=username, title=title, description=description))


class VendingSettingView(discord.ui.View):
    def __init__(self, bot: commands.Bot, username: str = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.username = username

    @discord.ui.button(label="📈 販売ログの表示", style=discord.ButtonStyle.primary, custom_id="vending_log_button")
    async def log_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        files = [f for f in os.listdir(f"file/account/{self.username}/vending/{button.guild.id}") if os.path.isfile(
            os.path.join(f"file/account/{self.username}/vending/{button.guild.id}", f))]
        files = [os.path.splitext(f)[0] for f in files if f.endswith(".json")]
        options = [discord.SelectOption(label=f) for f in files]
        await button.response.send_message(view=VendingSettingSelectView(bot=self.bot, types="log", options=options, username=self.username), ephemeral=True)

    @discord.ui.button(label="✅ PayPayとの連携", style=discord.ButtonStyle.secondary, custom_id="vending_paypay_button")
    async def paypay_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        files = [f for f in os.listdir(f"file/account/{self.username}/vending/{button.guild.id}") if os.path.isfile(
            os.path.join(f"file/account/{self.username}/vending/{button.guild.id}", f))]
        files = [os.path.splitext(f)[0] for f in files if f.endswith(".json")]
        options = [discord.SelectOption(label=f) for f in files]
        await button.response.send_message(view=VendingSettingSelectView(bot=self.bot, types="paypay", options=options, username=self.username), ephemeral=True)

    @discord.ui.button(label="🔄 商品の補充", style=discord.ButtonStyle.primary, custom_id="vending_restock_button")
    async def restock_product_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        files = [f for f in os.listdir(f"file/account/{self.username}/vending/{button.guild.id}") if os.path.isfile(
            os.path.join(f"file/account/{self.username}/vending/{button.guild.id}", f))]
        files = [os.path.splitext(f)[0] for f in files if f.endswith(".json")]
        options = [discord.SelectOption(label=f) for f in files]
        await button.response.send_message(view=VendingSettingSelectView(bot=self.bot, types="restock_product", options=options, username=self.username), ephemeral=True)

    @discord.ui.button(label="🔀 商品の手動取り出し", style=discord.ButtonStyle.secondary, custom_id="vending_take_button")
    async def take_product_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        files = [f for f in os.listdir(f"file/account/{self.username}/vending/{button.guild.id}") if os.path.isfile(
            os.path.join(f"file/account/{self.username}/vending/{button.guild.id}", f))]
        files = [os.path.splitext(f)[0] for f in files if f.endswith(".json")]
        options = [discord.SelectOption(label=f) for f in files]
        await button.response.send_message(view=VendingSettingSelectView(bot=self.bot, types="take_product", options=options, username=self.username), ephemeral=True)

    @discord.ui.button(label="➕ 商品の追加", style=discord.ButtonStyle.primary, custom_id="vending_add_button")
    async def add_product_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        files = [f for f in os.listdir(f"file/account/{self.username}/vending/{button.guild.id}") if os.path.isfile(
            os.path.join(f"file/account/{self.username}/vending/{button.guild.id}", f))]
        files = [os.path.splitext(f)[0] for f in files if f.endswith(".json")]
        options = [discord.SelectOption(label=f) for f in files]
        await button.response.send_message(view=VendingSettingSelectView(bot=self.bot, types="add_product", options=options, username=self.username), ephemeral=True)

    @discord.ui.button(label="✏ 商品の編集", style=discord.ButtonStyle.secondary, custom_id="vending_edit_button")
    async def edit_product_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        files = [f for f in os.listdir(f"file/account/{self.username}/vending/{button.guild.id}") if os.path.isfile(
            os.path.join(f"file/account/{self.username}/vending/{button.guild.id}", f))]
        files = [os.path.splitext(f)[0] for f in files if f.endswith(".json")]
        options = [discord.SelectOption(label=f) for f in files]
        await button.response.send_message(view=VendingSettingSelectView(bot=self.bot, types="edit_product", options=options, username=self.username), ephemeral=True)
    
    @discord.ui.button(label="✏ 商品の削除", style=discord.ButtonStyle.danger, custom_id="vending_delete_button")
    async def edit_product_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        files = [f for f in os.listdir(f"file/account/{self.username}/vending/{button.guild.id}") if os.path.isfile(
            os.path.join(f"file/account/{self.username}/vending/{button.guild.id}", f))]
        files = [os.path.splitext(f)[0] for f in files if f.endswith(".json")]
        options = [discord.SelectOption(label=f) for f in files]
        await button.response.send_message(view=VendingSettingSelectView(bot=self.bot, types="delete_product", options=options, username=self.username), ephemeral=True)


class AutoVendingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        views = [
            VendingSettingView(bot=self.bot),
            VendingCreateButtonView(bot=self.bot),
            VendingPurcaseButtonView(bot=self.bot),
            VendingPurcaseSelectView(bot=self.bot),
            VendingSettingSelectView(bot=self.bot),
            VendingSettingTakeSelectView(bot=self.bot),
            VendingSettingProductSelectView(bot=self.bot)
        ]
        for view in views:
            self.bot.add_view(view)
        print("[COGS]AutoVendingSlashCog on ready.")

    vending = app_commands.Group(name="vending", description="自動販売機関係コマンド")

    @vending.command(
        name="create",
        description="新しい自販機を作成します"
    )
    async def vending_create(self, interaction: discord.Interaction):
        if os.path.isfile(f"file/keep_login/{interaction.user.id}.json") is False:
            print("a")
            await interaction.response.send_modal(VendingLoginModal(types="create", bot=self.bot))
        else:
            with open(f"file/keep_login/{interaction.user.id}.json", "r") as keep_f:
                data1 = json.load(keep_f)
            with open(f"file/account/{data1[str(interaction.user.id)]}/info.json", "r") as account_f:
                data = json.load(account_f)
                if data["user_id"] == interaction.user.id:
                    if data["subscription"] == True:
                        await interaction.response.send_message("自販機作成に進みます。", view=VendingCreateButtonView(bot=self.bot, username=data["username"]), ephemeral=True)
                    else:
                        await interaction.response.send_message("このZeTNONアカウントは有料プランに契約していません。`/account setting`を使って有料プランに契約してください", ephemeral=True)
                else:
                    await interaction.response.send_message("このZeTNONアカウントはあなたのDiscordアカウントと連携されていません。`/account relink`を使ってアカウントを再連携してください", ephemeral=True)

    @vending.command(
        name="set",
        description="作成した自販機パネルを設置します"
    )
    @app_commands.describe(title="自販機パネルのタイトル")
    @app_commands.describe(description="自販機パネルの説明")
    async def vending_set(self, interaction: discord.Interaction, title: str = None, description: str = None):
        if title is None:
            title = "自動販売機 | Auto Vending"
        if description is None:
            description = "商品を購入するには下のボタンを押してください"
        if os.path.isfile(f"file/keep_login/{interaction.user.id}.json") is False:
            await interaction.response.send_modal(VendingLoginModal(bot=self.bot, types="set", embed_title=title, embed_description=description))
        else:
            with open(f"file/keep_login/{interaction.user.id}.json", "r") as keep_f:
                data1 = json.load(keep_f)
            with open(f"file/account/{data1[str(interaction.user.id)]}/info.json", "r") as account_f:
                data = json.load(account_f)
                if data["user_id"] == interaction.user.id:
                    if data["subscription"] == True:
                        files = [f for f in os.listdir(f"file/account/{data['username']}/vending/{interaction.guild.id}") if os.path.isfile(
                            os.path.join(f"file/account/{data['username']}/vending/{interaction.guild.id}", f))]
                        files = [os.path.splitext(
                            f)[0] for f in files if f.endswith(".json")]
                        options = [discord.SelectOption(
                            label=f) for f in files]
                        await interaction.response.send_message("設置を行う自販機を選択してください。", view=VendingSettingSelectView(bot=self.bot, types="set", options=options, username=data["username"], title=title, description=description), ephemeral=True)
                    else:
                        return await interaction.response.send_message("このZeTNONアカウントは有料プランに契約していません。`/account setting`を使って有料プランに契約してください", ephemeral=True)
                else:
                    return await interaction.response.send_message("このZeTNONアカウントはあなたのDiscordアカウントと連携されていません。`/account relink`を使ってアカウントを再連携してください", ephemeral=True)

    @vending.command(
        name="setting",
        description="自販機等の設定をします"
    )
    async def vending_setting(self, interaction: discord.Interaction):
        if os.path.isfile(f"file/keep_login/{interaction.user.id}.json") is False:
            await interaction.response.send_modal(VendingCreateModal(bot=self.bot))
        else:
            with open(f"file/keep_login/{interaction.user.id}.json", "r") as keep_f:
                data1 = json.load(keep_f)
            with open(f"file/account/{data1[str(interaction.user.id)]}/info.json", "r") as account_f:
                data = json.load(account_f)
                if data["user_id"] == interaction.user.id:
                    if data["subscription"] == True:
                        if os.path.isdir(f"file/account/{data1[str(interaction.user.id)]}/vending") is False:
                            embed = discord.Embed(
                                title="❌　Failure - Vending Setting", description=f"エラーが発生しました。\nこのDiscordアカウントは何も自販機を所持していません", color=0x00ffff)
                            embed.set_footer(text="Status - 404 | Made by Tettu0530#0530",
                                         icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                            return await interaction.response.send_message()
                        dirs = [d for d in os.listdir(f"file/account/{data1[str(interaction.user.id)]}/vending") if os.path.isdir(
                            os.path.join(f"file/account/{data1[str(interaction.user.id)]}/vending", d))]
                        dirs_count = len(dirs)
                        json_count = sum(count_json(os.path.join(
                            f"file/account/{data1[str(interaction.user.id)]}/vending", d)) for d in dirs)
                        embed = discord.Embed(
                            title="自動販売機設定 | Vending Setting", description=f"あなたは{dirs_count}サーバーに{json_count}個の自動販売機を所持しています。", color=0x00ffff)
                        embed.set_footer(text="Status - 200 | Made by Tettu0530#0530",
                                         icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
                        await interaction.response.send_message(embed=embed, view=VendingSettingView(bot=self.bot, username=data["username"]), ephemeral=True)
                    else:
                        return await interaction.response.send_message("このZeTNONアカウントは有料プランに契約していません。`/account setting`を使って有料プランに契約してください", ephemeral=True)
                else:
                    return await interaction.response.send_message("このZeTNONアカウントはあなたのDiscordアカウントと連携されていません。`/account relink`を使ってアカウントを再連携してください", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoVendingCog(bot))
