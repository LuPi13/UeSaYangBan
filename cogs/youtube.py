import discord
from discord import app_commands
from discord.ext import commands
import os
from pytubefix import YouTube
import logging

log = logging.getLogger(__name__)


class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="youtube", description="유튜브 URL을 현재 음성 채널에서 재생합니다.")
    @app_commands.describe(url="재생할 유튜브 URL")
    @app_commands.describe(channel="음성 채널")
    async def say(self, interaction: discord.Interaction, url: str, channel: discord.VoiceChannel = None):
        log.info(f"{interaction.user.name} requested to play YouTube URL: {url} in channel: {channel.name if channel else 'None'}")
        if channel is None:
            channel = interaction.user.voice.channel if interaction.user.voice else None

        if channel is None:
            await interaction.response.send_message("음성 채널에 연결되어 있지 않습니다.", ephemeral=True)
            log.warning(f"{interaction.user.name} is not connected to a voice channel.")
            return

        voice_client = interaction.guild.voice_client
        if voice_client is None or not voice_client.is_connected():
            voice_client = await channel.connect()

            await interaction.response.send_message(f"음원 추출을 시작합니다. 영상 길이가 길 경우 시간이 걸릴 수 있습니다.", ephemeral=True)

        # 유튜브 URL 재생 로직
        # 유튜브 URL에서 음원만 추출하여 youtube.mp3로 저장
        try:
            yt = YouTube(url)
            audio_stream = yt.streams.filter(only_audio=True).first()

            # 폴더 내부 제거
            if os.path.exists(f"{os.getcwd()}/youtube"):
                for file in os.listdir(f"{os.getcwd()}/youtube"):
                    file_path = os.path.join(f"{os.getcwd()}/youtube", file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)

            audio_file = audio_stream.download(f"{os.getcwd()}/youtube")


            # convert to mp3
            base, ext = os.path.splitext(audio_file)
            mp3_file = base + ".mp3"
            os.rename(audio_file, mp3_file)

            log.info(f"Downloaded audio from {url} to {mp3_file}")

            if voice_client.is_playing():
                voice_client.stop()

            def after_playback(error):
                if error:
                    log.error(f"Error playing audio: {error}")
                # 재생 종료 후 음성 채널에서 나가기
                if voice_client.is_connected():
                    self.bot.loop.create_task(voice_client.disconnect())
                    log.info(f"Disconnected from voice channel {channel.name} after playing {yt.title}.")

                    # Clean up the downloaded mp3 file
                    if os.path.exists(mp3_file):
                        os.remove(mp3_file)
                        log.info(f"Removed temporary file {mp3_file}")

            await interaction.response.send_message(f"{channel.mention}에서 유튜브 URL을 재생합니다: {url}")
            voice_client.play(discord.FFmpegPCMAudio(mp3_file, executable="C:/ffmpeg/bin/ffmpeg.exe"), after=after_playback)


        # 다른 프로세스가 파일 사용 중 에러는 다른 음악을 재생할 수 있도록 예외 처리



        except Exception as e:
            log.error(f"Error processing YouTube URL {url}: {str(e)}")
            await interaction.followup.send(f"유튜브 URL을 처리하는 중 오류가 발생했습니다: {str(e)}", ephemeral=True)
            return


async def setup(bot):
    await bot.add_cog(Youtube(bot))