import os
from openai import OpenAI

client = OpenAI(
    # 从环境变量中读取您的方舟API Key
    api_key=os.environ.get("ARK_API_KEY"), 
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    )
completion = client.chat.completions.create(
    # 将推理接入点 <Model>替换为 Model ID
    model="<Model>",
    messages=[
        {"role": "user", "content": "你好"}
    ]
)
print(completion.choices[0].message)