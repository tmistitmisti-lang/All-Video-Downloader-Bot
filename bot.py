import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ---- Fake Server for Render Free Tier ----
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running Successfully!"

def run_server():
    # Render default port is 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ---- Telegram Bot Logic ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "আসসালামু আলাইকুম! আমি আপনার টেলিগ্রাম ডাউনলোডার বট। "
        "যেকোনো ভিডিও বা ফাইলের লিঙ্ক পাঠালে আমি সেটি ডাউনলোড করে দিতে সাহায্য করব।"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # এখানে আপনার ডাউনলোডের মূল লজিক থাকবে। আপাতত বটটি রিপ্লাই দেবে।
    await update.message.reply_text(f"আপনার লিঙ্কটি পেয়েছি: {user_text}\nএটি প্রসেস করা হচ্ছে...")

def main():
    # Environment Variable থেকে টোকেন নেওয়া
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN নামের কোনো Environment Variable পাওয়া যায়নি!")
        return

    # Flask সার্ভার ব্যাকগ্রাউন্ড থ্রেডে চালু করা
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # টেলিগ্রাম বট চালু করা
    print("Bot is starting...")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
