import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# PAMIĘĆ GIEŁDY - w RAM (jak chcesz bazę to powiem)
gielda_items = []

class WystawModal(Modal, title="Wystaw przedmiot"):
    przedmiot = TextInput(label="Nazwa przedmiotu", placeholder="Np. Miecz+9", max_length=50)
    cena = TextInput(label="Cena", placeholder="Np. 50kk / 100sm")
    opis = TextInput(label="Opis", style=discord.TextStyle.paragraph, required=False, max_length=200)

    async def on_submit(self, interaction: discord.Interaction):
        item = {
            "przedmiot": self.przedmiot.value,
            "cena": self.cena.value,
            "opis": self.opis.value,
            "seller_id": interaction.user.id,
            "seller_name": interaction.user.display_name
        }
        gielda_items.append(item)
        
        # Tylko dla niego, znika po 10s
        await interaction.response.send_message(
            f"✅ Wystawiono **{self.przedmiot.value}** za **{self.cena.value}**!\nWyślij teraz zdjęcie przedmiotu na ten czat (zniknie za 60s)",
            ephemeral=True, delete_after=10
        )

class GieldaView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🛒 KUP", style=discord.ButtonStyle.green, custom_id="kup")
    async def kup(self, interaction: discord.Interaction, button: Button):
        if not gielda_items:
            await interaction.response.send_message("❌ Giełda jest pusta!", ephemeral=True, delete_after=5)
            return
        
        # Tworzy prywatną listę tylko dla klikającego
        desc = ""
        for i, it in enumerate(gielda_items[-10:], 1): # ostatnie 10
            desc += f"**{i}. {it['przedmiot']}** - {it['cena']} | od {it['seller_name']}\n"
        
        view = KupView()
        await interaction.response.send_message(f"**📜 OSTATNIE OFERTY:**\n{desc}\nKliknij numer żeby kupić:", view=view, ephemeral=True)

    @discord.ui.button(label="📩 WYSTAW", style=discord.ButtonStyle.blurple, custom_id="wystaw")
    async def wystaw(self, interaction: discord.Interaction, button: Button):
        # Otwiera ODDZIELNE OKNO - o to Ci chodziło
        await interaction.response.send_modal(WystawModal())

    @discord.ui.button(label="👀 PRZEGLĄDAJ", style=discord.ButtonStyle.gray, custom_id="przegladaj")
    async def przegladaj(self, interaction: discord.Interaction, button: Button):
        moje = [x for x in gielda_items if x['seller_id'] == interaction.user.id]
        if not moje:
            await interaction.response.send_message("Nie masz wystawionych przedmiotów.", ephemeral=True, delete_after=5)
            return
        desc = "\n".join([f"{i+1}. {x['przedmiot']} - {x['cena']}" for i, x in enumerate(moje)])
        await interaction.response.send_message(f"**Twoje oferty:**\n{desc}", ephemeral=True, delete_after=15)

class KupView(View):
    def __init__(self):
        super().__init__(timeout=60)
        # Dodaj przyciski 1-5 dynamicznie
        for i in range(min(5, len(gielda_items))):
            self.add_item(KupButton(i))

class KupButton(Button):
    def __init__(self, index):
        super().__init__(label=f"Kup #{index+1}", style=discord.ButtonStyle.green)
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        item = gielda_items[self.index]
        guild = interaction.guild
        
        # Tworzy ticket
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.get_member(item['seller_id']): discord.PermissionOverwrite(view_channel=True, send_messages=True) if guild.get_member(item['seller_id']) else None
        }
        # wyczyść None
        overwrites = {k:v for k,v in overwrites.items() if v}
        
        channel = await guild.create_text_channel(
            f"ticket-{interaction.user.name}-{self.index}",
            overwrites=overwrites,
            reason="Giełda zakup"
        )
        
        view = CloseView()
        await channel.send(f"{interaction.user.mention} <@{item['seller_id']}> KUPUJE **{item['przedmiot']}** za **{item['cena']}**\nDogadajcie się co do handlu w grze!", view=view)
        await interaction.response.send_message(f"✅ Ticket stworzony: {channel.mention}", ephemeral=True, delete_after=10)

class CloseView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🔒 ZAMKNIJ TICKET", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Zamykam za 3s...", ephemeral=True)
        await asyncio.sleep(3)
        await interaction.channel.delete()

@bot.event
async def on_ready():
    bot.add_view(GieldaView())
    bot.add_view(CloseView())
    print(f"Online {bot.user}")

@bot.command()
async def setup_gielda(ctx):
    embed = discord.Embed(title="⚔️ GIEŁDA PANDORA MT2 ⚔️", description="Kupuj i wystawiaj przedmioty bez spamu na kanale!", color=0x00ff00)
    embed.add_field(name="Jak to działa?", value="Kliknij przycisk poniżej. Wszystko otworzy się tylko dla Ciebie w prywatnym oknie.", inline=False)
    await ctx.send(embed=embed, view=GieldaView())
    await ctx.message.delete()

bot.run(os.getenv("DISCORD_TOKEN"))
