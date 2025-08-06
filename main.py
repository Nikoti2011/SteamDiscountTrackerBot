import requests
from bs4 import BeautifulSoup
import os

# === Add your links here ===
steam_links = [
    "https://store.steampowered.com/app/413150/Stardew_Valley/",
    "https://store.steampowered.com/app/1030300/Hollow_Knight_Silksong/",
    "https://store.steampowered.com/app/739630/Phasmophobia/",
    "https://store.steampowered.com/app/1091500/Cyberpunk_2077/"
]

# === Discord Webhook from GitHub Secret ===
webhook = os.environ.get("DISCORD_WEBHOOK")

# === Prepare message parts ===
on_sale = []
not_on_sale = []

headers = {"User-Agent": "Mozilla/5.0"}

for link in steam_links:
    try:
        response = requests.get(link, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.find("div", class_="apphub_AppName")
        name = title_tag.text.strip() if title_tag else "Unknown Game"

        discount = soup.find("div", class_="discount_pct")
        if discount:
            discount_percent = discount.get_text(strip=True)
            original_price = soup.find("div", class_="discount_original_price").get_text(strip=True)
            final_price = soup.find("div", class_="discount_final_price").get_text(strip=True)

            on_sale.append(
                f"**{name}** is on sale!\n"
                f"{discount_percent} off\n"
                f"~~{original_price}~~ → **{final_price}**\n🔗 {link}"
            )
        else:
            not_on_sale.append(f"{name} is not on sale\n🔗 {link}")

    except Exception as e:
        not_on_sale.append(f"Error checking game at {link}:\n{e}")

# === Combine into one message ===
if on_sale:
    message = "@everyone 🔥 Some games are currently on sale!\n\n"
    message += "\n\n".join(on_sale)
else:
    message = "🔍 None of your tracked games are on sale.\n"

if not_on_sale:
    message += "\n\n❌ Not on sale:\n" + "\n".join(not_on_sale)

# === Send to Discord ===
payload = {"content": message}
res = requests.post(webhook, json=payload)

# === Debug ===
if res.status_code == 204:
    print("✅ Message sent to Discord.")
else:
    print(f"❌ Failed to send message: {res.status_code} {res.text}")
