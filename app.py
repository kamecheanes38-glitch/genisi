# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import json

app = Flask(__name__)
CORS(app)  # لضمان عمل ميزة التسجيل عبر جوجل من أي موقع

# ترويسات تخطي حماية 403 (Keep it as is)
custom_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

# إعداد عميل OpenAI
client = OpenAI(
    api_key="sk-scitely-c9c3eb789bc3bf41ad5f8047dc808cb587db4f7923d69af449ad60317d76e370",
    base_url="https://api.scitely.com/v1",
    default_headers=custom_headers
)

@app.route('/genisi_engine', methods=['POST', 'OPTIONS'])
def genisi_engine():
    # إعدادات CORS اليدوية للمتصفحات
    if request.method == 'OPTIONS':
        return '', 204

    try:
        request_data = request.json
        user_input = request_data.get("message", "")
        image_url = request_data.get("image_url", None)
        uid = request_data.get("uid")  # معرف المستخدم القادم من Google Auth
        
        # التأكد من وجود UID (ميزة الأمان للتسجيل عبر جوجل)
        if not uid:
            return jsonify({"error": "Unauthorized: Please login with Google"}), 401

        # ملاحظة: تم إزالة جلب الذاكرة من Firestore هنا لجعله مستقلاً 
        # يمكنك إضافة نظام ملفات JSON بسيط بدلاً منه إذا أردت لاحقاً
        chat_history = [] 

        # --- منطق التوجيه والنموذج ---
        if image_url:
            selected_model = "qwen3-vl-plus"
            sys_msg = "أنت جينيسي البصري. حلل الصور والملفات المرفقة بدقة واشرحها للمستخدم بأسلوب دقيق ومرح."
            current_content = [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": user_input}
            ]
        elif any(word in user_input for word in ["حل", "احسب", "لماذا", "كيف", "برمج", "فكر"]):
            selected_model = "qwen3-235b-thinking"
            sys_msg = "أنت جينيسي العبقري. فكر بعمق وحل المشكلات المعقدة خطوة بخطوة."
            current_content = user_input
        else:
            selected_model = "deepseek-v3.2"
            sys_msg = "أنت جينيسي، المساعد المرح والصديق المقرب للمستخدم. رد بذكاء وفكاهة."
            current_content = user_input

        # بناء الرسائل
        messages = [{"role": "system", "content": sys_msg}] + chat_history + [{"role": "user", "content": current_content}]

        # طلب الرد من المحرك
        completion = client.chat.completions.create(
            model=selected_model,
            messages=messages,
            temperature=0.7
        )
        ai_reply = completion.choices[0].message.content

        # الرد النهائي للواجهة
        return jsonify({
            "status": "success",
            "reply": ai_reply,
            "engine": selected_model,
            "user_id": uid, # تأكيد هوية المستخدم المسجل بجوجل
            "save_to_drive_flag": True
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # تشغيل السيرفر على المنفذ 5000
    app.run(host='0.0.0.0', port=5000)
