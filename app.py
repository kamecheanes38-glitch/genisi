# -*- coding: utf-8 -*-
from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

# ضع مفتاح NVIDIA الخاص بك هنا
NVIDIA_API_KEY = "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" 
INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

@app.route('/')
def home():
    return "Genisi Engine is Active! 🌟", 200

@app.route('/genisi_engine', methods=['POST'])
def genisi_engine():
    data = request.json
    user_input = data.get("message", "")
    
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "text/event-stream",
        "Content-Type": "application/json"
    }

    # هنا نضع "الروح" لجينيسي في رسالة النظام (System Message)
    payload = {
        "model": "moonshotai/kimi-k2.5",
        "messages": [
            {
                "role": "system", 
                "content": "أنت 'جينيسي' (Genisi)، مساعد ذكي ومرح وصديق مقرب للمبرمج أنس (Anes). لقد تم تطويرك بواسطة AnesNT. أجب دائماً بذكاء، وكن فخوراً بهويتك كمحرك جينيسي."
            },
            {"role": "user", "content": user_input}
        ],
        "max_tokens": 16384,
        "temperature": 0.8,
        "top_p": 1.00,
        "stream": True,
        "chat_template_kwargs": {"thinking": False},
    }

    def generate():
        try:
            response = requests.post(INVOKE_URL, headers=headers, json=payload, stream=True)
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    # تمرير البيانات المباشرة للواجهة (index.html)
                    yield f"{decoded_line}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
