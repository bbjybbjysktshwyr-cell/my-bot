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

bot = Bot(token=TOKEN)
dp = Dispatcher()

# قاعدة بيانات محلية للروابط
LINK_DATABASE = {
    "https://boostylink.com/EbnbkEHt": "https://link-center.net/2603650/nY1W5wuviUhS",
    "https://boostylink.com/nYsaet7F": "https://bstshrt.com/u/vc691v"
}

# 🎛️ أسماء الأزرار الأساسية (قابلة للتغيير)
BUTTON_TEXTS = {
    "supported_links": "🔗 الروابط المدعومة",
    "bypass_link": "⚡️ تجاوز رابط",
    "about": "ℹ️ حول البوت",
    "admin_panel": "⚙️ لوحة تحكم المدير",
    "broadcast": "💬 إرسال إذاعة للكل",
    "add_custom_btn": "➕ إضافة زر جديد للقائمة",
    "change_names": "✏️ تغيير أسماء الأزرار",
    "maintenance": "🛠️ تفعيل وضع الصيانة",
    "maintenance_off": "🟢 إلغاء وضع الصيانة",
    "back_to_menu": "🔙 رجوع للقائمة",
    "copy_link": "📋 نسخ الرابط",
    "support": "👨‍💻 تواصل مع الدعم الفني",
    "cancel": "❌ إلغاء"
}

# قائمة الأزرار الإضافية التي يضيفها المدير (تخزين مؤقت)
# الصيغة: {"اسم_الزر": "الرابط_أو_المحتوى"}
CUSTOM_BUTTONS = {}

USERS_SET = set()
ADMIN_STATE = {}
MAINTENANCE_MODE = False

def get_main_menu(is_admin=False):
    keyboard = [
        [InlineKeyboardButton(text=BUTTON_TEXTS["supported_links"], callback_data="supported_links")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["bypass_link"], callback_data="bypass_link")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["about"], callback_data="about")]
    ]
    
    # إضافة الأزرار المخصصة التي أضافها المدير للقائمة الرئيسية
    for btn_name, btn_url in CUSTOM_BUTTONS.items():
        if btn_url.startswith("http"):
            keyboard.append([InlineKeyboardButton(text=btn_name, url=btn_url)])
        else:
            keyboard.append([InlineKeyboardButton(text=btn_name, callback_data=f"custom_cb_{btn_name}")])

    if is_admin:
        keyboard.append([InlineKeyboardButton(text=BUTTON_TEXTS["admin_panel"], callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_menu():
    m_text = BUTTON_TEXTS["maintenance_off"] if MAINTENANCE_MODE else BUTTON_TEXTS["maintenance"]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXTS["broadcast"], callback_data="start_broadcast")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["add_custom_btn"], callback_data="start_add_btn")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["change_names"], callback_data="open_change_names")],
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
    status_text = "🟢 (يعمل بشكل طبيعي)" if not MAINTENANCE_MODE else "🔴 (وضع الصيانة مفعل)"
    await callback.message.edit_text(
        f"⚙️ **لوحة تحكم المدير:**\n\nحالة البوت: {status_text}\n\nتحكم في إعدادات البوت من الأزرار أدناه:",
        reply_markup=get_admin_menu()
    )
    await callback.answer()

# بدء إضافة زر جديد
@dp.callback_query(F.data == "start_add_btn")
async def start_add_btn(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    ADMIN_STATE[callback.from_user.id] = "waiting_btn_name"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXTS["cancel"], callback_data="admin_panel")]
    ])
    await callback.message.edit_text(
        "➕ **إضافة زر جديد للقائمة الرئيسية:**\n\nأرسل الآن **اسم الزر** الذي تريده (مثلاً: 📢 قناتنا على تيليجرام):",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "open_change_names")
async def open_change_names(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="تغيير زر: الروابط المدعومة", callback_data="edit_supported_links")],
        [InlineKeyboardButton(text="تغيير زر: تجاوز رابط", callback_data="edit_bypass_link")],
        [InlineKeyboardButton(text="تغيير زر: حول البوت", callback_data="edit_about")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["back_to_menu"], callback_data="admin_panel")]
    ])
    await callback.message.edit_text(
        "✏️ **اختر الزر الأساسي الذي تريد تغيير اسمه:**",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_"))
async def start_editing_button(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    btn_key = callback.data.replace("edit_", "")
    ADMIN_STATE[callback.from_user.id] = f"changing_btn_{btn_key}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXTS["cancel"], callback_data="open_change_names")]
    ])
    await callback.message.edit_text(
        f"✍️ **أرسل الاسم الجديد لهذا الزر في المحادثة:**",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "toggle_maintenance")
async def toggle_maintenance_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    global MAINTENANCE_MODE
    MAINTENANCE_MODE = not MAINTENANCE_MODE
    state_msg = "تم تفعيل وضع الصيانة 🔴" if MAINTENANCE_MODE else "تم إيقاف وضع الصيانة 🟢"
    await callback.answer(state_msg, show_alert=True)
    
    status_text = "🟢 (يعمل بشكل طبيعي)" if not MAINTENANCE_MODE else "🔴 (وضع الصيانة مفعل)"
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
        "📢 **وضع الإذاعة نشط:**\n\nأرسل الآن الرسالة التي تريد إرسالها لجميع المستخدمين:",
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

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_messages(message: Message):
    user_id = message.from_user.id
    
    # 1. استقبال اسم الزر الجديد
    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id) == "waiting_btn_name":
        btn_name = message.text.strip()
        ADMIN_STATE[user_id] = f"waiting_btn_url_{btn_name}"
        await message.answer(
            f"✅ ممتاز! اسم الزر: `{btn_name}`\n\n🔗 الآن أرسل **الرابط** الذي سيفتح عندما يضغط المستخدم على هذا الزر (مثلاً رابط قناتك `https://t.me/...`):"
        )
        return

    # 2. استقبال رابط الزر الجديد وحفظه
    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id, "").startswith("waiting_btn_url_"):
        btn_name = ADMIN_STATE.pop(user_id).replace("waiting_btn_url_", "")
        btn_url = message.text.strip()
        CUSTOM_BUTTONS[btn_name] = btn_url
        
        await message.answer(
            f"🎉 **تمت إضافة الزر الجديد بنجاح إلى القائمة الرئيسية!**\n\n🏷️ الاسم: `{btn_name}`\n🔗 الرابط: `{btn_url}`",
            reply_markup=get_admin_menu()
        )
        return

    # 3. تغيير اسم الزر الأساسي
    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id, "").startswith("changing_btn_"):
        btn_key = ADMIN_STATE.pop(user_id).replace("changing_btn_", "")
        new_name = message.text.strip()
        BUTTON_TEXTS[btn_key] = new_name
        
        await message.answer(
            f"✅ **تم تحديث اسم الزر بنجاح إلى:** `{new_name}`",
            reply_markup=get_admin_menu()
        )
        return

    # 4. وضع الصيانة
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=BUTTON_TEXTS["support"], url=SUPPORT_USER_URL)]
        ])
        await message.answer(
            "🛠️ **البوت متوقف حالياً للصيانة والتحديث.**\n\nيرجى المحاولة لاحقاً أو التواصل مع الدعم الفني.",
            reply_markup=keyboard
        )
        return

    # 5. نظام الإذاعة
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

    # 6. فحص الروابط واستخراجها
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
