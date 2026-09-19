import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Online jako {bot.user}")
    try:
        await bot.tree.sync()
        print("Slash zsyncowane")
    except Exception as e:
        print(e)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.guild is None:
        return
    await bot.process_commands(message)

@bot.tree.command(name="metin_boss", description="Bossy PandoraMT2")
async def metin_boss(interaction: discord.Interaction):
    embed = discord.Embed(title="PANDORA MT2 - Bossy", color=0x00ff00)
    embed.add_field(name="Azrael", value="Loch Azraela - 60min", inline=False)
    embed.add_field(name="Beran Setaou", value="DT - 30min", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Ping bota")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong {round(bot.latency*1000)}ms")

bot.run(os.getenv("TOKEN"))
