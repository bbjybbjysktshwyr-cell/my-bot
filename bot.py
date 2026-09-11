import os
import re
import html
import asyncio
import cloudscraper
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

TOKEN = "8966597040:AAFRs5K7XJD5bXToG4m3IqVSHy6gw7BgSDQ"

# الآيدي الخاص بك كمدير للبوت
ADMIN_ID = 6697426766

# يوزر تيليجرام الخاص بك للدعم الفني
SUPPORT_USER_URL = "https://t.me/AL_shz1"

# 🎛️ يمكنك تغيير أسماء الأزرار والنصوص من هنا بكل سهولة في أي وقت:
BUTTON_TEXTS = {
    "supported_links": "🔗 الروابط المدعومة",
    "bypass_link": "⚡️ تجاوز رابط",
    "about": "ℹ️ حول البوت",
    "admin_panel": "⚙️ لوحة تحكم المدير",
    "broadcast": "💬 إرسال إذاعة للكل",
    "maintenance": "🛠️ تفعيل وضع الصيانة",
    "maintenance_off": "🟢 إلغاء وضع الصيانة",
    "back_to_menu": "🔙 رجوع للقائمة",
    "copy_link": "📋 نسخ الرابط",
    "support": "👨‍💻 تواصل مع الدعم الفني",
    "cancel": "❌ إلغاء"
}

bot = Bot(token=TOKEN)
dp = Dispatcher()

# قاعدة بيانات محلية للروابط
LINK_DATABASE = {
    "https://boostylink.com/EbnbkEHt": "https://link-center.net/2603650/nY1W5wuviUhS",
    "https://boostylink.com/nYsaet7F": "https://bstshrt.com/u/vc691v"
}

USERS_SET = set()
ADMIN_STATE = {}
MAINTENANCE_MODE = False  # حالة وضع الصيانة (معطلة افتراضياً)

def get_main_menu(is_admin=False):
    keyboard = [
        [InlineKeyboardButton(text=BUTTON_TEXTS["supported_links"], callback_data="supported_links")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["bypass_link"], callback_data="bypass_link")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["about"], callback_data="about")]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton(text=BUTTON_TEXTS["admin_panel"], callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_menu():
    m_text = BUTTON_TEXTS["maintenance_off"] if MAINTENANCE_MODE else BUTTON_TEXTS["maintenance"]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXTS["broadcast"], callback_data="start_broadcast")],
        [InlineKeyboardButton(text=m_text, callback_data="toggle_maintenance")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["back_to_menu"], callback_data="back_to_menu")]
    ])

def get_copy_keyboard(target_url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXTS["copy_link"], url=target_url)],
        [InlineKeyboardButton(text=BUTTON_TEXTS["back_to_menu"], callback_data="back_to_menu")]
    ])

def get_unknown_link_keyboard(target_url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXTS["copy_link"], url=target_url)],
        [InlineKeyboardButton(text=BUTTON_TEXTS["support"], url=SUPPORT_USER_URL)],
        [InlineKeyboardButton(text=BUTTON_TEXTS["back_to_menu"], callback_data="back_to_menu")]
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
    status_text = "🟢 (المصنوع حالياً: يعمل بشكل طبيعي)" if not MAINTENANCE_MODE else "🔴 (المصنوع حالياً: وضع الصيانة مفعل)"
    await callback.message.edit_text(
        f"⚙️ **لوحة تحكم المدير:**\n\nحالة البوت: {status_text}\n\nتحكم في إعدادات البوت من الأزرار أدناه:",
        reply_markup=get_admin_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "toggle_maintenance")
async def toggle_maintenance_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    global MAINTENANCE_MODE
    MAINTENANCE_MODE = not MAINTENANCE_MODE
    state_msg = "تم تفعيل وضع الصيانة بنجاح 🔴" if MAINTENANCE_MODE else "تم إيقاف وضع الصيانة وعمل البوت بشكل طبيعي 🟢"
    await callback.answer(state_msg, show_alert=True)
    
    status_text = "🟢 (الحالة: يعمل بشكل طبيعي)" if not MAINTENANCE_MODE else "🔴 (الحالة: وضع الصيانة مفعل)"
    await callback.message.edit_text(
        f"⚙️ **لوحة تحكم المدير:**\n\nحالة البوت: {status_text}\n\nتحكم في إعدادات البوت من الأزرار أدناه:",
        reply_markup=get_admin_menu()
    )

@dp.callback_query(F.data == "start_broadcast")
async def start_broadcast_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    ADMIN_STATE[callback.from_user.id] = "waiting_broadcast"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXTS["cancel"], callback_data="admin_panel")]
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
        [InlineKeyboardButton(text=BUTTON_TEXTS["back_to_menu"], callback_data="back_to_menu")]
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
        [InlineKeyboardButton(text=BUTTON_TEXTS["back_to_menu"], callback_data="back_to_menu")]
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
    
    # التحقق من وضع الصيانة للمستخدمين العاديين
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=BUTTON_TEXTS["support"], url=SUPPORT_USER_URL)]
        ])
        await message.answer(
            "🛠️ **البوت متوقف حالياً للصيانة والتحديث.**\n\nيرجى المحاولة لاحقاً أو التواصل مع الدعم الفني.",
            reply_markup=keyboard
        )
        return

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
                result_text = (
                    f"🔗 {text}\n\n"
                    f"💡 لمعالجة هذا الرابط، يرجى التواصل مع الدعم الفني:"
                )
                await processing_msg.edit_text(result_text, reply_markup=get_unknown_link_keyboard(text))
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
    print("🤖 البوت يعمل الآن بكفاءة عالية وبدون إعلانات...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
