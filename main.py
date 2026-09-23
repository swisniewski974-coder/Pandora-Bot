import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import time

# --- KONFIGURACJA BOTA ---
TOKEN = "TUTAJ_WKLEJ_SWOJ_TOKEN_DISCORD"  # Zamień na swój token z Discord Developer Portal

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

PREZENTACJA_URL = "https://forum.pandoramt2.pl/topic/31300-s2-prezentacja-serwera"

# --- SYSTEM ANTYSPAMOWY ---
spam_tracker = defaultdict(list)
SPAM_LIMIT = 4
TIME_WINDOW = 5

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Prosty anty-spam
    user_id = message.author.id
    current_time = time.time()
    spam_tracker[user_id] = [t for t in spam_tracker[user_id] if current_time - t < TIME_WINDOW]
    spam_tracker[user_id].append(current_time)

    if len(spam_tracker[user_id]) > SPAM_LIMIT:
        await message.channel.send(f"⚠️ {message.author.mention}, zwolnij! Nie spamuj komendami.")
        return

    await bot.process_commands(message)

# --- BAZA WIEDZY O BOSSACH (KOMENDA !boss) ---
BOSSY_DATABASE = {
    "azazel": {
        "nazwa": "Azazel",
        "poziom": "100+",
        "bony": "⚡ **Silny przeciwko Diabłom**, Odporność na Ogień",
        "eq": "Miecz z KD Potwora, Zbroja Ogień/Magia, Biżuteria z Diabłami",
        "resp": "Nie dotyczy (Dungeon)",
        "drop": "Szkatułka Azazela, Perły, Kamienie Duchowe",
        "kolor": 0xff0000
    },
    "minotaur": {
        "nazwa": "Minotaur (Dolina Śmierci)",
        "poziom": "110",
        "bony": "⚡ **Silny przeciwko Diabłom**",
        "eq": "Broń z wysokimi Średnimi Obrażeniami, FULL EQ Diabły",
        "resp": "⏱️ Co 1 godzinę",
        "drop": "Kamyki, Sztabki Złota, Przedmioty Ulepszające",
        "kolor": 0xff5500
    },
    "wiedźma": {
        "nazwa": "Lodowa Wiedźma (Atlantyda V1)",
        "poziom": "75+",
        "bony": "⚡ **Silny przeciwko Diabłom**, Odporność na Lód",
        "eq": "FULL Diabły, Blok Ciosów w Tarczy/Kasku, KD Potwora",
        "resp": "⏱️ Co 4 godziny",
        "drop": "Stale, Biżuteria, Kamienie Dusz +4, Perły",
        "kolor": 0x00aaff
    },
    "dżinn": {
        "nazwa": "Grota Dżinna (Dung)",
        "poziom": "150",
        "bony": "⚡ **Silny przeciwko Mistykom**",
        "eq": "EQ 150lvl + FULL Bony na Mistyków",
        "resp": "⏱️ Co 4 godziny (Przepustka: Bransoleta Sułtana)",
        "drop": "Skrzynia Dżinna, Szkatułki, Rzadkie Ulepszacze",
        "kolor": 0xaa00ff
    }
}

@bot.command()
async def boss(ctx, *, nazwa_bossa: str = None):
    if not nazwa_bossa:
        await ctx.send("❓ Wpisz nazwę bossa, np.: `!boss azazel`, `!boss minotaur`, `!boss wiedźma`, `!boss dżinn`")
        return

    klucz = nazwa_bossa.lower().strip()
    
    if klucz in BOSSY_DATABASE:
        data = BOSSY_DATABASE[klucz]
        embed = discord.Embed(
            title=f"👾 BOSS: {data['nazwa']}",
            color=data['kolor']
        )
        embed.add_field(name="🎯 Wymagane Bony", value=data['bony'], inline=False)
        embed.add_field(name="🛡️ Polecane EQ / Strategia", value=data['eq'], inline=False)
        embed.add_field(name="⏱️ Resp / Czas", value=data['resp'], inline=True)
        embed.add_field(name="📊 Poziom Mapy", value=data['poziom'], inline=True)
        embed.add_field(name="🎁 Główny Drop", value=data['drop'], inline=False)
        embed.set_footer(text="PandoraMT2 S2 Bot • Wpisz !wiki po szukanie na forum")
        
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ Nie mam `{nazwa_bossa}` w szybkiej bazie. Szukam na żywo na forum... Użyj `!wiki {nazwa_bossa}`!")

# --- KOMENDA !wiki (SZUKANIE NA ŻYWO Z FORUM) ---
@bot.command()
async def wiki(ctx, *, fraza: str):
    await ctx.send(f"🔍 Przeszukuję najnowszą prezentację PandoryMT2 dla: **{fraza}**...")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(PREZENTACJA_URL, headers=headers, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            post = soup.find('div', {'class': 'cPost_contentWrap'})
            
            if post:
                tekst = post.get_text()
                linie = [l.strip() for l in tekst.split('\n') if l.strip()]
                
                znalezione = []
                łapanie = False
                
                for line in linie:
                    if fraza.lower() in line.lower():
                        łapanie = True
                    if łapanie:
                        znalezione.append(line)
                        if len(znalezione) >= 6: # 6 linijek kontekstu z forum
                            break
                
                if znalezione:
                    embed = discord.Embed(
                        title=f"📖 Wynik z Forum: {fraza.capitalize()}",
                        description="\n".join(znalezione),
                        color=0x00ff00
                    )
                    embed.set_footer(text="Dane pobrane na żywo z forum.pandoramt2.pl")
                    await ctx.send(embed=embed)
                    return

        await ctx.send(f"❌ Nie znaleziono informacji o `{fraza}` w prezentacji na forum.")
    except Exception as e:
        await ctx.send("❌ Błąd podczas połączenia z forum Pandory.")

@bot.event
async def on_ready():
    print(f'✅ Bot PandoraMT2 uruchomiony jako: {bot.user}')

# Uruchomienie bota
bot.run(TOKEN)

