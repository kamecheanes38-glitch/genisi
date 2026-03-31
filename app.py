# -*- coding: utf-8 -*-
from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
from openai import OpenAI
import json
import os

app = Flask(__name__)
CORS(app)

# إعداد العميل بنموذج NVIDIA الجديد
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

@app.route('/')
def home():
    return "Genisi Engine (Step-3.5-Flash) is Flying! 🚀", 200

@app.route('/genisi_engine', methods=['POST'])
def genisi_engine():
    data = request.json
    user_input = data.get("message", "")

    def generate():
        try:
            # طلب البث من NVIDIA
            stream = client.chat.completions.create(
                model="stepfun-ai/step-3.5-flash",
                messages=[
                    {"role": "system", "content": "أنت جينيسي (Genisi)، مساعد ذكي وسريع جداً، طورك أنس (AnesNT). أجب بأسلوب مرح وذكي."},
                    {"role": "user", "content": user_input}
                ],
                temperature=1,
                top_p=0.9,
                max_tokens=4096,
                stream=True
            )

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    # نرسل البيانات بتنسيق يفهمه الـ index.html الخاص بنا
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'choices': [{'delta': {'content': content}}]})}\n\n"
            
            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'choices': [{'delta': {'content': 'خطأ: ' + str(e)}}]})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    # بورت Render التلقائي
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
