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

class RestoreCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("[COGS]RestoreSlashCog on ready.")
    


    
async def setup(bot: commands.Bot):
    await bot.add_cog(RestoreCog(bot))