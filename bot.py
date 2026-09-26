import os
import asyncio
import traceback
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# استيراد ملفاتك الداخلية مباشرة لضمان عمل كافة الوظائف
import main as MAIN_ENGINE
import auth_client as AUTH
try:
    import link_generator
except ImportError:
    pass
try:
    import server
except ImportError:
    pass

TOKEN = "8618789887:AAGKxnDN6a0ulOS9aLyB1HnuNygukFsIVHs"
ADMIN_ID = 6697426766

bot = Bot(token=TOKEN)
dp = Dispatcher()

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
        "⚡️ **أرسل رابط Delta الآن في المحادثة وسأقوم بمعالجته عبر ملفات الأداة مباشرة!**",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "about")
async def about_callback(callback: CallbackQuery):
    is_admin = (callback.from_user.id == ADMIN_ID)
    await callback.message.edit_text(
        "هذا البوت يدمج كافة ملفات التجاوز (main, auth_client, link_generator) لاستخراج المفاتيح بكفاءة عالية.",
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
        processing_msg = await message.answer("⏳ جاري معالجة الرابط عبر ملفات الأداة ومحاولة التجاوز...")
        
        try:
            # استخراج التيكت باستخدام وظائف auth_client الحقيقية
            try:
                ticket = AUTH.extract_ticket(text)
            except Exception:
                ticket = None

            if not ticket or len(ticket) < getattr(AUTH, 'MIN_TICKET_LEN', 30):
                ticket = text

            # تشغيل دالة solve_chain من ملف main في خلفية غير متزامنة
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None, 
                MAIN_ENGINE.solve_chain, 
                ticket, 
                False, 
                getattr(MAIN_ENGINE, "MAX_ROUNDS", 3),
                None
            )
            
            # استخراج المفتاح بدقة من النتيجة أياً كان شكلها (Tuple أو Dict أو String)
            key = None
            if isinstance(result, tuple):
                key = result[0]
            elif isinstance(result, dict):
                key = result.get("key") or result.get("token")
            else:
                key = result

            if key and str(key) != "None":
                await processing_msg.edit_text(
                    f"🎉 **تم بنجاح استخراج المفتاح!**\n\n`{key}`",
                    parse_mode="Markdown"
                )
            else:
                await processing_msg.edit_text("❌ **فشل التخطي:**\n`لم يتم العثور على المفتاح أو أن الرابط تالف أو منتهي الصلاحية.`")
                
        except Exception as e:
            traceback.print_exc()
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء معالجة الرابط:\n`{str(e)}`")
    else:
        await message.answer("يرجى إرسال رابط صالح يبدأ بـ http.")

async def main():
    try:
        AUTH.start_version_watcher()
    except Exception:
        pass

    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 بوت تيليجرام يعمل الآن ومستعد لاستدعاء كافة ملفات التجاوز الداخلية...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("تم إيقاف البوت.")
