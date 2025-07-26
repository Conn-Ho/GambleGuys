from camel.models import AzureOpenAIModel
from camel.types import ModelType
from camel.agents import ChatAgent
from camel.messages import BaseMessage
import os
import sys
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from camel_agent.toolkits.imgen_tool import ImageGenerationToolkit
from camel_agent.toolkits import MemoryToolkit
from camel_agent.memory.memory import memory
from camel_agent.prompts.leading_prompt import leading_prompt  # 使用故事引导提示词
from camel_agent.libs.imgen import generate_image

os.environ["AZURE_OPENAI_API_KEY"] = "ES3vLOAy8MUTMui8udIAk2vZO1Fo7qCBHKlaAvcprOXicYTkjzwbJQQJ99BDACHYHv6XJ3w3AAAAACOG4FT8"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://ai-philxia4932ai122623990161.openai.azure.com/"
os.environ["AZURE_API_VERSION"] = "2024-02-15-preview"
os.environ["AZURE_DEPLOYMENT_NAME"] = "gpt-4.1"  # 修改为正确的部署名称

DOUBAO_API_KEY = "9184e6fa-3267-4188-bf11-094bc7536823"
os.environ["ARK_API_KEY"] = DOUBAO_API_KEY

app = Flask(__name__)
CORS(app)

def init_model():
    try:
        return AzureOpenAIModel(
            model_type=ModelType.GPT_4O_MINI,
            model_config_dict={
                "temperature": 0.8,
                "max_tokens": 1200,
                "top_p": 0.95,
                "stream": False
            }
        )
    except Exception as e:
        print(f"Error initializing Azure OpenAI model: {str(e)}")
        return None

def init_tools():
    imgen_toolkit = ImageGenerationToolkit()
    memory_toolkit = MemoryToolkit(memory)
    all_tools = []
    all_tools.extend(imgen_toolkit.get_tools())
    all_tools.extend(memory_toolkit.get_tools())
    return all_tools, imgen_toolkit

def create_agent(model, tools, memory):
    """创建AI故事引导助手代理"""
    sys_msg = BaseMessage.make_assistant_message(
        role_name='AI Story Guide',
        content=str(leading_prompt)  # 使用leading_prompt中的故事引导逻辑
    )
    return ChatAgent(
        system_message=sys_msg,
        model=model,
        tools=tools,
        memory=memory
    )

def get_memory_context(memory):
    if hasattr(memory, 'chat_messages') and memory.chat_messages:
        chat_history = memory.chat_messages[-10:]
        if chat_history:
            context = "\n历史对话记忆\n"
            for i, msg in enumerate(chat_history):
                role = msg.role_name if hasattr(msg, 'role_name') else msg.role
                content = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
                context += f"{i+1}. {role}: {content}\n"
            return context + "请基于以上历史继续故事\n"
    return "\n新的对话开始\n"

def generate_image_prompt(story_content, model=None):
    """使用AzureOpenAI根据故事内容生成图片提示词"""
    if not model:
        # 如果没有传入模型，使用全局模型
        if 'model' in globals() and globals()['model'] is not None:
            used_model = globals()['model']
        else:
            used_model = init_model()
    else:
        used_model = model
    
    if not used_model:
        # 如果模型不可用，返回基础提示词
        print("⚠️ AzureOpenAI模型不可用，使用基础提示词")
        return f"pixel art dreamcore scene, {story_content[:50]}, nostalgic atmosphere, dreamy blue-purple tones, low saturation, 8-bit style"
    
    try:
        # 构建系统提示词
        system_prompt = """你是一个专业的图像提示词生成专家。请根据给定的故事内容，生成一个适合的英文图像提示词。

要求：
1. 风格：像素风+梦核风格 (pixel art + dreamcore)
2. 色调：蓝紫调，低饱和度
3. 氛围：怀旧、梦幻、温馨
4. 长度：不超过80个英文单词
5. 包含具体的场景、物体、氛围描述
6. 不要包含人物面部特征

示例格式：pixel art dreamcore scene, [具体场景描述], nostalgic atmosphere, soft blue-purple tones, low saturation, 8-bit style

请只返回提示词，不要添加其他解释。"""

        user_prompt = f"请为以下故事内容生成图像提示词：\n\n{story_content}"
        
        # 创建临时的ChatAgent来生成提示词
        sys_msg = BaseMessage.make_assistant_message(
            role_name='Image Prompt Generator',
            content=system_prompt
        )
        
        temp_agent = ChatAgent(
            system_message=sys_msg,
            model=used_model
        )
        
        user_message = BaseMessage.make_user_message(
            role_name='User',
            content=user_prompt
        )
        
        # 调用临时agent生成提示词
        response = temp_agent.step(user_message)
        
        if response and response.msgs and len(response.msgs) > 0:
            generated_prompt = response.msgs[0].content.strip()
            print(f"🎨 AI生成的提示词: {generated_prompt}")
            return generated_prompt
        else:
            print("⚠️ AzureOpenAI返回空响应，使用基础提示词")
            return f"pixel art dreamcore scene, {story_content[:50]}, nostalgic atmosphere, dreamy blue-purple tones, low saturation, 8-bit style"
            
    except Exception as e:
        print(f"❌ 生成图片提示词时出错: {str(e)}")
        # 出错时返回基础提示词
        base_prompt = "pixel art dreamcore scene"
        words = story_content.lower().split()
        keywords = [word for word in words if len(word) > 3 and word.isalpha()][:3]
        if keywords:
            return f"{base_prompt}, {', '.join(keywords)}, nostalgic atmosphere, dreamy blue-purple tones, low saturation, 8-bit style"
        return f"{base_prompt}, nostalgic atmosphere, dreamy blue-purple tones, low saturation, 8-bit style"

