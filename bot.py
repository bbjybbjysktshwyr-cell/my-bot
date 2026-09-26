import os
import asyncio
import subprocess
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

TOKEN = "8618789887:AAGKxnDN6a0ulOS9aLyB1HnuNygukFsIVHs"
ADMIN_ID = 6697426766
API_URL = "http://127.0.0.1:2233/delta"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# تشغيل السيرفر تلقائياً في الخلفية عند بدء تشغيل البوت
server_process = None

def start_local_server():
    global server_process
    if server_process is None:
        # تشغيل سيرفر بايثون على البورت 2233
        server_process = subprocess.Popen(["python", "server.py", "--port", "2233"])
        print("🚀 تم تشغيل سيرفر دلتا المحلي تلقائياً في الخلفية...")

def get_main_menu(is_admin=False):
    keyboard = [
        [InlineKeyboardButton(text="⚡️ تجاوز رابط دلتا", callback_data="bypass_link")],
        [InlineKeyboardButton(text="ℹ️ حول البوت", callback_data="about")]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton(text="⚙️ لوحة التحكم", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(Command("start"))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    is_admin = (user_id == ADMIN_ID)
    await message.answer(
        "مرحباً بك في بوت تخطي مفاتيح Delta 🚀\nأرسل رابط دلتا أو اختر من القائمة أدناه:",
        reply_markup=get_main_menu(is_admin)
    )

@dp.callback_query(F.data == "bypass_link")
async def bypass_prompt(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="back_to_menu")]
    ])
    await callback.message.edit_text(
        "⚡️ **أرسل رابط Delta الآن في المحادثة وسأقوم بجلب المفتاح لك تلقائياً!**",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "about")
async def about_callback(callback: CallbackQuery):
    is_admin = (callback.from_user.id == ADMIN_ID)
    await callback.message.edit_text(
        "هذا البوت يقوم بتشغيل السيرفر المحلي وجلب مفاتيح دلتا بكفاءة عالية.",
        reply_markup=get_main_menu(is_admin)
    )
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_menu(callback: CallbackQuery):
    is_admin = (callback.from_user.id == ADMIN_ID)
    await callback.message.edit_text(
        "مرحباً بك من جديد! اختر ما تحتاجه:",
        reply_markup=get_main_menu(is_admin)
    )
    await callback.answer()

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_user_links(message: Message):
    text = message.text.strip()
    if "http" in text:
        processing_msg = await message.answer("⏳ جاري التواصل مع السيرفر وتخطي الرابط (قد يستغرق بضع ثوانٍ)...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, params={"url": text}, timeout=60) as response:
                    if response.status == 200:
                        data = await response.json()
                        key = data.get("key")
                        error = data.get("error")
                        times = data.get("times")
                        cached = data.get("cached", False)
                        
                        if key:
                            cache_text = " (من التخزين المؤقت ⚡️)" if cached else f" (الوقت: {times})"
                            await processing_msg.edit_text(
                                f"🎉 **تم بنجاح استخراج المفتاح!**{cache_text}\n\n`{key}`",
                                parse_mode="Markdown"
                            )
                        else:
                            await processing_msg.edit_xt(f"❌ **فشل التخطي:**\n`{error}`")
                    else:
                        await processing_msg.edit_text(f"❌ حدث خطأ في استجابة السيرفر (كود: {response.status})")
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء الاتصال بالسيرفر المحلي:\n`{str(e)}`")
    else:
        await message.answer("يرجى إرسال رابط صالح يبدأ بـ http.")

async def main():
    start_local_server()
    await asyncio.sleep(2)
    
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 بوت تيليجرام يعمل الآن والسيرفر يعمل معه في الخلفية...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        if server_process:
            server_process.terminate()
