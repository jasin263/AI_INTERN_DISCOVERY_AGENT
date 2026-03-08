import requests
import time
import os
from typing import Callable, Optional
from dotenv import load_dotenv

load_dotenv()

class TelegramListener:
    """
    Listens for incoming Telegram messages and triggers an internship search.
    """
    def __init__(self, callback: Callable[[str], None], token: str, chat_id: str):
        self.token = token
        self.chat_id = str(chat_id)
        self.callback = callback
        self.offset = 0
        self.is_running = False
        self.api_url = f"https://api.telegram.org/bot{self.token}"

    def check_messages(self):
        """
        Polls for new messages from the specific user.
        """
        if not self.token or not self.chat_id:
            return

        try:
            url = f"{self.api_url}/getUpdates"
            params = {"offset": self.offset, "timeout": 10}
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                print(f"Telegram Listener: Error fetching updates: {response.text}")
                return

            updates = response.json().get("result", [])
            for update in updates:
                self.offset = update["update_id"] + 1
                
                message = update.get("message")
                if not message:
                    continue
                
                from_id = str(message.get("from", {}).get("id"))
                text = message.get("text")
                
                if from_id == self.chat_id and text:
                    print(f"Telegram Triggered: {text}")
                    # Only process if it looks like a query (not a command unless handled)
                    if text.startswith('/'):
                        if text == '/start':
                            self.send_reply("Hello! I'm your Internship Finder Agent. Send me a message (e.g., 'Python Intern') to start a search.")
                        continue
                    
                    self.callback(text)

        except Exception as e:
            print(f"Telegram Listener Error: {e}")

    def send_reply(self, text: str):
        """Sends a simple text reply back to the user."""
        url = f"{self.api_url}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text}
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Error sending Telegram reply: {e}")

    def start_polling(self, interval: int = 5):
        """
        Blocking loop for polling.
        """
        self.is_running = True
        print(f"Telegram polling started (every {interval}s)...")
        # Get initial offset to avoid processing old messages
        try:
            resp = requests.get(f"{self.api_url}/getUpdates", params={"limit": 1})
            if resp.status_code == 200:
                results = resp.json().get("result", [])
                if results:
                    self.offset = results[-1]["update_id"] + 1
        except:
            pass

        while self.is_running:
            self.check_messages()
            time.sleep(interval)

    def stop_polling(self):
        self.is_running = False
        print("Telegram polling stopped.")
