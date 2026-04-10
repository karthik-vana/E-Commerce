import sys
sys.stdout.reconfigure(encoding='utf-8')

from config import AppConfig
from src.services.chat_service import ChatService

cfg = AppConfig()
svc = ChatService(cfg)
history = []
settings = {"persona": "friendly", "temperature": 0.7, "max_tokens": 1024, "model": "llama-3.3-70b-versatile"}

response = svc.get_response("I want to buy a product", history, settings)
print("\n--- RESPONSE ---")
print(response)
print("----------------")
