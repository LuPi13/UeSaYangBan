import discord
from discord import app_commands
from discord.ext import commands


class DM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dm")
    @app_commands.describe(message="dm to send")
    @app_commands.describe(count="Number of times to send the message")
    async def say(self, interaction: discord.Interaction, message: str, count: int = 1):
        for _ in range(count):
            try:
                await interaction.user.send(message)
                await interaction.response.send_message(f"DM을 {interaction.user.mention} 님에게 성공적으로 보냈습니다.", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("DM 발송에 실패했습니다. '설정 - 콘텐츠 및 소셜 - 다이렉트 메시지 스팸' 항목을 '필터링하지 않기' 로 바꾸어 주세요.", ephemeral=True)
                return

async def setup(bot):
    await bot.add_cog(DM(bot))