import os
from fastapi import FastAPI, Request, Response, HTTPException
import requests
from google import genai
from google.genai import types

app = FastAPI()

# 1. جلب متغيرات واجهة Meta الرسمية بأمان من بيئة سيرفر Render
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

# 2. قراءة مفاتيح الأمان لـ Gemini و Supabase
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# تهيئة عميل الذكاء الاصطناعي لـ Gemini
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# رمز التحقق الثابت للـ Webhook في Meta
VERIFY_TOKEN = "thouq-and-jamal-db"

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

# دالة التحقق الإجبارية عند الرابط الرئيسي - تعيد الاستجابة لفيسبوك فوراً بدون تعقيد
@app.get("/")
async def verify_webhook_root(request: Request):
    params = request.query_params
    challenge = params.get("hub.challenge")
    
    # إذا كان الطلب يحتوي على الرمز المطلوب من فيسبوك، أرسله له فوراً وبشكل مباشر
    if challenge:
        print(f"🎯 إرسال الرمز الإجباري لفيسبوك: {challenge}")
        return Response(content=challenge, media_type="text/plain")
        
    return {"status": "Thouq and Jamal API is running"}

# دالة التحقق الاحتياطية عند مسار /webhook - تعيد الاستجابة مباشرة أيضاً
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    challenge = params.get("hub.challenge")
    
    if challenge:
        print(f"🎯 إرسال الرمز الإجباري لمسار الويب هوك: {challenge}")
        return Response(content=challenge, media_type="text/plain")
        
    raise HTTPException(status_code=400, detail="Missing parameters")

# [ثانياً] دالة استقبال الرسائل ومعالجتها والرد عليها عبر Meta API (POST)
@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    try:
        data = await request.json()
        print("📩 بيانات مستقبلة من Meta Webhook:", data)
        
        # التحقق من هيكلية الرسالة الواردة من ميتا لضمان وجود رسالة نصية فعالة
        if "entry" in data and data["entry"]:
            changes = data["entry"][0].get("changes", [])
            if changes and "value" in changes[0]:
                value = changes[0]["value"]
                messages = value.get("messages", [])
                
                if messages:
                    msg = messages[0]
                    # استقبال رسائل النصوص فقط
                    if msg.get("type") == "text":
                        incoming_msg = msg["text"].get("body", "").strip()
                        sender_number = msg.get("from") # رقم العميل (صيغة دولية مثل 96777xxxxxx)
                        
                        # 1. حفظ رسالة الزبون في قاعدة بيانات Supabase فوراً
                        save_message_to_supabase(sender_number, "user", incoming_msg)
                        
                        # 2. سحب سياق المحادثة التاريخي من السحاب لـ Gemini
                        past_history = get_chat_history_from_supabase(sender_number)
                        print(f"📜 تم استرجاع {len(past_history)} رسالة سابقة للرقم {sender_number}")
                        
                        # 3. فتح جلسة دردشة لـ Gemini وتلقيمها بالتاريخ والتعليمات الصنعانية
                        chat = ai_client.chats.create(
                            model="gemini-2.5-flash",
                            config=types.GenerateContentConfig(
                                system_instruction=SYSTEM_PROMPT,
                                temperature=0.7
                            ),
                            history=past_history
                        )
                        
                        # توليد الرد الذكي
                        ai_response = chat.send_message(incoming_msg)
                        bot_reply = ai_response.text
                        
                        # 4. حفظ رد البوت في قاعدة بيانات Supabase
                        save_message_to_supabase(sender_number, "model", bot_reply)
                        
                        # 5. إرسال الرد الرسمي المجاني عبر واجهة Meta Cloud API إلى العميل
                        url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
                        headers = {
                            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
                            "Content-Type": "application/json"
                        }
                        payload = {
                            "messaging_product": "whatsapp",
                            "recipient_type": "individual",
                            "to": sender_number,
                            "type": "text",
                            "text": {
                                "preview_url": False,
                                "body": bot_reply
                            }
                        }
                        
                        response = requests.post(url, json=payload, headers=headers)
                        print("حالة إرسال الرد من Meta Cloud API:", response.status_code, response.text)
                        
        return {"status": "success"}
        
    except Exception as e:
        print(f"حدث خطأ أثناء معالجة الويب هوك لـ Meta: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
