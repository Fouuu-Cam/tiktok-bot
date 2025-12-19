# tiktok_bot.py
import os
import asyncio
import re
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN")

TIKTOK_PATTERN = re.compile(
    r'(https?://)?(www\.)?(tiktok\.com|vm\.tiktok\.com|vt\.tiktok\.com)/[@\w./]+'
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "👋 Send me a TikTok link and I'll download the video for you!"
    )

async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle TikTok video downloads"""
    message_text = update.message.text
    
    # Check if it's a command (skip processing)
    if message_text.startswith('/'):
        return
    
    # Validate TikTok URL
    match = TIKTOK_PATTERN.search(message_text)
    if not match:
        await update.message.reply_text("❌ Please send a valid TikTok link.")
        return
    
    url = match.group(0)
    status_msg = await update.message.reply_text("⬇️ Downloading...")
    
    # Unique filename
    filename = f"video_{update.message.chat_id}_{update.message.message_id}.mp4"
    
    ydl_opts = {
        'outtmpl': filename,
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        # Download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Send video to user
        await status_msg.edit_text("📤 Sending video...")
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video)
        
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Download failed: {str(e)}")
    
    finally:
        # Clean up file
        if os.path.exists(filename):
            os.remove(filename)

def main():
    """Start the bot"""
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set!")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_tiktok))
    
    print("🤖 Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
