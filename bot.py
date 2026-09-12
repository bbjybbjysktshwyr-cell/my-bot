import os
import re
import html
import asyncio
import cloudscraper
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

TOKEN = "8966597040:AAFRs5K7XJD5bXToG4m3IqVSHy6gw7BgSDQ"
ADMIN_ID = 6697426766
SUPPORT_USER_URL = "https://t.me/AL_shz1"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# قاعدة بيانات قنوات الاشتراك الإجباري (تحفظ الآيدي كمعرف أساسي والرابط كزر)
# مثال: {-100123456789: "https://t.me/your_channel"}
CHANNELS_DB = {}

LINK_DATABASE = {
    "https://boostylink.com/EbnbkEHt": "https://link-center.net/2603650/nY1W5wuviUhS",
    "https://boostylink.com/nYsaet7F": "https://bstshrt.com/u/vc691v"
}

BUTTON_TEXTS = {
    "supported_links": "🔗 الروابط المدعومة",
    "bypass_link": "⚡️ تجاوز رابط",
    "about": "ℹ️ حول البوت",
    "admin_panel": "⚙️ لوحة تحكم المدير",
    "broadcast": "💬 إرسال إذاعة للكل",
    "manage_scripts": "📂 إدارة الماباعات والسكربتات",
    "manage_channels": "📢 إدارة قنوات الاشتراك",
    "maintenance": "🛠️ تفعيل وضع الصيانة",
    "maintenance_off": "🟢 إلغاء وضع الصيانة",
    "back_to_menu": "🔙 رجوع للقائمة",
    "copy_link": "📋 نسخ الرابط",
    "support": "👨‍💻 تواصل مع الدعم الفني",
    "cancel": "❌ إلغاء"
}

MAPS_DB = {
    "🌴 Town": {"type": "script_menu"},
    " Adopt Me! 🐾": {"type": "script_menu"}
}

SCRIPTS_DB = {
    "🌴 Town": [
        {"title": "سكريبت الطيران ✈️", "content": "loadstring(game:HttpGet('example.com/town1'))()"},
        {"title": "سكريبت الفلوس 💰", "content": "loadstring(game:HttpGet('example.com/town2'))()"}
    ],
    " Adopt Me! 🐾": [
        {"title": "سكريبت التصفير 🥚", "content": "loadstring(game:HttpGet('example.com/adoptme'))()"}
    ]
}

USERS_SET = set()
ADMIN_STATE = {}
MAINTENANCE_MODE = False

# دالة التحقق الحقيقي من الاشتراك باستخدام آيدي القناة
async def check_subscription(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return True  # المدير مستثنى دائماً
    
    if not CHANNELS_DB:
        return True  # إذا لم توجد قنوات مضافة، يسمح بالدخول
        
    for chat_id in CHANNELS_DB.keys():
        try:
            member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception:
            # إذا حدث خطأ (مثلاً البوت ليس مشرفاً في القناة) يعتبره غير مشترك ليتم تنبيه المدير
            return False
    return True

def get_sub_keyboard():
    keyboard = []
    for chat_id, ch_url in CHANNELS_DB.items():
        # محاولة جلب معلومات القناة لعرض اسمها الحقيقي على الزر
        keyboard.append([InlineKeyboardButton(text="📢 اشترك في القناة", url=ch_url)])
    keyboard.append([InlineKeyboardButton(text="✅ لقد اشتركت، تحقق", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_main_menu(is_admin=False):
    keyboard = [
        [InlineKeyboardButton(text=BUTTON_TEXTS["supported_links"], callback_data="supported_links")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["bypass_link"], callback_data="bypass_link")],
        [InlineKeyboardButton(text="📜 السكربتات والماباعات", callback_data="open_maps_menu")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["about"], callback_data="about")]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton(text=BUTTON_TEXTS["admin_panel"], callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_menu():
    m_text = BUTTON_TEXTS["maintenance_off"] if MAINTENANCE_MODE else BUTTON_TEXTS["maintenance"]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXTS["broadcast"], callback_data="start_broadcast")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["manage_scripts"], callback_data="admin_manage_scripts")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["manage_channels"], callback_data="admin_manage_channels")],
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
    
    if not await check_subscription(user_id):
        await message.answer(
            "⚠️ **عذراً، يجب عليك الاشتراك في قنوات البوت أولاً لتتمكن من استخدامها!**\n\n"
            "اشترك في القناة أدناه ثم اضغط على زر التحقق:",
            reply_markup=get_sub_keyboard()
        )
        return

    is_admin = (user_id == ADMIN_ID)
    await message.answer(
        "مرحباً بك في بوت السكربتات وتجاوز الروابط. اختر ما تحتاجه من القائمة أدناه:",
        reply_markup=get_main_menu(is_admin)
    )

