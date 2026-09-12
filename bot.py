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
REQUIRED_CHANNEL_USERNAME = "@scriptRoger"

bot = Bot(token=TOKEN)
dp = Dispatcher()

LINK_DATABASE = {
    "https://boostylink.com/EbnbkEHt": "https://link-center.net/2603650/nY1W5wuviUhS",
    "https://boostylink.com/nYsaet7F": "https://bstshrt.com/u/vc691v"
}

BUTTON_TEXTS = {
    "supported_links": "🔗 الروابط المدعومة",
    "bypass_link": "⚡️ تجاوز رابط",
    "about": "ℹ️ حول البوت",
    "admin_panel": "⚙️ لوحة تحكم المدير",
    "test_as_user": "👤 تجربة البوت كعضو",
    "exit_test": "🔙 الخروج من التجربة",
    "broadcast": "💬 إرسال إذاعة للكل",
    "manage_scripts": "📂 إدارة الماباعات والسكربتات",
    "maintenance": "🛠️ تفعيل وضع الصيانة",
    "maintenance_off": "🟢 إلغاء وضع الصيانة",
    "back_to_menu": "🔙 رجوع للقائمة",
    "copy_link": "📋 نسخ الرابط",
    "support": "👨‍💻 تواصل مع الدعم الفني",
    "cancel": "❌ إلغاء"
}

MAPS_DB = {}
SCRIPTS_DB = {}
USERS_SET = set()
ADMIN_STATE = {}
MAINTENANCE_MODE = False
TESTING_USERS = set()

def init_databases():
    if not MAPS_DB:
        MAPS_DB.update({
            "🌴 Town": {"type": "script_menu"},
            " Adopt Me! 🐾": {"type": "script_menu"}
        })
    if not SCRIPTS_DB:
        SCRIPTS_DB.update({
            "🌴 Town": [
                {"title": "سكريبت الطيران ✈️", "content": "loadstring(game:HttpGet('example.com/town1'))()"},
                {"title": "سكريبت الفلوس 💰", "content": "loadstring(game:HttpGet('example.com/town2'))()"}
            ],
            " Adopt Me! 🐾": [
                {"title": "سكريبت التصفير 🥚", "content": "loadstring(game:HttpGet('example.com/adoptme'))()"}
            ]
        })

async def check_subscription(user_id: int) -> bool:
    if user_id == ADMIN_ID and user_id not in TESTING_USERS:
        return True
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL_USERNAME, user_id=user_id)
        if member.status in ["left", "kicked"]:
            return False
        return True
    except Exception:
        return False

