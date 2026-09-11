import os
import re
import html
import asyncio
import cloudscraper
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

TOKEN = "8512256766:AAGmFS1y0JnmACIb42bDGREbZ-gcfPliev4"

# تم ضبط الآيدي الخاص بك كمدير للبوت
ADMIN_ID = 6697426766

bot = Bot(token=TOKEN)
dp = Dispatcher()

# قاعدة بيانات محلية قابلة للتحديث
LINK_DATABASE = {
    "https://boostylink.com/EbnbkEHt": "https://link-center.net/2603650/nY1W5wuviUhS",
    "https://boostylink.com/nYsaet7F": "https://bstshrt.com/u/vc691v"
}

# تخزين مؤقت لآخر رابط أرسله المستخدم لسهولة إضافته بضغطة زر
PENDING_LINKS = {}

def get_main_menu(is_admin=False):
    keyboard = [
        [InlineKeyboardButton(text="🔗 الروابط المدعومة", callback_data="supported_links")],
        [InlineKeyboardButton(text="ℹ️ حول البوت", callback_data="about")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_copy_keyboard(target_url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 نسخ الرابط", url=target_url)],
        [InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="back_to_menu")]
    ])

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        "مرحباً بك! أرسل رابط الاختصار وسأقوم باستخراج الرابط:",
        reply_markup=get_main_menu(message.from_user.id == ADMIN_ID)
    )

@dp.callback_query(F.data == "about")
async def about_callback(callback: CallbackQuery):
    is_admin = callback.from_user.id == ADMIN_ID
    await callback.message.edit_text(
        "هذا البوت مخصص لاستخراج الروابط الأصلية وتجاوز صفحات الاختصار بدقة وسرعة.",
        reply_markup=get_main_menu(is_admin)
    )
    await callback.answer()

@dp.callback_query(F.data == "supported_links")
async def supported_links_callback(callback: CallbackQuery):
    links_list = "\n".join([f"• `{k}`" for k in LINK_DATABASE.keys()]) if LINK_DATABASE else "لا توجد روابط مخزنة حالياً."
    supported_text = (
        f"📋 **الروابط والخدمات المدعومة حالياً:**\n\n"
        f"{links_list}\n\n"
        f"💡 *أرسل أي رابط من القائمة وسأستخرج هدفه فوراً!*"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="back_to_menu")]
    ])
    await callback.message.edit_text(supported_text, reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_menu(callback: CallbackQuery):
    is_admin = callback.from_user.id == ADMIN_ID
    await callback.message.edit_text("أرسل الرابط المطلوب فحصه:", reply_markup=get_main_menu(is_admin))
    await callback.answer()

# زر تفاعلي يظهر للمدير فقط عند إرسال رابط غير موجود لإضافته بضغطة زر
@dp.callback_query(F.data.startswith("add_quick_"))
async def quick_add_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ هذا الزر لمدير البوت فقط!", show_alert=True)
        return
    
    short_link = PENDING_LINKS.get(callback.from_user.id)
    if short_link:
        await callback.message.edit_text(
            f"✍️ يرجى إرسال الرابط النهائي (الهدف) الخاص بهذا الرابط:\n`{short_link}`\n\n"
            f"بصيغة:\n`/add الهدف` أو قم بإرساله مباشرة كـ رد (Reply) على رسالة البوت."
        )
    else:
        await callback.message.edit_text("⚠️ انتهت صلاحية الرابط، أرسله من جديد.")
    await callback.answer()

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_links(message: Message):
    text = message.text.strip()
    if text and text.startswith("http"):
        processing_msg = await message.answer("⏳ جاري فحص الرابط...")
        
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

        # 2. محاولة التتبع
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
                # إذا كان المرسل هو أنت (المدير)، سنعرض لك زر "إضافة للقاعدة" فوراً
                if message.from_user.id == ADMIN_ID:
                    PENDING_LINKS[message.from_user.id] = text
                    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="➕ إضافة هذا الرابط للقاعدة", callback_data="add_quick_link")],
                        [InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="back_to_menu")]
                    ])
                    await processing_msg.edit_text(
                        "⚠️ هذا الرابط غير موجود في قاعدة بيانات البوت.\nبصفتك المدير، يمكنك إضافته بضغطة زر:",
                        reply_markup=admin_keyboard
                    )
                else:
                    await processing_msg.edit_text(
                        "⚠️ عذراً، هذا الرابط غير مدعوم حالياً أو يتطلب تفاعلاً بشرياً.",
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