@dp.callback_query(F.data == "check_sub")
async def verify_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_name = callback.from_user.full_name
    username = callback.from_user.username
    
    if await check_subscription(user_id):
        if user_id != ADMIN_ID:
            try:
                user_info = f"👤 المستخدم: {user_name} (رابطه: @{username if username else 'لا يوجد'} | الآيدي: `{user_id}`)"
                await bot.send_message(ADMIN_ID, f"🔔 **إشعار اشتراك جديد!**\n\n{user_info}\nقام باجتياز اشتراك القنوات بنجاح ودخل البوت ✅")
            except Exception:
                pass
                
        await callback.message.delete()
        is_admin = (user_id == ADMIN_ID)
        await callback.message.answer(
            "✅ شكراً لاشتراكاتك! تم تفعيل البوت بنجاح:",
            reply_markup=get_main_menu(is_admin)
        )
    else:
        await callback.answer("❌ لم تقم بالاشتراك في القناة المطلوبة، أو أن البوت ليس مشرفاً فيها!", show_alert=True)

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

@dp.callback_query(F.data == "admin_manage_channels")
async def admin_manage_channels(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    
    ch_list_text = "\n".join([f"• الآيدي: `{chat_id}` ➡️ {url}" for chat_id, url in CHANNELS_DB.items()]) if CHANNELS_DB else "لا توجد قنوات مضافة حالياً."
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ إضافة قناة جديدة", callback_data="add_channel_prompt")],
        [InlineKeyboardButton(text="🗑️ حذف قناة", callback_data="del_channel_prompt")],
        [InlineKeyboardButton(text="🔙 رجوع لوحة التحكم", callback_data="admin_panel")]
    ])
    
    await callback.message.edit_text(
        f"📢 **إدارة قنوات الاشتراك الإجباري الحقيقية:**\n\nالقنوات الحالية:\n{ch_list_text}\n\nاختر العملية التي تريدها:",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "add_channel_prompt")
async def add_channel_prompt(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    ADMIN_STATE[callback.from_user.id] = "waiting_channel_forward"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXTS["cancel"], callback_data="admin_manage_channels")]
    ])
    await callback.message.edit_text(
        "➕ **خطوات إضافة قناة حقيقية:**\n\n1️⃣ تأكد أنك أضفت البوت **مشرفاً** في قناتك.\n2️⃣ قم **بتحويل (Forward)** أي رسالة من قناتك هنا الآن:",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "del_channel_prompt")
