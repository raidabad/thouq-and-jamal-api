import os
from fastapi import FastAPI, Request
import requests
from google import genai
from google.genai import types

app = FastAPI()

# 1. بيانات حسابك الفعالة في UltraMsg
ULTRAMSG_INSTANCE = "instance181605"
ULTRAMSG_TOKEN = "lcc1iapeumtgb5dj"

# قراءة المفتاح السري بأمان من بيئة السيرفر
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# تهيئة عميل الذكاء الاصطناعي لـ Gemini
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# 2. قاموس عالمي لتخزين جلسات دردشة الزبائن (الذاكرة)
# الهيكل سيكون: { "sender_number": chat_session }
whatsapp_chats = {}

# 3. صياغة "تعليمات النظام" الصارمة لضبط الشخصية والهوية
SYSTEM_PROMPT = """
أنت المساعد الذكي الوقور والمهذب لمتجر (ذوق وجمال) المتواجد في العاصمة صنعاء والمتخصص في العناية بالشعر.
منتجك الوحيد والحصري الحالي هو: صابونة الشعر الخضراء الطبيعية (Seven Green).

قواعد صارمة جداً يجب أن تلتزم بها في ردودك:
1. التحدث بلهجة صنعانية يمنية أصيلة، محببة، ومحترمة للغاية.
2. يجب استخدام صيغة الجمع دائماً عند مخاطبة أي زبون بدافع الاحترام والتقدير الصنعاني (مثل: حياكم الله، أهلاً وسهلاً بكم، تفضلوا، كيف أنتم، يسرنا خدمتكم).
3. يُمنع منعاً باتاً استخدام عبارات الغزل أو الألقاب غير الرسمية والمبالغ فيها مثل "يا ست الكل"، "يا غالي"، "حبيبي". بدلاً من ذلك، خاطب الزبائن بأسلوب الجمع المحترم (يا رعاكم الله، أخي الكريم/أختي الكريمة إذا اتضح الجنس، أو بالصيغة العامة المحترمة "أهلنا الكرام").
4. تفاصيل العرض الثابتة: السعر 8000 ريال يمني، التوصيل مجاني تماماً داخل صنعاء، ومشط هدية متميز مع كل صابونة.
5. مكونات الصابونة: 12 عشبة ونباتاً طبيعياً (عشبة الأسمان لإنبات الفراغات، الجينسينغ لتغذية الجذور، الزنجبيل لمكافحة القشرة، والروزماري لتطويل الشعر) وزيوت مرطبة كزبدة الشيا وزيت الزيتون.
6. للأمانة العلمية: الصابونة تنظف الفروة بعمق وتحفز إنبات البيبي هير، ولكن ننصح بترطيب أطراف الشعر ببلسم بعدها لتجنب الجفاف الطفيف.
7. لا تذكر أو تخترع أي أسعار أخرى أو منتجات أخرى غير صابونة الشعر الخضراء.
8. شجع العميل في نهاية الرد على إرسال اسمه وعنوانه في صنعاء لتجهيز الطلب فوراً بأسلوب الجمع (أرسلوا لنا اسمكم وعنوانكم).
"""

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    try:
        data = await request.json()
        print("البيانات المستقبلة من الواتساب:", data)
        
        # استخراج تفاصيل الرسالة بناءً على هيكل UltraMsg
        msg_data = data.get("data", {})
        if isinstance(msg_data, list) and len(msg_data) > 0:
            msg_data = msg_data[0]
            
        if not msg_data or "body" not in msg_data:
            return {"status": "no_message_body"}
            
        incoming_msg = str(msg_data.get("body", "")).strip() # نص رسالة الزبون
        sender_number = msg_data.get("from")                 # رقم جوال الزبون
        is_from_me = msg_data.get("fromMe")                 # هل الرسالة صادرة مني؟
        
        # لمنع البوت من الرد على نفسه والدخول في حلقة مفرغة
        if is_from_me or str(is_from_me).lower() == "true":
            return {"status": "ignored"}
            
        # 4. إدارة الذاكرة تلقائياً لكل زبون على حدة
        if sender_number not in whatsapp_chats:
            # إذا كان الزبون يراسلنا لأول مرة، ننشئ له جلسة دردشة مستقلة ونخزنها في القاموس
            print(f"🔄 إنشاء جلسة ذاكرة جديدة للرقم: {sender_number}")
            whatsapp_chats[sender_number] = ai_client.chats.create(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7
                )
            )
            
        # استدعاء جلسة الدردشة الخاصة بهذا الزبون بالتحديد من القاموس
        current_chat_session = whatsapp_chats[sender_number]
        
        # إرسال الرسالة الجديدة داخل الجلسة (Gemini سيقرأ الـ History تلقائياً ويرد بناءً عليه)
        ai_response = current_chat_session.send_message(incoming_msg)
        bot_reply = ai_response.text
        
        # 5. إرسال الرد الذكي المعتمد على السياق والذاكرة عبر UltraMsg
        url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE}/messages/chat"
        payload = {
            "token": ULTRAMSG_TOKEN,
            "to": sender_number,
            "body": bot_reply
        }
        headers = {"content-type": "application/x-www-form-urlencoded"}
        
        response = requests.post(url, data=payload, headers=headers)
        print("حالة إرسال الرد من UltraMsg:", response.status_code, response.text)
        
        return {"status": "success"}
        
    except Exception as e:
        print(f"حدث خطأ أثناء معالجة الويب هوك: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
