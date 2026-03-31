# -*- coding: utf-8 -*-
from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

API_KEY = "sk-scitely-c9c3eb789bc3bf41ad5f8047dc808cb587db4f7923d69af449ad60317d76e370"

# محاكاة تامة لمتصفح إنسان حقيقي
HUMAN_HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/event-stream",
    "Referer": "https://api.scitely.com/",
    "Origin": "https://api.scitely.com"
}

@app.route('/')
def home():
    return "جينيسي يحييك يا أنس! 🌟", 200

@app.route('/genisi_engine', methods=['POST'])
def genisi_engine():
    data = request.json
    user_input = data.get("message", "")
    image_url = data.get("image_url", None)

    # اختيار "العقل" المناسب
    model = "qwen3-vl-plus" if image_url else "deepseek-v3"
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "أنت جينيسي، صديق أنس المقرب ومساعده الذكي. لغتك مرحة وبشرية جداً."},
            {"role": "user", "content": [
                {"type": "text", "text": user_input},
                {"type": "image_url", "image_url": {"url": image_url}}
            ] if image_url else user_input}
        ],
        "stream": True
    }

    def generate():
        try:
            # نرسل الطلب وكأننا إنسان يضغط على زر
            response = requests.post(
                "https://api.scitely.com/v1/chat/completions",
                headers=HUMAN_HEADERS,
                json=payload,
                stream=True,
                timeout=60
            )

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        if "[DONE]" in decoded_line: break
                        try:
                            json_data = json.loads(decoded_line[6:])
                            content = json_data['choices'][0]['delta'].get('content', '')
                            if content:
                                yield f"data: {json.dumps({'content': content})}\n\n"
                        except: continue
        except Exception as e:
            yield f"data: {json.dumps({'content': 'يا أنس، يبدو أن هناك حاجزاً.. سأحاول مجدداً!'})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
