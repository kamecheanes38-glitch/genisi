# -*- coding: utf-8 -*-
from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
from openai import OpenAI
import json
import os

app = Flask(__name__)
CORS(app)

client = OpenAI(
    api_key="sk-scitely-c9c3eb789bc3bf41ad5f8047dc808cb587db4f7923d69af449ad60317d76e370",
    base_url="https://api.scitely.com/v1",
    default_headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
)

@app.route('/')
def home():
    return "Genisi Dual-Engine (Qwen + DeepSeek) is Live! 🚀", 200

@app.route('/genisi_engine', methods=['POST', 'OPTIONS'])
def genisi_engine():
    if request.method == 'OPTIONS': return '', 200

    data = request.json
    user_input = data.get("message", "")
    image_url = data.get("image_url", None)

    # اختيار الموديل تلقائياً
    if image_url:
        selected_model = "qwen3-vl-plus"
        system_msg = "أنت جينيسي البصري، خبير في تحليل الصور والملفات الدراسية."
        content = [
            {"type": "text", "text": user_input},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
    else:
        selected_model = "deepseek-v3.2"
        system_msg = "أنت جينيسي، مساعد ذكي ومرح وصديق مقرب . أجب بذكاء وخفة دم."
        content = user_input

    def generate():
        try:
            stream = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": content}
                ],
                stream=True,
                temperature=0.7
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': text})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'content': '⚠️ خطأ: ' + str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