def extract_story_content(ai_response):
    story_pattern = re.search(r"---\s*(.*?)\s*---", ai_response, re.DOTALL)
    if story_pattern:
        return story_pattern.group(1).strip()
    
    story_match = re.search(r"Story（故事）[:：]\s*(.*?)(?=\n\s*Image（|一幅|一段|$)", ai_response, re.DOTALL)
    if story_match:
        return story_match.group(1).strip()
    
    cleaned = ai_response
    patterns_to_remove = [
        r'用户.*?[:：].*?\n',
        r'像素风.*?音乐.*?\n',
        r'8-bit.*?\n',
        r'梦核.*?\n',
        r'调用：.*?\n',
        r'参数：.*?\n',
        r'描述[:：].*?\n',
        r'\[.*?\]\(.*?\)',
        r'!\[.*?\]\(.*?\)',
        r'\{.*?\}',
    ]
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned)
    
    cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
    return cleaned.strip()

model = init_model()
tools, imgen_toolkit = init_tools()
agent = create_agent(model, tools, memory)

user_preferences = {
    "故事类型": "温暖、治愈的故事",
    "图片风格": "像素风+梦核风的风景画",
    "主角偏好": "喜欢回忆往事",
    "音乐风格要求": "梦核+像素风格"
}

# 故事场景计数器（在实际应用中应该保存到数据库）
scene_counter = 0
story_state = {
    "scenes_count": 0,
    "story_active": True,
    "last_scene_type": None
}

@app.route('/api/chat', methods=['POST'])
def chat():
    if model is None:
        return jsonify({
            'error': 'Azure OpenAI model initialization failed. Please check your configuration.',
            'status': 'error'
        }), 500
        
    global story_state
    
    data = request.json
    user_input = data.get('message', '')
    
    if not user_input:
        return jsonify({'error': '消息不能为空'}), 400
        
    try:
        # 更新场景计数
        story_state["scenes_count"] += 1
        
        # 获取记忆上下文
        memory_context = get_memory_context(memory)
        
        # 构建故事引导上下文
        story_guidance = f"""
当前场景数: {story_state["scenes_count"]}
故事状态: {"进行中" if story_state["story_active"] else "已结束"}

请遵循以下故事引导原则：
1. 回复字数限制在150字以内
2. 描述简洁明了，避免过多细节
3. 每次推进一个小情节
4. 每个场景持续约5分钟体验时间
5. 每10个场景后有20%概率触发BE结局
6. 玩家行为需符合当前世界观的人类能力范围
7. 根据剧情调整对话语气和玩家情绪
8. 包含10%的随机事件增加不可预测性

用户偏好: {', '.join([f'{k}:{v}' for k, v in user_preferences.items()])}
"""
        
        enhanced_content = f"""
{memory_context}

{story_guidance}

用户输入: {user_input}

请基于上述引导原则和历史记忆，继续推进故事发展。记住要保持故事的连贯性和情感一致性。
"""
        
        user_message = BaseMessage.make_user_message(
            role_name='User',
            content=enhanced_content
        )
        
        # 执行对话
        response = agent.step(user_message)
        full_reply = response.msgs[0].content if response.msgs else "抱歉，我现在无法回复。"
        
        # 提取故事内容
        story_content = extract_story_content(full_reply)
        
        # 初始化图片URL变量
        image_url = None
        
        # 每次对话都生成图片
        should_generate_image = True  # 简化：每次都生成图片
        
        if should_generate_image and story_content:
            prompt = generate_image_prompt(story_content, model)  # 传入模型参数
            print(f"🎨 准备生成图片，提示词: {prompt}")
            result = generate_image(prompt=prompt, api_key=DOUBAO_API_KEY)
            print(f"🎨 图片生成结果: {result}")
            if result.get("success"):
                image_url = result["image_url"]
                print(f"✅ 图片生成成功: {image_url}")
            else:
                print(f"❌ 图片生成失败: {result.get('error', 'Unknown error')}")
        
        # 检查是否达到结局条件
        if story_state["scenes_count"] >= 10 and story_state["scenes_count"] % 10 == 0:
            # 20%概率触发BE结局（简化版本）
            import random
            if random.random() < 0.2:
                story_state["story_active"] = False
                story_content += "\n\n[故事在此刻戛然而止...]"
        
        return jsonify({
            'reply': story_content,
            'image_url': image_url,
            'status': 'success',
            'scene_count': story_state["scenes_count"],
            'story_active': story_state["story_active"]
        })
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': '处理请求时发生错误，请稍后重试',
            'status': 'error'
        }), 500

@app.route('/api/test-image', methods=['POST'])
def test_image():
    data = request.json
    prompt = data.get('prompt', 'pixel art dreamcore scene, peaceful landscape')
    result = generate_image(prompt=prompt, api_key=DOUBAO_API_KEY)
    return jsonify({'result': result, 'status': 'success'})

@app.route('/api/debug-image', methods=['POST'])
def debug_image():
    """调试图片生成功能"""
    data = request.json
    prompt = data.get('prompt', 'pixel art dreamcore scene')
    
    print(f"调试 - 使用API Key: {DOUBAO_API_KEY[:10]}...")
    print(f"调试 - 生成提示词: {prompt}")
    
    result = generate_image(prompt=prompt, api_key=DOUBAO_API_KEY)
    
    print(f"调试 - 生成结果: {result}")
    
    return jsonify({
        'prompt': prompt,
        'api_key_preview': DOUBAO_API_KEY[:10] + "...",
        'result': result,
        'status': 'debug'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
