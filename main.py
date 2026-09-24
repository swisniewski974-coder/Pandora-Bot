import json
import os
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
GIELDA_CHANNEL_ID = 1551642032680730735

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

MARKET_FILE = "market_offers.json"
WIKI_FILE = "wiki_data.json"

# Wstępna baza danych Wiki zaciągnięta bezpośrednio z prezentacji serwera
DEFAULT_WIKI_DATA = {
    "bossy": {
        "minotaur": {
            "title": "Minotaur",
            "info": "Boss na mapie Dolina Śmierci.",
            "stats": "Wymagany lvl: 110 | Bonus: Silny przeciwko Nieumarłym",
        },
        "beransetao": {
            "title": "Beran-Setao",
            "info": "Główny Boss w Komnacie Smoka.",
            "stats": (
                "Wymagany lvl: 110 | Koszt wejścia: 70kk Yang + Kręty Klucz |"
                " Bonus: Diabły"
            ),
        },
        "lodowawiedzma": {
            "title": "Silna Lodowa Wiedźma",
            "info": "Mapowy Boss (resp 1h).",
            "stats": (
                "Koszt wejścia: 200kk Yang | Bonus: Silny przeciwko Diabłom"
            ),
        },
    },
    "dungeony": {
        "komnatasmoka": {
            "title": "Komnata Smoka",
            "info": "Dungeon z bossem Beran-Setao.",
            "stats": (
                "Wymagany lvl: 110 | Koszt: 70.000.000 Yang + Kręty Klucz |"
                " Bonus: Diabły"
            ),
        }
    },
    "mapy": {
        "dolinasmierci": {
            "title": "Dolina Śmierci",
            "info": "Mapa z bossem Minotaur i Metinem Zagłady.",
            "stats": (
                "Wymagany lvl: 110 | Koszt: 100.000.000 Yang | Bonus: Nieumarłe"
            ),
        },
        "pustyniawygnancow": {
            "title": "Pustynia Wygnańców V2",
            "info": "Mapa z Elit. Olbrzymim Żółwiem V2.",
            "stats": (
                "Wymagany lvl: 260 | Koszt: 300.000.000 Yang | Bonus: Nieumarłe"
            ),
        },
        "kopalniazlota": {
            "title": "Kopalnia Złota",
            "info": "Mapa eventowa/zarobkowa z bossem Alladyn.",
            "stats": (
                "Wymagany lvl: 35 - 55 | Przepustka: Kamień Glyph | Bonus: Orki"
            ),
        },
    },
    "nowosci": {
        "legendarnekd": {
            "title": "Legendarne Kamienie Duszy",
            "info": (
                "Wytwarzane u Seon-Pyeonga / Ołtarzu Dusz z 10x KD +6 (60%"
                " szans)."
            ),
            "stats": "Można ulepszać do +5, posiadają dodatkowe unikalne bonusy.",
        },
        "autobuff": {
            "title": "Panel Autobuffa",
            "info": (
                "Pełni rolę pomocniczą dla klas innych niż Szaman (daje 50%"
                " oryginalnego efektu)."
            ),
            "stats": "Wymaga Pieczęci Autobuffa.",
        },
        "zwierzaki": {
            "title": "Panel Zwierzaka i Obroże",
            "info": "System rozwoju towarzysza posiadający sloty na obroże.",
            "stats": (
                "Obroże zwiększają exp, obrażenia w potwory lub ludzi (Obroża"
                " Bogacza)."
            ),
        },
    },
}


def load_json(filename):
  if os.path.exists(filename):
    with open(filename, "r", encoding="utf-8") as f:
      try:
        return json.load(f)
      except:
        return {} if filename == WIKI_FILE else []
  if filename == WIKI_FILE:
    save_json(WIKI_FILE, DEFAULT_WIKI_DATA)
    return DEFAULT_WIKI_DATA
  return []


