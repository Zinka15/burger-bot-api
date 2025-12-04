import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

# Загружаем настройки
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Подключаем AI
client = Groq(api_key=GROQ_API_KEY)

# Создаём API
app = FastAPI(title="Burger Bot API")

# Разрешаем запросы с мобильного приложения
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Память разговоров
conversations = {}

# Промпт на немецком
SYSTEM_PROMPT = """
Du bist ein freundlicher Assistent des Burgerladens "Lecker Burger".

Unsere Speisekarte:
- Klassischer Burger — 8,50€ (Rindfleisch, Salat, Tomate, Soße)
- Cheeseburger — 9,50€ (Rindfleisch, doppelt Käse, Soße)
- Double Burger — 12,90€ (doppeltes Patty, Käse, Gemüse)
- Scharfer Burger — 10,50€ (Rindfleisch, Jalapeños, scharfe Soße)
- Cola — 2,50€
- Saft — 2,80€
- Pommes klein — 3,00€
- Pommes groß — 4,50€

Antworte kurz, sachlich und freundlich auf Deutsch.
Benutze Emojis.
"""

# Модель запроса
class ChatRequest(BaseModel):
    user_id: str
    message: str

# Модель ответа
class ChatResponse(BaseModel):
    response: str

# Функция AI
def ask_ai(user_id: str, user_message: str) -> str:
    if user_id not in conversations:
        conversations[user_id] = []
    
    conversations[user_id].append({
        "role": "user",
        "content": user_message
    })
    
    if len(conversations[user_id]) > 20:
        conversations[user_id] = conversations[user_id][-20:]
    
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(conversations[user_id])
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        assistant_message = response.choices[0].message.content
        
        conversations[user_id].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return "Entschuldigung, etwas ist schief gelaufen 😅"

# === ЭНДПОИНТЫ ===

@app.get("/")
def home():
    return {"status": "ok", "message": "Burger Bot API läuft!"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Отправить сообщение боту"""
    response = ask_ai(request.user_id, request.message)
    return ChatResponse(response=response)

@app.post("/clear/{user_id}")
def clear_history(user_id: str):
    """Очистить историю пользователя"""
    conversations[user_id] = []
    return {"status": "ok", "message": "Verlauf gelöscht"}

@app.get("/menu")
def get_menu():
    """Получить меню"""
    return {
        "items": [
            {"id": "1", "name": "Klassischer Burger", "price": 8.50},
            {"id": "2", "name": "Cheeseburger", "price": 9.50},
            {"id": "3", "name": "Double Burger", "price": 12.90},
            {"id": "4", "name": "Scharfer Burger", "price": 10.50},
            {"id": "5", "name": "Cola", "price": 2.50},
            {"id": "6", "name": "Saft", "price": 2.80},
            {"id": "7", "name": "Pommes klein", "price": 3.00},
            {"id": "8", "name": "Pommes groß", "price": 4.50},
        ]
    }