def get_sub_keyboard(is_testing=False):
    keyboard = [
        [InlineKeyboardButton(text="📢 اشترك في قناة البوت", url="https://t.me/scriptRoger")],
        [InlineKeyboardButton(text="✅ لقد اشتركت، تحقق", callback_data="check_sub")]
    ]
    if is_testing:
        keyboard.append([InlineKeyboardButton(text=BUTTON_TEXTS["exit_test"], callback_data="exit_test_mode")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_main_menu(is_admin=False, is_testing=False):
    keyboard = [
        [InlineKeyboardButton(text=BUTTON_TEXTS["supported_links"], callback_data="supported_links")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["bypass_link"], callback_data="bypass_link")],
        [InlineKeyboardButton(text="📜 السكربتات والماباعات", callback_data="open_maps_menu")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["about"], callback_data="about")]
    ]
    if is_admin and not is_testing:
        keyboard.append([InlineKeyboardButton(text=BUTTON_TEXTS["admin_panel"], callback_data="admin_panel")])
    elif is_testing:
        keyboard.append([InlineKeyboardButton(text=BUTTON_TEXTS["exit_test"], callback_data="exit_test_mode")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_menu():
    m_text = BUTTON_TEXTS["maintenance_off"] if MAINTENANCE_MODE else BUTTON_TEXTS["maintenance"]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXTS["broadcast"], callback_data="start_broadcast")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["manage_scripts"], callback_data="admin_manage_scripts")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["test_as_user"], callback_data="enter_test_mode")],
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
    if user_id == ADMIN_ID and user_id in TESTING_USERS:
        TESTING_USERS.discard(ADMIN_ID)
    is_testing = False
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        await message.answer("🛠️ البوت في وضع الصيانة حالياً.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=BUTTON_TEXTS["support"], url=SUPPORT_USER_URL)]]))
        return
    if not await check_subscription(user_id):
        await message.answer("⚠️ يجب عليك الاشتراك في قناة البوت أولاً!", reply_markup=get_sub_keyboard(is_testing))
        return
    is_admin = (user_id == ADMIN_ID)
    await message.answer("مرحباً بك في بوت السكربتات وتجاوز الروابط:", reply_markup=get_main_menu(is_admin, is_testing))

@dp.callback_query(F.data == "enter_test_mode")
async def enter_test_mode(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    TESTING_USERS.add(ADMIN_ID)
    await callback.message.edit_text("🧪 أنت تجرب البوت كعضو عادي:", reply_markup=get_main_menu(False, True))
    await callback.answer()

@dp.callback_query(F.data == "exit_test_mode")
async def exit_test_mode(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    TESTING_USERS.discard(ADMIN_ID)
    await callback.message.edit_text("⚙️ لوحة تحكم المدير:", reply_markup=get_admin_menu())
    await callback.answer()

@dp.callback_query(F.data == "check_sub")
async def verify_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_testing = (user_id in TESTING_USERS)
    if await check_subscription(user_id):
        is_admin = (user_id == ADMIN_ID and not is_testing)
        await callback.message.edit_text("✅ تم التحقق بنجاح:", reply_markup=get_main_menu(is_admin, is_testing))
    else:
        await callback.answer("❌ لم تقم بالاشتراك بعد!", show_alert=True)

@dp.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID or callback.from_user.id in TESTING_USERS:
        return
    await callback.message.edit_text("⚙️ لوحة تحكم المدير:", reply_markup=get_admin_menu())
    await callback.answer()

@dp.callback_query(F.data == "admin_manage_scripts")
async def admin_manage_scripts(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID or callback.from_user.id in TESTING_USERS:
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ إضافة ماب جديد", callback_data="add_map_prompt")],
        [InlineKeyboardButton(text="➕ إضافة سكريبت داخل ماب", callback_data="add_script_prompt")],
        [InlineKeyboardButton(text="🗑️ حذف ماب", callback_data="delete_map_prompt")],
        [InlineKeyboardButton(text=BUTTON_TEXTS["back_to_menu"], callback_data="admin_panel")]
    ])
    await callback.message.edit_text("📂 إدارة السكربتات:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "add_map_prompt")
async def add_map_prompt(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID or callback.from_user.id in TESTING_USERS:
        return
    ADMIN_STATE[callback.from_user.id] = "waiting_new_map_name"
    await callback.message.edit_text("➕ أرسل اسم الماب الجديد:")
    await callback.answer()

@dp.callback_query(F.data == "add_script_prompt")
async def add_script_prompt(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID or callback.from_user.id in TESTING_USERS:
        return
    if not MAPS_DB:
        await callback.answer("⚠️ أضف ماب أولاً!", show_alert=True)
        return
    kb = [[InlineKeyboardButton(text=m, callback_data=f"select_map_for_script_{m}")] for m in MAPS_DB.keys()]
    kb.append([InlineKeyboardButton(text=BUTTON_TEXTS["cancel"], callback_data="admin_manage_scripts")])
    await callback.message.edit_text("📂 اختر الماب:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback.answer()

@dp.callback_query(F.data.startswith("select_map_for_script_"))
async def select_map_for_script(callback: CallbackQuery):
    map_name = callback.data.replace("select_map_for_script_", "")
    ADMIN_STATE[callback.from_user.id] = f"waiting_script_title_{map_name}"
    await callback.message.edit_text(f"📝 أرسل عنوان السكريبت لـ {map_name}:")
    await callback.answer()

@dp.callback_query(F.data == "delete_map_prompt")
async def delete_map_prompt(callback: CallbackQuery):
    if not MAPS_DB:
        await callback.answer("⚠️ لا توجد ماباعات!", show_alert=True)
        return
    kb = [[InlineKeyboardButton(text=f"🗑️ {m}", callback_data=f"del_map_{m}")] for m in MAPS_DB.keys()]
    kb.append([InlineKeyboardButton(text=BUTTON_TEXTS["cancel"], callback_data="admin_manage_scripts")])
    await callback.message.edit_text("🗑️ اختر الماب للحذف:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback.answer()

@dp.callback_query(F.data.startswith("del_map_"))
async def execute_delete_map(callback: CallbackQuery):
    map_name = callback.data.replace("del_map_", "")
    MAPS_DB.pop(map_name, None)
    SCRIPTS_DB.pop(map_name, None)
    await callback.answer(f"✅ تم الحذف", show_alert=True)
    await admin_manage_scripts(callback)

@dp.callback_query(F.data == "open_maps_menu")
async def open_maps_menu(callback: CallbackQuery):
    if not MAPS_DB:
        await callback.answer("⚠️ لا توجد ماباعات!", show_alert=True)
        return
    kb = [[InlineKeyboardButton(text=m, callback_data=f"map_view_{m}")] for m in MAPS_DB.keys()]
    kb.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="back_to_menu")])
    await callback.message.edit_text("🗺️ اختر الماب:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback.answer()

@dp.callback_query(F.data.startswith("map_view_"))
async def map_view(callback: CallbackQuery):
    map_name = callback.data.replace("map_view_", "")
    scripts_list = SCRIPTS_DB.get(map_name, [])
    if not scripts_list:
        await callback.answer("⚠️ لا توجد سكريبتات!", show_alert=True)
        return
    kb = [[InlineKeyboardButton(text=s["title"], callback_data=f"get_script_{map_name}_{idx}")] for idx, s in enumerate(scripts_list)]
    kb.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="open_maps_menu")])
    await callback.message.edit_text(f"🎮 ماب: {map_name}", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback.answer()

@dp.callback_query(F.data.startswith("get_script_"))
async def get_script_content(callback: CallbackQuery):
    parts = callback.data.replace("get_script_", "").rsplit("_", 1)
    script_data = SCRIPTS_DB[parts[0]][int(parts[1])]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 رجوع", callback_data=f"map_view_{parts[0]}")]])
    await callback.message.edit_text(f"📜 {script_data['title']}\n\n{script_data['content']}", reply_markup=kb)
    await callback.answer()

@dp.callback_query(F.data == "toggle_maintenance")
async def toggle_maintenance_callback(callback: CallbackQuery):
    global MAINTENANCE_MODE
    MAINTENANCE_MODE = not MAINTENANCE_MODE
    await callback.answer("تم تغيير وضع الصيانة", show_alert=True)
    await admin_panel_callback(callback)

@dp.callback_query(F.data == "start_broadcast")
async def start_broadcast_callback(callback: CallbackQuery):
    ADMIN_STATE[callback.from_user.id] = "waiting_broadcast"
    await callback.message.edit_text("📢 أرسل رسالة الإذاعة:")
    await callback.answer()

@dp.callback_query(F.data == "about")
async def about_callback(callback: CallbackQuery):
    await callback.message.edit_text("ℹ️ بوت تجاوز الروابط والسكربتات.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 رجوع", callback_data="back_to_menu")]]))
    await callback.answer()

