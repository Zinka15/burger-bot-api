import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# Загружаем настройки
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Подключаем AI
client = Groq(api_key=GROQ_API_KEY)

# ПАМЯТЬ: история разговоров для каждого пользователя
conversations = {}

# Информация о бургерной для AI — НА НЕМЕЦКОМ
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

Deine Aufgaben:
1. Hilf bei der Auswahl des Essens
2. Beantworte Fragen zu Zutaten und Preisen
3. Nimm Bestellungen entgegen
4. Sei höflich und benutze Emojis

Antworte kurz, sachlich und freundlich.
Wenn der Kunde bestellen möchte — bestätige die Bestellung und nenne den Gesamtpreis.
Erinnere dich an alles, was der Kunde vorher gesagt hat.
Antworte IMMER auf Deutsch!
"""

# Функция для общения с AI (с памятью)
def ask_ai(user_id: int, user_message: str) -> str:
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
        print(f"Ошибка AI: {e}")
        return "Entschuldigung, etwas ist schief gelaufen 😅 Bitte versuche es noch einmal!"

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversations[user_id] = []
    
    await update.message.reply_text(
        f"Hallo, {update.effective_user.first_name}! 👋\n\n"
        "Ich bin der smarte Bot von Lecker Burger 🍔🤖\n\n"
        "Frag mich einfach:\n"
        "• Was ist lecker bei euch?\n"
        "• Was empfiehlst du?\n"
        "• Ich möchte etwas Scharfes\n"
        "• Was kostet ein Cheeseburger?\n\n"
        "Oder schreib einfach, was du möchtest!\n\n"
        "Schreib /clear um das Gespräch neu zu starten"
    )

# Команда /clear
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversations[user_id] = []
    await update.message.reply_text("Verlauf gelöscht! 🧹 Fangen wir von vorne an. Was darf es sein?")

# Команда /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    response = ask_ai(user_id, "Zeig mir die komplette Speisekarte mit Preisen")
    await update.message.reply_text(response)

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    await update.message.chat.send_action("typing")
    
    response = ask_ai(user_id, user_message)
    
    await update.message.reply_text(response)

# Запуск бота
def main():
    print("Deutscher AI Bot startet...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot läuft! Drücke Ctrl+C zum Beenden")
    app.run_polling()

if __name__ == "__main__":
    main()
