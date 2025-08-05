import requests
import os

webhook = os.environ.get("DISCORD_WEBHOOK")

data = {
    "content": "✅ This is a test from the GitHub Actions bot! It works!"
}

response = requests.post(webhook, json=data)

if response.status_code == 204:
    print("Message sent to Discord!")
else:
    print("Failed to send message:", response.status_code, response.text)
