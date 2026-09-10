import time
import requests

TOKEN = "8815004150:AAEO-paQOWRnQ88w_tSKHyG71TA37ndF1xg"
URL = f"https://api.telegram.org/bot{TOKEN}/"

def get_updates(offset=None):
    params = {"timeout": 30, "offset": offset}
    try:
        response = requests.get(URL + "getUpdates", params=params, timeout=35)
        return response.json()
    except:
        return {}

def send_menu(chat_id):
    # إرسال القائمة الرئيسية مع أزرار تفاعلية (Inline Keyboards)
    payload = {
        "chat_id": chat_id,
        "text": "مرحباً بك في بوت تجاوز الروابط الاحترافي! 👋\n\nاختر القسم الذي ترغب به من الأسفل:",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "🔗 تجاوز رابط", "callback_data": "bypass_menu"}],
                [{"text": "🎮 سكريبتات و هاكات", "callback_data": "scripts_menu"}],
                [{"text": "❓ الروابط المدعومة", "callback_data": "supported_links"}],
                [{"text": "📖 شرح البوت", "callback_data": "bot_help"}],
                [{"text": "✅ الطلبات المتكاملة: 24941", "callback_data": "stats"}]
            ]
        }
    }
    requests.post(URL + "sendMessage", json=payload)

def edit_message(chat_id, message_id, text, back_button=True):
    keyboard = [[{"text": "🔙 رجوع للقائمة", "callback_data": "back_home"}]] if back_button else []
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": {"inline_keyboard": keyboard}
    }
    requests.post(URL + "editMessageText", json=payload)

def answer_callback(callback_query_id, text=""):
    payload = {"callback_query_id": callback_query_id, "text": text}
    requests.post(URL + "answerCallbackQuery", json=payload)

def main():
    print("🚀 البوت الاحترافي يعمل الآن بنجاح...")
    offset = None
    user_state = {} # لمتابعة حالة المستخدم (هل ينتظر إرسال رابط؟)
    
    while True:
        try:
            updates = get_updates(offset)
            if "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    
                    # معالجة الضغط على الأزرار (Callback Queries)
                    if "callback_query" in update:
                        cq = update["callback_query"]
                        cq_id = cq["id"]
                        chat_id = cq["message"]["chat"]["id"]
                        message_id = cq["message"]["message_id"]
                        data = cq["data"]
                        
                        if data == "bypass_menu":
                            user_state[chat_id] = "waiting_for_link"
                            edit_message(chat_id, message_id, "🗂️ **أرسل الرابط المراد تجاوزه الآن في الدرشة:**")
                            answer_callback(cq_id)
                        elif data == "back_home":
                            user_state[chat_id] = None
                            # حذف الرسالة القديمة وإرسال القائمة من جديد لتحديث الأزرار
                            requests.post(URL + "deleteMessage", json={"chat_id": chat_id, "message_id": message_id})
                            send_menu(chat_id)
                            answer_callback(cq_id)
                        elif data == "scripts_menu":
                            edit_message(chat_id, message_id, "🎮 قسم السكريبتات والهاكات قيد التحديث المستمر...")
                            answer_callback(cq_id)
                        elif data == "supported_links":
                            edit_message(chat_id, message_id, "🌐 الروابط المدعومة حالياً:\n- LootLabs\n- Boosty\n- Linkvertise")
                            answer_callback(cq_id)
                        elif data == "bot_help":
                            edit_message(chat_id, message_id, "📖 هذا البوت مصمم لتجاوز الروابط المختصرة بسرعة واحترافية.")
                            answer_callback(cq_id)
                        elif data == "stats":
                            answer_callback(cq_id, "عدد الطلبات المتكاملة مكتمل بنجاح!")

                    # معالجة الرسائل النصية العادية
                    elif "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        user_text = update["message"]["text"]
                        
                        if user_text == "/start":
                            user_state[chat_id] = None
                            send_menu(chat_id)
                        elif user_state.get(chat_id) == "waiting_for_link" and ("http://" in user_text or "https://" in user_text):
                            # رسالة انتظار مؤقتة
                            sent_msg = requests.post(URL + "sendMessage", json={"chat_id": chat_id, "text": "⏳ جاري تجاوز الرابط... انتظر قليلاً."}).json()
                            msg_id = sent_msg.get("result", {}).get("message_id")
                            
                            start_time = time.time()
                            try:
                                target_url = user_text.strip()
                                api_url = f"https://bypass.pm/api?url={target_url}"
                                res = requests.get(api_url, timeout=20)
                                bypassed_link = None
                                
                                if res.status_code == 200:
                                    try:
                                        data = res.json()
                                        bypassed_link = data.get("destination") or data.get("url") or data.get("result")
                                    except:
                                        if "http" in res.text:
                                            bypassed_link = res.text.strip()
                                            
                                elapsed = round(time.time() - start_time, 2)
                                
                                if bypassed_link and "http" in str(bypassed_link):
                                    result_text = (
                                        f"🎉 **تم تجاوز الرابط بنجاح!**\n\n"
                                        f"🔗 `{bypassed_link}`\n\n"
                                        f"⏱️ **الوقت المستغرق:** {elapsed} ثانية"
                                    )
                                    requests.post(URL + "editMessageText", json={"chat_id": chat_id, "message_id": msg_id, "text": result_text, "parse_mode": "Markdown"})
                                else:
                                    requests.post(URL + "editMessageText", json={"chat_id": chat_id, "message_id": msg_id, "text": "❌ فشل التجاوز، قد يتطلب الرابط حماية يدوية."})
                            except Exception as e:
                                requests.post(URL + "editMessageText", json={"chat_id": chat_id, "message_id": msg_id, "text": f"❌ حدث خطأ: {str(e)}"})
                                
                            user_state[chat_id] = None
                        else:
                            if user_state.get(chat_id) == "waiting_for_link":
                                requests.post(URL + "sendMessage", json={"chat_id": chat_id, "text": "الرجاء إرسال رابط صحيح يبدأ بـ http أو https."})
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
