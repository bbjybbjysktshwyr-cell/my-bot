import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# استيراد الوظائف من الملفات الموجودة عندك في المشروع
try:
    from core import bypass_link_core  # افتراض دالة المعالجة الأساسية في core.py
except ImportError:
    bypass_link_core = None

TOKEN = "8975068395:AAFD_ups14mfcBbopumiZt7NCxzXaxmwC7s"
ADMIN_ID = 6697426766

bot = Bot(token=TOKEN)
dp = Dispatcher()

# أسماء الأزرار (قابلة للتغيير من لوحة التحكم مثل ما اتفقنا)
BUTTON_TEXTS = {
    "supported_links": "🔗 الروابط المدعومة (Linkvertise)",
    "bypass_link": "⚡️ تجاوز رابط",
    "about": "ℹ️ حول البوت",
    "admin_panel": "⚙️ لوحة تحكم المدير",
    "back_to_menu": "🔙 رجوع للقائمة"
}

def get_main_menu(is_admin=False):
    keyboard = [
        [InlineKeyboardButton(text=BUTTON_TEXTS["supported_links"], callback_data="supported_links")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["bypass_link"], callback_data="bypass_link")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["about"], callback_data="about")]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton(text=BUTTON_TEXTS["admin_panel"], callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(Command("start"))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    is_admin = (user_id == ADMIN_ID)
    await message.answer(
        "مرحباً بك في بوت تخطي الروابط (معتمد على ملفات المشروع المحلية).\nاختر ما تحتاجه من القائمة أدناه:",
        reply_markup=get_main_menu(is_admin)
    )

@dp.callback_query(F.data == "bypass_link")
async def bypass_prompt(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXTS["back_to_menu"], callback_data="back_to_menu")]
    ])
    await callback.message.edit_text(
        "⚡️ **أرسل رابط Linkvertise الآن في المحادثة وسأقوم بتخطيه باستخدام ملفات المشروع!**",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "supported_links")
async def supported_links_callback(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXTS["back_to_menu"], callback_data="back_to_menu")]
    ])
    await callback.message.edit_text(
        "📋 **الخدمات المدعومة حالياً:**\n\n• روابط `Linkvertise` باستخدام ملفات السكربت المحلي.\n\n💡 *أرسل الرابط وسأتولى الباقي!*",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "about")
async def about_callback(callback: CallbackQuery):
    is_admin = (callback.from_user.id == ADMIN_ID)
    await callback.message.edit_text(
        "هذا البوت مبرمج ليعمل مباشرة مع ملفات السكربت المحلي الخاصة بك.",
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

# استقبال الروابط ومعالجتها عبر ملفات المشروع
@dp.message(F.text & ~F.text.startswith("/"))
async def handle_user_links(message: Message):
    text = message.text.strip()
    if text.startswith("http"):
        processing_msg = await message.answer("⏳ جاري معالجة الرابط عبر ملفات المشروع المحلية...")
        
        try:
            # هنا نقوم باستدعاء دالة التخطي من ملفاتك (إذا كانت الدالة موجودة في core.py)
            if bypass_link_core:
                # محاولة تمرير الرابط للدالة المحلية
                result = bypass_link_core(text) # أو await إذا كانت دالة غير متزامنة async
            else:
                # طريقة بديلة في حال احتجنا لتشغيل ملف cli أو استدعاء النظام الداخلي
                import subprocess
                process = subprocess.Popen(
                    ["python", "cli.py", text],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate()
                result = stdout if process.returncode == 0 else f"خطأ: {stderr}"

            await processing_msg.edit_text(f"🎉 **النتيجة:**\n\n`{result}`")
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء التشغيل:\n`{str(e)}`")
    else:
        await message.answer("يرجى إرسال رابط صالح تبدأ بـ http لتخطيه.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 البوت يعمل الآن مع ملفات المشروع المحلية...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
