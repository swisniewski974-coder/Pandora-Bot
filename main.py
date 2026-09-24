import json
import os
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
GIELDA_CHANNEL_ID = 1551642032680730735
GENERAL_CHANNEL_ID = 1550071190859685988

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

MARKET_FILE = "market_offers.json"
WIKI_FILE = "wiki_data.json"


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
          f"**Sprzedawca:** <@{o['seller_id']}>\n**Treść:**"
          f" {o['item']}\n*Wystawiono automatycznie*"
      )
      if o.get("image_url"):
        desc += f"\n[📸 Zobacz zdjęcie oferty]({o['image_url']})"

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
          "Napisz swoją ofertę (tekst + opcjonalnie zdjęcie) na tym kanale, a"
          " bot natychmiast ją przechwyci!\n\nKliknij przycisk poniżej, aby"
          " sprawdzić oferty."
      ),
      color=discord.Color.blue(),
  )
  await ctx.send(embed=embed, view=MarketView())


@bot.command(name="wiki")
async def wiki(ctx, *, query: str = None):
  if not query:
    embed = discord.Embed(
        title="📖 Wiki Pandoramt2Mobile",
        description=(
            "Użycie: `!wiki <nazwa>`\nKategorie: **!bossy**, **!dungeony**,"
            " **!mapy**, **!nowosci**"
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
      embed.add_field(name="ℹ️ Informacje", value=found["info"], inline=False)
    if "stats" in found:
      embed.add_field(name="📊 Drop / Bonusy", value=found["stats"], inline=False)
    await ctx.send(embed=embed)
  else:
    await ctx.send(f"❌ Nie znaleziono wpisu dla `{query}` w bazie Wiki.")


async def send_wiki_list(ctx, category_name, title_text, color):
  wiki_data = load_json(WIKI_FILE)
  items_list = wiki_data.get(category_name, {})

  embed = discord.Embed(
      title=title_text, description="Zarejestrowane wpisy:", color=color
  )
  if not items_list:
    embed.add_field(name="Brak danych", value="Brak wpisów w tej kategorii.")
  else:
    for key, data in items_list.items():
      embed.add_field(
          name=data["title"], value=data.get("info", "Brak info"), inline=False
      )
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
  # kategoria może być: bossy, dungeony, mapy, nowosci
  wiki_data = load_json(WIKI_FILE)
  if kategoria not in wiki_data:
    wiki_data[kategoria] = {}
  wiki_data[kategoria][klucz.lower()] = {
      "title": tytul,
      "info": info,
      "stats": stats,
      "desc": f"Oficjalny wpis z prezentacji serwera dla {tytul}.",
  }
  save_json(WIKI_FILE, wiki_data)
  await ctx.send(f"✅ Dodano do **{kategoria}**: **{tytul}**!")


@bot.event
async def on_message(message):
  if message.author.bot:
    return

  # Obsługa kanału giełdy (tekst + zdjęcia)
  if message.channel.id == GIELDA_CHANNEL_ID:
    image_url = message.attachments[0].url if message.attachments else None
    content = message.content

    if not content and not image_url:
      return  # Pusta wiadomość bez niczego

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
  print(f"Zalogowano jako {bot.user}! Gotowy do działania.")


if TOKEN:
  bot.run(TOKEN)
else:
  print("BŁĄD: Brak zmiennej środowiskowej TOKEN!")
