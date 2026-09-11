import os
import re
import html
import asyncio
import cloudscraper
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

TOKEN = "8512256766:AAGmFS1y0JnmACIb42bDGREbZ-gcfPliev4"

# الآيدي الخاص بك كمدير للبوت
ADMIN_ID = 6697426766

bot = Bot(token=TOKEN)
dp = Dispatcher()

# قاعدة بيانات محلية قابلة للتحديث
LINK_DATABASE = {
    "https://boostylink.com/EbnbkEHt": "https://link-center.net/2603650/nY1W5wuviUhS",
    "https://boostylink.com/nYsaet7F": "https://bstshrt.com/u/vc691v"
}

def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 الروابط المدعومة", callback_data="supported_links")],
        [InlineKeyboardButton(text="⚡️ تجاوز رابط", callback_data="bypass_link")],
        [InlineKeyboardButton(text="ℹ️ حول البوت", callback_data="about")]
    ])

def get_copy_keyboard(target_url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 نسخ الرابط", url=target_url)],
        [InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="back_to_menu")]
    ])

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        "مرحباً بك في بوت استختراج وتجاوز الروابط. اختر ما تحتاجه من القائمة أدناه:",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "about")
async def about_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "هذا البوت مخصص لاستخراج الروابط الأصلية وتجاوز صفحات الاختصار بدقة وسرعة.",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "bypass_link")
async def bypass_prompt(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="back_to_menu")]
    ])
    await callback.message.edit_text(
        "⚡️ **أرسل الرابط المختصر الآن في المحادثة مباشرة وسأقوم باستخراج هدفه النهائي لك!**",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "supported_links")
async def supported_links_callback(callback: CallbackQuery):
    supported_text = (
        "📋 **الروابط والخدمات المدعومة في البوت:**\n\n"
        "• `https://boostylink.com`\n\n"
        "💡 *أرسل أي رابط مدعوم وسأستخرج هدفه فوراً!*"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="back_to_menu")]
    ])
    await callback.message.edit_text(supported_text, reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "مرحباً بك من جديد! اختر ما تحتاجه من القائمة أدناه:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

# أمر الإضافة المباشر والسريع لك وحدك
@dp.message(Command("add"))
async def add_new_link(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        parts = message.text.replace("/add", "").strip().split("|")
        if len(parts) == 2:
            short_link = parts[0].strip()
            target_link = parts[1].strip()
            
            LINK_DATABASE[short_link] = target_link
            await message.answer(
                f"✅ **تمت إضافة الرابط بنجاح للقاعدة!**\n\n"
                f"🔗 الاختصار: `{short_link}`\n"
                f"🎯 الهدف: `{target_link}`"
            )
        else:
            await message.answer(
                "⚠️ صيغة غير صحيحة!\n"
                "استخدم الأمر بالشكل التالي:\n"
                "`/add الرابط_المختصر | الرابط_النهائي`"
            )
    except Exception as e:
        await message.answer(f"❌ حدث خطأ أثناء الإضافة: `{str(e)}`")

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_links(message: Message):
    text = message.text.strip()
    if text and text.startswith("http"):
        processing_msg = await message.answer("⏳ جاري فحص الرابط واستخراج الهدف...")
        
        # 1. التحقق من قاعدة البيانات
        if text in LINK_DATABASE:
            clean_url = LINK_DATABASE[text]
            result_text = (
                f"🎉 **تم استخراج الرابط بنجاح!**\n\n"
                f"🔗 {clean_url}\n\n"
                f"🔔 اضغط على زر النسخ أدناه:"
            )
            await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
            return

        # 2. التتبع التلقائي
        extracted_url = text
        try:
            scraper = cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'android', 'desktop': False}
            )
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
                "Referer": text
            }
            
            response = scraper.get(text, headers=headers, allow_redirects=False, timeout=10)
            if response.status_code in [301, 302, 303, 307, 308]:
                redirect_target = response.headers.get("Location")
                if redirect_target:
                    extracted_url = redirect_target

            clean_url = html.unescape(extracted_url).strip()
            clean_url = re.sub(r'\s+', '', clean_url)

            if clean_url == text:
                await processing_msg.edit_text(
                    "⚠️ هذا الرابط غير موجود في القاعدة المحلية.\n\n"
                    "إذا كنت تريد إضافته، استخدم الأمر:\n"
                    "`/add الرابط_المختصر | الرابط_النهائي`",
                    reply_markup=get_copy_keyboard(text)
                )
            else:
                result_text = (
                    f"🎉 **تم استخراج الرابط بنجاح!**\n\n"
                    f"🔗 {clean_url}\n\n"
                    f"🔔 اضغط على زر النسخ أدناه:"
                )
                await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
                
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء المعالجة:\n`{str(e)}`")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 البوت يعمل الآن بكفاءة عالية...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
