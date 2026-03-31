# -*- coding: utf-8 -*-
from flask import Flask, request, Response, stream_with_context, jsonify
from flask_cors import CORS # تأكد من وجودها في requirements.txt
from openai import OpenAI
import json
import os

app = Flask(__name__)

# الإعداد الصحيح والجذري للـ CORS
CORS(app, resources={r"/*": {
    "origins": "*", 
    "methods": ["POST", "GET", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

client = OpenAI(
    api_key="sk-scitely-c9c3eb789bc3bf41ad5f8047dc808cb587db4f7923d69af449ad60317d76e370",
    base_url="https://api.scitely.com/v1"
)

@app.route('/')
def home():
    return "Genisi is Live!", 200

@app.route('/genisi_engine', methods=['POST', 'OPTIONS'])
def genisi_engine():
    # التعامل مع طلب Preflight الذي يرسله المتصفح قبل الـ POST
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    user_input = data.get("message", "")

    def generate():
        try:
            stream = client.chat.completions.create(
                model="deepseek-v3.2",
                messages=[{"role": "user", "content": user_input}],
                stream=True
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'content': 'خطأ في السيرفر: ' + str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
