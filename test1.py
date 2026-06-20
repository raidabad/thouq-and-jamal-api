""" import re

# 1. الرسالة الأصلية القادمة من الواتساب مع التشويش
raw_message = "أريد سيروم... للشعر الجاف!!؟"

# 2. تنظيف النص (استبدال علامات الترقيم بفراغ)
# هذا السطر يخبر بايثون بحذف أي رمز ليس حرفاً عربياً أو إنجليزياً
cleaned_message = re.sub(r'[^\w\s]', '', raw_message)

print("النص بعد التنظيف:", cleaned_message) 
# سيطبع: أريد سيروم للشعر الجاف

# 3. التقطيع (Tokenization) تحويل الجملة إلى كلمات منفصلة
words = cleaned_message.split()
print("الكلمات المفردة:", words)
# سيطبع: ['أريد', 'سيروم', 'للشعر', 'الجاف'] """


import re

customer_text = "بكم سعر زيت الإكليل ... ؟؟"

# اكتب هنا سطر التنظيف باستخدام re.sub
cleaned_text = re.sub(r'[^\w\s]', '', customer_text)

# اكتب هنا سطر التقطيع باستخدام split
words = cleaned_text.split()

# اطباع النتيجة النهائية
print(words)