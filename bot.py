import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Загружаем токен из .env файла
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Меню бургерной
MENU = """
🍔 *НАШЕ МЕНЮ*

*Бургеры:*
1. Классический — 250₽
2. Чизбургер — 290₽
3. Двойной — 390₽
4. Острый — 320₽

*Напитки:*
5. Кола — 80₽
6. Сок — 90₽

*Картошка:*
7. Маленькая — 100₽
8. Большая — 150₽

Напиши номер или название, чтобы заказать!
"""

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}! 👋\n\n"
        "Я бот бургерной 🍔\n\n"
        "Напиши /menu чтобы посмотреть меню\n"
        "Или просто напиши что хочешь заказать!"
    )

# Команда /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MENU, parse_mode="Markdown")

# Обработка любых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    # Простая логика ответов
    if "классич" in text or text == "1":
        await update.message.reply_text("Отличный выбор! 🍔 Классический бургер — 250₽\n\nХочешь оформить заказ? Напиши 'да'")
    elif "чизбургер" in text or text == "2":
        await update.message.reply_text("Вкуснятина! 🧀 Чизбургер — 290₽\n\nХочешь оформить заказ? Напиши 'да'")
    elif "двойной" in text or text == "3":
        await update.message.reply_text("Для голодных! 🍔🍔 Двойной бургер — 390₽\n\nХочешь оформить заказ? Напиши 'да'")
    elif "острый" in text or text == "4":
        await update.message.reply_text("Огонь! 🌶️ Острый бургер — 320₽\n\nХочешь оформить заказ? Напиши 'да'")
    elif "да" in text:
        await update.message.reply_text("✅ Заказ принят!\n\nБудет готов через 15 минут 🕐\n\nСпасибо что выбрали нас! 🙏")
    elif "меню" in text:
        await update.message.reply_text(MENU, parse_mode="Markdown")
    else:
        await update.message.reply_text(
            "Не совсем понял 🤔\n\n"
            "Напиши /menu чтобы посмотреть меню\n"
            "Или напиши название бургера!"
        )

# Запуск бота
def main():
    print("Бот запускается...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Бот работает! Нажми Ctrl+C чтобы остановить")
    app.run_polling()

if __name__ == "__main__":
    main()
