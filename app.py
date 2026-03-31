# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
# حل مشكلة الـ CORS نهائياً للسماح بالاتصال من المتصفح
CORS(app, resources={r"/*": {"origins": "*"}})

# إعدادات العميل (Scitely / OpenAI)
client = OpenAI(
    api_key="sk-scitely-c9c3eb789bc3bf41ad5f8047dc808cb587db4f7923d69af449ad60317d76e370",
    base_url="https://api.scitely.com/v1"
)

# نظام الذاكرة المؤقتة (Session Memory)
sessions = {}

@app.route('/')
def health_check():
    return "Genisi Engine is Live! 🚀", 200

@app.route('/genisi_engine', methods=['POST', 'OPTIONS'])
def genisi_engine():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.json
        user_input = data.get("message", "")
        uid = data.get("uid", "guest")
        image_url = data.get("image_url", None)

        # إدارة الذاكرة (آخر 4 رسائل)
        if uid not in sessions: sessions[uid] = []
        history = sessions[uid][-4:]

        # التوجيه الذكي للموديلات
        if image_url:
            model, sys_msg = "qwen3-vl-plus", "أنت جينيسي البصري. حلل الصور بدقة ومرح."
            content = [{"type": "image_url", "image_url": {"url": image_url}}, {"type": "text", "text": user_input}]
        elif any(w in user_input for w in ["حل", "فكر", "برمج", "لماذا"]):
            model, sys_msg = "qwen3-235b-thinking", "أنت جينيسي العبقري. فكر بعمق وحل المشكلات خطوة بخطوة."
            content = user_input
        else:
            model, sys_msg = "deepseek-v3.2", "أنت جينيسي، المساعد المرح والصديق المقرب."
            content = user_input

        # طلب الرد
        msgs = [{"role": "system", "content": sys_msg}] + history + [{"role": "user", "content": content}]
        completion = client.chat.completions.create(model=model, messages=msgs, temperature=0.7)
        ai_reply = completion.choices[0].message.content

        # حفظ في الذاكرة
        sessions[uid].append({"role": "user", "content": user_input})
        sessions[uid].append({"role": "assistant", "content": ai_reply})

        return jsonify({"reply": ai_reply, "engine": model})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
