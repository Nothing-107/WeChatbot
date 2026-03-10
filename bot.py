from datetime import date
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8620917501:AAFGYN1FloUd0sPwW8Gu2wTKmrGhZ1Flqc0"
ADMIN_ID = 7660915205

users = {}
waiting = []
pairs = {}

panel_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("• New Chat ✅ •", callback_data="new_chat")],
    [
        InlineKeyboardButton("• Settings ⚙️ •", callback_data="settings"),
        InlineKeyboardButton("• Help ❓ •", callback_data="help")
    ]
])

settings_menu = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("Boy 👦", callback_data="gender_boy"),
        InlineKeyboardButton("Girl 👧", callback_data="gender_girl"),
        InlineKeyboardButton("Anonymous 👤", callback_data="gender_anon")
    ],
    [InlineKeyboardButton("Set Age 🎂", callback_data="set_age")],
    [InlineKeyboardButton("⬅ Back", callback_data="back_main")]
])

chat_menu = ReplyKeyboardMarkup(
[
["Next 🔄", "Leave ❌"],
["Clear Chat 🧹", "Report 🚨"]
],
resize_keyboard=True
)

def partner_of(user_id):
    return pairs.get(user_id)

async def connect(user_id, context):
    if waiting:
        partner = waiting.pop(0)

        pairs[user_id] = partner
        pairs[partner] = user_id

        g1 = users[user_id]["gender"]
        a1 = users[user_id]["age"]

        g2 = users[partner]["gender"]
        a2 = users[partner]["age"]

        await context.bot.send_message(user_id, f"{g2} {a2} Connected", reply_markup=chat_menu)
        await context.bot.send_message(partner, f"{g1} {a1} Connected", reply_markup=chat_menu)
    else:
        waiting.append(user_id)
        await context.bot.send_message(user_id, "Searching for stranger...")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {"gender": "👤", "age": "?", "stage": None}

    await update.message.reply_text("Anonymous Chat 👤", reply_markup=panel_menu)

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user_id = q.from_user.id
    await q.answer()

    if q.data == "new_chat":
        await connect(user_id, context)

    elif q.data == "settings":
        await q.message.edit_text("Settings ⚙️", reply_markup=settings_menu)

    elif q.data == "help":
        await q.message.edit_text("Press New Chat to meet strangers.", reply_markup=panel_menu)

    elif q.data == "gender_boy":
        users[user_id]["gender"] = "👦"

    elif q.data == "gender_girl":
        users[user_id]["gender"] = "👧"

    elif q.data == "gender_anon":
        users[user_id]["gender"] = "👤"

    elif q.data == "set_age":
        users[user_id]["stage"] = "dob"
        await q.message.reply_text("Send DOB like: DD-MM-YYYY")

    elif q.data == "back_main":
        await q.message.edit_text("Anonymous Chat 👤", reply_markup=panel_menu)

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if users.get(user_id, {}).get("stage") == "dob":
        try:
            d, m, y = map(int, text.split("-"))
            today = date.today()
            age = today.year - y - ((today.month, today.day) < (m, d))

            users[user_id]["age"] = age
            users[user_id]["stage"] = None

            await update.message.reply_text(f"Age saved: {age}")
        except:
            await update.message.reply_text("Use format DD-MM-YYYY")
        return

    if text == "Next 🔄":
        partner = partner_of(user_id)

        if partner:
            del pairs[user_id]
            del pairs[partner]

            await context.bot.send_message(partner, "Stranger skipped")
            await connect(partner, context)
            await connect(user_id, context)

    elif text == "Leave ❌":
        partner = partner_of(user_id)

        if partner:
            del pairs[user_id]
            del pairs[partner]
            await context.bot.send_message(partner, "Stranger left")

        await update.message.reply_text("You left the chat")

    elif text == "Clear Chat 🧹":
        for _ in range(20):
            await update.message.reply_text(" ")

    elif text == "Report 🚨":
        partner = partner_of(user_id)

        if partner:
            await context.bot.send_message(
                ADMIN_ID,
                f"User {user_id} reported {partner}"
            )

        await update.message.reply_text("Report sent")

    else:
        partner = partner_of(user_id)

        if partner:
            await context.bot.send_message(partner, text)

async def block_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Media not allowed. Text only.")

print("Bot starting...")

app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(menu))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))

app.add_handler(
    MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.AUDIO |
        filters.Document.ALL | filters.Sticker.ALL,
        block_media
    )
)

app.run_polling(drop_pending_updates=True)