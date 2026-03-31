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
    base_url="https://api.scitely.com/v1"
)

@app.route('/genisi_engine', methods=['POST'])
def genisi_engine():
    data = request.json
    user_input = data.get("message", "")

    def generate():
        stream = client.chat.completions.create(
            model="deepseek-v3.2", # تأكد من اسم الموديل المدعوم في Scitely
            messages=[{"role": "user", "content": user_input}],
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                # نرسل البيانات بتنسيق يفهمه المتصفح (SSE)
                yield f"data: {json.dumps({'content': content})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
