import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8429628607:AAGhCWjJbiBM9a1QkBnsadr_Y93oOw1GDJI")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "849129286"))

WAITING_RECEIPT = 1
WAITING_NAME = 2

WELCOME_TEXT = (
    "Привет, я рада, что ты здесь 🤍\n\n"
    "Я Элина — педагог-хореограф и основатель закрытого танцевального "
    "онлайн-клуба «Ты — есть Вселенная».\n\n"
    "Это пространство для девушек, которые хотят раскрыть женственность "
    "и уверенность, начать танцевать и найти своё комьюнити — через контемпорари.\n\n"
    "Выбери, с чего начнём:"
)

CLUB_INFO_TEXT = (
    "Клуб «Ты — есть Вселенная» — это закрытое онлайн-пространство, где девушки "
    "раскрывают женственность и уверенность через контемпорари.\n\n"
    "Что внутри каждый месяц:\n"
    "— Авторская хореография\n"
    "— Тренировки по растяжке в записи\n"
    "— Мини-тренировки по 5-7 минут\n"
    "— Медитация и рекомендация месяца\n"
    "— Живые созвоны-мастермайнды\n"
    "— Чат участниц и чат домашних заданий\n"
    "— Моя личная обратная связь\n\n"
    "Находясь в клубе ты получаешь:\n"
    "— Начнёшь танцевать — поймаешь себя на том, что двигаешься под музыку просто так, на кухне\n"
    "— Уберёшь зажимы в теле — и почувствуешь, как стало легче дышать, держаться, быть собой\n"
    "— Окажешься в тёплом женском комьюнити — и удивишься, как много значит быть среди своих\n"
    "— Почувствуешь уверенность в себе, в своём теле\n"
    "— Станешь пластичнее и женственнее — и это начнут замечать окружающие раньше, чем ты сама\n\n"
    "Стоимость: 2 490 ₽ / месяц"
)

PAYMENT_TEXT = (
    "Рада тебя видеть!\n\n"
    "Для оплаты переведи 2 490 ₽ по номеру:\n"
    "+7 918 018-35-14\n"
    "(Сбербанк, Т-банк)\n\n"
    "После перевода отправь сюда скриншот — и я добавлю тебя в клуб "
    "в течение нескольких часов 🤍"
)


def main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("О клубе", callback_data="about"),
            InlineKeyboardButton("Оплатить участие", callback_data="pay")
        ]
    ])


def about_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Оплатить участие", callback_data="pay")],
        [InlineKeyboardButton("← Назад", callback_data="back")]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, reply_markup=main_keyboard())
    return ConversationHandler.END


async def button_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(CLUB_INFO_TEXT, reply_markup=about_keyboard())


async def button_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(WELCOME_TEXT, reply_markup=main_keyboard())


async def button_pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(PAYMENT_TEXT)
    return WAITING_RECEIPT


async def receipt_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data["receipt_id"] = update.message.photo[-1].file_id
        context.user_data["receipt_type"] = "photo"
    elif update.message.document:
        context.user_data["receipt_id"] = update.message.document.file_id
        context.user_data["receipt_type"] = "document"

    await update.message.reply_text("Получила, спасибо! Напиши своё имя 🤍")
    return WAITING_NAME


async def name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    user = update.message.from_user
    username = f"@{user.username}" if user.username else f"(без ника, ID: {user.id})"

    await update.message.reply_text(
        f"{name}, рада тебя видеть! Добавлю тебя в клуб в течение нескольких часов 🤍"
    )

    notification = (
        f"🆕 Новая участница!\n\n"
        f"Имя: {name}\n"
        f"Ник: {username}\n"
        f"ID: {user.id}"
    )
    await context.bot.send_message(ADMIN_ID, notification)

    receipt_id = context.user_data.get("receipt_id")
    receipt_type = context.user_data.get("receipt_type")

    if receipt_id:
        if receipt_type == "photo":
            await context.bot.send_photo(ADMIN_ID, receipt_id, caption="Чек оплаты")
        else:
            await context.bot.send_document(ADMIN_ID, receipt_id, caption="Чек оплаты")

    return ConversationHandler.END


async def fallback_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Чтобы начать — напиши /start 🤍"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_pay, pattern="^pay$")],
        states={
            WAITING_RECEIPT: [
                MessageHandler(filters.PHOTO | filters.Document.ALL, receipt_received)
            ],
            WAITING_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, name_received)
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_about, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(button_back, pattern="^back$"))
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_text))

    logger.info("Бот запущен")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
