import discord
from discord import app_commands
from discord.ext import commands
import logging

log = logging.getLogger(__name__)

class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello")
    async def hello(self, interaction: discord.Interaction):
        log.info(f"Hello command called by {interaction.user.name}")
        await interaction.response.send_message(f"Hello, {interaction.user.name}!", ephemeral=True)
        await interaction.channel.send("Hi.")

async def setup(bot):
    await bot.add_cog(Hello(bot))