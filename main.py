import discord
from discord.ext import commands
import os, json
from datetime import timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "gielda.json"
WULGARYZMY = ["kurw","chuj","jeb","pierd","pizd","huj","kutas","cwel","suka"]
oczekuje_zdjecia = {} # user_id -> oferta_id

def load_data():
    if not os.path.exists(DATA_FILE): return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return []
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
def zawiera_wulgaryzm(t):
    t=t.lower()
    for w in WULGARYZMY:
        if w in t: return w
    return None

async def create_ticket(guild, buyer, seller, oferta):
    category = discord.utils.get(guild.categories, name="GIEŁDA TICKETY")
    if not category: category = await guild.create_category("GIEŁDA TICKETY")
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        buyer: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        seller: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    for role in guild.roles:
        if role.permissions.administrator:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    channel = await guild.create_text_channel(name=f"ticket-{buyer.name}-{oferta['id']}", category=category, overwrites=overwrites)
    embed = discord.Embed(title="💰 TICKET GIEŁDY", color=0x00ff00)
    embed.add_field(name="Przedmiot", value=oferta['przedmiot'], inline=False)
    embed.add_field(name="Cena", value=oferta['cena'], inline=True)
    embed.add_field(name="Sprzedawca", value=seller.mention, inline=True)
    embed.add_field(name="Kupujący", value=buyer.mention, inline=True)
    embed.add_field(name="Opis", value=oferta.get('opis','Brak'), inline=False)
    if oferta.get('image_url'):
        embed.set_image(url=oferta['image_url'])
    await channel.send(content=f"{buyer.mention} {seller.mention}", embed=embed)
    return channel

class WystawModal(discord.ui.Modal, title="Wystaw przedmiot"):
    przedmiot = discord.ui.TextInput(label="Co sprzedajesz?", placeholder="Np. Sztylet 60lvl +9")
    cena = discord.ui.TextInput(label="Cena", placeholder="50kk / 10 won")
    opis = discord.ui.TextInput(label="Opis", style=discord.TextStyle.paragraph, required=False)
    zdjecie_link = discord.ui.TextInput(label="Link do zdjęcia (opcjonalnie)", placeholder="Wklej link lub zostaw puste - zdjęcie dodasz za chwilę", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_data()
        nowa = {
            "id": len(data)+1,
            "przedmiot": self.przedmiot.value,
            "cena": self.cena.value,
            "opis": self.opis.value,
            "image_url": self.zdjecie_link.value if self.zdjecie_link.value else None,
            "seller_id": interaction.user.id,
            "seller_name": str(interaction.user)
        }
        data.append(nowa)
        save_data(data)

        if not nowa['image_url']:
            oczekuje_zdjecia[interaction.user.id] = nowa['id']
            await interaction.response.send_message(f"✅ Wystawiono **{self.przedmiot.value}**!\n\n**TERAZ wyślij ZDJĘCIE jako załącznik na tym kanale w ciągu 60 sekund.**\nJeśli nie chcesz zdjęcia, zignoruj.", ephemeral=True)
        else:
            await interaction.response.send_message(f"✅ Wystawiono **{self.przedmiot.value}** ze zdjęciem!", ephemeral=True)

class OfertaView(discord.ui.View):
    def __init__(self, oferta):
        super().__init__(timeout=None)
        self.oferta = oferta
    @discord.ui.button(label="Pokaż / Kup - Ticket", style=discord.ButtonStyle.green, emoji="🎫")
    async def kup_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        seller = guild.get_member(self.oferta['seller_id']) or await guild.fetch_member(self.oferta['seller_id'])
        if seller.id == interaction.user.id:
            await interaction.response.send_message("To Twoja oferta!", ephemeral=True); return
        await interaction.response.send_message("Tworzę ticket...", ephemeral=True)
        channel = await create_ticket(guild, interaction.user, seller, self.oferta)
        await interaction.followup.send(f"Ticket: {channel.mention}", ephemeral=True)

class GieldaView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="KUP", style=discord.ButtonStyle.blurple, emoji="🛒", custom_id="gielda_kup")
    async def kup(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        if not data: await interaction.response.send_message("Pusto.", ephemeral=True); return
        await interaction.response.send_message("📦 **Oferty (tylko dla Ciebie):**", ephemeral=True)
        for o in data[-10:]:
            embed = discord.Embed(title=o['przedmiot'], description=f"**Cena:** {o['cena']}\n**Opis:** {o.get('opis','-')}", color=0x2b2d31)
            if o.get('image_url'): embed.set_image(url=o['image_url'])
            embed.set_footer(text=f"ID {o['id']} | {o['seller_name']}")
            await interaction.followup.send(embed=embed, view=OfertaView(o), ephemeral=True)

    @discord.ui.button(label="WYSTAW", style=discord.ButtonStyle.green, emoji="📤", custom_id="gielda_wystaw")
    async def wystaw(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(WystawModal())

    @discord.ui.button(label="PRZEGLĄDAJ", style=discord.ButtonStyle.gray, emoji="👀", custom_id="gielda_przegladaj")
    async def przegladaj(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        moje = [o for o in data if o['seller_id'] == interaction.user.id]
        if not moje: await interaction.response.send_message("Brak ofert.", ephemeral=True); return
        msg = "\n".join([f"ID {o['id']}: {o['przedmiot']} - {o['cena']} {'[📷]' if o.get('image_url') else ''}" for o in moje])
        await interaction.response.send_message(f"📋 **Twoje:**\n{msg}", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Online {bot.user}")
    bot.add_view(GieldaView())
    for o in load_data(): bot.add_view(OfertaView(o))
    try: await bot.tree.sync()
    except: pass

@bot.event
async def on_message(message):
    if message.author.bot: return
    # DODAWANIE ZDJĘCIA PO WYSTAWIENIU
    if message.author.id in oczekuje_zdjecia and message.attachments:
        oferta_id = oczekuje_zdjecia[message.author.id]
        data = load_data()
        for o in data:
            if o['id'] == oferta_id:
                o['image_url'] = message.attachments[0].url
                save_data(data)
                await message.delete()
                await message.channel.send(f"✅ Dodano zdjęcie do oferty **{o['przedmiot']}**!", delete_after=5)
                del oczekuje_zdjecia[message.author.id]
                return

    if message.guild and not message.author.guild_permissions.manage_messages:
        if zawiera_wulgaryzm(message.content):
            try: await message.delete()
            except: pass
            await message.author.timeout(timedelta(minutes=10), reason="wulgaryzm")
            return
    await bot.process_commands(message)

@bot.tree.command(name="setup-gielda", description="Panel giełdy")
async def setup_gielda(interaction: discord.Interaction):
    embed = discord.Embed(title="💰 GIEŁDA PANDORA MT2", description="🛒 **KUP** - Prywatne oferty\n📤 **WYSTAW** - Dodaj przedmiot + zdjęcie\n👀 **PRZEGLĄDAJ** - Twoje oferty\n\n**Zdjęcia:** Po wystawieniu wyślij zdjęcie jako załącznik lub wklej link!", color=0x00ff00)
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Brak uprawnień admina!", ephemeral=True); return
    await interaction.response.send_message(embed=embed, view=GieldaView())

@bot.tree.command(name="close", description="Zamknij ticket")
async def close(interaction: discord.Interaction):
    if "ticket-" in interaction.channel.name:
        await interaction.response.send_message("Zamykam...")
        import asyncio; await asyncio.sleep(2)
        await interaction.channel.delete()
    else:
        await interaction.response.send_message("To nie ticket!", ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN"))
