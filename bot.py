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
        processing_msg = await message.reply("⏳ جاري بدء التتبع وتحليل الروابط خطوة بخطوة...")
        
        extracted_url = text
        steps_log = [f"الرابط الأصلي: {text}"]
        
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
                            steps_log.append(f"من API: {extracted_url}")
                        elif "url" in api_data:
                            extracted_url = api_data["url"]
                            steps_log.append(f"من API (url): {extracted_url}")
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
                                steps_log.append(f"من JSON الداخلي: {extracted_url}")
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
                            steps_log.append(f"من محتوى الصفحة: {extracted_url}")
                            break

            if extracted_url == text and response.url != text and 'boostylink.com' not in response.url:
                extracted_url = response.url
                steps_log.append(f"من إعادة التوجيه السريع: {extracted_url}")

            # تتبع عميق لـ rm358 والروابط الوسيطة مع فحص الـ Meta Refresh والـ Script Forms
            redirect_count = 0
            while any(domain in extracted_url for domain in ["rm358.com", "rtmark.net"]) and redirect_count < 5:
                try:
                    redirect_count += 1
                    sub_resp = scraper.get(extracted_url, headers=headers, allow_redirects=True, timeout=15)
                    sub_html = sub_resp.text
                    
                    # البحث عن الـ Meta Refresh
                    meta_match = re.search(r'<meta[^>]*http-equiv=["\']refresh["\'][^>]*content=["\'][^;]+;\s*url=([^\s"\']+)["\']', sub_html, re.IGNORECASE)
                    if meta_match:
                        extracted_url = meta_match.group(1)
                        steps_log.append(f"تتبع (Meta Refresh): {extracted_url}")
                        continue

                    # البحث عن نافذة التوجيه أو المتغيرات
                    loc_match = re.search(r'(?:window\.)?location(?:\.href)?\s*=\s*["\'](https?://[^"\']+)["\']', sub_html, re.IGNORECASE)
                    if loc_match:
                        extracted_url = loc_match.group(1)
                        steps_log.append(f"تتبع (JS Location): {extracted_url}")
                        continue
                        
                    # البحث عن روابط داخل النص تتجاوز الدومينات الوسيطة
                    all_sub_links = re.findall(r'https?://[^\s<>"\']+', sub_html)
                    found_next = False
                    for sl in all_sub_links:
                        clean_sl = sl.rstrip('\\"\'.,;')
                        if not any(d in clean_sl.lower() for d in ['rm358.com', 'rtmark.net', 'boostylink.com', 'google.com', 'w3.org', 'cloudflare', 'img.gif']):
                            extracted_url = clean_sl
                            steps_log.append(f"تتبع (رابط فرعي): {extracted_url}")
                            found_next = True
                            break
                    if not found_next:
                        if sub_resp.url != extracted_url:
                            extracted_url = sub_resp.url
                            steps_log.append(f"تتبع (استجابة نهائية): {extracted_url}")
                        else:
                            break
                except:
                    break

            clean_url = html.unescape(extracted_url).strip()
            clean_url = re.sub(r'\s+', '', clean_url)

            # طباعة خطوات التتبع مع الرابط النهائي لتكتشف أي خطوة تقف عندها
            logs_str = "\n".join([f"🔹 {step}" for step in steps_log])
            result_text = (
                f"🎉 **خطوات التتبع والنتيجة:**\n\n"
                f"{logs_str}\n\n"
                f"🔗 **الرابط النهائي المستخرج:**\n{clean_url}\n\n"
                f"🔔 اضغط على زر النسخ أدناه للنسخ السريع:"
            )
            
            await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء التتبع:\n`{str(e)}`")
    else:
        await message.reply("يرجى إرسال رابط صالح يبدأ بـ http أو https.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
