# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import json
import os

app = Flask(__name__)
CORS(app)  # لضمان اتصال موقعك (Frontend) بالسيرفر بدون مشاكل

# إعدادات تخطي الحماية (Headers)
custom_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://genisi.web.app",
    "Referer": "https://genisi.web.app/"
}

# إعداد محرك OpenAI للاتصال بـ Scitely
client = OpenAI(
    api_key="sk-scitely-c9c3eb789bc3bf41ad5f8047dc808cb587db4f7923d69af449ad60317d76e370",
    base_url="https://api.scitely.com/v1",
    default_headers=custom_headers
)

# ذاكرة موحدة بسيطة (تعتمد على RAM السيرفر حالياً)
# تخزن آخر الرسائل لكل مستخدم بناءً على الـ UID الخاص بجوجل
sessions_memory = {}

@app.route('/genisi_engine', methods=['POST'])
def genisi_engine():
    try:
        request_data = request.json
        user_input = request_data.get("message", "")
        image_url = request_data.get("image_url", None)
        uid = request_data.get("uid") # المعرف القادم من تسجيل دخول جوجل من موقعك

        if not uid:
            return jsonify({"error": "يجب تسجيل الدخول عبر جوجل أولاً"}), 401

        # --- إدارة الذاكرة الموحدة ---
        if uid not in sessions_memory:
            sessions_memory[uid] = []
        
        # جلب سياق المحادثة (آخر 4 رسائل لضمان استمرارية الذاكرة)
        context = sessions_memory[uid][-4:]

        # --- منطق التوجيه الذكي للموديلات ---
        if image_url:
            selected_model = "qwen3-vl-plus"
            sys_msg = "أنت جينيسي البصري. حلل الصور والملفات بدقة واشرحها للمستخدم بأسلوب مرح."
            content = [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": user_input}
            ]
        elif any(word in user_input for word in ["حل", "احسب", "برمج", "كيف", "لماذا", "فكر"]):
            selected_model = "qwen3-235b-thinking"
            sys_msg = "أنت جينيسي العبقري. استخدم قدراتك التفكيرية العميقة لحل المسائل المعقدة للمستخدم خطوة بخطوة."
            content = user_input
        else:
            selected_model = "deepseek-v3.2"
            sys_msg = "أنت جينيسي، المساعد المرح والصديق المقرب للمستخدم. رد بذكاء وفكاهة."
            content = user_input

        # بناء الرسائل مع دمج الذاكرة
        messages = [{"role": "system", "content": sys_msg}] + context + [{"role": "user", "content": content}]

        # طلب الرد من OpenAI API
        completion = client.chat.completions.create(
            model=selected_model,
            messages=messages,
            temperature=0.7
        )
        ai_reply = completion.choices[0].message.content

        # تحديث الذاكرة الموحدة (حفظ السؤال والجواب)
        sessions_memory[uid].append({"role": "user", "content": user_input})
        sessions_memory[uid].append({"role": "assistant", "content": ai_reply})

        return jsonify({
            "status": "success",
            "reply": ai_reply,
            "engine": selected_model,
            "uid": uid,
            "save_to_drive_flag": True
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # بورت 5000 هو الافتراضي لـ Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
