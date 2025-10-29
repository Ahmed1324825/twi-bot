import os
import random
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import json
import asyncio
import time

# اسم ملف الكاش
CACHE_FILE = 'cache.json'

# تحميل الكاش
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

# حفظ الكاش
def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=4)

# إنشاء اسم ملف عشوائي
def random_filename():
    return f"{random.randint(100000, 999999)}.mp4"

# تحميل الفيديوهات
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if not text:
        await update.message.reply_text('من فضلك، ابعت لينك فيديو من تويتر أو تيك توك أو يوتيوب.')
        return

    cache = load_cache()
    user = update.message.from_user
    user_name = user.username or user.first_name or "Unknown"
    filename = random_filename()

    await update.message.reply_text('جاري التحميل... ⏳')

    try:
        ydl_opts = {'outtmpl': filename, 'format': 'best'}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(text, download=True)

        # حساب الحجم
        file_size = info.get("filesize", 0) or info.get("filesize_approx", 0)
        if file_size and file_size > 400 * 1024 * 1024:
            os.remove(filename)
            await update.message.reply_text('❌ الفيديو أكبر من 400 ميجا، مش هينفع أرفعه.')
            return

        # حفظ بيانات الكاش
        cache[text] = {
            'file': filename,
            'count': cache.get(text, {}).get('count', 0) + 1,
            'user': user_name
        }
        save_cache(cache)

        await update.message.reply_text('🛫 جاري رفع الفيديو...')
        with open(filename, 'rb') as video_file:
            await update.message.reply_document(document=video_file)

    except asyncio.TimeoutError:
        await update.message.reply_text('❗ حصل تايم آوت أثناء رفع الفيديو.')
    except Exception as e:
        await update.message.reply_text(f'❌ حصل خطأ أثناء التحميل أو الإرسال: {str(e)}')
    finally:
        # حذف الملف بعد الإرسال
        if os.path.exists(filename):
            os.remove(filename)

# تشغيل البوت
app = ApplicationBuilder().token("7524924745:AAH0ub_WRc1lOQuhzpanZ1qGD42NwTfS5o8").read_timeout(1200).write_timeout(1200).build()
app.add_handler(MessageHandler(filters.TEXT, download_video))

if __name__ == "__main__":
    while True:
        try:
            print("🚀 Bot is running...")
            app.run_polling()
        except Exception as e:
            print(f"❌ Bot crashed with error: {e}")
            time.sleep(5)
