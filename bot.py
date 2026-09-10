import time
import requests

TOKEN = "8512256766:AAGmFS1y0JnmACIb42bDGREbZ-gcfPliev4"
URL = f"https://api.telegram.org/bot{TOKEN}/"

def get_updates(offset=None):
    params = {"timeout": 30, "offset": offset}
    try:
        response = requests.get(URL + "getUpdates", params=params, timeout=35)
        return response.json()
    except:
        return {}

def send_message(chat_id, text):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(URL + "sendMessage", json=payload, timeout=10)
    except:
        pass

def main():
    print("🤖 البوت يعمل الان بنجاح...")
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            if "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        user_text = update["message"]["text"]
                        
                        if user_text == "/start":
                            send_message(chat_id, "أهلاً بك يا بطل! 🚀\nأرسل لي الرابط المختصر وسأقوم بمحاولة تخطيه لك.")
                        elif "http://" in user_text or "https://" in user_text:
                            send_message(chat_id, "⏳ جاري الاتصال بخوادم التخطي، انتظر قليلاً...")
                            
                            try:
                                target_url = user_text.strip()
                                bypassed_link = None
                                
                                # محاولة عبر خدمة تخطي موثوقة ومستقرة
                                api_url = f"https://bypass.pm/api?url={target_url}"
                                res = requests.get(api_url, timeout=20)
                                
                                if res.status_code == 200:
                                    data = res.json()
                                    bypassed_link = data.get("destination") or data.get("url") or data.get("result")
                                
                                # إذا لم تنجح، نحاول بخدمة بديلة
                                if not bypassed_link or "http" not in str(bypassed_link):
                                    alt_api = f"https://api.botspace.org/bypass?url={target_url}"
                                    alt_res = requests.get(alt_api, timeout=20)
                                    if alt_res.status_code == 200:
                                        alt_data = alt_res.json()
                                        bypassed_link = alt_data.get("result") or alt_data.get("url")

                                if bypassed_link and "http" in str(bypassed_link):
                                    send_message(chat_id, f"✅ **تم تخطي الرابط بنجاح!**\n\nالرابط المباشر:\n`{bypassed_link}`")
                                else:
                                    send_message(chat_id, "❌ عذراً، الخادم استجاب لكنه لم يرجع الرابط المباشر. قد يكون الرابط متطلب حماية يدوية.")
                            except Exception as e:
                                send_message(chat_id, f"❌ حدث خطأ في الاتصال بالخادم: {str(e)}")
                        else:
                            send_message(chat_id, "الرجاء إرسال رابط صحيح يبدأ بـ http أو https.")
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
