import imaplib
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    host = "imap.gmail.com"
    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not user or not password:
        print("Error: EMAIL_USER or EMAIL_PASS not set in .env")
        return

    try:
        print(f"Attempting to connect to {host} as {user}...")
        mail = imaplib.IMAP4_SSL(host)
        mail.login(user, password)
        print("Login successful!")
        
        status, folders = mail.list()
        if status == "OK":
            print("Successfully retrieved folder list.")
        
        mail.select("inbox")
        status, messages = mail.search(None, 'ALL')
        if status == "OK":
            count = len(messages[0].split())
            print(f"Success! Found {count} total messages in Inbox.")
        
        mail.logout()
        print("Test complete.")
    except Exception as e:
        print(f"Connection failed: {e}")
        print("\nTIP: If you're using Gmail, ensure you've enabled 2FA and created an 'App Password'.")

if __name__ == "__main__":
    test_connection()
