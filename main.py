import requests
from bs4 import BeautifulSoup
import os

# Discord webhook desde variable de entorno
webhook = os.environ.get("DISCORD_WEBHOOK")

# Lista de juegos/bundles que quieres trackear
games = {
    "Cyberpunk 2077 Ultimate Edition": "https://store.steampowered.com/bundle/32470/Cyberpunk_2077_Ultimate_Edition/"
}

headers = {"User-Agent": "Mozilla/5.0"}
messages = []
any_sale = False  # Para decidir si usamos @everyone

for name, url in games.items():
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        discount_block = soup.find("div", class_="discount_pct")

        if discount_block:  # Si hay descuento
            discount_percent = discount_block.get_text(strip=True)
            original_price = soup.find("div", class_="discount_original_price").get_text(strip=True)
            final_price = soup.find("div", class_="discount_final_price").get_text(strip=True)

            messages.append(
                f"🎮 **{name}** está en oferta!\n"
                f"**{discount_percent}** off\n"
                f"~~{original_price}~~ → **{final_price}**\n"
                f"🔗 {url}\n"
            )
            any_sale = True
        else:
            messages.append(
                f"🔎 **{name}** no está en oferta.\n"
                f"🔗 {url}\n"
            )
    except Exception as e:
        messages.append(f"⚠️ Error revisando {name}: {e}")

# Unir todos los mensajes en uno solo
final_message = "\n".join(messages)

# Agregar @everyone solo si al menos un juego tiene descuento
if any_sale:
    final_message = "@everyone 🔥 Ofertas detectadas:\n\n" + final_message
else:
    final_message = "📢 Estado de juegos en Steam:\n\n" + final_message

# Enviar a Discord
payload = {"content": final_message}
res = requests.post(webhook, json=payload)

# Debug
if res.status_code == 204:
    print("✅ Mensaje enviado a Discord.")
else:
    print(f"❌ Error al enviar: {res.status_code} {res.text}")
