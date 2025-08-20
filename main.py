import os
import requests

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

    # Handle app vs bundle price info
    if steam_type == "app":
        price_info = details.get("price_overview")
    else:
        price_info = details.get("price", {}).get("discounted")

    if not price_info:
        return {
            "name": details.get("name", "Unknown title"),
            "discount": 0,
            "original": None,
            "final": None,
            "url": f"https://store.steampowered.com/{steam_type}/{steam_id}"
        }

    discount = price_info.get("discount_percent", 0)
    final_price = price_info.get("final_formatted", "Unknown price")
    original_price = price_info.get("initial_formatted", None)
    name = details.get("name", "Unknown title")

    return {
        "name": name,
        "discount": discount,
        "original": original_price,
        "final": final_price,
        "url": f"https://store.steampowered.com/{steam_type}/{steam_id}"
    }

def send_to_discord(message):
    """
    Send a message to Discord via webhook.
    """
    payload = {"content": message}
    requests.post(WEBHOOK_URL, json=payload)

def main():
    for game_url in GAMES:
        steam_type, steam_id = get_steam_id(game_url)
        if not steam_type:
            continue

        discount_info = fetch_discount(steam_type, steam_id)
        if discount_info["discount"] > 0:
            message = (
                f"@everyone 🔥 **{discount_info['name']} is on sale!**\n\n"
                f"**{discount_info['discount']}%** off\n"
                f"~~{discount_info['original']}~~ → **{discount_info['final']}**\n\n"
                f"🔗 {discount_info['url']}"
            )
        else:
            message = (
                f"🔎 **{discount_info['name']} is not on sale right now.**\n"
                f"Check it here: {discount_info['url']}"
            )

        send_to_discord(message)

if __name__ == "__main__":
    main()
