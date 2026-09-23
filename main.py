from flask import Flask
from threading import Thread
import os
import discord
from discord.ext import commands

# --- to trzyma bota za darmo na Render, nie ruszaj ---
app = Flask('')
@app.route('/')
def home():
    return "Bot dziala!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

Thread(target=run).start()
# --- koniec keep-alive ---

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")

# TU WKLEJ SWOJE KOMENDY - np:
# @bot.command()
# async def ping(ctx):
#     await ctx.send("Pong!")

bot.run(os.getenv("DISCORD_TOKEN"))
