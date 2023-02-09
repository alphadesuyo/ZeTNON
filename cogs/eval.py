# Import General Package
from discord.ext import commands
from discord import app_commands
import discord
import configparser
import contextlib
import textwrap
import traceback
import io

conf = configparser.ConfigParser()
conf.read("file/conf/config.ini", encoding="utf-8")
MANAGE_USERS = [941871491337814056, 935563914354253924, 994953877625507851, 1044937269162823751]

# Import Discord Package


class EvalCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("[COGS]EvalSlashCog on ready.")

    @app_commands.command(
        name="eval",
        description="Bot管理者用コマンド"
    )
    @app_commands.describe(code="実行するコードを入力できます")
    async def eval(self, interaction: discord.Interaction, code: str):
        if interaction.user.id in MANAGE_USERS:
            global result1, result2
            code_eval = str(code)
            env = {
                "bot": self.bot,
                "interaction": interaction,
            }
            env.update(globals())
            stdout = io.StringIO()
            to_compile = f"async def func():\n{textwrap.indent(code_eval, '  ')}"
            try:
                exec(to_compile, env)
            except Exception as e:
                return await interaction.response.send_message(f"```py\n{e.__class__.__name__}: {e}\n```")
            func = env["func"]
            try:
                with contextlib.redirect_stdout(stdout):
                    ret = await func()
            except Exception as e:
                value = stdout.getvalue()
                await interaction.response.send_message(f"```py\n{value}{traceback.format_exc()}\n```")
            else:
                value = stdout.getvalue()
                if ret is None:
                    if value:
                        await interaction.response.send_message(f"```py\n{value}\n```")
                else:
                    result = ret
                    await interaction.response.send_message(f"```py\n{value}{ret}\n```")


async def setup(bot: commands.Bot):
    await bot.add_cog(EvalCog(bot))
