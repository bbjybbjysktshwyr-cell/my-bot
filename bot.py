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
    "manage_buttons": "🎛️ إدارة الأزرار (إضافة/حذف)",
    "maintenance": "🛠️ تفعيل وضع الصيانة",
    "maintenance_off": "🟢 إلغاء وضع الصيانة",
    "back_to_menu": "🔙 رجوع للقائمة",
    "copy_link": "📋 نسخ الرابط",
    "support": "👨‍💻 تواصل مع الدعم الفني",
    "cancel": "❌ إلغاء"
}

# هياكل تخزين الأزرار المخصصة والمتداخلة
# CUSTOM_BUTTONS تخزن الأزرار الرئيسية الإضافية
# SUB_BUTTONS تخزن الأزرار التي بداخل الأزرار (الأزرار المتداخلة)
CUSTOM_BUTTONS = {}  # الصيغة: {"اسم_الزر": {"type": "link/menu", "content": "رابط_أو_نص"}}
SUB_BUTTONS = {}     # الصيغة: {"اسم_الزر_الرئيسي": {"اسم_الزر_الفرعي": "رابط_أو_نص"}}

USERS_SET = set()
ADMIN_STATE = {}
MAINTENANCE_MODE = False

def get_main_menu(is_admin=False):
    keyboard = [
        [InlineKeyboardButton(text=BUTTON_TEXTS["supported_links"], callback_data="supported_links")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["bypass_link"], callback_data="bypass_link")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["about"], callback_data="about")]
    ]
    
    # إضافة الأزرار المخصصة للقائمة الرئيسية
    for btn_name, data in CUSTOM_BUTTONS.items():
        if data["type"] == "link":
            keyboard.append([InlineKeyboardButton(text=btn_name, url=data["content"])])
        else:
            keyboard.append([InlineKeyboardButton(text=btn_name, callback_data=f"sub_menu_{btn_name}")])

    if is_admin:
        keyboard.append([InlineKeyboardButton(text=BUTTON_TEXTS["admin_panel"], callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_menu():
    m_text = BUTTON_TEXTS["maintenance_off"] if MAINTENANCE_MODE else BUTTON_TEXTS["maintenance"]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXTS["broadcast"], callback_data="start_broadcast")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["manage_buttons"], callback_data="manage_buttons_menu")],
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

# قائمة إدارة الأزرار (إضافة أو حذف)
@dp.callback_query(F.data == "manage_buttons_menu")
async def manage_buttons_menu(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ إضافة زر جديد للقائمة الرئيسية", callback_data="start_add_btn")],
        [InlineKeyboardButton(text="➕ إضافة زر بداخل زر (قائمة فرعية)", callback_data="start_add_sub_btn")],
        [InlineKeyboardButton(text="🗑️ حذف زر موجود", callback_data="start_delete_btn")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["back_to_menu"], callback_data="admin_panel")]
    ])
    await callback.message.edit_text(
        "🎛️ **قسم إدارة وصناعة الأزرار:**\n\nاختر ما ترغب به:",
        reply_markup=keyboard
    )
    await callback.answer()

# 1. إضافة زر جديد رئيسي
@dp.callback_query(F.data == "start_add_btn")
async def start_add_btn(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    ADMIN_STATE[callback.from_user.id] = "waiting_btn_name"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXTS["cancel"], callback_data="manage_buttons_menu")]
    ])
    await callback.message.edit_text(
        "➕ **إضافة زر رئيسي جديد:**\n\nأرسل الآن **اسم الزر** (مثلاً: 📢 قناتنا):",
        reply_markup=keyboard
    )
    await callback.answer()

