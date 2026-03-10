from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8620917501:AAFGYN1FloUd0sPwW8Gu2wTKmrGhZ1Flqc0"

users = {}
waiting = []
pairs = {}

# ---------- MENUS ----------

menu = ReplyKeyboardMarkup(
[
["New Chat 🔎"],
["Next 🔄", "Stop ❌"],
["Cancel Search 🛑", "Clear Chat 🧹"],
["Settings ⚙️"]
],
resize_keyboard=True
)

settings_menu = ReplyKeyboardMarkup(
[
["Gender 👤", "Age 🎂"],
["Back ⬅️"]
],
resize_keyboard=True
)

gender_menu = ReplyKeyboardMarkup(
[
["👦 Boy", "👧 Girl"],
["👤 Anonymous"],
["Back ⬅️"]
],
resize_keyboard=True
)

age_menu = ReplyKeyboardMarkup(
[
["18-21", "22-25"],
["26-30", "31+"],
["Back ⬅️"]
],
resize_keyboard=True
)

# ---------- HELPERS ----------

def partner_of(user):
    return pairs.get(user)

def remove_from_waiting(user):
    if user in waiting:
        waiting.remove(user)

# ---------- COMMAND ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.chat_id

    users[user] = {
        "gender": None,
        "age": None
    }

    await update.message.reply_text(
        "Anonymous Chat Bot",
        reply_markup=menu
    )

# ---------- CHAT MATCHING ----------

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

        await context.bot.send_message(u1, "Connected to stranger")
        await context.bot.send_message(u2, "Connected to stranger")

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

# ---------- CLEAR CHAT ----------

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    for _ in range(15):
        await update.message.reply_text(" ")

# ---------- SETTINGS ----------

async def open_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "⚙️ Settings\nChoose what you want to change.",
        reply_markup=settings_menu
    )

# ---------- MESSAGE HANDLER ----------

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.chat_id
    text = update.message.text

    # CHAT CONTROLS

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

    # SETTINGS

    elif text == "Settings ⚙️":
        await open_settings(update, context)

    elif text == "Gender 👤":
        await update.message.reply_text(
            "Select your gender:",
            reply_markup=gender_menu
        )

    elif text == "👦 Boy":
        users[user]["gender"] = "Boy"
        await update.message.reply_text(
            "✅ Gender set to: Boy 👦",
            reply_markup=settings_menu
        )

    elif text == "👧 Girl":
        users[user]["gender"] = "Girl"
        await update.message.reply_text(
            "✅ Gender set to: Girl 👧",
            reply_markup=settings_menu
        )

    elif text == "👤 Anonymous":
        users[user]["gender"] = "Anonymous"
        await update.message.reply_text(
            "✅ Gender set to: Anonymous 👤",
            reply_markup=settings_menu
        )

    elif text == "Age 🎂":
        await update.message.reply_text(
            "Select your age group:",
            reply_markup=age_menu
        )

    elif text in ["18-21","22-25","26-30","31+"]:
        users[user]["age"] = text
        await update.message.reply_text(
            f"✅ Age set to: {text}",
            reply_markup=settings_menu
        )

    elif text == "Back ⬅️":
        await update.message.reply_text(
            "⬅️ Returned to main menu.",
            reply_markup=menu
        )

    # MESSAGE RELAY

    else:

        partner = partner_of(user)

        if partner:
            await context.bot.send_message(partner, text)
        else:
            await update.message.reply_text("Press New Chat to start.")

# ---------- BLOCK MEDIA ----------

async def block_media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("Media not allowed. Text only.")

# ---------- START BOT ----------

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
