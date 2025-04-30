
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# Токен бота и Chat ID твоей группы
BOT_TOKEN = "7829313022:AAG6-al_3mm4pjCBxJLxvDAfIRdMn1z-WIE"
GROUP_CHAT_ID = -1001799013576

CHOOSING, TYPING = range(2)

reply_keyboard = [
    ["AI-доступы", "Фейк-документы"],
    ["AI-схемы", "Задания / контрольные"],
    ["Отмена"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

user_data_cache = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Выбери нужную категорию:",
        reply_markup=markup
    )
    return CHOOSING

async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_cache[update.effective_user.id] = {
        "category": update.message.text
    }
    await update.message.reply_text("Опиши, что конкретно тебе нужно:")
    return TYPING

async def receive_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Не указан"
    category = user_data_cache[user_id]["category"]
    details = update.message.text

    msg = (
        "[НОВЫЙ ЗАКАЗ]\n"
        f"Категория: {category}\n"
        f"Детали: {details}\n"
        f"Юзер: @{username} (ID: {user_id})"
    )

    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
    await update.message.reply_text("Заказ отправлен. С тобой скоро свяжутся!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_category)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_details)]
        },
        fallbacks=[MessageHandler(filters.Regex("^(Отмена)$"), cancel)],
    )

    app.add_handler(conv_handler)
    print("Бот запущен.")
    app.run_polling()
