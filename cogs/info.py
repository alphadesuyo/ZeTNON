# Import General Package
import datetime
import mcstatus
import typing

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands


class InfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("[COGS]InfoSlashCog on ready.")

    info = app_commands.Group(name="info", description="情報表示関係コマンド")

    @info.command(
        name="server",
        description="このサーバーの情報を表示します"
    )
    async def info_server(self, interaction: discord.Interaction):
        guild = interaction.guild
        member_count = guild.member_count
        now = datetime.datetime.now()
        created_at1 = guild.created_at
        created_at2 = (now - created_at1)
        target = "days"
        created_at3 = created_at2.find(target)
        created_at = created_at2[:created_at3 + len(target)]
        boosts1 = guild.premium_subscription_count
        boost_level = guild.premium_tier
        boosts = str(guild.premium_subscription_count)
        icon = guild.icon
        icon_url = f"https://cdn.discordapp.com/icons/{interaction.guild_id}/{icon}.webp?size"
        user_count = sum(1 for member in guild.members if not member.bot)
        bot_count = sum(1 for member in guild.members if member.bot)
        embed = discord.Embed(title="✅ Succeess - Guild", color=0x00ff00)
        embed.add_field(name="📄サーバーネーム", value=guild.name)
        embed.add_field(name="🆔サーバーID", value=guild.id)
        embed.add_field(
            name="👥人数", value=f"{guild.member_count}人\n(ユーザー数:{user_count} Bot数:{bot_count})")
        embed.add_field(
            name="💎ブースト数", value=f"{boosts}Boosts (Level{boost_level})")
        embed.add_field(name="👑Owner", value=f"{guild.owner.mention}")
        embed.add_field(name="📅サーバー作成日", value=f"{created_at}前")
        embed.add_field(name="👤実行者", value=f"{interaction.user.name}")
        embed.set_thumbnail(url=icon_url)
        embed.set_footer(text="Status - 200 | Made by Tettu0530#7110",
                         icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
        await interaction.response.send_message(embed=embed)

    @info.command(
        name="user",
        description="指定したユーザーの情報を表示します"
    )
    @app_commands.describe(user="表示するユーザーを指定できます")
    async def info_user(self, interaction: discord.Interaction, user: discord.User):
        guild = interaction.guild
        member = guild.get_member(user.id)
        avatar = user.avatar.url
        created_at = user.created_at
        joined_at = member.joined_at
        status = member.status
        embed = discord.Embed(title=f"✅ Success - User", color=0xffff00)
        embed.add_field(name="📝ユーザー名", value=f"{user.name}")
        embed.add_field(name="🆔ユーザーID", value=f"{user.id}")
        embed.add_field(name="🤖Botか", value=f"{user.bot}")
        embed.add_field(name="🧰アカウント作成時刻", value=f"{created_at}")
        embed.add_field(name="🚪サーバー入室時刻", value=f"{joined_at}")
        embed.add_field(name="🟢ステータス", value=f"{status}")
        embed.set_thumbnail(url=avatar)
        embed.set_footer(text="Status - 200 | Made by Tettu0530#7110",
                         icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")

    @info.command(
        name="mcserver",
        description="Minecraftサーバーの情報を表示します"
    )
    @app_commands.describe(type="Javaサーバーか統合版サーバーか指定できます(デフォルトはJava)")
    @app_commands.describe(server="表示するサーバーのアドレスを指定できます")
    async def info_mcserver(self, interaction: discord.Interaction, server: str, type: typing.Literal["Java", "Bedrock"] = None):
        if type == "Java":
            server = mcstatus.JavaServer(server, 25565)
        elif type == "Bedrock":
            server = mcstatus.BedrockServer(server, 19132)
        status = server.status()
        embed = discord.Embed(title="✅ Success - Mcserver", color=0x00ff00)
        embed.add_field(name="👥オンライン数", value=status.players.online, inline=True)
        embed.add_field(name="💨レイテンシ", value=str(round(status.latency, 1)) + "ms", inline=True)
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(InfoCog(bot))