# -*- coding: utf-8 -*-
from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
from openai import OpenAI
import json
import os

app = Flask(__name__)
CORS(app)

# إعداد المحرك مع الموديل العملاق الذي اخترته
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

@app.route('/')
def health_check():
    return "Genisi Engine (GPT-OSS-120B) is Online with Memory! 🧠🚀", 200

@app.route('/genisi_engine', methods=['POST'])
def genisi_engine():
    data = request.json
    
    # الذاكرة: نستقبل مصفوفة الرسائل كاملة من الواجهة
    messages_history = data.get("messages", [])
    
    # إذا كانت الواجهة ترسل رسالة واحدة فقط، نحولها لتنسيق مصفوفة
    if not messages_history:
        user_input = data.get("message", "")
        messages_history = [{"role": "user", "content": user_input}]

    # تثبيت هوية جينيسي وتذكيره بأنه صديق أنس
    system_instruction = {
        "role": "system", 
        "content": "أنت جينيسي (Genisi)، مساعد ذكي جداً وقوي، طورك المبرمج المبدع أنس (AnesNT). تذكر سياق المحادثة جيداً وأجب بدقة واحترافية."
    }
    
    # دمج التعليمات مع سجل المحادثة الكامل
    full_messages = [system_instruction] + messages_history

    def generate():
        try:
            # استخدام الموديل الذي اخترته: openai/gpt-oss-120b
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=full_messages,
                temperature=0.8, # رفعنا الحرارة قليلاً ليكون أكثر إبداعاً
                top_p=0.9,
                max_tokens=4096,
                stream=True
            )

            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'choices': [{'delta': {'content': text}}]})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'choices': [{'delta': {'content': 'خطأ تقني في المحرك: ' + str(e)}}]})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
