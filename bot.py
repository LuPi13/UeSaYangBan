import datetime
import logging
import os
import json

import discord
from discord.ext import commands

# 로그 디렉토리 생성
if not os.path.exists('logs'):
    os.makedirs('logs')

# 로깅 설정
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f"logs/log-{datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')}.log", encoding='utf-8'),
                        logging.StreamHandler()
                    ])


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



# 봇 토큰을 config.json에서 읽어오기
try:
    logging.info("Attempting to read token from config.json")
    with open("config.json", "r") as f:
        config = json.load(f)
        token = config["token"]
    logging.info("Token read successfully.")

    if token == "YOUR_TOKEN_HERE":
        logging.error("Please replace 'YOUR_TOKEN_HERE' with your actual bot token in config.json.")
        exit()

    logging.info("Starting bot...")
    client.run(token)
except FileNotFoundError:
    logging.error("config.json not found. Please create it from config.template.json and add your bot token.")
except (KeyError, TypeError):
    logging.error("Token not found in config.json. Make sure it has a 'token' key.")
except Exception as e:
    logging.error(f"An error occurred while running the bot: {e}")
