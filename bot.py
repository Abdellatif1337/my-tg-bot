import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# التوكن ديالك
TOKEN = '8215464725:AAFS_qFHuOtEFDfOPhFdbD1GUdMiCgmAsZg'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً! صيفط رابط يوتيوب وغادي نحاول ننزلو ليك.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    if not ("youtube.com" in url or "youtu.be" in url):
        await update.message.reply_text("الرابط غير صحيح ⚠️")
        return
    await update.message.reply_text("جاري التحميل... ⏳")
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'downloads/{chat_id}_%(id)s.%(ext)s',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        await update.message.reply_text("تم التحميل! جاري الإرسال... 📤")
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption="ها هو الفيديو 🚀")
        os.remove(filename)
    except Exception as e:
        logging.error(e)
        await update.message.reply_text(f"مشكل: {str(e)}")

def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.run_polling()

if __name__ == '__main__':
    main()
