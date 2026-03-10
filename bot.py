from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8620917501:AAFGYN1FloUd0sPwW8Gu2wTKmrGhZ1Flqc0"

users = {}
waiting = []
pairs = {}

menu = ReplyKeyboardMarkup(
[
["New Chat 🔎"],
["Next 🔄", "Stop ❌"],
["Cancel Search 🛑", "Clear Chat 🧹"]
],
resize_keyboard=True
)

def partner_of(user):
    return pairs.get(user)

def remove_from_waiting(user):
    if user in waiting:
        waiting.remove(user)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.chat_id

    users[user] = {"state": "idle"}

    await update.message.reply_text(
        "Anonymous Chat Bot",
        reply_markup=menu
    )

async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.chat_id

    if user in waiting:
        await update.message.reply_text("Already searching...")
        return

    if partner_of(user):
        await update.message.reply_text("You are already in chat")
        return

    waiting.append(user)

    if len(waiting) >= 2:

        u1 = waiting.pop(0)
        u2 = waiting.pop(0)

        pairs[u1] = u2
        pairs[u2] = u1

        await context.bot.send_message(u1, "Connected")
        await context.bot.send_message(u2, "Connected")

    else:

        await update.message.reply_text("Searching for stranger...")

async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.chat_id

    if user in waiting:
        waiting.remove(user)
        await update.message.reply_text("Search stopped.")
    else:
        await update.message.reply_text("You are not searching.")

async def next_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.chat_id

    partner = partner_of(user)

    if partner:

        del pairs[user]
        del pairs[partner]

        await context.bot.send_message(partner, "Stranger skipped")

        await start_search(update, context)

    else:
        await update.message.reply_text("You are not in chat.")

async def stop_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.chat_id

    partner = partner_of(user)

    if partner:

        del pairs[user]
        del pairs[partner]

        await context.bot.send_message(partner, "Stranger left")

    remove_from_waiting(user)

    await update.message.reply_text("Chat ended.")

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    for _ in range(15):
        await update.message.reply_text(" ")

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.chat_id
    text = update.message.text

    if text == "New Chat 🔎":
        await start_search(update, context)

    elif text == "Cancel Search 🛑":
        await cancel_search(update, context)

    elif text == "Next 🔄":
        await next_chat(update, context)

    elif text == "Stop ❌":
        await stop_chat(update, context)

    elif text == "Clear Chat 🧹":
        await clear_chat(update, context)

    else:

        partner = partner_of(user)

        if partner:
            await context.bot.send_message(partner, text)
        else:
            await update.message.reply_text("Press New Chat to start.")

async def block_media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("Media not allowed. Text only.")

print("Bot starting...")

app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))

app.add_handler(
    MessageHandler(
        filters.PHOTO |
        filters.VIDEO |
        filters.AUDIO |
        filters.Document.ALL |
        filters.Sticker.ALL,
        block_media
    )
)

app.run_polling(drop_pending_updates=True)
