import os
import requests

# List of Steam store links (games or bundles)
steam_links = [
    "https://store.steampowered.com/bundle/32470/Cyberpunk_2077_Ultimate_Edition/"
]

# Your Discord webhook (read from GitHub secret or env variable)
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

def check_discount(url):
    """
    Returns (on_sale: bool, name: str, discount: str, old_price: str, new_price: str)
    """
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code != 200:
            return False, None, None, None, None

        html = r.text

        # Extract game/bundle name
        start = html.find('<title>') + 7
        end = html.find('</title>')
        name = html[start:end].split("on Steam")[0].strip()

        # Check for discount
        if 'discount_pct' in html:
            # Extract discount
            discount_start = html.find('discount_pct">') + len('discount_pct">')
            discount_end = html.find('%', discount_start)
            discount = html[discount_start:discount_end + 1].strip()

            # Extract prices
            old_price_start = html.find('discount_original_price">') + len('discount_original_price">')
            old_price_end = html.find('</div>', old_price_start)
            old_price = html[old_price_start:old_price_end].strip()

            new_price_start = html.find('discount_final_price">') + len('discount_final_price">')
            new_price_end = html.find('</div>', new_price_start)
            new_price = html[new_price_start:new_price_end].strip()

            return True, name, discount, old_price, new_price

        return False, name, None, None, None

    except Exception:
        return False, None, None, None, None


def send_webhook(content):
    payload = {"content": content}
    requests.post(WEBHOOK_URL, json=payload)


def main():
    any_discount = False
    messages = []

    for link in steam_links:
        on_sale, name, discount, old_price, new_price = check_discount(link)
        if on_sale:
            any_discount = True
            messages.append(
                f"🔥 **{name}** is on sale!\n\n"
                f"{discount} off\n"
                f"{old_price} → {new_price}\n\n"
                f"🔗 {link}"
            )
        else:
            messages.append(
                f"🔎 **{name}** is not on sale right now.\n"
                f"Check it here: {link}"
            )

    if any_discount:
        message = "@everyone\n\n" + "\n\n".join(messages)
    else:
        message = "\n\n".join(messages)

    send_webhook(message)


if __name__ == "__main__":
    main()
