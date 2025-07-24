import enum

import discord
from discord import app_commands
from discord.ext import commands
import os
from pytubefix import YouTube
import logging
import json

log = logging.getLogger(__name__)

class YoutubeControl(enum.Enum):
    PLAY = "play"
    ADD = "add"
    REMOVE = "remove"
    EXIT = "exit"
    QUEUE = "queue"
    LOOP = "loop"
    SKIP = "skip"
    PAUSE = "pause"
    RESUME = "resume"
    CLEAR = "clear"


import re
from pytubefix.exceptions import PytubeFixError

class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playlists = {}

    def _get_playlist(self, guild_id: int):
        """Ensure a playlist dictionary exists for the guild and return it."""
        if guild_id not in self.playlists:
            self.playlists[guild_id] = {
                "queue": [],
                "now_playing_index": -1,
                "loop": False
            }
        return self.playlists[guild_id]

    def _sanitize_filename(self, name: str) -> str:
        """Remove characters that are invalid for file names."""
        return re.sub(r'[\\/*?:"<>|]', "", name)

    youtube = app_commands.Group(name="youtube", description="유튜브 음원 재생")

    async def _start_playback(self, interaction: discord.Interaction, channel: discord.VoiceChannel = None):
        guild_id = interaction.guild_id
        playlist_data = self._get_playlist(guild_id)
        voice_client = interaction.guild.voice_client

        if not playlist_data["queue"]:
            await interaction.followup.send("재생 목록이 비어있습니다.", ephemeral=True)
            return

        if voice_client and voice_client.is_playing():
            # Already playing, don't start a new playback loop
            await interaction.followup.send("이미 재생 중입니다.", ephemeral=True)
            return

        if channel is None:
            if interaction.user.voice:
                channel = interaction.user.voice.channel
            else:
                await interaction.followup.send("음성 채널에 들어가 있거나, 채널을 명시해 주세요.", ephemeral=True)
                return

        if voice_client is None or not voice_client.is_connected():
            voice_client = await channel.connect()
        elif voice_client.channel != channel:
            await voice_client.move_to(channel)

        # The index is already set by the play command.
        await self._play_next(interaction)

    async def _play_next(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        playlist_data = self._get_playlist(guild_id)
        voice_client = interaction.guild.voice_client

        if not voice_client or not voice_client.is_connected():
            return # Bot was disconnected

        # Stop current playback if any
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()

        queue = playlist_data["queue"]
        index = playlist_data["now_playing_index"]

        if index >= len(queue):
            # Reached end of playlist
            if playlist_data["loop"]:
                playlist_data["now_playing_index"] = 0
            else:
                # No loop, playback finished
                await interaction.followup.send("재생 목록이 끝났습니다.")
                await voice_client.disconnect(force=True)
                return
        
        index = playlist_data["now_playing_index"]
        song = queue[index]
        
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                ffmpeg_path = config["ffmpeg_path"]

            audio_source = discord.FFmpegPCMAudio(song["path"], executable=ffmpeg_path)
            
            def after_playback(error):
                if error:
                    log.error(f"Error during playback: {error}")
                # Prepare for next song
                playlist_data["now_playing_index"] += 1
                self.bot.loop.create_task(self._play_next(interaction))

            voice_client.play(audio_source, after=after_playback)
            await interaction.followup.send(f"Now Playing: **{song['title']}** (요청: {song['requester']})", ephemeral=False)

        except Exception as e:
            log.error(f"Error playing next song: {e}")
            await interaction.followup.send(f"다음 곡을 재생하는 중 오류가 발생했습니다: {e}", ephemeral=False)
            await voice_client.disconnect(force=True)

    @youtube.command(name=YoutubeControl.PLAY.value, description="플레이리스트를 재생합니다. 특정 번호부터 재생할 수 있습니다.")
    @app_commands.describe(index="재생을 시작할 곡의 번호 (기본값: 1)", channel="음성 채널 (선택)")
    async def play(self, interaction: discord.Interaction, index: int = None, channel: discord.VoiceChannel = None):
        await interaction.response.defer(thinking=True, ephemeral=True)
        guild_id = interaction.guild_id
        playlist_data = self._get_playlist(guild_id)
        queue = playlist_data["queue"]

        if not queue:
            await interaction.followup.send("재생 목록이 비어있습니다.", ephemeral=True)
            return

        start_index = 0 # Default to start from the beginning
        if index is not None:
            if 1 <= index <= len(queue):
                start_index = index - 1
            else:
                await interaction.followup.send(f"잘못된 번호입니다. 1부터 {len(queue)} 사이의 숫자를 입력해주세요.", ephemeral=True)
                return

        playlist_data["now_playing_index"] = start_index
        await self._start_playback(interaction, channel)

    @youtube.command(name=YoutubeControl.ADD.value, description="재생 목록에 유튜브 URL을 추가합니다.")
    @app_commands.describe(url="추가할 유튜브 URL", index="추가할 위치 (기본값: 마지막)")
    async def add(self, interaction: discord.Interaction, url: str, index: int = None):
        await interaction.response.defer(thinking=True, ephemeral=True)
        guild_id = interaction.guild_id
        playlist_data = self._get_playlist(guild_id)
        queue = playlist_data['queue']

        try:
            yt = YouTube(url)
            video_id = yt.video_id
            sanitized_title = self._sanitize_filename(yt.title)
            
            guild_dir = os.path.join(os.getcwd(), "youtube", str(guild_id))
            if not os.path.exists(guild_dir):
                os.makedirs(guild_dir)

            file_path = os.path.join(guild_dir, f"{video_id}.mp3")

            if not os.path.exists(file_path):
                audio_stream = yt.streams.filter(only_audio=True).first()
                downloaded_file = audio_stream.download(output_path=guild_dir)
                
                base, ext = os.path.splitext(downloaded_file)
                new_file_path = os.path.join(guild_dir, f"{video_id}.mp3")
                os.rename(downloaded_file, new_file_path)
                file_path = new_file_path

            song = {
                "title": yt.title,
                "url": url,
                "path": file_path,
                "video_id": video_id,
                "requester": interaction.user.mention
            }

            if index is None:
                queue.append(song)
                await interaction.followup.send(f"**{yt.title}**을(를) 재생 목록 마지막에 추가했습니다.")
            else:
                # Adjust index to be 0-based
                if 1 <= index <= len(queue) + 1:
                    queue.insert(index - 1, song)
                    await interaction.followup.send(f"**{yt.title}**을(를) 재생 목록 {index}번에 추가했습니다.")
                else:
                    await interaction.followup.send(f"잘못된 위치입니다. 1부터 {len(queue) + 1} 사이의 숫자를 입력해주세요.", ephemeral=True)
                    return

        except PytubeFixError as e:
            log.error(f"PytubeFix error while adding URL {url}: {e}")
            await interaction.followup.send(f"유튜브 URL을 처리하는 중 오류가 발생했습니다: {e}", ephemeral=False)
        except Exception as e:
            log.error(f"Error adding song: {e}")
            await interaction.followup.send(f"노래를 추가하는 중 오류가 발생했습니다: {e}", ephemeral=False)

    @youtube.command(name=YoutubeControl.REMOVE.value, description="재생 목록에서 항목을 제거하고 파일을 삭제합니다.")
    @app_commands.describe(number="제거할 항목의 번호")
    async def remove(self, interaction: discord.Interaction, number: int):
        await interaction.response.defer(ephemeral=True)
        guild_id = interaction.guild_id
        playlist_data = self._get_playlist(guild_id)
        queue = playlist_data["queue"]

        if not 1 <= number <= len(queue):
            await interaction.followup.send(f"잘못된 번호입니다. 1부터 {len(queue)} 사이의 숫자를 입력해주세요.", ephemeral=True)
            return

        removed_song = queue.pop(number - 1)
        await interaction.followup.send(f"**{removed_song['title']}**을(를) 재생 목록에서 제거했습니다.")

        # Check if the song file is used in any other playlist
        is_used_elsewhere = False
        for other_guild_id, other_playlist_data in self.playlists.items():
            if other_guild_id != guild_id:
                for song in other_playlist_data["queue"]:
                    if song["path"] == removed_song["path"]:
                        is_used_elsewhere = True
                        break
            if is_used_elsewhere:
                break

        if not is_used_elsewhere and os.path.exists(removed_song["path"]):
            try:
                os.remove(removed_song["path"])
                log.info(f"Removed song file: {removed_song['path']}")
            except OSError as e:
                log.error(f"Error removing file {removed_song['path']}: {e}")

        current_index = playlist_data["now_playing_index"]
        if current_index == number - 1:
            if current_index >= len(queue):
                playlist_data["now_playing_index"] = -1
                if interaction.guild.voice_client:
                    interaction.guild.voice_client.stop()
            else:
                await self._play_next(interaction)
        elif current_index > number - 1:
            playlist_data["now_playing_index"] -= 1

    @youtube.command(name=YoutubeControl.EXIT.value, description="봇을 음성 채널에서 내보냅니다.")
    async def exit(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        playlist_data = self._get_playlist(interaction.guild_id)

        if voice_client and voice_client.is_connected():
            # Stop playback and disconnect
            playlist_data["now_playing_index"] = -1
            voice_client.stop()
            await voice_client.disconnect()
            await interaction.response.send_message("음성 채널에서 나갔습니다. 플레이리스트는 유지됩니다.", ephemeral=False)
        else:
            await interaction.response.send_message("봇이 음성 채널에 없습니다.", ephemeral=True)

    @youtube.command(name=YoutubeControl.QUEUE.value, description="재생 목록을 보여줍니다.")
    async def queue(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild_id = interaction.guild_id
        playlist_data = self._get_playlist(guild_id)
        queue = playlist_data["queue"]

        if not queue:
            await interaction.followup.send("재생 목록이 비어있습니다.", ephemeral=True)
            return

        embed = discord.Embed(title="🎶 재생 목록", color=discord.Color.blue())
        
        queue_text = ""
        for i, song in enumerate(queue):
            is_playing = "▶️ " if i == playlist_data["now_playing_index"] else ""
            queue_text += f"{is_playing}{i + 1}. **{song['title']}** - 요청: {song['requester']}\n"

        embed.description = queue_text
        embed.set_footer(text=f"총 {len(queue)}곡 | 반복: {"활성화" if playlist_data["loop"] else "비활성화"}")
        
        await interaction.followup.send(embed=embed)

    @youtube.command(name=YoutubeControl.LOOP.value, description="플레이리스트 반복 재생을 설정하거나 해제합니다.")
    async def loop(self, interaction: discord.Interaction):
        playlist_data = self._get_playlist(interaction.guild_id)
        playlist_data["loop"] = not playlist_data["loop"]
        status = "활성화" if playlist_data["loop"] else "비활성화"
        await interaction.response.send_message(f"🔁 반복 재생이 **{status}**되었습니다.", ephemeral=False)

    @youtube.command(name=YoutubeControl.SKIP.value, description="현재 재생 중인 곡을 건너뜁니다.")
    async def skip(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop() # This will trigger the after_playback callback
            await interaction.response.send_message("⏭️ 현재 곡을 건너뛰었습니다.", ephemeral=False)
        else:
            await interaction.response.send_message("❌ 재생 중인 곡이 없습니다.", ephemeral=True)

    @youtube.command(name=YoutubeControl.PAUSE.value, description="현재 재생 중인 곡을 일시정지합니다.")
    async def pause(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("⏸️ 재생을 일시정지했습니다.", ephemeral=False)
        else:
            await interaction.response.send_message("❌ 일시정지할 곡이 없습니다.", ephemeral=True)

    @youtube.command(name=YoutubeControl.RESUME.value, description="일시정지된 곡을 다시 재생합니다.")
    async def resume(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("▶️ 재생을 다시 시작합니다.", ephemeral=False)
        else:
            await interaction.response.send_message("❌ 다시 재생할 곡이 없습니다.", ephemeral=True)

    @youtube.command(name=YoutubeControl.CLEAR.value, description="플레이리스트를 모두 삭제합니다.")
    async def clear(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        playlist_data = self._get_playlist(guild_id)
        queue = playlist_data["queue"]

        if not queue:
            await interaction.response.send_message("❌ 삭제할 플레이리스트가 없습니다.", ephemeral=True)
            return

        # Stop playback if it's running
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
        
        # Create a copy of the queue to iterate over for file deletion
        queue_copy = list(queue)
        # Clear the actual queue
        queue.clear()
        playlist_data["now_playing_index"] = -1

        # Delete song files if they are not used in other playlists
        for song_to_delete in queue_copy:
            is_used_elsewhere = False
            for other_guild_id, other_playlist_data in self.playlists.items():
                if other_guild_id != guild_id:
                    for song in other_playlist_data["queue"]:
                        if song["path"] == song_to_delete["path"]:
                            is_used_elsewhere = True
                            break
                if is_used_elsewhere:
                    break
            
            if not is_used_elsewhere and os.path.exists(song_to_delete["path"]):
                try:
                    os.remove(song_to_delete["path"])
                    log.info(f"Removed song file: {song_to_delete["path"]}")
                except OSError as e:
                    log.error(f"Error removing file {song_to_delete["path"]}: {e}")

        await interaction.response.send_message("🗑️ 플레이리스트를 모두 삭제했습니다.", ephemeral=False)


async def setup(bot):
    await bot.add_cog(Youtube(bot))