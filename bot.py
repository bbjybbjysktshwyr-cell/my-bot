
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

# قاعدة بيانات محلية للروابط
LINK_DATABASE = {
    "https://boostylink.com/EbnbkEHt": "https://link-center.net/2603650/nY1W5wuviUhS",
    "https://boostylink.com/nYsaet7F": "https://bstshrt.com/u/vc691v"
}

# تخزين المستخدمين للإذاعة
USERS_SET = set()
ADMIN_STATE = {}

def get_main_menu(is_admin=False):
    keyboard = [
        [InlineKeyboardButton(text="🔗 الروابط المدعومة", callback_data="supported_links")],
        [InlineKeyboardButton(text="⚡️ تجاوز رابط", callback_data="bypass_link")],
        [InlineKeyboardButton(text="ℹ️ حول البوت", callback_data="about")]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton(text="⚙️ لوحة تحكم المدير", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 إرسال إذاعة للكل", callback_data="start_broadcast")],
        [InlineKeyboardButton(text="🔙 عودة للقائمة الرئيسية", callback_data="back_to_menu")]
    ])

def get_copy_keyboard(target_url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 نسخ الرابط", url=target_url)],
        [InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="back_to_menu")]
    ])

@dp.message(Command("start"))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    USERS_SET.add(user_id)
    is_admin = (user_id == ADMIN_ID)
    await message.answer(
        "مرحباً بك في بوت استخراج وتجاوز الروابط. اختر ما تحتاجه من القائمة أدناه:",
        reply_markup=get_main_menu(is_admin)
    )

@dp.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("للمدير فقط!", show_alert=True)
        return
    await callback.message.edit_text(
        "⚙️ **لوحة تحكم المدير:**\n\nتحكم في إعدادات البوت والخدمات من الأزرار أدناه:",
        reply_markup=get_admin_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "start_broadcast")
async def start_broadcast_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    ADMIN_STATE[callback.from_user.id] = "waiting_broadcast"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="admin_panel")]
    ])
    await callback.message.edit_text(
        "📢 **وضع الإذاعة نشط:**\n\nأرسل الآن الرسالة التي تريد إذاعتها لجميع المستخدمين (صورة، نص، أو فيديو):",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "about")
async def about_callback(callback: CallbackQuery):
    is_admin = (callback.from_user.id == ADMIN_ID)
    await callback.message.edit_text(
        "هذا البوت مخصص لاستخراج الروابط الأصلية وتجاوز صفحات الاختصار بدقة وسرعة.",
        reply_markup=get_main_menu(is_admin)
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
    ADMIN_STATE.pop(callback.from_user.id, None)
    is_admin = (callback.from_user.id == ADMIN_ID)
    await callback.message.edit_text(
        "مرحباً بك من جديد! اختر ما تحتاجه من القائمة أدناه:",
        reply_markup=get_main_menu(is_admin)
    )
    await callback.answer()

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
                "⚠️ صيغة غير صحيحة!\nاستخدم الأمر بالشكل التالي:\n`/add الرابط_المختصر | الرابط_النهائي`"
            )
    except Exception as e:
        await message.answer(f"❌ حدث خطأ: `{str(e)}`")

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_messages(message: Message):
    user_id = message.from_user.id
    
    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id) == "waiting_broadcast":
        ADMIN_STATE.pop(user_id, None)
        sent_count = 0
        fail_count = 0
        status_msg = await message.answer("⏳ جاري بدء الإذاعة لجميع المستخدمين...")
        
        for uid in USERS_SET:
            try:
                await message.send_copy(chat_id=uid)
                sent_count += 1
                await asyncio.sleep(0.05)
            except Exception:
                fail_count += 1
                
        await status_msg.edit_text(
            f"✅ **تم إكمال الإذاعة بنجاح!**\n\n"
            f"📤 تم الإرسال إلى: `{sent_count}` مستخدماً\n"
            f"❌ فشل الإرسال لـ: `{fail_count}` مستخدماً"
        )
        return

    text = message.text.strip()
    if text and text.startswith("http"):
        processing_msg = await message.answer("⏳ جاري فحص الرابط واستخراج الهدف...")
        
        if text in LINK_DATABASE:
            clean_url = LINK_DATABASE[text]
            result_text = (
                f"🎉 **تم استخراج الرابط بنجاح!**\n\n"
                f"🔗 {clean_url}\n\n"
                f"🔔 اضغط على زر النسخ أدناه:"
            )
            await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
            return

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
    print("🤖 البوت يعمل الآن بكفاءة عالية وبدون تعليق...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
