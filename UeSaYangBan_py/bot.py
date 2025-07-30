import datetime
import logging
import os
import yaml

import discord
from discord.ext import commands


import datetime
import logging
import os
import yaml
from aiohttp import web

import discord
from discord.ext import commands


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=None, intents=intents)
        self.web_server = None
        self.web_runner = None

    async def setup_hook(self):
        # Cogs 디렉토리에서 모든 .py 파일을 로드
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                logging.info(f'{filename} Cog loaded.')
        await self.tree.sync()
        logging.info("Command tree synced.")

        # HTTP 서버 설정
        app = web.Application()
        event_handler_cog = self.get_cog("EventHandlerCog")
        if event_handler_cog:
            app.router.add_post("/event", event_handler_cog.handle_minecraft_event)
            logging.info("Added /event route to the web server.")
        else:
            logging.warning("EventHandlerCog not found, /event route not set.")

        self.web_runner = web.AppRunner(app)
        await self.web_runner.setup()

        host = config.get("http_host", "127.0.0.1")
        port = config.get("http_port", 8080)
        self.web_server = web.TCPSite(self.web_runner, host, port)
        await self.web_server.start()
        logging.info(f"HTTP server started on http://{host}:{port}")

    async def on_ready(self):
        logging.info(f'Logged on as {self.user}!')

    async def on_message(self, message: discord.Message):
        # 텍스트 기반 command에 반응하지 않도록 on_message를 override
        if message.author.bot:
            return

    async def close(self):
        # 봇이 종료될 때 웹 서버도 함께 정리
        await super().close()
        if self.web_server:
            await self.web_server.stop()
            logging.info("HTTP server stopped.")
        if self.web_runner:
            await self.web_runner.cleanup()
            logging.info("HTTP runner cleaned up.")

logging.info("Setting up intents.")
intents = discord.Intents.default()
intents.message_content = True

client = MyBot()



# 봇 토큰 및 설정값을 config.yml에서 읽어오기
try:
    logging.info("Attempting to read config.yml")
    with open("config.yml", "r", encoding='utf-8') as f:
        config = yaml.safe_load(f)
        token = config.get("token")
        save_log = config.get("save_log", True) # save_log 값이 없으면 기본값 True

    logging.info("Config read successfully.")

    if token == "YOUR_TOKEN_HERE":
        logging.error("Please replace 'YOUR_TOKEN_HERE' with your actual bot token in config.yml.")
        exit()

    # 로깅 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 기존 핸들러 제거 (중복 방지)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # StreamHandler (콘솔 출력) 항상 추가
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(stream_handler)

    if save_log:
        # 로그 디렉토리 생성
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # FileHandler 추가
        file_handler = logging.FileHandler(f"logs/log-{datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')}.log", encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        root_logger.addHandler(file_handler)
        logging.info("File logging is enabled as per config.yml.")
    else:
        logging.info("File logging is disabled as per config.yml.")

    logging.info("Starting bot...")
    client.run(token)
except FileNotFoundError:
    logging.error("config.yml not found. Please create it from config.template.yml and add your bot token.")
except (KeyError, TypeError) as e:
    logging.error(f"Error reading config.yml: {e}. Please ensure it has the correct format, same as config.template.json.")
except Exception as e:
    logging.error(f"An error occurred while running the bot: {e}")
