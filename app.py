# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

API_KEY = "sk-scitely-c9c3eb789bc3bf41ad5f8047dc808cb587db4f7923d69af449ad60317d76e370"

@app.route('/')
def home():
    return "جينيسي جاهز للعمل! 🚀", 200

@app.route('/genisi_engine', methods=['POST'])
def genisi_engine():
    try:
        data = request.get_json()
        user_input = data.get("message", "")
        image_url = data.get("image_url", None)

        # نختار الموديل بناءً على وجود صورة
        model = "qwen3-vl-plus" if image_url else "deepseek-v3"
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "أنت جينيسي، مساعد أنس الذكي والمرح."},
                {"role": "user", "content": user_input}
            ],
            "stream": False # نلغي الـ Stream مؤقتاً للتجربة
        }

        # نرسل الطلب بـ Timeout محدد (30 ثانية) لكي لا يظل السيرفر معلقاً
        response = requests.post(
            "https://api.scitely.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            reply = result['choices'][0]['message']['content']
            return jsonify({"reply": reply})
        else:
            return jsonify({"error": f"Scitely responded with {response.status_code}"}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
