import os
import re
import html
import asyncio
import cloudscrapr if False else None  # تأكد من استيراد أدواتك حسب الرغبة
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = "8966597040:AAFRs5K7XJD5bXToG4m3IqVSHy6gw7BgSDQ"
ADMIN_ID = 6697426766
SUPPORT_USER_URL = "https://t.me/AL_shz1"
REQUIRED_CHANNEL_USERNAME = "@scriptRoger"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

LINK_DATABASE = {
    "https://boostylink.com/EbnbkEHt": "https://link-center.net/",
    "https://boostylink.com/nYsaet7F": "https://bstshrt.com/"
}

BUTTON_TEXTS = {
    "supported_links": "🔗 روابط مدعومة",
    "bypass_link": "⚡ تجاوزرابط",
    "about": "ℹ️ حول البوت"
}

@dp.message_handler(commands=['start'])
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text=BUTTON_TEXTS["supported_links"], callback_data="supported_links"),
        InlineKeyboardButton(text=BUTTON_TEXTS["bypass_link"], callback_data="bypass_link")
    )
    keyboard.add(InlineKeyboardButton(text=BUTTON_TEXTS["about"], callback_data="about"))
    
    await message.answer(
        "مرحباً بك في بوت التجاوز والخدمات الذكية.\nاختر أحد الخيارات أدناه للبدء:",
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == 'about')
async def process_about(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        f"للدعم الفني والاستفسار، يمكنك التواصل مع المسؤول مباشرة عبر الرابط:\n{SUPPORT_USER_URL}"
    )

@dp.callback_query_handler(lambda c: c.data == 'supported_links')
async def process_supported_links(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    links_text = "\n".join([f"• {k} ➡️ {v}" for k, v in LINK_DATABASE.items()])
    await bot.send_message(
        callback_query.from_user.id,
        f"الروابط المدعومة حالياً:\n\n{links_text}"
    )

@dp.callback_query_handler(lambda c: c.data == 'bypass_link')
async def process_bypass_menu(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        "الرجاء إرسال الرابط المراد تجاوزه مباشرة في المحادثة."
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
