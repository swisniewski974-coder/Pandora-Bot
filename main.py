import json
import os
import discord
from discord.ext import commands

# --- KONFIGURACJA ---
# Wklej swój token w cudzysłowie poniżej:
TOKEN = "TUTAJ_WKLEJ_SWÓJ_TOKEN_DISCORD"
GIELDA_CHANNEL_ID = (  # Zmień na ID swojego kanału giełdowego (musi być samymi cyframi!)
    123456789012345678
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

MARKET_FILE = "market_offers.json"
WIKI_FILE = "wiki_data.json"


# --- FUNKCJE POMOCNICZE (Baza Danych JSON) ---
def load_json(filename):
  if os.path.exists(filename):
    with open(filename, "r", encoding="utf-8") as f:
      try:
        return json.load(f)
      except:
        return {} if filename == WIKI_FILE else []
  return {} if filename == WIKI_FILE else []


def save_json(filename, data):
  with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)


# ==========================================
# 1. MODUŁ GIEŁDY (Czat -> Chmura + Przyciski)
# ==========================================


class MarketView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="📦 Zobacz Oferty",
      style=discord.ButtonStyle.green,
      custom_id="view_market",
  )
  async def view_market(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    offers = load_json(MARKET_FILE)
    if not offers:
      await interaction.response.send_message(
          "Aktualnie brak ofert na giełdzie!", ephemeral=True
      )
      return

    embed = discord.Embed(
        title="🛒 Giełda Pandoramt2Mobile",
        description="Aktualnie wystawione przedmioty z czatu:",
        color=discord.Color.gold(),
    )

    for i, o in enumerate(offers, 1):
      embed.add_field(
          name=f"#{i} | {o['item']}",
          value=(
              f"**Sprzedawca:** <@{o['seller_id']}>\n*Wystawiono"
              " automatycznie*"
          ),
          inline=False,
      )

    await interaction.response.send_message(embed=embed, ephemeral=True)

  @discord.ui.button(
      label="🗑️ Usuń swoje oferty",
      style=discord.ButtonStyle.red,
      custom_id="clear_my_offers",
  )
  async def clear_my(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    offers = load_json(MARKET_FILE)
    new_offers = [o for o in offers if o["seller_id"] != interaction.user.id]

    if len(new_offers) == len(offers):
      await interaction.response.send_message(
          "Nie masz żadnych aktywnych ofert.", ephemeral=True
      )
      return

    save_json(MARKET_FILE, new_offers)
    await interaction.response.send_message(
        "Usunięto Twoje oferty z giełdy!", ephemeral=True
    )


@bot.command(name="panel_gieldy")
@commands.has_permissions(administrator=True)
async def panel_gieldy(ctx):
  embed = discord.Embed(
      title="🏛️ Oficjalna Giełda Pandoramt2Mobile",
      description=(
          "Napisz swoją ofertę na kanale giełdowym, a bot w sekundę ją"
          " przechwyci i wrzuci do chmury!\n\nKliknij przycisk poniżej, aby"
          " sprawdzić tabelę ofert."
      ),
      color=discord.Color.blue(),
  )
  await ctx.send(embed=embed, view=MarketView())


# ==========================================
# 2. MODUŁ WIKI OGÓLNEJ PANDORAMT2MOBILE
# ==========================================


@bot.command(name="wiki")
async def wiki(ctx, *, query: str = None):
  """Ogólna wyszukiwarka po całej bazie Wiki"""
  if not query:
    embed = discord.Embed(
        title="📖 Ogólne Wiki Pandoramt2Mobile",
        description=(
            "Użycie: `!wiki <nazwa>` (np. `!wiki azrael`, `!wiki dt`, `!wiki"
            " stalka`)\n\nMożesz też używać dedykowanych komend:"
            " **!bossy**, **!dungeony**"
        ),
        color=discord.Color.dark_purple(),
    )
    await ctx.send(embed=embed)
    return

  wiki_data = load_json(WIKI_FILE)
  query_lower = query.lower()

  found = None
  found_category = ""
  for category, items in wiki_data.items():
    for key, data in items.items():
      if query_lower in key or query_lower in data["title"].lower():
        found = data
        found_category = category
        break
    if found:
      break

  if found:
    embed = discord.Embed(
        title=f"📖 [{found_category.upper()}] {found['title']}",
        description=found.get("desc", "Brak opisu."),
        color=discord.Color.purple(),
    )
    if "info" in found:
      embed.add_field(
          name="ℹ️ Informacje / Drop", value=found["info"], inline=False
      )
    if "stats" in found:
      embed.add_field(
          name="📊 Statystyki / Bonusy", value=found["stats"], inline=False
      )
    await ctx.send(embed=embed)
  else:
    await ctx.send(f"❌ Nie znaleziono wpisu dla `{query}` w ogólnej Wiki.")


@bot.command(name="bossy")
async def bossy(ctx):
  """Wyświetla listę głównych bossów z bazy Wiki"""
  wiki_data = load_json(WIKI_FILE)
  boss_list = wiki_data.get("bossy", {})

  embed = discord.Embed(
      title="👹 Bossy w Pandoramt2Mobile",
      description="Lista zarejestrowanych bossów:",
      color=discord.Color.red(),
  )
  if not boss_list:
    embed.add_field(
        name="Brak danych",
        value=(
            "Administrator nie dodał jeszcze bossów. Użyj `!dodaj_wiki` aby"
            " dodać."
        ),
    )
  else:
    for key, data in boss_list.items():
      embed.add_field(
          name=data["title"],
          value=data.get("info", "Brak info"),
          inline=False,
      )
  await ctx.send(embed=embed)


@bot.command(name="dungeony")
async def dungeony(ctx):
  """Wyświetla listę dungeonów z bazy Wiki"""
  wiki_data = load_json(WIKI_FILE)
  dung_list = wiki_data.get("dungeony", {})

  embed = discord.Embed(
      title="🏰 Dungeony w Pandoramt2Mobile",
      description="Wymagania i informacje o wyprawach:",
      color=discord.Color.orange(),
  )
  if not dung_list:
    embed.add_field(
        name="Brak danych",
        value=(
            "Administrator nie dodał jeszcze dungeonów. Użyj `!dodaj_wiki`"
            " aby dodać."
        ),
    )
  else:
    for key, data in dung_list.items():
      embed.add_field(
          name=data["title"],
          value=data.get("info", "Brak info"),
          inline=False,
      )
  await ctx.send(embed=embed)


@bot.command(name="dodaj_wiki")
@commands.has_permissions(administrator=True)
async def dodaj_wiki(
    ctx, kategoria: str, klucz: str, tytul: str, info: str, *, stats: str = "Brak"
):
  """Komenda do dodawania wpisów przez admina"""
  wiki_data = load_json(WIKI_FILE)

  if kategoria not in wiki_data:
    wiki_data[kategoria] = {}

  wiki_data[kategoria][klucz.lower()] = {
      "title": tytul,
      "info": info,
      "stats": stats,
      "desc": f"Wpis z ogólnej bazy wiedzy Pandora dla {tytul}.",
  }
  save_json(WIKI_FILE, wiki_data)
  await ctx.send(
      f"✅ Dodano do kategorii **{kategoria}** wpis: **{tytul}**!"
  )


# ==========================================
# NASŁUCHIWANIE WIADOMOŚCI (Giełda i eventy)
# ==========================================


@bot.event
async def on_message(message):
  if message.author.bot:
    return

  # Działanie Giełdy: przechwytywanie w sekundę
  if message.channel.id == GIELDA_CHANNEL_ID:
    try:
      await message.delete()  # Usuwa natychmiast z czatu
    except:
      pass

    offers = load_json(MARKET_FILE)
    offers.append({
        "seller_id": message.author.id,
        "seller_name": message.author.name,
        "item": message.content,
    })
    save_json(MARKET_FILE, offers)
    return

  await bot.process_commands(message)


@bot.event
async def on_ready():
  print(
      f"Zalogowano jako {bot.user} - Giełda i ogólne Wiki działają bezbłędnie!"
  )


bot.run(TOKEN)