async def del_channel_prompt(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    if not CHANNELS_DB:
        await callback.answer("⚠️ لا توجد قنوات للحذف!", show_alert=True)
        return
        
    kb = []
    for chat_id in CHANNELS_DB.keys():
        kb.append([InlineKeyboardButton(text=f"🗑️ حذف الآيدي: {chat_id}", callback_data=f"remove_ch_{chat_id}")])
    kb.append([InlineKeyboardButton(text=BUTTON_TEXTS["cancel"], callback_data="admin_manage_channels")])
    
    await callback.message.edit_text(
        "🗑️ **اختر القناة المراد حذفها:**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("remove_ch_"))
async def execute_remove_channel(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    chat_id = int(callback.data.replace("remove_ch_", ""))
    CHANNELS_DB.pop(chat_id, None)
    await callback.answer(f"✅ تم حذف القناة بنجاح!", show_alert=True)
    await admin_manage_channels(callback)

@dp.callback_query(F.data == "admin_manage_scripts")
async def admin_manage_scripts(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ إضافة ماب جديد", callback_data="add_map_prompt")],
        [InlineKeyboardButton(text="➕ إضافة سكريبت داخل ماب", callback_data="add_script_prompt")],
        [InlineKeyboardButton(text="🗑️ حذف ماب", callback_data="delete_map_prompt")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["back_to_menu"], callback_data="admin_panel")]
    ])
    await callback.message.edit_text(
        "📂 **لوحة إدارة السكربتات والماباعات:**\n\nاختر العملية التي تريدها:",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "add_map_prompt")
async def add_map_prompt(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    ADMIN_STATE[callback.from_user.id] = "waiting_new_map_name"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXTS["cancel"], callback_data="admin_manage_scripts")]
    ])
    await callback.message.edit_text("➕ **إضافة ماب جديد:**\n\nأرسل الآن اسم الماب:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "add_script_prompt")
async def add_script_prompt(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    if not MAPS_DB:
        await callback.answer("⚠️ يجب إضافة ماب أولاً!", show_alert=True)
        return
    kb = []
    for m_name in MAPS_DB.keys():
        kb.append([InlineKeyboardButton(text=m_name, callback_data=f"select_map_for_script_{m_name}")])
    kb.append([InlineKeyboardButton(text=BUTTON_TEXTS["cancel"], callback_data="admin_manage_scripts")])
    await callback.message.edit_text("📂 **اختر الماب لإضافة السكريبت:**", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback.answer()

@dp.callback_query(F.data.startswith("select_map_for_script_"))
async def select_map_for_script(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    map_name = callback.data.replace("select_map_for_script_", "")
    ADMIN_STATE[callback.from_user.id] = f"waiting_script_title_{map_name}"
    await callback.message.edit_text(f"📝 الماب: `{map_name}`\n\nأرسل **عنوان السكريبت**:")
    await callback.answer()

@dp.callback_query(F.data == "delete_map_prompt")
async def delete_map_prompt(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    if not MAPS_DB:
        await callback.answer("⚠️ لا توجد ماباعات!", show_alert=True)
        return
    kb = []
    for m_name in MAPS_DB.keys():
        kb.append([InlineKeyboardButton(text=f"🗑️ حذف: {m_name}", callback_data=f"del_map_{m_name}")])
    kb.append([InlineKeyboardButton(text=BUTTON_TEXTS["cancel"], callback_data="admin_manage_scripts")])
    await callback.message.edit_text("🗑️ **اختر الماب للحذف:**", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback.answer()

@dp.callback_query(F.data.startswith("del_map_"))
async def execute_delete_map(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    map_name = callback.data.replace("del_map_", "")
    MAPS_DB.pop(map_name, None)
    SCRIPTS_DB.pop(map_name, None)
    await callback.answer(f"✅ تم حذف {map_name}", show_alert=True)
    await admin_manage_scripts(callback)

@dp.callback_query(F.data == "open_maps_menu")
async def open_maps_menu(callback: CallbackQuery):
    if not await check_subscription(callback.from_user.id):
        await callback.answer("⚠️ اشترك في القنوات أولاً!", show_alert=True)
        return
    kb = []
    for m_name in MAPS_DB.keys():
        kb.append([InlineKeyboardButton(text=m_name, callback_data=f"map_view_{m_name}")])
    kb.append([InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="back_to_menu")])
    await callback.message.edit_text("🗺️ **اختر الماب لعرض السكريبتات:**", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback.answer()

@dp.callback_query(F.data.startswith("map_view_"))
async def map_view(callback: CallbackQuery):
    map_name = callback.data.replace("map_view_", "")
    scripts_list = SCRIPTS_DB.get(map_name, [])
    kb = []
    for idx, script in enumerate(scripts_list):
        kb.append([InlineKeyboardButton(text=script["title"], callback_data=f"get_script_{map_name}_{idx}")])
    kb.append([InlineKeyboardButton(text="🔙 رجوع للماباعات", callback_data="open_maps_menu")])
    await callback.message.edit_text(f"🎮 **ماب: {map_name}**", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback.answer()

@dp.callback_query(F.data.startswith("get_script_"))
async def get_script_content(callback: CallbackQuery):
    parts = callback.data.replace("get_script_", "").rsplit("_", 1)
    map_name = parts[0]
    idx = int(parts[1])
    script_data = SCRIPTS_DB[map_name][idx]
    text = f"📜 **{script_data['title']}**\n\nقُم بالنسخ والاستخدام:\n\n`{script_data['content']}`"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 رجوع", callback_data=f"map_view_{map_name}")]])
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()

@dp.callback_query(F.data == "toggle_maintenance")
async def toggle_maintenance_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    global MAINTENANCE_MODE
    MAINTENANCE_MODE = not MAINTENANCE_MODE
    state_msg = "تم تفعيل الصيانة 🔴" if MAINTENANCE_MODE else "تم إلغاء الصيانة 🟢"
    await callback.answer(state_msg, show_alert=True)
    await admin_panel_callback(callback)

@dp.callback_query(F.data == "start_broadcast")
async def start_broadcast_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    ADMIN_STATE[callback.from_user.id] = "waiting_broadcast"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=BUTTON_TEXTS["cancel"], callback_data="admin_panel")]])
    await callback.message.edit_text("📢 **أرسل رسالة الإذاعة الآن:**", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "about")
async def about_callback(callback: CallbackQuery):
    is_admin = (callback.from_user.id == ADMIN_ID)
    await callback.message.edit_text("بوت السكربتات وتجاوز الروابط.", reply_markup=get_main_menu(is_admin))
    await callback.answer()

@dp.callback_query(F.data == "bypass_link")
async def bypass_prompt(callback: CallbackQuery):
    if not await check_subscription(callback.from_user.id):
        await callback.answer("⚠️ اشترك أولاً!", show_alert=True)
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=BUTTON_TEXTS["back_to_menu"], callback_data="back_to_menu")]])
    await callback.message.edit_text("⚡️ **أرسل الرابط المختصر الآن في المحادثة مباشرة:**", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "supported_links")
