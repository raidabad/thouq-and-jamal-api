from fastapi import FastAPI, Request
import requests

app = FastAPI()

# بيانات حسابك الفعالة في UltraMsg
ULTRAMSG_INSTANCE = "instance181605"
ULTRAMSG_TOKEN = "lcc1iapeumtgb5dj"

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    try:
        data = await request.json()
        print("البيانات المستقبلة من الواتساب:", data) # لمراقبة المدخلات في Render Logs
        
        # استخراج تفاصيل الرسالة بناءً على الهيكل القياسي لـ UltraMsg
        msg_data = data.get("data", {})
        if isinstance(msg_data, list) and len(msg_data) > 0:
            msg_data = msg_data[0]
            
        if not msg_data or "body" not in msg_data:
            return {"status": "no_message_body"}
            
        incoming_msg = str(msg_data.get("body", "")).strip().lower() # نص رسالة الزبون
        sender_number = msg_data.get("from")               # رقم جوال الزبون
        is_from_me = msg_data.get("fromMe")                 # هل الرسالة صادرة مني؟
        
        # لمنع البوت من الرد على نفسه والدخول في حلقة مفرغة
        if is_from_me or str(is_from_me).lower() == "true":
            return {"status": "ignored"}
            
        # منطق الرد الذكي لمتجر ذوق وجمال (صابونة الشعر الخضراء) - نسخة صنعاء
        bot_reply = ""
        
        # إذا استفسر عن الصابونة أو العرض أو الهدية
        if any(word in incoming_msg for word in ["مرحبا", "صابون", "صابونة", "الخضراء", "مشط", "هدية", "العرض"]):
            bot_reply = (
                "أهلاً بك! صابونة الشعر الخضراء الطبيعية متوفرة الآن في متجر ذوق وجمال لتغذية الشعر وتقويته. 🌿🧼\n\n"
                "🔥 **العرض الخاص الحالي:**\n"
                "💰 السعر: 8000 ريال يمني فقط!\n"
                "🚗 التوصيل: مجاني تماماً داخل صنعاء! 🛵💨\n"
                "🎁 الهدية: مشط متميز مجاناً مع كل صابونة!\n\n"
                "للطلب الفوري، يرجى تزويدنا بالاسم والعنوان بالتفصيل وسنقوم بتجهيز طلبك وتوصيله إليك فوراً! 🤝"
            )
            
        # إذا استفسر عن السعر أو التوصيل أو الشحن
        elif any(word in incoming_msg for word in ["السعر", "بكم", "قيمة", "توصيل", "شحن"]):
            bot_reply = (
                "أهلاً بك في متجر ذوق وجمال! ✨\n\n"
                "نوفر لكم خدمة التوصيل المجاني والسريع مباشرة إلى باب بيتك داخل صنعاء! 🚗💨\n\n"
                "العرض الحالي على (صابونة الشعر الخضراء):\n"
                "السعر 8000 ريال فقط، والتوصيل مجاني، وبتحصل على مشط هدية! 🎁\n\n"
                "إذا أحببت قراءة تفاصيل أكثر اكتب كلمة (صابونة)."
            )
            
        # إذا استفسر عن موقع المتجر
        elif any(word in incoming_msg for word in ["الموقع", "أين", "مكان", "صنعاء"]):
            bot_reply = "متجر ذوق وجمال متواجد في صنعاء، ونوفر خدمة التوصيل المجاني والسريع مباشرة إلى موقعك داخل العاصمة! 🏙️🛵"
            
        # الرد الترحيبي الافتراضي
        else:
            bot_reply = (
                "أهلاً بك في متجر ذوق وجمال! ✨\n\n"
                "نحن متخصصون في منتجات العناية بالشعر، ومنتجنا الحصري حالياً هو (صابونة الشعر الخضراء) الطبيعية.\n\n"
                "💡 لدينا عرض لفترة محدودة: صابونة بـ 8000 ريال + توصيل مجاني (داخل صنعاء) + مشط هدية! 🎁\n\n"
                "للاستفسار أو الطلب اكتب (صابونة)، أو اترك رسالتك وسيرد عليك أحد موظفينا قريباً."
            )
            
        # إرسال الرد تلقائياً إلى جوال العميل عبر API الخاص بـ UltraMsg
        url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE}/messages/chat"
        payload = {
            "token": ULTRAMSG_TOKEN,
            "to": sender_number,
            "body": bot_reply
        }
        headers = {"content-type": "application/x-www-form-urlencoded"}
        
        # إطلاق الرسالة تلقائياً
        response = requests.post(url, data=payload, headers=headers)
        print("حالة إرسال الرد من UltraMsg:", response.status_code, response.text)
        
        return {"status": "success"}
        
    except Exception as e:
        print(f"حدث خطأ أثناء معالجة الويب هوك: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
