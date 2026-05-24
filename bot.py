import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# إعدادات الـ Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ⚠️ حط التوكن ديالك هنا ⚠️ ---
TOKEN = '8215464725:AAFS_qFHuOtEFDfOPhFdbD1GUdMiCgmAsZg'

# دالة الترحيب
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! صيفط ليا رابط فيديو من يوتيوب، وغادي ننزلو ليك بأفضل جودة ممكنة.")

# دالة التحميل
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    if not ("youtube.com" in url or "youtu.be" in url):
        await update.message.reply_text("عافاك صيفط رابط صحيح ديال يوتيوب. ⚠️")
        return

    await update.message.reply_text("جاري التحميل... تسنى شوية ⏳")

    # إعدادات التحميل - جودة 'best' كتجمع الصوت والفيديو بلا الحاجة لـ FFmpeg
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'downloads/{chat_id}_%(id)s.%(ext)s',
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await update.message.reply_text("تم التحميل بنجاح! جاري إرسال الفيديو... 📤")
        
        # فتح وإرسال الفيديو (حيدنا timeout باش ما يوقعش خطأ)
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption="ها هو الفيديو ديالك! 🚀"
            )

        # مسح الملف باش ما يعمرش التيليفون
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        logging.error(e)
        await update.message.reply_text(f"وقع مشكل: {str(e)}")

def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # بناء التطبيق
    app = Application.builder().token(TOKEN).build()

    #Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("البوت خدام دابا... صيفط الرابط فـ تيليغرام!")
    app.run_polling()

if __name__ == '__main__':
    main()