# 2. إضافة زر بداخل زر (زر متداخل)
@dp.callback_query(F.data == "start_add_sub_btn")
async def start_add_sub_btn(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    if not CUSTOM_BUTTONS:
        await callback.answer("⚠️ يجب أن تبتكر زر رئيسي من نوع 'قائمة' أولاً لتضع بداخله أزراراً!", show_alert=True)
        return
    
    # عرض الأزرار الرئيسية المتاحة لوضع أزرار بداخلها
    kb = []
    for b_name, data in CUSTOM_BUTTONS.items():
        if data["type"] == "menu":
            kb.append([InlineKeyboardButton(text=b_name, callback_data=f"pick_parent_{b_name}")])
    kb.append([InlineKeyboardButton(text=BUTTON_TEXTS["cancel"], callback_data="manage_buttons_menu")])
    
    await callback.message.edit_text(
        "📂 **اختر الزر الرئيسي الذي تريد وضع زر بداخله:**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("pick_parent_"))
async def pick_parent_button(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    parent_name = callback.data.replace("pick_parent_", "")
    ADMIN_STATE[callback.from_user.id] = f"waiting_sub_name_{parent_name}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXTS["cancel"], callback_data="manage_buttons_menu")]
    ])
    await callback.message.edit_text(
        f"📥 **أنت تضيف زر داخل:** `[{parent_name}]`\n\nأرسل الآن **اسم الزر الداخلي الجديد**:",
        reply_markup=keyboard
    )
    await callback.answer()

# 3. حذف زر
@dp.callback_query(F.data == "start_delete_btn")
async def start_delete_btn(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    if not CUSTOM_BUTTONS:
        await callback.answer("⚠️ لا توجد أزرار مخصصة لحذفها!", show_alert=True)
        return
    
    kb = []
    for b_name in CUSTOM_BUTTONS.keys():
        kb.append([InlineKeyboardButton(text=f"🗑️ حذف: {b_name}", callback_data=f"del_btn_{b_name}")])
    kb.append([InlineKeyboardButton(text=BUTTON_TEXTS["cancel"], callback_data="manage_buttons_menu")])
    
    await callback.message.edit_text(
        "🗑️ **اختر الزر الذي تريد حذفه:**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("del_btn_"))
async def delete_specific_button(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    btn_name = callback.data.replace("del_btn_", "")
    CUSTOM_BUTTONS.pop(btn_name, None)
    SUB_BUTTONS.pop(btn_name, None)
    
    await callback.answer(f"✅ تم حذف الزر '{btn_name}' بنجاح!", show_alert=True)
    await manage_buttons_menu(callback)

# التعامل مع الضغط على الزر المتداخل (الذي بداخله أزرار)
@dp.callback_query(F.data.startswith("sub_menu_"))
async def open_sub_menu(callback: CallbackQuery):
    main_btn = callback.data.replace("sub_menu_", "")
    sub_dict = SUB_BUTTONS.get(main_btn, {})
    
    keyboard = []
    for s_name, s_url in sub_dict.items():
        if s_url.startswith("http"):
            keyboard.append([InlineKeyboardButton(text=s_name, url=s_url)])
        else:
            keyboard.append([InlineKeyboardButton(text=s_name, callback_data="sub_info_msg")])
            
    keyboard.append([InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="back_to_menu")])
    
    await callback.message.edit_text(
        f"📁 **أنت الآن في قائمة:** `{main_btn}`\n\nاختر من الأزرار أدناه:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()

@dp.callback_query(F.data == "sub_info_msg")
async def sub_info_msg(callback: CallbackQuery):
    await callback.answer("هذا زر فرعي مخصص!", show_alert=True)

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
        "📢 **وضع الإذاعة نشط:**\n\nأرسل الآن الرسالة التي تريد إذاعتها للمستخدمين:",
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
        "📋 **الروابط والروابط المدعومة:**\n\n"
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
    
    # 1. استقبال اسم الزر الرئيسي الجديد
    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id) == "waiting_btn_name":
        btn_name = message.text.strip()
        ADMIN_STATE[user_id] = f"waiting_btn_type_{btn_name}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔗 زر يفتح رابط مباشر", callback_data=f"btype_link_{btn_name}")],
            [InlineKeyboardButton(text="📂 زر يفتح قائمة (بداخله أزرار)", callback_data=f"btype_menu_{btn_name}")]
        ])
        await message.answer(f"✅ اسم الزر: `{btn_name}`\n\nاختر نوع هذا الزر:", reply_markup=keyboard)
        return

    # استقبال نوع الزر (رابط أم قائمة)
    if user_id == ADMIN_ID and message.text and ("btype_link_" in ADMIN_STATE.get(user_id, "") or "btype_menu_" in ADMIN_STATE.get(user_id, "")):
        pass # يُعالج عبر الـ Callback بالأفل

    # 2. استقبال رابط الزر الرئيسي المباشر
    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id, "").startswith("waiting_btn_url_"):
        btn_name = ADMIN_STATE.pop(user_id).replace("waiting_btn_url_", "")
        btn_url = message.text.strip()
        CUSTOM_BUTTONS[btn_name] = {"type": "link", "content": btn_url}
        
        await message.answer(f"🎉 **تمت إضافة الزر بنجاح للقائمة الرئيسية!**\n🏷️ الاسم: `{btn_name}`\n🔗 الرابط: `{btn_url}`", reply_markup=get_admin_menu())
        return

    # 3. استقبال تفاصيل الزر الداخلي (الذي بداخل الزر)
    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id, "").startswith("waiting_sub_name_"):
        parent_name = ADMIN_STATE.pop(user_id).replace("waiting_sub_name_", "")
        sub_name = message.text.strip()
        ADMIN_STATE[user_id] = f"waiting_sub_url_{parent_name}_{sub_name}"
        
        await message.answer(f"✅ اسم الزر الداخلي: `{sub_name}`\n\n🔗 الآن أرسل **الرابط** الذي سيفتحه هذا الزر الداخلي:")
        return

    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id, "").startswith("waiting_sub_url_"):
        parts = ADMIN_STATE.pop(user_id).replace("waiting_sub_url_", "").split("_", 1)
        parent_name = parts[0]
        sub_name = parts[1]
        sub_url = message.text.strip()
        
        if parent_name not in SUB_BUTTONS:
            SUB_BUTTONS[parent_name] = {}
        SUB_BUTTONS[parent_name][sub_name] = sub_url
        
        await message.answer(f"🎉 **تمت إضافة الزر الداخلي بنجاح!**\n📁 بداخل: `{parent_name}`\n🏷️ الزر: `{sub_name}`\n🔗 الرابط: `{sub_url}`", reply_markup=get_admin_menu())
        return

    # 4. وضع الصيانة
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=BUTTON_TEXTS["support"], url=SUPPORT_USER_URL)]
        ])
        await message.answer(
            "🛠️ **البوت متوقف حالياً للصيانة والتحديث.**\n\nيرجى المحاولة لاحقاً.",
            reply_markup=keyboard
        )
        return

    # 5. الإذاعة
    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id) == "waiting_broadcast":
        ADMIN_STATE.pop(user_id, None)
        sent_count = 0
        fail_count = 0
        status_msg = await message.answer("⏳ جاري بدء الإذاعة للمستخدمين...")
        
        for uid in USERS_SET:
            try:
                await message.send_copy(chat_id=uid)
                sent_count += 1
                await asyncio.sleep(0.05)
            except Exception:
                fail_count += 1
                
        await status_msg.edit_text(f"✅ **تمت الإذاعة بنجاح!**\n📤 تم الإرسال إلى: `{sent_count}` مستخدماً")
        return

    # 6. معالجة الروابط
    text = message.text.strip()
    if text and text.startswith("http"):
        processing_msg = await message.answer("⏳ جاري فحص الرابط واستخراج الهدف...")
        
        if text in LINK_DATABASE:
            clean_url = LINK_DATABASE[text]
            result_text = f"🎉 **تم استخراج الرابط بنجاح!**\n\n🔗 {clean_url}\n\n🔔 اضغط على زر النسخ أدناه:"
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
                result_text = f"🔗 {text}\n\n💡 لمعالجة هذا الرابط، يرجى التواصل مع الدعم الفني:"
                await processing_msg.edit_text(result_text, reply_markup=get_unknown_link_keyboard(text))
            else:
                result_text = f"🎉 **تم استخراج الرابط بنجاح!**\n\n🔗 {clean_url}\n\n🔔 اضغط على زر النسخ أدناه:"
                await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
                
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء المعالجة:\n`{str(e)}`")

# معالجة أنواع الأزرار الرئيسية المختارة
@dp.callback_query(F.data.startswith("btype_"))
async def process_button_type(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    parts = callback.data.split("_", 2)
    b_type = parts[1] # link أو menu
    btn_name = parts[2]
    
    if b_type == "link":
        ADMIN_STATE[callback.from_user.id] = f"waiting_btn_url_{btn_name}"
        await callback.message.edit_text(f"🔗 الآن أرسل **الرابط** الذي سيفعته الزر `[{btn_name}]` عند الضغط عليه:")
    else:
        CUSTOM_BUTTONS[btn_name] = {"type": "menu", "content": ""}
        await callback.message.edit_text(f"✅ **تم إنشاء الزر الرئيسي كقائمة فرعية بنجاح!**\n\nيمكنك الآن الدخول إلى قسم 'إضافة زر بداخل زر' لوضع أزرار بداخله.", reply_markup=get_admin_menu())
    await callback.answer()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 البوت يعمل الآن بكفاءة عالية وبدون إعلانات...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