async def supported_links_callback(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=BUTTON_TEXTS["back_to_menu"], callback_data="back_to_menu")]])
    await callback.message.edit_text("📋 **الروابط المدعومة:**\n• `https://boostylink.com`", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not await check_subscription(user_id):
        await callback.message.edit_text("⚠️ يجب عليك الاشتراك في القنوات أولاً!", reply_markup=get_sub_keyboard())
        return
    ADMIN_STATE.pop(user_id, None)
    is_admin = (user_id == ADMIN_ID)
    await callback.message.edit_text("مرحباً بك من جديد في القائمة الرئيسية:", reply_markup=get_main_menu(is_admin))
    await callback.answer()

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_messages(message: Message):
    user_id = message.from_user.id
    
    if not await check_subscription(user_id):
        await message.answer("⚠️ **يجب عليك الاشتراك في القنوات أولاً لاستخدام البوت!**", reply_markup=get_sub_keyboard())
        return

    # استقبال تحويل الرسالة للقناة لحفظها كاشتراك إجباري حقيقي
    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id) == "waiting_channel_forward":
        if message.forward_from_chat and message.forward_from_chat.type == "channel":
            chat_id = message.forward_from_chat.id
            ADMIN_STATE[user_id] = f"waiting_channel_link_{chat_id}"
            await message.answer(
                f"✅ تم التقاط آيدي القناة بنجاح (`{chat_id}`).\n\nالخطوة الأخيرة: أرسل الآن **رابط القناة** (مثال: `https://t.me/scriptRoger`) لكي يظهر في زر الاشتراك:"
            )
        else:
            await message.answer("❌ هذه ليست رسالة محولة من قناة! يرجى تحويل رسالة من قناتك الخاصة التي أضفت البوت مشرفاً فيها.")
        return

    # استقبال رابط الزر بعد حفظ الآيدي
    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id, "").startswith("waiting_channel_link_"):
        chat_id = int(ADMIN_STATE.pop(user_id).replace("waiting_channel_link_", ""))
        ch_url = message.text.strip()
        CHANNELS_DB[chat_id] = ch_url
        await message.answer(f"🎉 **تمت إضافة القناة بنجاح كاشتراك إجباري حقيقي!**\n\n🆔 الآيدي: `{chat_id}`\n🔗 الرابط: `{ch_url}`", reply_markup=get_admin_menu())
        return

    # استقبال اسم الماب الجديد
    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id) == "waiting_new_map_name":
        map_name = message.text.strip()
        MAPS_DB[map_name] = {"type": "script_menu"}
        SCRIPTS_DB[map_name] = []
        ADMIN_STATE.pop(user_id, None)
        await message.answer(f"✅ تمت إضافة الماب: `{map_name}`", reply_markup=get_admin_menu())
        return

    # استقبال عنوان السكريبت
    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id, "").startswith("waiting_script_title_"):
        map_name = ADMIN_STATE.pop(user_id).replace("waiting_script_title_", "")
        script_title = message.text.strip()
        ADMIN_STATE[user_id] = f"waiting_script_content_{map_name}_{script_title}"
        await message.answer(f"🔗 أرسل الآن **محتوى السكريبت**:")
        return

    # استقبال محتوى السكريبت
    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id, "").startswith("waiting_script_content_"):
        parts = ADMIN_STATE.pop(user_id).replace("waiting_script_content_", "").split("_", 1)
        map_name = parts[0]
        script_title = parts[1]
        script_content = message.text.strip()
        if map_name not in SCRIPTS_DB:
            SCRIPTS_DB[map_name] = []
        SCRIPTS_DB[map_name].append({"title": script_title, "content": script_content})
        await message.answer(f"🎉 تم حفظ السكريبت في ماب `{map_name}` بنجاح!", reply_markup=get_admin_menu())
        return

    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        await message.answer("🛠️ البوت في صيانة حالياً.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=BUTTON_TEXTS["support"], url=SUPPORT_USER_URL)]]))
        return

    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id) == "waiting_broadcast":
        ADMIN_STATE.pop(user_id, None)
        sent_count = 0
        status_msg = await message.answer("⏳ جاري الإذاعة...")
        for uid in USERS_SET:
            try:
                await message.send_copy(chat_id=uid)
                sent_count += 1
                await asyncio.sleep(0.05)
            except Exception:
                pass
        await status_msg.edit_text(f"✅ تمت الإذاعة إلى `{sent_count}` مستخدماً.")
        return

    # فحص الروابط
    text = message.text.strip()
    if text and text.startswith("http"):
        processing_msg = await message.answer("⏳ جاري الفحص واستخراج الهدف...")
        if text in LINK_DATABASE:
            clean_url = LINK_DATABASE[text]
            await processing_msg.edit_text(f"🎉 **تم الاستخراج بنجاح!**\n\n🔗 {clean_url}", reply_markup=get_copy_keyboard(clean_url))
            return

        extracted_url = text
        try:
            scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'android', 'desktop': False})
            headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36", "Referer": text}
            response = scraper.get(text, headers=headers, allow_redirects=False, timeout=10)
            if response.status_code in [301, 302, 303, 307, 308]:
                if response.headers.get("Location"):
                    extracted_url = response.headers.get("Location")

            clean_url = html.unescape(extracted_url).strip()
            clean_url = re.sub(r'\s+', '', clean_url)

            if clean_url == text:
                await processing_msg.edit_text(f"🔗 {text}\n\n💡 تواصل مع الدعم الفني:", reply_markup=get_unknown_link_keyboard(text))
            else:
                await processing_msg.edit_text(f"🎉 **تم الاستخراج بنجاح!**\n\n🔗 {clean_url}", reply_markup=get_copy_keyboard(clean_url))
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ:\n`{str(e)}`")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 البوت يعمل الآن بكفاءة...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
