from fastapi import Request, Form
from typing import Callable
import os

class WhatsAppListener:
    """
    Handles incoming WhatsApp messages via Twilio webhooks.
    """
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback

    async def handle_webhook(self, request: Request):
        """
        FastAPI endpoint handler for Twilio WhatsApp webhooks.
        Twilio sends data as Form parameters.
        """
        form_data = await request.form()
        incoming_msg = form_data.get('Body', '').strip()
        sender_phone = form_data.get('From', '')

        if incoming_msg:
            print(f"WhatsApp Triggered from {sender_phone}: {incoming_msg}")
            self.callback(incoming_msg)
            
            # Twilio expects a TwiML response (even if empty)
            return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response></Response>"
        
        return "No body found"

def create_whatsapp_handler(callback: Callable[[str], None]):
    listener = WhatsAppListener(callback)
    return listener.handle_webhook
