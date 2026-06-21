import os
from fastapi import FastAPI, Request
import requests
from google import genai
from google.genai import types

app = FastAPI()

# 1. بيانات حسابك الفعالة في UltraMsg
ULTRAMSG_INSTANCE = "instance181605"
ULTRAMSG_TOKEN = "lcc1iapeumtgb5dj"

# 2. قراءة مفاتيح الأمان بأمان من بيئة سيرفر Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# تهيئة عميل الذكاء الاصطناعي لـ Gemini
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# 3. صياغة "تعليمات النظام" الصارمة لضبط الشخصية والهوية الصنعانية الوقورة
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

# دالة برمجية لجلب تاريخ المحادثة من Supabase وترتيبها لـ Gemini
def get_chat_history_from_supabase(phone_number: str):
    history_contents = []
    try:
        # استعلام لجلب آخر 10 رسائل مرتبة من الأقدم إلى الأحدث لهذا الرقم تحديداً
        url = f"{SUPABASE_URL}chat_history"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        params = {
            "phone_number": f"eq.{phone_number}",
            "order": "created_at.asc",
            "limit": "10"
        }
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            records = response.json()
            for record in records:
                # تشكيل الهيكل البرمجي القياسي الذي يفهمه نموذج Gemini
                history_contents.append(
                    types.Content(
                        role=record.get("role"),
                        parts=[types.Part.from_text(text=record.get("content"))]
                    )
                )
    except Exception as e:
        print(f"⚠️ خطأ أثناء جلب تاريخ المحادثة: {e}")
    return history_contents

# دالة برمجية لحفظ الرسائل الجديدة في Supabase
def save_message_to_supabase(phone_number: str, role: str, content: str):
    try:
        url = f"{SUPABASE_URL}chat_history"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "phone_number": phone_number,
            "role": role,
            "content": content
        }
        requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"⚠️ خطأ أثناء حفظ الرسالة في السحاب: {e}")

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
            
        # 1. حفظ رسالة الزبون الجديدة في قاعدة البيانات السحابية فوراً
        save_message_to_supabase(sender_number, "user", incoming_msg)
        
        # 2. سحب سياق المحادثة التاريخي بالكامل من السحاب
        past_history = get_chat_history_from_supabase(sender_number)
        print(f"📜 تم استرجاع {len(past_history)} رسالة سابقة للرقم {sender_number}")
        
        # 3. فتح جلسة دردشة لـ Gemini وتلقيمها بالتاريخ والتعليمات الصارمة
        chat = ai_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7
            ),
            history=past_history # هنا السحر! Gemini يقرأ الماضي بالكامل قبل كتابة الرد
        )
        
        # توليد الرد الذكي
        ai_response = chat.send_message(incoming_msg)
        bot_reply = ai_response.text
        
        # 4. حفظ رد البوت في قاعدة البيانات السحابية ليتذكره في المرات القادمة
        save_message_to_supabase(sender_number, "model", bot_reply)
        
        # 5. إرسال الرد المعتمد على السياق والذاكرة عبر UltraMsg إلى واتساب العميل
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
