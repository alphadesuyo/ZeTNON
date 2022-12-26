# Import General Package
import asyncio
import json
import os
import datetime
import pytz
import glob

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands


class VendingButtonView(discord.ui.View):
    def __init__(self, bot, username=None, owner: discord.User = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.username = username
        self.owner = owner

    @discord.ui.button(label="🛒購入", style=discord.ButtonStyle.green, custom_id="persistent_view:btn_vending_purchase")
    async def callback_vending_purchase(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.username is None:
            with open(f"file/vending/{str(interaction.guild_id)}")


class VendingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("[COGS]VendingSlashCog on ready.")

    vending = app_commands.Group(name="vending", description="自販機関係のコマンド")

    @vending.command(
        name="set",
        description="自販機を設置します"
    )
    async def vending_set(self, interaction: discord.Interaction):
        is_dir = os.path.isdir(f"file/account/{str(interaction.user.id)}")
        if is_dir is True:
            os.makedirs(f"file/account/{str(interaction.user.id)}/vending")
            with open(f"file/account/{str(interaction.user.id)}/vending/general.txt", "w", encoding="utf-8") as f:
                content = {
                        "guild_id": str(interaction.guild_id),
                        "product1": {
                            "name": "商品1",
                            "price": "100"
                        },
                        "product2": {
                            "name": "商品2",
                            "price": "100"
                        },
                        "product3": {
                            "name": "商品3",
                            "price": "100"
                        },
                        "product4": {
                            "name": "商品4",
                            "price": "100"
                        },
                        "product5": {
                            "name": "商品5",
                            "price": "100"
                        }
                    }
                json.dump(content, f)
            with open(f"file/account/{str(interaction.user.id)}/vending/general.txt", "r") as f:
                content = json.load(f)
                embed = discord.Embed(
                    title="自販機", description="注文するには下のボタンを押してください", color=0x00ff00)
                for i in range(1, len(content) - 1):
                    embed.add_field(
                        name=content[f"product{i}"]["name"], value=f"価格: `{content[f'product{i}']['price']}円`")
                await interaction.response.send_message(embed=embed, view=VendingButtonView(bot=self.bot, username=, owner=interaction.user))
        else:
            is_dir2 = os.path.isdir(
                f"file/vending/{str(interaction.guild_id)}")
            if is_dir2 is True:
                with open(f"file/vending/{str(interaction.guild_id)}/general.txt", "w", encoding="utf-8") as f:
                    content = {
                        "guild_id": str(interaction.guild_id),
                        "product1": {
                            "name": "商品1",
                            "price": "100"
                        },
                        "product2": {
                            "name": "商品2",
                            "price": "100"
                        },
                        "product3": {
                            "name": "商品3",
                            "price": "100"
                        },
                        "product4": {
                            "name": "商品4",
                            "price": "100"
                        },
                        "product5": {
                            "name": "商品5",
                            "price": "100"
                        }
                    }
                    json.dump(content, f)
                with open(f"file/vending/{str(interaction.guild_id)}/general.txt", "r") as f:
                    content = json.load(f)
                    embed = discord.Embed(
                        title="自販機", description="注文するには下のボタンを押してください", color=0x00ff00)
                    for i in range(1, len(content) - 1):
                        embed.add_field(
                            name=content[f"product{i}"]["name"], value=f"価格: `{content[f'product{i}']['price']}円`")
                    await interaction.response.send_message(embed=embed, view=VendingButtonView(bot=self.bot, username=None, owner=interaction.user))
            else:
                os.makedirs(f"file/vending/{str(interaction.guild_id)}")
                with open(f"file/vending/{str(interaction.guild_id)}/general.txt", "w", encoding="utf-8") as f:
                    content = {
                        "guild_id": str(interaction.guild_id),
                        "product1": {
                            "name": "商品1",
                            "price": "100"
                        },
                        "product2": {
                            "name": "商品2",
                            "price": "100"
                        },
                        "product3": {
                            "name": "商品3",
                            "price": "100"
                        },
                        "product4": {
                            "name": "商品4",
                            "price": "100"
                        },
                        "product5": {
                            "name": "商品5",
                            "price": "100"
                        }
                    }
                    json.dump(content, f)
                with open(f"file/vending/{str(interaction.guild_id)}/general.txt", "r") as f:
                    content = json.load(f)
                    embed = discord.Embed(
                        title="自販機", description="注文するには下のボタンを押してください", color=0x00ff00)
                    for i in range(1, len(content) - 1):
                        embed.add_field(
                            name=content[f"product{i}"]["name"], value=f"価格: `{content[f'product{i}']['price']}円`", inline=False)
                    embed2 = discord.Embed(title="✅Success - Vending", description="自販機パネルを設置しました。\nZeTNONアカウントで自販機パネル保存するのをお勧めします。")
                    await interaction.response.send_message(embed=embed2)
                    await interaction.followup.send(embed=embed, view=VendingButtonView(bot=self.bot, username=None, owner=interaction.user))


async def setup(bot: commands.Bot):
    await bot.add_cog(VendingCog(bot))