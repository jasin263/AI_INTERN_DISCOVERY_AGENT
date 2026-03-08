import imaplib
import email
from email.header import decode_header
import time
import socket
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Callable, Optional

load_dotenv()

class EmailListener:
    """
    Listens for incoming emails from the user and triggers an internship search.
    """
    def __init__(self, callback: Callable[[str], None]):
        self.host = "imap.gmail.com"
        self.user = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASS")
        self.callback = callback
        self.is_running = False

    def _decode_content(self, s):
        if s is None:
            return ""
        if isinstance(s, bytes):
            return s.decode()
        return s

    def check_emails(self):
        """
        Polls the inbox for new, unread emails from the owner.
        """
        if not self.user or not self.password:
            print("Email Listener: Missing credentials in .env")
            return

        try:
            # Connect to Gmail with a 30-second timeout to avoid WinError 10060 hangs
            socket.setdefaulttimeout(30)
            mail = imaplib.IMAP4_SSL(self.host)
            mail.login(self.user, self.password)
            mail.select("inbox")

            # 1. First, try searching specifically for UNSEEN emails FROM the user
            # This is MUCH more efficient than fetching headers for thousands of emails
            status, messages = mail.search(None, f'UNSEEN FROM "{self.user}"')
            
            if status != "OK" or not messages[0]:
                # 2. Fallback to any UNSEEN if the specific search failed (though it shouldn't for Gmail)
                status, messages = mail.search(None, 'UNSEEN')
            
            if status != "OK":
                print(f"IMAP Search failed with status: {status}")
                return

            msg_ids = messages[0].split()
            if not msg_ids:
                return
                
            print(f"Found {len(msg_ids)} relevant UNSEEN emails. Scanning latest 5...")
            
            # Reverse to get newest first and take only the latest 5
            msg_ids.reverse()
            msg_ids = msg_ids[:5]
            
            for num in msg_ids:
                # Fetch the email headers
                status, data = mail.fetch(num, "(RFC822.HEADER)")
                if status != "OK":
                    print(f"Failed to fetch headers for msg {num}")
                    continue
                
                msg_header = email.message_from_bytes(data[0][1])
                from_addr = msg_header.get("From", "")
                subject_raw = msg_header.get("Subject", "")
                
                subject = ""
                if subject_raw:
                    decoded = decode_header(subject_raw)[0]
                    subject, encoding = decoded
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                
                print(f"Checking msg {num}: Subject='{subject}', From='{from_addr}'")

                # 1. Ignore if it's an agent reply to prevent infinite loops
                # We check for both our prefix and if the user is the sender (which we already know from the search)
                if "Agent Reply:" in subject or "🤖" in subject:
                    print(f"Skipping agent reply to prevent loop: {subject}")
                    mail.store(num, '+FLAGS', '\\Seen') # Mark as read so we don't check again
                    continue

                # 2. Double check sender (extra safety)
                if self.user not in from_addr:
                    print(f"Skipping email from other sender: {from_addr}")
                    continue

                # 3. Process ANY subject that passed the above filters
                print(f"Email {num} passed all filters. Fetching full content...")

                # Now fetch the full message
                status, data = mail.fetch(num, "(RFC822)")
                if status != "OK":
                    print(f"Failed to fetch full message {num}")
                    continue

                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    payload = part.get_payload(decode=True)
                                    if payload:
                                        body = payload.decode()
                                    break
                        else:
                            payload = msg.get_payload(decode=True)
                            if payload:
                                body = payload.decode()

                        print(f"Final trigger for Subject='{subject}'")
                        
                        # Any email from the user to themselves is now treated as a search request
                        query = subject.strip()
                        if not query:
                            # Fallback to body if subject is empty
                            query = body.strip().split('\n')[0][:50] # Take first line of body
                        
                        if not query:
                            query = "internship"
                        
                        print(f"Invoking callback for query: {query}")
                        self.callback(query)
                        
                        # Mark as read
                        mail.store(num, '+FLAGS', '\\Seen')

            mail.close()
            mail.logout()

        except (socket.timeout, ConnectionError, OSError) as e:
            print(f"Email Listener Network Error (will retry): {e}")
        except Exception as e:
            print(f"Email Listener Error: {e}")
        finally:
            # Reset socket timeout so it doesn't affect other parts of the app
            socket.setdefaulttimeout(None)

    def start_polling(self, interval: int = 60):
        """
        Blocking loop for polling - intended to be run in a thread.
        Uses exponential backoff on network errors (up to 5 minutes).
        """
        self.is_running = True
        backoff = 0
        print(f"Email polling started (every {interval}s)...")
        while self.is_running:
            try:
                self.check_emails()
                backoff = 0  # Reset backoff on success
            except Exception as e:
                backoff = min(backoff + 60, 300)  # Increase up to 5 min
                print(f"Email polling encountered an error, backing off {backoff}s: {e}")
                time.sleep(backoff)
                continue
            time.sleep(interval)

    def stop_polling(self):
        self.is_running = False
        print("Email polling stopped.")