@dp.callback_query(F.data == "bypass_link")
async def bypass_prompt(callback: CallbackQuery):
    await callback.message.edit_text("⚡️ أرسل الرابط المختصر الآن:")
    await callback.answer()

@dp.callback_query(F.data == "supported_links")
async def supported_links_callback(callback: CallbackQuery):
    await callback.message.edit_text("📋 الروابط المدعومة: boostylink, link-center, bstshrt", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 رجوع", callback_data="back_to_menu")]]))
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    ADMIN_STATE.pop(user_id, None)
    await callback.message.edit_text("القائمة الرئيسية:", reply_markup=get_main_menu(user_id == ADMIN_ID, user_id in TESTING_USERS))
    await callback.answer()

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_messages(message: Message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id) == "waiting_new_map_name":
        map_name = message.text.strip()
        MAPS_DB[map_name] = {"type": "script_menu"}
        SCRIPTS_DB[map_name] = []
        ADMIN_STATE.pop(user_id, None)
        await message.answer(f"✅ تمت إضافة الماب: {map_name}", reply_markup=get_admin_menu())
        return

    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id, "").startswith("waiting_script_title_"):
        map_name = ADMIN_STATE.pop(user_id).replace("waiting_script_title_", "")
        ADMIN_STATE[user_id] = f"waiting_script_content_{map_name}_{message.text.strip()}"
        await message.answer("🔗 أرسل محتوى السكريبت:")
        return

    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id, "").startswith("waiting_script_content_"):
        parts = ADMIN_STATE.pop(user_id).replace("waiting_script_content_", "").split("_", 1)
        SCRIPTS_DB[parts[0]].append({"title": parts[1], "content": message.text.strip()})
        await message.answer("🎉 تم الحفظ بنجاح!", reply_markup=get_admin_menu())
        return

    if user_id == ADMIN_ID and ADMIN_STATE.get(user_id) == "waiting_broadcast":
        ADMIN_STATE.pop(user_id, None)
        for uid in USERS_SET:
            try:
                await message.send_copy(chat_id=uid)
                await asyncio.sleep(0.05)
            except Exception:
                pass
        await message.answer("✅ تمت الإذاعة.")
        return

    text = message.text.strip()
    if text.startswith("http"):
        processing_msg = await message.answer("⏳ جاري الفحص...")
        if text in LINK_DATABASE:
            await processing_msg.edit_text(f"🎉 تم الاستخراج:\n\n🔗 {LINK_DATABASE[text]}", reply_markup=get_copy_keyboard(LINK_DATABASE[text]))
            return
        try:
            scraper = cloudscraper.create_scraper()
            res = scraper.get(text, allow_redirects=False, timeout=10)
            clean = res.headers.get("Location", text)
            await processing_msg.edit_text(f"🎉 تم الاستخراج:\n\n🔗 {clean}", reply_markup=get_copy_keyboard(clean))
        except Exception as e:
            await processing_msg.edit_text(f"❌ خطأ: {e}")

async def main():
    init_databases()
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 البوت يعمل الآن بنظام الذاكرة الذكية للماباعات...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
