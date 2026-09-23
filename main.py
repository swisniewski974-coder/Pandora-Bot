import os
import discord
from discord.ext import commands
from collections import defaultdict
import time

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Słownik do śledzenia spamu: {user_id: [timestamp1, timestamp2, ...]}
spam_tracker = defaultdict(list)

# Limity anty-spamu: np. max 4 wiadomości w ciągu 5 sekund to spam
SPAM_LIMIT = 4
TIME_WINDOW = 5

class GieldaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="KUP", style=discord.ButtonStyle.green, custom_id="gielda_kup")
    async def kup_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Funkcja zakupu w budowie.", ephemeral=True)

    @discord.ui.button(label="WYSTAW", style=discord.ButtonStyle.primary, custom_id="gielda_wystaw")
    async def wystaw_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Aby wystawić przedmiot, wrzuć zdjęcie z ceną na ten kanał.", ephemeral=True)

    @discord.ui.button(label="PRZEGLĄDAJ", style=discord.ButtonStyle.secondary, custom_id="gielda_przegladaj")
    async def przegladaj_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Tutaj pojawi się tabela ofert.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Sprawdzamy tylko kanał giełda
    if message.channel.name == "giełda":
        user_id = message.author.id
        current_time = time.time()

        # Czyszczenie starych wpisów czasowych dla użytkownika
        spam_tracker[user_id] = [t for t in spam_tracker[user_id] if current_time - t < TIME_WINDOW]
        spam_tracker[user_id].append(current_time)

        # Jeśli użytkownik przekroczył limit wiadomości (spam / zabawa botem)
        if len(spam_tracker[user_id]) > SPAM_LIMIT:
            try:
                # Zabieramy użytkownikowi uprawnienia do pisania/czytania na tym konkretnym kanale
                await message.channel.set_permissions(message.author, send_messages=False, read_messages=False)
                await message.delete() # Usuwamy wiadomość spamową
                
                # Informacja prywatna lub ostrzeżenie na kanale
                warning_msg = await message.channel.send(f"⚠️ {message.author.mention} został wyrzucony z kanału za spam/śmiecenie!")
                # Usunięcie ostrzeżenia po 5 sekundach żeby nie śmiecić
                await warning_msg.delete(delay=5)
            except Exception as e:
                print(f"Błąd anty-spamu: {e}")
            return

    await bot.process_commands(message)

@bot.command()
async def setup_gielda(ctx):
    """Komenda wysyłająca główny panel giełdy na kanał"""
    if ctx.channel.name != "giełda":
        await ctx.send("Tę komendę można wykonać tylko na kanale #giełda.")
        return

    embed = discord.Embed(
        title="⚔️ GIEŁDA PANDORA MT2 ⚔️",
        description="Kupuj i wystawiaj przedmioty bez spamu na kanale!\n\n**Jak to działa?**\nKliknij przycisk poniżej.",
        color=discord.Color.blue()
    )
    view = GieldaView()
    await ctx.send(embed=embed, view=view)

if __name__ == "__main__":
    bot.run(TOKEN)
