import os
import requests
from bs4 import BeautifulSoup
import discord
from discord.ext import tasks

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# Add your Steam links here (games or bundles)
steam_links = [
   "https://store.steampowered.com/bundle/32470/Cyberpunk_2077_Ultimate_Edition/"
]

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def check_discount(url):
    """Check if a game or bundle has a discount."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    discount = soup.select_one(".discount_pct")
    final_price = soup.select_one(".discount_final_price")
    original_price = soup.select_one(".discount_original_price")
    title_tag = soup.select_one(".apphub_AppName") or soup.select_one(".pageheader")

    if title_tag:
        title = title_tag.get_text(strip=True)
    else:
        title = "Unknown Title"

    if discount and final_price:
        return {
            "title": title,
            "discount": discount.get_text(strip=True),
            "final_price": final_price.get_text(strip=True),
            "original_price": original_price.get_text(strip=True) if original_price else None,
            "url": url
        }
    return None

@tasks.loop(minutes=5)
async def check_sales():
    channel = client.get_channel(CHANNEL_ID)
    results = []

    for link in steam_links:
        deal = check_discount(link)
        if deal:
            results.append(f"**{deal['title']}** is {deal['discount']} off!\n"
                           f"Now: {deal['final_price']} (was {deal['original_price']})\n{deal['url']}")

    if results:
        message = "@everyone 🎉 Steam Sale Alert! 🎉\n\n" + "\n\n".join(results)
        await channel.send(message)

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    check_sales.start()

client.run(TOKEN)
