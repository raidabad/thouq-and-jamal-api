import os
from fastapi import FastAPI, Request
import requests
from google import genai
from google.genai import types

app = FastAPI()

# 1. بيانات حسابك الفعالة في UltraMsg والذكاء الاصطناعي
ULTRAMSG_INSTANCE = "instance181605"
ULTRAMSG_TOKEN = "lcc1iapeumtgb5dj"
# 🔐 هنا التعديل الآمن: الكود سيقرا المفتاح من السيرفر مباشرة دون كشفه
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 2. تهيئة عميل الذكاء الاصطناعي لـ Gemini
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# 3. صياغة "تعليمات النظام" لضبط شخصية البوت وهويته
SYSTEM_PROMPT = """
أنت المساعد الذكي اللطيف لمتجر (ذوق وجمال) المتواجد في العاصمة صنعاء والمتخصص في العناية بالشعر.
منتجك الوحيد والحصري الحالي هو: صابونة الشعر الخضراء الطبيعية (Seven Green).

قواعد صارمة يجب أن تلتزم بها في ردودك:
- أسلوبك يجب أن يكون ترحيبياً، احترافياً، وله لمسة يمنية صنعانية لطيفة ومحببة للزبائن.
- تفاصيل العرض الثابتة لديك: السعر 8000 ريال يمني، التوصيل مجاني تماماً داخل صنعاء، ويحصل العميل على مشط هدية متميز مع كل صابونة.
- إذا سألك العميل عن مكونات الصابونة، تذكر له أنها تتكون من 12 عشبة ونباتاً طبيعياً وأبرزها (عشبة الأسمان السحرية لإنبات الفراغات، الجينسينغ لتغذية الجذور، الزنجبيل لمكافحة القشرة، والروزماري لتطويل الشعر) وزيوت مرطبة كزبدة الشيا وزيت الزيتون.
- طبياً وعلمياً كن صادقاً وأميناً: وضح أن الصابونة تنظف الفروة بعمق وتحفز إنبات البيبي هير، لكن يجب ترطيب أطراف الشعر ببلسم بعدها لتجنب الجفاف الطفيف.
- لا تذكر أو تخترع أي أسعار أخرى أو منتجات أخرى غير صابونة الشعر الخضراء.
- شجع العميل في نهاية الردود على إرسال اسمه وعنوانه في صنعاء لتجهيز الطلب فوراً.
"""

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    try:
        data = await request.json()
        print("البيانات المستقبلة من الواتساب:", data) # لمراقبة المدخلات في Render Logs
        
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
            
        # 4. توليد الرد الذكي عبر Gemini بناءً على رسالة الزبون الحقيقية
        ai_response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=incoming_msg, # هنا نمرر نص رسالة الزبون تلقائياً
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7
            ),
        )
        
        bot_reply = ai_response.text # هذا هو الرد الذكي المبتكر
        
        # 5. إرسال الرد تلقائياً إلى جوال العميل عبر UltraMsg
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