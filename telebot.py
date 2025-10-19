import os
import random
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import re
import json
import asyncio

# اسم ملف الكاش
CACHE_FILE = 'cache.json'

# إذا كان الملف موجود بالفعل، نقرأ الكاش منه
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

# حفظ الكاش في الملف
def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=4)

# إنشاء اسم ملف عشوائي
def random_filename():
    return f"{random.randint(100000, 999999)}.mp4"

# التعامل مع الفيديوهات
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # تحميل النص من الرسالة
    text = update.message.text

    # لو مافيش لينك، يرد على المستخدم
    if not text:
        await update.message.reply_text('من فضلك، ابعت لينك فيديو من تويتر أو تيك توك أو يوتيوب.')
        return

    # تحميل الكاش الموجود
    cache = load_cache()

    # ✅ لو اللينك موجود في الكاش
    if text in cache and os.path.exists(cache[text]['file']):
        # تحديث عدد المرات
        cache[text]['count'] += 1
        save_cache(cache)
        await update.message.reply_text('الفيديو موجود، جاري الإرسال... 📤')

        try:
            with open(cache[text]['file'], 'rb') as video_file:
                await update.message.reply_document(document=video_file)

        except Exception as e:
            await update.message.reply_text(f'حصل خطأ أثناء الإرسال: {str(e)}')

        return  # خلصنا خلاص

    filename = random_filename()

    await update.message.reply_text('جاري التحميل... ⏳')

    try:
        # لو مش عايز تستخدم yt_dlp، ممكن تضيف هنا أي طريقة تحميل فيديوهات تانية
        ydl_opts = {
            'outtmpl': filename,
            'format': 'best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([text])

        # 📝 سجل اللينك والفايل في الكاش مع عدد المرات
        cache[text] = {'file': filename, 'count': 1}

        # حفظ الكاش في الملف
        save_cache(cache)

        await update.message.reply_text('🛫 جاري رفع الفيديو...')

        with open(filename, 'rb') as video_file:
            await update.message.reply_document(document=video_file)

    except asyncio.TimeoutError:
        await update.message.reply_text('❗ حصل تايم آوت أثناء رفع الفيديو.')

    except Exception as e:
        await update.message.reply_text(f'حصل خطأ: {str(e)}')

    finally:
        pass  # ما تمسحش الملف دلوقتي عشان الكاش

# بناء التطبيق وتحديد الـ token
app = ApplicationBuilder().token("7524924745:AAH0ub_WRc1lOQuhzpanZ1qGD42NwTfS5o8").read_timeout(1200).write_timeout(1200).build()

# إضافة الهايدلرز للبوت
app.add_handler(MessageHandler(filters.TEXT, download_video))

# تشغيل البوت
app.run_polling()
