from fastapi import FastAPI, Request
import requests

app = FastAPI()

# بيانات حسابك في UltraMsg (ستحصل عليها بعد التسجيل)
ULTRAMSG_INSTANCE = "YOUR_INSTANCE_ID"  # استبدله برقم الـ Instance لاحقاً
ULTRAMSG_TOKEN = "YOUR_TOKEN"          # استبدله بالـ Token لاحقاً

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    print("البيانات المستقبلة من الواتساب:", data) # لمراقبة الرسائل في الـ Logs
    
    # التحقق من أن البيانات تحتوي على رسالة واردة
    if "data" in data and "body" in data["data"]:
        incoming_msg = data["data"]["body"].strip() # نص رسالة الزبون
        sender_number = data["data"]["from"]       # رقم جوال الزبون
        is_from_me = data["data"]["fromMe"]         # هل الرسالة صادرة مني؟
        
        # لمنع البوت من الرد على رسائله الشخصية والدخول في حلقة مفرغة
        if is_from_me:
            return {"status": "ignored"}
            
        # منطق الرد الذكي لمتجر ذوق وجمال
        bot_reply = ""
        if "سيروم" in incoming_msg or "الأرجان" in incoming_msg:
            bot_reply = "سيروم الأرجان المغربي الأصلي متوفر بسعر 60 ريال. ✨"
        elif "السعر" in incoming_msg or "بكم" in incoming_msg:
            bot_reply = "أهلاً بك في متجر ذوق وجمال! يرجى تحديد المنتج لمعرفة سعره، أو اكتب (سيروم الأرجان)."
        else:
            bot_reply = "أهلاً بك في متجر ذوق وجمال! سيقوم أحد موظفينا بالرد عليك قريباً، أو يمكنك الاستفسار عن أسعار المنتجات مباشرة."
            
        # إرسال الرد تلقائياً إلى جوال العميل عبر API الخاص بـ UltraMsg
        url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE}/messages/chat"
        payload = {
            "token": ULTRAMSG_TOKEN,
            "to": sender_number,
            "body": bot_reply
        }
        headers = {"content-type": "application/x-www-form-urlencoded"}
        
        # إطلاق الرسالة
        requests.post(url, data=payload, headers=headers)
        
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)































""" from fastapi import FastAPI
import re

# 1. إنشاء تطبيق الـ API
app = FastAPI()

# دالة الرد الذكي الخاصة بك (من تحديك السابق)
def generate_bot_reply(customer_message):
    cleaned_text = re.sub(r'[^\w\s]', '', customer_message)
    words = cleaned_text.split()
    
    if "زيت" in words and "الإكليل" in words:
        return "زيت إكليل الجبل متوفر لدينا! سعره 45 ريال."
    elif "شامبو" in words or "البيوتين" in words:
        return "أهلاً بكِ! شامبو البيوتين متوفر بسعر 35 ريال."
    elif "سيروم" in words or "الأرجان" in words:
        return "سيروم الأرجان المغربي الأصلي متوفر بسعر 60 ريال."
    elif "سعر" in words or "بكم" in words:
        return "يمكنكِ الاطلاع على أسعار كافة المنتجات من رابط متجر ذوق وجمال."
    else:
        return "مرحباً بكِ في متجر ذوق وجمال! يرجى كتابة اسم المنتج لمساعدتكِ فوراً."

# 2. إنشاء المسار (Endpoint) لاستقبال رسائل الواتساب
@app.get("/whatsapp")
def reply_to_whatsapp(msg: str):
    # تشغيل منطق الفحص على الرسالة القادمة من الرابط
    reply = generate_bot_reply(msg)
    # إرجاع النتيجة بصيغة JSON الذكية
    return {"bot_reply": reply}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) """



