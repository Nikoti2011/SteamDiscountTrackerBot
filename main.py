bu tkkep the same message system of this version import requests
from bs4 import BeautifulSoup
import os

# Load Discord webhook URL from secret
webhook = os.environ.get("DISCORD_WEBHOOK")

# Steam URL for Stardew Valley
steam_url = "https://store.steampowered.com/app/413150/Stardew_Valley/"

# Get the page content
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(steam_url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Try to find a discount block
discount_block = soup.find("div", class_="discount_pct")

if discount_block:
    discount_percent = discount_block.get_text(strip=True)
    original_price = soup.find("div", class_="discount_original_price").get_text(strip=True)
    final_price = soup.find("div", class_="discount_final_price").get_text(strip=True)

    message = (
        f"@everyone 🔥 **Stardew Valley is on sale!**\n\n"
        f"**{discount_percent}** off\n"
        f"~~{original_price}~~ → **{final_price}**\n\n"
        f"🔗 {steam_url}"
    )
else:
    message = (
        "🔎 **Stardew Valley is not on sale right now.**\n"
        f"Check it here: {steam_url}"
    )

# Send to Discord
payload = {"content": message}
res = requests.post(webhook, json=payload)

# Debugging
if res.status_code == 204:
    print("✅ Message sent to Discord.")
else:
    print(f"❌ Failed to send message: {res.status_code} {res.text}")
