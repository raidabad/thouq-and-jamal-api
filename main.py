from fastapi import FastAPI
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
    uvicorn.run(app, host="0.0.0.0", port=8000)