import discord
from discord.ext import commands
from discord import app_commands
import yaml
from yaml.loader import SafeLoader
import os
import logging
import base64
import json
import aiohttp
import typing

log = logging.getLogger(__name__)

# 채널-포트 매핑을 저장하기 위한 JSON 파일 경로
LINKS_FILE = 'links.yml'


def load_links():
    """yml 파일에서 모든 연결정보 반환"""
    if not os.path.exists(LINKS_FILE):
        return {}
    try:
        with open(LINKS_FILE, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=SafeLoader)
            return data if data is not None else {}
    except Exception as e:
        log.error(e)
        return {}

def save_links(links):
    """yml 파일에 해당 연결정보 저장"""
    try:
        with open(LINKS_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(links, f, allow_unicode=True, indent=4)
    except Exception as e:
        log.error(f"Failed to save links: {e}")


class Link(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.links = load_links()



    link_group = app_commands.Group(name="link", description="Discord 채널과 Minecraft 서버 연결을 관리합니다.")

    @link_group.command(name="add", description="Discord 채널-Minecraft 서버 연결을 추가합니다. Minecraft 서버에서 `/linkdiscord` 명령어로 나온 문자열이 필요합니다.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(base64_string="/linkdiscord 명령어로 나온 문자열",
                           name="해당 연결의 이름을 지어주세요(영어+숫자, 띄어쓰기X)",
                           channel="연결할 Discord 채널",
                           purpose="연결 목적 (기본값: default)"
                           )
    async def link(self,
                   interaction: discord.Interaction,
                   base64_string: str,
                   name: str,
                   channel: typing.Union[discord.TextChannel, discord.VoiceChannel],
                   purpose: str = "default"
                   ):
        decoded_json_str = None
        await interaction.response.defer(thinking=True, ephemeral=True)

        # base64 디코딩
        try:
            decoded_string = base64.b64decode(base64_string)
            decoded_json_str = decoded_string.decode('utf-8')
        except Exception as e:
            await interaction.followup.send("유효하지 않은 base64 문자열입니다. 다시 시도해주세요.", ephemeral=True)
            log.error(f"Failed to decode base64 string: {e}")

        # JSON parsing
        try:
            data = json.loads(decoded_json_str)
            address = data.get("server_address")
            token = data.get("token")

            if not address or not token:
                log.error("Missing 'server_address' or 'token' in the decoded data. Data: %s", data)
                await interaction.followup.send("유효하지 않은 데이터입니다. 'server_address'와 'token'이 필요합니다.", ephemeral=True)
                return

        except Exception as e:
            log.error(f"Failed to parse JSON: {e}")
            await interaction.followup.send("데이터 형식이 올바르지 않습니다.", ephemeral=True)
            return

        # 중복 연결 확인
        all_links = load_links()
        if name in all_links:
            await interaction.followup.send(f"이미 '{name}'이라는 이름으로 연결이 존재합니다. 다른 이름을 사용해주세요.", ephemeral=True)
            return

        # POST 요청
        if isinstance(channel, discord.TextChannel):
            channel_type = "text"
        elif isinstance(channel, discord.VoiceChannel):
            channel_type = "voice"
        else:
            await interaction.followup.send("지원하지 않는 채널 유형입니다.", ephemeral=True)
            return

        payload = {
            "name": name,
            "token": token,
            "discord_server_id": str(interaction.guild.id),
            "discord_channel_id": str(channel.id),
            "type": channel_type,
            "purpose": purpose
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(address + "/verify", json=payload) as response:
                    if response.status == 200:
                        all_links = load_links()

                        new_link_data = {
                            "discord_server_id": interaction.guild.id,
                            "discord_channel_id": channel.id,
                            "mc_server_address": address,
                            "purpose": purpose
                        }
                        all_links[name] = new_link_data
                        save_links(all_links)
                        log.info(f"Link added: {name} -> {address} for channel {channel.id}")
                        await interaction.followup.send(f"연결이 성공적으로 추가되었습니다: {name} -> {address} ({channel_type})", ephemeral=False)

                    else:
                        error_data = await response.text()
                        log.error(f"Failed to link: {response.status} - {error_data}")
                        await interaction.followup.send(f"연결에 실패했습니다. 서버 응답: {response.status}\n{error_data}", ephemeral=True)
        except aiohttp.ClientError as e:
            log.error(f"HTTP request failed: {e}")
            await interaction.followup.send(f"연결에 실패했습니다. 서버에 접근할 수 없습니다.\n{e}", ephemeral=True)
        except Exception as e:
            log.error(f"Failed to link: {e}")
            await interaction.followup.send(f"연결에 실패했습니다.\n{e}", ephemeral=True)





async def setup(bot):
    await bot.add_cog(Link(bot))
