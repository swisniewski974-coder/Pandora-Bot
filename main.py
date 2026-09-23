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

# === AUTO-MODERACJA - LISTA WULGARYZMÓW ===
WULGARYZMY = [
    "kurw", "chuj", "jeb", "pierd", "pizd", "huj", "kutas", "cwel",
    "suka", "szmat", "dziwk", "cip", "debil", "down", "spierd",
    "zjeb", "pojeb", "kurwa", "kurwo", "kurwy", "kurew",
    "wypierdal", "zajeb", "jebany", "jebana", "jebane",
    "pierdol", "pierdole", "pierdolisz",
    "kys", "fuck", "shit", "bitch", "asshole", "faggot", "nigger",
    "retard", "idiot", "menda", "ścierwo", "śmieć"
]

# żeby łapało np. kuuuurwa, k.u.r.w.a
def zawiera_wulgaryzm(text):
    text = text.lower()
    text_clean = re.sub(r'[^a-z0-9ąćęłńóśźż]', '', text)
    for w in WULGARYZMY:
        if w in text.lower() or w in text_clean:
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

    # ADMINI I MODERATORZY OMINIĘCI
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
            powod = f"Auto-mod: wulgaryzm ({znalezione})"
        elif warns[user_id] == 2:
            timeout = timedelta(hours=1)
            powod = f"Auto-mod: 2-gi wulgaryzm ({znalezione})"
        else:
            timeout = timedelta(hours=24)
            powod = f"Auto-mod: {warns[user_id]} wulgaryzmów"

        try:
            await message.author.timeout(timeout, reason=powod)
        except:
            pass

        embed = discord.Embed(
            title="🚫 AUTO-MODERACJA",
            description=f"{message.author.mention} - wiadomość usunięta!\n**Powód:** wulgaryzm/wyzwisko\n**Timeout:** {timeout}",
            color=0xff0000
        )
        embed.set_footer(text=f"Wykryto: {znalezione} | Warn: {warns[user_id]}/3")
        
        try:
            await message.channel.send(embed=embed, delete_after=10)
        except:
            pass

        # DM do użytkownika
        try:
            await message.author.send(f"⚠️ Twoja wiadomość na **{message.guild.name}** została usunięta za wulgaryzm. Timeout {timeout}. Zachowuj kulturę!")
        except:
            pass
        
        return

    await bot.process_commands(message)

@bot.tree.command(name="metin_boss", description="Sprawdź resp bossów")
async def metin_boss(interaction: discord.Interaction):
    embed = discord.Embed(title="PANDORA MT2 - Bossy", color=0xff0000)
    embed.add_field(name="Azrael", value="Lodowa Kraina", inline=False)
    embed.add_field(name="Beran Setaou", value="Dolina Seungryong", inline=False)
    embed.add_field(name="Smok", value="Dolina Seungryong", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Ping bota")
async def ping(interaction: discord.Interaction):
   
