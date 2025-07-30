import datetime
import logging
import os
import json

import discord
from discord.ext import commands


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=None, intents=intents)

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                logging.info(f'{filename} Cog loaded.')
        await self.tree.sync()
        logging.info("Command tree synced.")


    async def on_ready(self):
        logging.info(f'Logged on as {self.user}!')
        print(f'Logged on as {self.user}!')

    async def on_message(self, message: discord.Message):
        # 텍스트 기반 command에 반응하지 않도록 on_message를 override
        if message.author.bot:
            return

logging.info("Setting up intents.")
intents = discord.Intents.default()
intents.message_content = True

client = MyBot()



# 봇 토큰 및 설정값을 config.json에서 읽어오기
try:
    logging.info("Attempting to read config.json")
    with open("config.json", "r") as f:
        config = json.load(f)
        token = config["token"]
        save_log = config.get("save_log", True) # save_log 값이 없으면 기본값 True

    logging.info("Config read successfully.")

    if token == "YOUR_TOKEN_HERE":
        logging.error("Please replace 'YOUR_TOKEN_HERE' with your actual bot token in config.json.")
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
        logging.info("File logging is enabled as per config.json.")
    else:
        logging.info("File logging is disabled as per config.json.")

    logging.info("Starting bot...")
    client.run(token)
except FileNotFoundError:
    logging.error("config.json not found. Please create it from config.template.json and add your bot token.")
except (KeyError, TypeError) as e:
    logging.error(f"Error reading config.json: {e}. Please ensure it has the correct format, same as config.template.json.")
except Exception as e:
    logging.error(f"An error occurred while running the bot: {e}")
