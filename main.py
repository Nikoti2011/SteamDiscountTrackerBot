import requests
from bs4 import BeautifulSoup
import os

STEAM_URL = "https://store.steampowered.com/app/413150/Stardew_Valley/"
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def check_discount():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(STEAM_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    discount_tag = soup.find("div", class_="discount_pct")
    if discount_tag:
        discount = discount_tag.text.strip()
        price = soup.find("div", class_="discount_final_price").text.strip()
        print(f"Discount found: {discount}, now {price}")

        if DISCORD_WEBHOOK:
            requests.post(DISCORD_WEBHOOK, json={"content": f"🎉 Stardew Valley is on sale! {discount}, now {price}\n{STEAM_URL}"})
    else:
        print("No discount.")

if __name__ == "__main__":
    check_discount()
