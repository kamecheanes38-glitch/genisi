from openai import OpenAI

client = OpenAI(
    api_key="sk-scitely-c9c3eb789bc3bf41ad5f8047dc808cb587db4f7923d69af449ad60317d76e370",
    base_url="https://api.scitely.com/v1"
)

# Streaming
stream = client.chat.completions.create(
    model="deepseek-v3.2",
    messages=[
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": ""
      }
    ],
    temperature=0.7,
    max_tokens=4096,
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
