import discord
from discord import app_commands
from discord.ext import commands


class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="say", description="Say something to the channel.")
    @app_commands.describe(message="The message to say.")
    @app_commands.describe(channel="The channel to say.")
    async def say(self, interaction: discord.Interaction, message: str, channel: discord.TextChannel):
        await channel.send(message)
        await interaction.response.send_message(f"Message sent to {channel.mention}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Say(bot))