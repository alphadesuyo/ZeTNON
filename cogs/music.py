# Import General Package
import asyncio
import youtube_dl

# Import Discord Package
import discord
from discord import app_commands
from discord.ext import commands

youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl':  "sample_music" + '.%(ext)s',
    'postprocessors': [
        {'key': 'FFmpegExtractAudio',
         'preferredcodec': 'mp3',
         'preferredquality': '192'},
        {'key': 'FFmpegMetadata'},
    ],
}

ydl = youtube_dl.YoutubeDL(ydl_opts)

ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


song_queue = asyncio.Queue()


async def play_queue(bot: commands.Bot, interaction: discord.Interaction):
    if interaction.guild.voice_client.is_playing():
        return
    if song_queue.empty():
        return
    msg = await song_queue.get()
    player = await YTDLSource.from_url(msg, loop=bot.loop, stream=True)
    loop = asyncio.get_event_loop()
    interaction.guild.voice_client.play(
        player, after=lambda _: loop.create_task(
            play_queue(bot=bot, interaction=interaction))
    )


class MusicCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("[COGS]MusicSlashCog on ready.")

    music = app_commands.Group(name="music", description="音楽関係コマンド")

    @music.command(
        name="join",
        description="ボイスチャットに入室します"
    )
    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice is None:
            embed = discord.Embed(
                title="❌ Failure - Join", description="エラーが発生しました。\nあなたはボイスチャンネルに接続していないか、Botがアクセスできないボイスチャンネルです", color=0x00ff00)
            embed.set_footer(text="Status - 400 | Made by Tettu0530New#7110")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            if interaction.guild.voice_client:
                if interaction.user.voice.channel == interaction.guild.voice_client.channel:
                    embed = discord.Embed(
                        title="❌ Failure - Join", description="エラーが発生しました。\nBotはすでにそのチャンネルに入室しています", color=0x00ff00)
                    embed.set_footer(
                        text="Status - 400 | Made by Tettu0530New#7110")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.guild.voice_client.disconnect()
                    await asyncio.sleep(0.5)
                    await interaction.user.voice.channel.connect()
            else:
                await interaction.user.voice.channel.connect()
                await interaction.response.send_message("✅ボイスチャンネルに接続しました")

    @music.command(
        name="leave",
        description="ボイスチャットから退出します"
    )
    async def leave(self, interaction: discord.Interaction):
        if interaction.guild.voice_client is None:
            embed = discord.Embed(
                title="❌ Failure - Leave", description="エラーが発生しました。\nBotはすでにそのチャンネルから退出しています", color=0x00ff00)
            embed.set_footer(text="Status - 400 | Made by Tettu0530#0530",
                             icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            if interaction.guild.voice_client.is_playing():
                interaction.guild.voice_client.stop()
            if song_queue.empty():
                await interaction.guild.voice_client.disconnect()
                await interaction.response.send_message("✅ボイスチャンネルから退出しました")
            else:
                for i in range(song_queue.qsize()):
                    song_queue.put_nowait(None)
                await asyncio.sleep(0.5)
                await interaction.guild.voice_client.disconnect()
                await interaction.response.send_message("✅ボイスチャンネルから退出しました")

    @music.command(
        name="play",
        description="入力ワードまたはURLをYouTubeで検索し再生します"
    )
    @app_commands.describe(word="検索ワードまたはURLから音楽を再生します")
    async def play(self, interaction: discord.Interaction, word: str):
        if interaction.user.voice is None:
            embed = discord.Embed(
                title="❌ Failure - Join", description="エラーが発生しました。\nあなたはボイスチャンネルに接続していません", color=0x00ff00)
            embed.set_footer(text="Status - 400 | Made by Tettu0530#0530",
                             icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            if interaction.guild.voice_client.is_playing():
                pl = await YTDLSource.from_url(url=word, loop=self.bot.loop, stream=True)
                await song_queue.put(word)
                await interaction.response.send_message("キューに`{}`を追加しました。".format(pl.title))
                await play_queue(bot=self.bot, interaction=interaction)
            else:
                await song_queue.put(word)
                player = await YTDLSource.from_url(url=word, loop=self.bot.loop, stream=True)
                await interaction.response.send_message("`{}`を再生中です。".format(player.title))
                await play_queue(bot=self.bot, interaction=interaction)

    @music.command(
        name="pause",
        description="再生中の曲を一時停止します"
    )
    async def music_pause(self, interaction: discord.Interaction):
        if interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.pause()
            await interaction.response.send_message("✅一時停止しました。再開時は`/resume`を使ってください")
        else:
            embed = discord.Embed(
                title="❌ Failure - Pause", description="エラーが発生しました。\n現在曲は再生されていません", color=0xff0000)
            embed.set_footer(
                text="Status - 400", icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @music.command(
        name="resume",
        description="一時停止中の曲を再開します"
    )
    async def music_resume(self, interaction: discord.Interaction):
        if interaction.guild.voice_client.is_playing():
            embed = discord.Embed(
                title="❌ Failure - Pause", description="エラーが発生しました。\n現在曲は再生されていません", color=0xff0000)
            embed.set_footer(
                text="Status - 400", icon_url="https://cdn.discordapp.com/avatars/941871491337814056/fb276cd1dc430e643f233594564e0559.webp?size=128")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            interaction.guild.voice_client.resume()

    @music.command(
        name="stop",
        description="再生中の音楽を停止します"
    )
    async def music_stop(self, interaction: discord.Interaction):
        if interaction.guild.voice_client is None:
            return
        if not interaction.guild.voice_client.is_playing():
            return
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("✅停止しました。")

    @music.command(
        name="skip",
        description="現在再生中の曲をスキップします"
    )
    async def music_skip(self, interaction: discord.Interaction):
        if interaction.guild.voice_client.is_playing():
            if song_queue.qsize() == 0:
                interaction.guild.voice_client.stop()
                await interaction.response.send_message("✅曲をスキップしました。再生が終了しました。")
            else:
                interaction.guild.voice_client.stop()
                song = await song_queue.get()
                player = await YTDLSource.from_url(url=song, loop=self.bot.loop, stream=True)
                loop = asyncio.get_event_loop()
                interaction.guild.voice_client.play(
                    player, after=lambda _: loop.create_task(
                        play_queue(interaction))
                )
                await interaction.response.send_message("✅曲をスキップしました。\n`{}`を再生中です。".format(player.title))
        else:
            if song_queue.qsize() == 0:
                interaction.guild.voice_client.stop()
                await interaction.response.send_message("✅曲をスキップしました。再生が終了しました。")
            else:
                song = await song_queue.get()
                player = await YTDLSource.from_url(url=song, loop=self.bot.loop, stream=True)
                loop = asyncio.get_event_loop()
                interaction.guild.voice_client.play(
                    player, after=lambda _: loop.create_task(
                        play_queue(interaction))
                )
                await interaction.response.send_message("✅曲をスキップしました。\n`{}`を再生中です。".format(player.title))


async def setup(bot: commands.Bot):
    await bot.add_cog(MusicCog(bot))