def save_json(filename, data):
  with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)


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
        description="Aktualnie wystawione przedmioty:",
        color=discord.Color.gold(),
    )
    for i, o in enumerate(offers, 1):
      desc = (
          f"**Sprzedawca:** <@{o['seller_id']}>\n**Treść:** {o['item']}"
          f"\n*Wystawiono automatycznie*"
      )
      if o.get("image_url"):
        desc += f"\n[📸 Zobacz zdjęcie]({o['image_url']})"
      embed.add_field(name=f"Oferta #{i}", value=desc, inline=False)

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
          "Napisz swoją ofertę (tekst + opcjonalnie zdjęcie) na tym kanale, a"
          " bot natychmiast ją przechwyci!"
      ),
      color=discord.Color.blue(),
  )
  await ctx.send(embed=embed, view=MarketView())


# --- SYSTEM WIKI ---


async def send_wiki_list(ctx, category_name, title_text, color):
  wiki_data = load_json(WIKI_FILE)
  items_list = wiki_data.get(category_name, {})

  embed = discord.Embed(
      title=title_text, description="Zarejestrowane wpisy z Wiki:", color=color
  )
  if not items_list:
    embed.add_field(name="Brak danych", value="Brak wpisów w tej kategorii.")
  else:
    for key, data in items_list.items():
      val = f"ℹ️ {data.get('info', 'Brak info')}\n📊 {data.get('stats', '')}"
      embed.add_field(name=data["title"], value=val, inline=False)
  await ctx.send(embed=embed)


@bot.command(name="bossy")
async def bossy(ctx):
  await send_wiki_list(
      ctx, "bossy", "👹 Bossy w Pandoramt2Mobile", discord.Color.red()
  )


@bot.command(name="dungeony")
async def dungeony(ctx):
  await send_wiki_list(
      ctx, "dungeony", "🏰 Dungeony w Pandoramt2Mobile", discord.Color.orange()
  )


@bot.command(name="mapy")
async def mapy(ctx):
  await send_wiki_list(
      ctx, "mapy", "🗺️ Mapy w Pandoramt2Mobile", discord.Color.green()
  )


@bot.command(name="nowosci")
async def nowosci(ctx):
  await send_wiki_list(
      ctx, "nowosci", "✨ Nowości i Aktualizacje", discord.Color.blue()
  )


@bot.command(name="dodaj_wiki")
@commands.has_permissions(administrator=True)
async def dodaj_wiki(
    ctx, kategoria: str, klucz: str, tytul: str, info: str, *, stats: str = "Brak"
):
  wiki_data = load_json(WIKI_FILE)
  if kategoria not in wiki_data:
    wiki_data[kategoria] = {}
  wiki_data[kategoria][klucz.lower()] = {
      "title": tytul,
      "info": info,
      "stats": stats,
  }
  save_json(WIKI_FILE, wiki_data)
  await ctx.send(f"✅ Dodano do **{kategoria}**: **{tytul}**!")


@bot.event
async def on_message(message):
  if message.author.bot:
    return

  # BEZPIECZNIK: Ignoruje komendy na kanale giełdy, żeby bot ich nie kasował
  if message.content.startswith("!"):
    await bot.process_commands(message)
    return

  # Obsługa giełdy (tekst + zdjęcia)
  if message.channel.id == GIELDA_CHANNEL_ID:
    image_url = message.attachments[0].url if message.attachments else None
    content = message.content

    if content or image_url:
      try:
        await message.delete()
      except:
        pass

      offers = load_json(MARKET_FILE)
      offers.append({
          "seller_id": message.author.id,
          "seller_name": message.author.name,
          "item": content if content else "[Załącznik / Zdjęcie]",
          "image_url": image_url,
      })
      save_json(MARKET_FILE, offers)
      return

  await bot.process_commands(message)


@bot.event
async def on_ready():
  print(f"Bot gotowy jako {bot.user}")


if TOKEN:
  bot.run(TOKEN)
