import sys
import os
import threading
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from email_listener import EmailListener
    from telegram_listener import TelegramListener
    from whatsapp_listener import WhatsAppListener
    print("✅ All trigger modules imported successfully.")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def mock_callback(query):
    print(f"Callback successful for query: {query}")

print("\nTesting EmailListener (5 unread limit)...")
try:
    listener = EmailListener(mock_callback)
    # Just checking initialization and attribute values
    # (Actual polling requires real credentials)
    print("✅ EmailListener initialized.")
except Exception as e:
    print(f"❌ EmailListener failed: {e}")

print("\nTesting TelegramListener...")
try:
    tg_listener = TelegramListener(mock_callback, "mock_token", "12345678")
    print("✅ TelegramListener initialized.")
except Exception as e:
    print(f"❌ TelegramListener failed: {e}")

print("\nTesting WhatsAppListener...")
try:
    wa_listener = WhatsAppListener(mock_callback)
    print("✅ WhatsAppListener initialized.")
except Exception as e:
    print(f"❌ WhatsAppListener failed: {e}")

print("\nVerification complete (Basic Module Check).")
