import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

gielda_items = []
GIELDA_CHANNEL_NAME = "giełda"

# --- FILTRY ---
METIN_KEYWORDS = ["miecz","zbroja","hełm","tarcza","buty","naszyjnik","kolczyki","bransoleta","sztylet","dzwon","wachlarz","łuk","kordelas","ostrza","yang","won","sm","kk","onyx","rubin","diament","szafir","granat","jadeit","perła","+0","+1","+2","+3","+4","+5","+6","+7","+8","+9","lvl","lv"]
BLACKLIST = ["yamal","lamine","messi","ronaldo","pilka","meme","zdjecie","fotka","test","kurwa","chuj","huj","pizda","jebac","jebać","pierdole","cwel","ciota","debil","idiota","szmata","dziwka","kutas","suka","spierdalaj","wypierdalaj"]

def is_valid(text):
    t = text.lower()
    if any(b in t for b in BLACKLIST):
        return False, "wulgaryzm"
    if any(k in t for k in METIN_KEYWORDS) or ("+" in t and any(str(i) in t for i in range(10))):
        return True, ""
    return False, "nie_metin"

class WystawModal(Modal, title="Wystaw przedmiot"):
    przedmiot = TextInput(label="Nazwa przedmiotu", placeholder="Np. Miecz+9")
    cena = TextInput(label="Cena", placeholder="Np. 50kk")
    opis = TextInput(label="Opis", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        full_text = f"{self.przedmiot.value} {self.cena.value} {self.opis.value}"
        valid, reason = is_valid(full_text)
        if not valid:
            if reason == "wulgaryzm":
                msg = "❌ **Wykryto wulgaryzmy / obelgi.** Oferta odrzucona."
            else:
                msg = f"❌ `{self.przedmiot.value}` to nie item z Metina! Wpisz np. Miecz+9"
            await interaction.response.send_message(msg, ephemeral=True, delete_after=7)
            return

        gielda_items.append({"przedmiot": self.przedmiot.value, "cena": self.cena.value, "opis": self.opis.value, "seller_id": interaction.user.id, "seller_name": interaction.user.display_name})
        await interaction.response.send_message(f"✅ Wystawiono **{self.przedmiot.value}**!", ephemeral=True, delete_after=5)

class GieldaView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🛒 KUP", style=discord.ButtonStyle.green, custom_id="kup_final")
    async def kup(self, interaction: discord.Interaction, button: Button):
        if not gielda_items: 
            await interaction.response.send_message("❌ Pusto!", ephemeral=True, delete_after=5); return
        desc = "\n".join([f"{i+1}. {x['przedmiot']} - {x['cena']}" for i,x in enumerate(gielda_items[-10:])])
        await interaction.response.send_message(f"**OFERTY:**\n{desc}", ephemeral=True, delete_after=30)
    @discord.ui.button(label="📩 WYSTAW", style=discord.ButtonStyle.blurple, custom_id="wystaw_final")
    async def wystaw(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(WystawModal())

@bot.event
async def on_message(message):
    if message.channel.name == GIELDA_CHANNEL_NAME and not message.author.bot and not message.content.startswith("!setup"):
        try: await message.delete(delay=1.0)
        except: pass
    await bot.process_commands(message)

@bot.event
async def on_ready():
    bot.add_view(GieldaView())
    print(f"ONLINE {bot.user}")

@bot.command()
async def setup_gielda(ctx):
    embed = discord.Embed(title="⚔️ GIEŁDA PANDORA MT2 ⚔️", description="Tylko itemy z Metina, bez bluzgów!", color=0x00ff00)
    await ctx.send(embed=embed, view=GieldaView())
    try: await ctx.message.delete()
    except: pass

bot.run(os.getenv("DISCORD_TOKEN"))
