import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# إعدادات الـ Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- حط التوكن ديالك هنا ---
TOKEN = '8215464725:AAFS_qFHuOtEFDfOPhFdbD1GUdMiCgmAsZg'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! صيفط ليا رابط فيديو من يوتيوب، وغادي نحاول ننزلو ليك.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    if not ("youtube.com" in url or "youtu.be" in url):
        await update.message.reply_text("عافاك صيفط رابط صحيح ديال يوتيوب. ⚠️")
        return

    await update.message.reply_text("جاري المحميل... تسنى شوية ⏳")

    # إعدادات معدلة لتجاوز الحظر
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'downloads/{chat_id}_%(id)s.%(ext)s',
        'noplaylist': True,
        # هاد السطر كيوهم يوتيوب أننا متصفح حقيقي
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await update.message.reply_text("تم التحميل! جاري الإرسال... 📤")
        
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption="ها هو الفيديو ديالك! 🚀",
                read_timeout=300,
                write_timeout=300
            )

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        logging.error(e)
        error_msg = str(e)
        if "Sign in to confirm" in error_msg:
            await update.message.reply_text("يوتيوب حجبات السيرفر ❌ خاص ضروري نزيدو ملف Cookies باش يخدم.")
        else:
            await update.message.reply_text(f"وقع مشكل: {error_msg}")

def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("البوت خدام... جرب الروابط دابا!")
    app.run_polling()

if __name__ == '__main__':
    main()
