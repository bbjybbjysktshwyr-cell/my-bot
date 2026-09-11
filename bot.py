import os
import re
import html
import json
import cloudscraper
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# توكن البوت
TOKEN = "8512256766:AAGmFS1y0JnmACIb42bDGREbZ-gcfPliev4"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 فحص وتجاوز رابط", callback_data="bypass_link")],
        [InlineKeyboardButton(text="ℹ️ حول البوت", callback_data="about")]
    ])

def get_copy_keyboard(target_url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 نسخ الرابط", url=target_url)],
        [InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="back_to_menu")]
    ])

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.reply(
        "مرحباً بك في بوت تجاوز الروابط المحلي!\n\nأرسل لي أي رابط وسأقوم باستخراج الوجهة النهائية بدقة:",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "about")
async def about_callback(callback: Message):
    await callback.message.edit_text(
        "هذا البوت مخصص لتجاوز الروابط واستخراج الوجهة النهائية محلياً.",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "bypass_link")
async def bypass_prompt(callback: Message):
    await callback.message.edit_text("يرجى إرسال الرابط المطلوب تخطيه مباشرة في المحادثة.")

@dp.callback_query(F.data == "back_to_menu")
async def back_menu(callback: Message):
    await callback.message.edit_text("أرسل الرابط المطلوب تجاوزه:", reply_markup=get_main_menu())

@dp.message()
async def handle_links(message: Message):
    text = message.text
    if text and text.startswith("http"):
        processing_msg = await message.reply("⏳ جاري تفكيك الروابط وتتبع التوجيهات النهائية...")
        
        extracted_url = text
        
        try:
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'android',
                    'desktop': False
                }
            )
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
                "Referer": text,
                "X-Requested-With": "XMLHttpRequest"
            }
            
            response = scraper.get(text, headers=headers, allow_redirects=True, timeout=25)
            html_content = response.text
            
            path_parts = text.rstrip('/').split('/')
            slug = path_parts[-1] if path_parts else ""
            
            if slug and len(slug) > 2:
                api_target_url = f"https://boostylink.com/api/links/{slug}"
                try:
                    api_resp = scraper.get(api_target_url, headers=headers, timeout=10)
                    if api_resp.status_code == 200:
                        api_data = api_resp.json()
                        if "destination" in api_data:
                            extracted_url = api_data["destination"]
                        elif "url" in api_data:
                            extracted_url = api_data["url"]
                except:
                    pass

            if extracted_url == text:
                json_matches = re.findall(r'(\{.*?"(?:destination|target_url|link|redirect_url)"\s*:\s*"https?://[^"]+".*?\})', html_content)
                for j_m in json_matches:
                    try:
                        data = json.loads(j_m)
                        for key in ["destination", "target_url", "link", "redirect_url"]:
                            if key in data and "boostylink.com" not in data[key]:
                                extracted_url = data[key]
                                break
                    except:
                        continue

            if extracted_url == text:
                found_links = re.findall(r'https?://[^\s<>"\']+', html_content)
                ignored_domains = [
                    'boostylink.com', 'google.com', 'cloudflare.com', 'w3.org', 
                    'youtube.com', 'youtu.be', 'discord.gg', 'discord.com', 't.me',
                    'maxcdn', 'jsdelivr', 'jquery', 'bootstrap', 'googletagmanager', 
                    'analytics', '#', 'javascript'
                ]
                
                for link in found_links:
                    clean_l = link.rstrip('\\"\'.,;')
                    if not any(domain in clean_l.lower() for domain in ignored_domains) and clean_l != text:
                        if not clean_l.startswith('#') and ('/' in clean_l.replace('https://', '').replace('http://', '')):
                            extracted_url = clean_l
                            break

            if extracted_url == text and response.url != text and 'boostylink.com' not in response.url:
                extracted_url = response.url

            # حلقة تتبع ذكية للروابط الوسيطة (مثل rm358 أو rtmark) عبر تتبع رأس الاستجابة والتحويلات
            redirect_count = 0
            while any(domain in extracted_url for domain in ["rm358.com", "rtmark.net"]) and redirect_count < 5:
                try:
                    redirect_count += 1
                    # تعطيل الـ redirects التلقائية مؤقتاً لنتمكن من قراءة هيدر التحويل (Location) يدوياً
                    sub_resp = scraper.get(extracted_url, headers=headers, allow_redirects=False, timeout=10)
                    
                    if "Location" in sub_resp.headers:
                        next_url = sub_resp.headers["Location"]
                        # إذا كان رابط التحويل نسبياً، نربطه بالدومين الأصلي
                        if next_url.startswith("/"):
                            parsed_base = re.match(r'(https?://[^/]+)', extracted_url)
                            next_url = parsed_base.group(1) + next_url if parsed_base else next_url
                        extracted_url = next_url
                    else:
                        # إذا لم يوجد هيدر تحويل، نفحص محتوى الصفحة عن أي سكربت تحويل
                        sub_html = sub_resp.text
                        loc_match = re.search(r'(?:window\.)?location(?:\.href)?\s*=\s*["\'](https?://[^"\']+)["\']', sub_html, re.IGNORECASE)
                        if loc_match:
                            extracted_url = loc_match.group(1)
                        else:
                            break
                except:
                    break

            clean_url = html.unescape(extracted_url).strip()
            clean_url = re.sub(r'\s+', '', clean_url)

            result_text = (
                f"🎉 **تم استخراج الرابط النهائي بنجاح!**\n\n"
                f"🔗 {clean_url}\n\n"
                f"🔔 اضغط على زر النسخ أدناه للنسخ السريع:"
            )
            
            await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ محلي:\n`{str(e)}`")
    else:
        await message.reply("يرجى إرسال رابط صالح يبدأ بـ http أو https.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
