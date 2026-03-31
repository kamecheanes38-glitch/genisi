# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
# السماح بجميع المصادر لضمان عمل الواجهة من أي مكان
CORS(app, resources={r"/*": {"origins": "*"}})

client = OpenAI(
    api_key="sk-scitely-c9c3eb789bc3bf41ad5f8047dc808cb587db4f7923d69af449ad60317d76e370",
    base_url="https://api.scitely.com/v1"
)

# ذاكرة الجلسات (تخزن في الرام مؤقتاً)
sessions = {}

@app.route('/')
def home():
    return "Genisi Engine is Running! 🚀", 200

@app.route('/genisi_engine', methods=['POST', 'OPTIONS'])
def genisi_engine():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.json
        user_input = data.get("message", "")
        uid = data.get("uid", "guest_user")
        
        # إدارة الذاكرة (حفظ آخر 6 رسائل لتركيز أفضل)
        if uid not in sessions: sessions[uid] = []
        history = sessions[uid][-6:]

        # نظام التوجيه (Thinking vs Normal)
        model = "qwen3-235b-thinking" if any(x in user_input for x in ["حل", "برمج", "لماذا"]) else "deepseek-v3.2"
        
        messages = [
            {"role": "system", "content": "أنت جينيسي، مساعد ذكي ومرح طوره AnesNT. واجهتك تشبه جيميناي وردودك منظمة."}
        ] + history + [{"role": "user", "content": user_input}]

        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        
        ai_reply = completion.choices[0].message.content

        # تحديث التاريخ
        sessions[uid].append({"role": "user", "content": user_input})
        sessions[uid].append({"role": "assistant", "content": ai_reply})

        return jsonify({"reply": ai_reply, "model": model})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
