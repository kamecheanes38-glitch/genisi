# -*- coding: utf-8 -*-
from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
from openai import OpenAI
import json
import os

app = Flask(__name__)
CORS(app)

# إعداد محرك جينيسي السريع (Step-3.5-Flash)
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

@app.route('/')
def health_check():
    return "Genisi Engine is Online! 🚀", 200

@app.route('/genisi_engine', methods=['POST'])
def genisi_engine():
    data = request.json
    user_input = data.get("message", "")

    def generate():
        try:
            # طلب البث المباشر (Streaming)
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "أنت جينيسي (Genisi)، مساعد ذكي وسريع، طورك المبرمج أنس (AnesNT). أجب دائماً بروح مرحة وصديقة."},
                    {"role": "user", "content": user_input}
                ],
                temperature=1,
                top_p=0.9,
                max_tokens=4096,
                stream=True
            )

            for chunk in completion:
                # التحقق من وجود محتوى في الرد
                if chunk.choices and chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    # نرسل البيانات بتنسيق EventStream
                    yield f"data: {json.dumps({'choices': [{'delta': {'content': text}}]})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'choices': [{'delta': {'content': 'خطأ تقني: ' + str(e)}}]})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    # تشغيل السيرفر على البورت الصحيح لـ Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
