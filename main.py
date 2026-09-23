import discord
from discord.ext import commands
import os
import re
from datetime import timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

WULGARYZMY = ["kurw","chuj","jeb","pierd","pizd","huj","kutas","cwel","suka","szmat","dziwk","cip","debil","zjeb","pojeb","kurwa","wypierdal","pierdol","fuck","shit","kys","menda","down"]

def zawiera_wulgaryzm(text):
    t = text.lower()
    for w in WULGARYZMY:
        if w in t:
            return w
    return None

warns = {}

@bot.event
async def on_ready():
    print(f"Online jako {bot.user} - PANDORA READY Z AUTO-MOD")
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
        await bot.process_commands(message)
        return
    if message.author.guild_permissions.manage_messages:
        await bot.process_commands(message)
        return
    znalezione = zawiera_wulgaryzm(message.content)
    if znalezione:
        try:
            await message.delete()
        except:
            pass
        user_id = message.author.id
        warns[user_id] = warns.get(user_id, 0) + 1
        if warns[user_id] == 1:
            timeout = timedelta(minutes=10)
        elif warns[user_id] == 2:
            timeout = timedelta(hours=1)
        else:
            timeout = timedelta(hours=24)
        try:
            await message.author.timeout(timeout, reason=f"Auto-mod: {znalezione}")
        except:
            pass
        embed = discord.Embed(title="🚫 AUTO-MODERACJA", description=f"{message.author.mention} - wiadomość usunięta za wulgaryzm!\nTimeout: {timeout}", color=0xff0000)
        embed.set_footer(text=f"Wykryto: {znalezione} | Warn: {warns[user_id]}/3")
        try:
            await message.channel.send(embed=embed, delete_after=10)
        except:
            pass
        return
    await bot.process_commands(message)

@bot.tree.command(name="ping", description="Ping bota")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency*1000)}ms")

@bot.tree.command(name="metin_boss", description="Bossy")
async def metin_boss(interaction: discord.Interaction):
    embed = discord.Embed(title="PANDORA MT2 - Bossy", color=0xff0000)
    embed.add_field(name="Azrael", value="Lodowa Kraina", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="setup-gielda", description="Giełda")
async def setup_gielda(interaction: discord.Interaction):
    embed = discord.Embed(title="💰 GIEŁDA PANDORA MT2", description="Kupuj / Sprzedawaj!", color=0x00ff00)
    await interaction.response.send_message(embed=embed)

token = os.getenv("DISCORD_TOKEN")
if not token:
    token = os.getenv("TOKEN")
bot.run(token)
