import random
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8620917501:AAFGYN1FloUd0sPwW8Gu2wTKmrGhZ1Flqc0"

users = {}
waiting = []
pairs = {}

captcha = {}
verified_users = set()

# -------- MENUS --------

menu = ReplyKeyboardMarkup(
[
["New Chat 🔎"],
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
["Gender 👤","DOB 🎂"],
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

# -------- HELPERS --------

def partner_of(user):
    return pairs.get(user)

def remove_waiting(user):
    if user in waiting:
        waiting.remove(user)

def user_info(user):
    gender = users[user].get("gender","👤")
    age = users[user].get("age","?")
    return gender, age

# -------- CAPTCHA --------

async def send_captcha(update, context):

    user = update.message.chat_id

    a = random.randint(1,9)
    b = random.randint(1,9)

    captcha[user] = a + b

    await update.message.reply_text(
        f"🤖 Verification\n\nWhat is {a} + {b} ?"
    )

# -------- START --------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.chat_id

    if user not in users:
        users[user] = {"gender":"👤","age":"?"}

    if user not in verified_users:
        await send_captcha(update,context)
        return

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

        g1, a1 = user_info(u2)
        g2, a2 = user_info(u1)

        await context.bot.send_message(
            u1,
            f"{g1} Connected\nAge: {a1}",
            reply_markup=chat_menu
        )

        await context.bot.send_message(
            u2,
            f"{g2} Connected\nAge: {a2}",
            reply_markup=chat_menu
        )

    else:

        await update.message.reply_text(
            "🔎 Searching for stranger...",
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

    # CAPTCHA CHECK

    if user not in verified_users:

        if user in captcha and text.isdigit():

            if int(text) == captcha[user]:

                verified_users.add(user)

                await update.message.reply_text(
                    "✅ Verified. Connecting..."
                )

                await start_search(update,context)

            else:

                await update.message.reply_text(
                    "❌ Wrong answer. Try again."
                )

        return

    # CHAT

    if text == "New Chat 🔎":
        await start_search(update,context)

    elif text == "Cancel Search 🛑":
        await cancel_search(update,context)

    elif text == "Another Chat 🔁":
        await another_chat(update,context)

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

    elif text == "DOB 🎂":
        users[user]["awaiting_dob"] = True
        await update.message.reply_text(
            "Enter DOB\nFormat: DD-MM-YYYY"
        )

    elif users[user].get("awaiting_dob"):

        try:

            dob = datetime.strptime(text,"%d-%m-%Y")
            today = datetime.today()

            age = today.year - dob.year - (
                (today.month,today.day) < (dob.month,dob.day)
            )

            users[user]["age"] = age
            users[user]["awaiting_dob"] = False

            await update.message.reply_text(
                f"Age set to {age}",
                reply_markup=settings_menu
            )

        except:

            await update.message.reply_text(
                "Invalid format.\nUse: DD-MM-YYYY"
            )

    elif text == "Back ⬅️":

        await update.message.reply_text(
            "Back to main menu",
            reply_markup=menu
        )

    # CHAT MESSAGE RELAY

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
