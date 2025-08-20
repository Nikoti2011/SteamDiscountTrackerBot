import os
import requests
from steam.steamid import SteamID

# Webhook URL (set this in your repository secrets as DISCORD_WEBHOOK)
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
GAMES = [
   "https://store.steampowered.com/bundle/32470/Cyberpunk_2077_Ultimate_Edition/"
]

def get_steam_id(url):
    """
    Extracts the appid or bundleid from a Steam URL.
    """
    if "/app/" in url:
        return "app", url.split("/app/")[1].split("/")[0]
    elif "/bundle/" in url:
        return "bundle", url.split("/bundle/")[1].split("/")[0]
    return None, None

def fetch_discount(steam_type, steam_id):
    """
    Fetch discount information for an app or bundle.
    """
    if steam_type == "app":
        api_url = f"https://store.steampowered.com/api/appdetails?appids={steam_id}&cc=us&l=en"
    elif steam_type == "bundle":
        api_url = f"https://store.steampowered.com/api/bundledetails/?bundleids={steam_id}&cc=us&l=en"
    else:
        return None

    response = requests.get(api_url)
    data = response.json()

    if not data or not data.get(steam_id):
        return None

    details = data[steam_id].get("data")
    if not details:
        return None

    if steam_type == "app":
        price_info = details.get("price_overview")
    else:
        price_info = details.get("price", {}).get("discounted")

    if not price_info:
        return None

    discount = price_info.get("discount_percent", 0)
    final_price = price_info.get("final_formatted", "Unknown price")
    name = details.get("name", "Unknown title")

    return {
        "name": name,
        "discount": discount,
        "price": final_price,
        "url": f"https://store.steampowered.com/{steam_type}/{steam_id}"
    }

def send_to_discord(message):
    """
    Send a message to Discord via webhook.
    """
    payload = {"content": message}
    requests.post(WEBHOOK_URL, json=payload)

def main():
    discounted_games = []
    for game_url in GAMES:
        steam_type, steam_id = get_steam_id(game_url)
        if not steam_type:
            continue

        discount_info = fetch_discount(steam_type, steam_id)
        if discount_info and discount_info["discount"] > 0:
            discounted_games.append(
                f"**{discount_info['name']}** is {discount_info['discount']}% off for {discount_info['price']}!\n{discount_info['url']}"
            )

    if discounted_games:
        send_to_discord("@everyone 🎮 **Steam Discounts!**\n\n" + "\n\n".join(discounted_games))
    else:
        send_to_discord("No discounts found today.")

if __name__ == "__main__":
    main()
