import os
import threading
import asyncio
import yt_dlp
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ---- Fake Server for Render Free Tier ----
app = Flask(__name__)

@app.route('/')
def home():
    return "⚡ Downloader Bot is Running Perfectly! ⚡"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ---- Telegram Bot Logic ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 আসসালামু আলাইকুম!\n"
        "আমি আপনার **অল-ইন-ওয়ান ভিডিও ডাউনলোডার বট**। 🤖✨\n\n"
        "আমাকে যেকোনো ভিডিওর লিঙ্ক পাঠান, আমি সেটি সরাসরি ডাউনলোড করে দেবো! 😎\n\n"
        "🎯 **আমি যা যা ডাউনলোড করতে পারি:**\n"
        "🔹 TikTok Videos 🎬\n"
        "🔹 YouTube Shorts & Videos 📺\n"
        "🔹 Facebook Videos 📱\n"
        "🔹 Instagram Reels 📸\n\n"
        "🚀 জাস্ট লিঙ্কটি কপি করে এখানে পেস্ট করে দিন!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    # লিঙ্কটি সঠিক কিনা চেক করা
    if not url.startswith("http://") and not url.startswith("https://"):
        await update.message.reply_text("⚠️ ওহ! দয়া করে একটি সঠিক ভিডিও লিঙ্ক (URL) পাঠান। 🧩")
        return

    # প্রথম স্ট্যাটাস মেসেজ
    status_message = await update.message.reply_text("🔍 লিঙ্কটি চেক করা হচ্ছে... একটু অপেক্ষা করুন! ⏳")

    # yt-dlp এর চমৎকার কনফিগারেশন
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded_video.%(ext)s', 
        'max_filesize': 50 * 1024 * 1024,      # ৫০ এমবি লিমিট (টেলিগ্রাম ফ্রি লিমিট)
        'quiet': True,
    }

    try:
        # স্ট্যাটাস আপডেট: ডাউনলোড শুরু
        await status_message.edit_text("⚡ আমাদের সার্ভারে ভিডিও ডাউনলোড শুরু হয়েছে... 📥")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # স্ট্যাটাস আপডেট: টেলিগ্রামে পাঠানো হচ্ছে
        await status_message.edit_text("🚀 ডাউনলোড সফল! এবার ভিডিওটি আপনার চ্যাটে পাঠানো হচ্ছে... 📤")

        # চ্যাটে ভিডিও সেন্ড করা
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file, 
                caption="🎉 আপনার কাঙ্ক্ষিত ভিডিওটি রেডি! উপভোগ করুন। 🔥\n\n🤖 Powered by Render Free Tier"
            )

        # সার্ভার পরিষ্কার করা
        if os.path.exists(filename):
            os.remove(filename)
            
        await status_message.delete() # ডামি মেসেজটি মুছে দেওয়া

    except Exception as e:
        print(f"Error: {str(e)}")
        await status_message.edit_text(
            "❌ দুঃখিত! ভিডিওটি ডাউনলোড করা সম্ভব হয়নি।\n\n"
            "💡 **সম্ভাব্য কারণ:**\n"
            "১. লিঙ্কটি ভুল হতে পারে। 🧩\n"
            "২. ভিডিওটির সাইজ ৫০ মেগাবাইটের বেশি। 🛑"
        )
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

def main():
    # ---- Python 3.14 Event Loop Fix ----
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN missing!")
        return

    # Flask সার্ভার চালু করা
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    print("Bot is starting with new Emoji UI...")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
