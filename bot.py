from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8620917501:AAFGYN1FloUd0sPwW8Gu2wTKmrGhZ1Flqc0"

users = {}
waiting = []
pairs = {}

# -------- MENUS --------

menu = ReplyKeyboardMarkup(
[
["New Chat 🔎","Another Chat 🔁"],
["Settings ⚙️"]
],
resize_keyboard=True
)

search_menu = ReplyKeyboardMarkup(
[
["Cancel Search 🛑"]
],
resize_keyboard=True
)

chat_menu = ReplyKeyboardMarkup(
[
["Another Chat 🔁","Leave Chat ❌"]
],
resize_keyboard=True
)

settings_menu = ReplyKeyboardMarkup(
[
["Gender 👤","Age 🎂"],
["Back ⬅️"]
],
resize_keyboard=True
)

gender_menu = ReplyKeyboardMarkup(
[
["👦 Boy","👧 Girl"],
["👤 Anonymous"],
["Back ⬅️"]
],
resize_keyboard=True
)

age_menu = ReplyKeyboardMarkup(
[
["18-21","22-25"],
["26-30","31+"],
["Back ⬅️"]
],
resize_keyboard=True
)

# -------- HELPERS --------

def partner_of(user):
    return pairs.get(user)

def remove_waiting(user):
    if user in waiting:
        waiting.remove(user)

def user_info(user):
    gender = users[user].get("gender","👤")
    age = users[user].get("age","?")
    return f"{gender} {age}"

# -------- START --------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.chat_id

    if user not in users:
        users[user] = {"gender":"👤","age":"?"}

    await update.message.reply_text(
        "Anonymous Chat",
        reply_markup=menu
    )

# -------- MATCHMAKING --------

async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.chat_id

    if user in waiting:
        return

    if partner_of(user):
        return

    waiting.append(user)

    if len(waiting) >= 2:

        u1 = waiting.pop(0)
        u2 = waiting.pop(0)

        pairs[u1] = u2
        pairs[u2] = u1

        await context.bot.send_message(
            u1,
            f"Connected with {user_info(u2)}",
            reply_markup=chat_menu
        )

        await context.bot.send_message(
            u2,
            f"Connected with {user_info(u1)}",
            reply_markup=chat_menu
        )

    else:

        await update.message.reply_text(
            "Searching for stranger...",
            reply_markup=search_menu
        )

# -------- CANCEL SEARCH --------

async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.chat_id
    remove_waiting(user)

    await update.message.reply_text(
        "Search cancelled.",
        reply_markup=menu
    )

# -------- ANOTHER CHAT --------

async def another_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.chat_id
    partner = partner_of(user)

    if partner:

        del pairs[user]
        del pairs[partner]

        await context.bot.send_message(
            partner,
            "Stranger left"
        )

    await start_search(update,context)

# -------- LEAVE CHAT --------

async def leave_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.chat_id
    partner = partner_of(user)

    if partner:

        del pairs[user]
        del pairs[partner]

        await context.bot.send_message(
            partner,
            "Stranger left"
        )

    await update.message.reply_text(
        "You left the chat.",
        reply_markup=menu
    )

# -------- SETTINGS --------

async def open_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "⚙️ Settings",
        reply_markup=settings_menu
    )

# -------- MESSAGE HANDLER --------

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.chat_id
    text = update.message.text

    # CHAT

    if text == "New Chat 🔎":
        await start_search(update,context)

    elif text == "Another Chat 🔁":
        await another_chat(update,context)

    elif text == "Cancel Search 🛑":
        await cancel_search(update,context)

    elif text == "Leave Chat ❌":
        await leave_chat(update,context)

    # SETTINGS

    elif text == "Settings ⚙️":
        await open_settings(update,context)

    elif text == "Gender 👤":
        await update.message.reply_text(
            "Select gender",
            reply_markup=gender_menu
        )

    elif text == "👦 Boy":
        users[user]["gender"] = "👦"
        await update.message.reply_text(
            "Gender set to Boy 👦",
            reply_markup=settings_menu
        )

    elif text == "👧 Girl":
        users[user]["gender"] = "👧"
        await update.message.reply_text(
            "Gender set to Girl 👧",
            reply_markup=settings_menu
        )

    elif text == "👤 Anonymous":
        users[user]["gender"] = "👤"
        await update.message.reply_text(
            "Gender set to Anonymous 👤",
            reply_markup=settings_menu
        )

    elif text == "Age 🎂":
        await update.message.reply_text(
            "Select age group",
            reply_markup=age_menu
        )

    elif text in ["18-21","22-25","26-30","31+"]:
        users[user]["age"] = text
        await update.message.reply_text(
            f"Age set to {text}",
            reply_markup=settings_menu
        )

    elif text == "Back ⬅️":
        await update.message.reply_text(
            "Back to main menu",
            reply_markup=menu
        )

    # MESSAGE RELAY

    else:

        partner = partner_of(user)

        if partner:
            await context.bot.send_message(partner,text)

# -------- MEDIA BLOCK --------

async def block_media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("Media not allowed.")

# -------- RUN --------

print("Bot starting...")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))

app.add_handler(
    MessageHandler(
        filters.PHOTO |
        filters.VIDEO |
        filters.Document.ALL |
        filters.Sticker.ALL,
        block_media
    )
)

app.run_polling(drop_pending_updates=True)
