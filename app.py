# -*- coding: utf-8 -*-
from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

API_KEY = "sk-scitely-c9c3eb789bc3bf41ad5f8047dc808cb587db4f7923d69af449ad60317d76e370"

@app.route('/')
def home():
    return "Genisi is Live! 🚀", 200

@app.route('/genisi_engine', methods=['POST'])
def genisi_engine():
    data = request.json
    user_msg = data.get("message", "")
    img_url = data.get("image_url", None)

    # اختيار الموديل
    selected_model = "qwen3-vl-plus" if img_url else "deepseek-v3"

    # التنسيق المباشر (Raw Payload)
    payload = {
        "model": selected_model,
        "messages": [{"role": "user", "content": user_msg}],
        "stream": True
    }

    # إضافة صورة إذا وجدت
    if img_url:
        payload["messages"][0]["content"] = [
            {"type": "text", "text": user_msg},
            {"type": "image_url", "image_url": {"url": img_url}}
        ]

    def generate():
        # هنا السر: إرسال الطلب كأنه متصفح (Headers بشرية)
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            response = requests.post(
                "https://api.scitely.com/v1/chat/completions",
                headers=headers,
                json=payload,
                stream=True,
                timeout=60
            )
            
            for line in response.iter_lines():
                if line:
                    # تمرير السطر كما هو للواجهة الأمامية
                    yield f"{line.decode('utf-8')}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
