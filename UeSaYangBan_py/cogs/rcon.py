import discord
import yaml
from discord.ext import commands
from discord import app_commands
import json
import os
from mcrcon import MCRcon, MCRconException
import asyncio
import logging

log = logging.getLogger(__name__)

# 채널-포트 매핑을 저장하기 위한 JSON 파일 경로
LINKS_FILE = 'links.yml'


def load_links():
    """JSON 파일에서 채널-포트 매핑을 불러옵니다."""
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return None


class Rcon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.links = load_links()

    def save_links(self):
        """JSON 파일에 채널-포트 매핑을 저장합니다."""
        with open(LINKS_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(self.links, f, indent=4, allow_unicode=True)


    rcon = app_commands.Group(name="rcon", description="RCON 명령어를 관리합니다.")

    @rcon.command(name="setting", description="RCON 서버의 포트, 비밀번호 등을 설정합니다.")
    @app_commands.describe(port="RCON 서버의 포트 (기본값: 25575)")
    @app_commands.describe(password="RCON 서버의 비밀번호")
    @app_commands.checks.has_permissions(administrator=True)
    async def setting(self, interaction: discord.Interaction, port: int = None, password: str = None):
        """RCON 서버의 비밀번호를 설정합니다."""
        # await interaction.response.defer(thinking=True, ephemeral=True)
        channel_id = str(interaction.channel_id)
        if (port is None) and (password is None):
            await interaction.followup.send("포트와 비밀번호 중 적어도 하나는 입력해주세요.", ephemeral=True)
            return

        keys = list(self.links.keys())
        print(keys)
        for key in keys:
            print(self.links[key])
            print(channel_id)
            if self.links[key]["purpose"] != "rcon":
                continue

            if str(self.links[key]["discord_channel_id"]) == str(channel_id):
                if port is not None:
                    self.links[key]["rcon_port"] = port
                if password is not None:
                    self.links[key]["rcon_password"] = password

                self.save_links()
                log.info(f"Setting RCON for channel {interaction.channel.id}")
                await interaction.followup.send("RCON 설정이 업데이트되었습니다.", ephemeral=False)
                return

        await interaction.followup.send("이 채널에 RCON 연결 정보가 없습니다. `/link <base64_string> purpose=rcon` 명령어로 먼저 연결해주세요.", ephemeral=True)
        log.warning(f"RCON password set attempted in unlinked channel {interaction.channel.id}")


    @rcon.command(name="send", description="연결된 RCON으로 명령어를 전송합니다.")
    @app_commands.describe(command="전송할 RCON 명령어")
    @app_commands.checks.has_permissions(administrator=True)
    async def send_command(self, interaction: discord.Interaction, command: str):
        """연결된 RCON으로 명령어를 전송하고 결과를 반환합니다."""
        # await interaction.response.defer(thinking=True, ephemeral=True)
        channel_id = str(interaction.channel_id)

        keys = list(self.links.keys())

        for key in keys:
            if self.links[key]["purpose"] != "rcon":
                continue

            if str(self.links[key]["discord_channel_id"]) == str(channel_id):
                host = self.links[key]["mc_http_address"]
                port = self.links[key]["rcon_port"]
                password = self.links[key]["rcon_password"]
                log.info(f"RCON command '{command}' will be sent to {host}:{port} from channel {interaction.channel.id}")

                try:
                    def rcon_command_sync():
                        with MCRcon(host, password, port, timeout=10) as mcr:
                            mcr.connect()
                            return mcr.command(command)

                    response = await asyncio.to_thread(rcon_command_sync)
                    log.info(f"RCON command '{command}' sent. Response: '{response}'")

                    if response:
                        await interaction.followup.send(f"```\n{response}\n```", ephemeral=False)
                    else:
                        await interaction.followup.send("명령어가 실행되었지만, 서버에서 별도의 응답을 반환하지 않았습니다.", ephemeral=False)

                    return

                except MCRconException as e:
                    log.error(f"MCRconException for channel {interaction.channel.id} to {host}:{port} with command '{command}': {e}")
                    await interaction.followup.send(f"RCON 오류: `{e}`\n서버 주소, 포트, 비밀번호가 올바른지 또는 서버가 실행 중인지 확인해주세요.", ephemeral=False)
                    return
                except Exception as e:
                    log.critical(f"Unexpected error during RCON command for channel {interaction.channel.id} to {host}:{port} with command '{command}': {e}", exc_info=True)
                    await interaction.followup.send(f"알 수 없는 오류가 발생했습니다: `{e}`\n연결 시간 초과일 수 있습니다. 서버 상태를 확인해주세요.", ephemeral=False)
                    return

            await interaction.followup.send("이 채널에 RCON 연결 정보가 없습니다. `/link <base64_string> purpose=rcon` 명령어로 먼저 연결해주세요.", ephemeral=True)
            return


async def setup(bot):
    await bot.add_cog(Rcon(bot))