from camel.models import AzureOpenAIModel
from camel.types import ModelType
from camel.agents import ChatAgent
from camel.messages import BaseMessage
import os
import sys
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from camel_agent.toolkits.imgen_tool import ImageGenerationToolkit
from camel_agent.toolkits import MemoryToolkit
from camel_agent.memory.memory import memory
from camel_agent.prompts.leading_prompt import leading_prompt  # 使用故事引导提示词
from camel_agent.libs.imgen import generate_image

os.environ["AZURE_OPENAI_API_KEY"] = "ES3vLOAy8MUTMui8udIAk2vZO1Fo7qCBHKlaAvcprOXicYTkjzwbJQQJ99BDACHYHv6XJ3w3AAAAACOG4FT8"
os.environ["AZURE_OPENAI_BASE_URL"] = "https://ai-philxia4932ai122623990161.openai.azure.com/"
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

def generate_image_prompt(story_content):
    base_prompt = "pixel art dreamcore scene"
    words = story_content.lower().split()
    keywords = [word for word in words if len(word) > 3 and word.isalpha()][:5]
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

def generate_music(emotion_value):
    """根据情绪值生成音乐"""
    print(f"音乐生成调试: 接收情绪值 {emotion_value}")
    try:
        # 调用音乐生成服务
        response = requests.post(
            "http://localhost:8080/generate",
            json={"emotion": emotion_value},
            timeout=10
        )
        print(f"音乐生成API响应状态: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"音乐生成结果: {result}")
            if result.get("status") == "success":
                # 由于是实时音乐流，返回成功状态而不是具体URL
                music_info = f"音乐已生成: {result.get('mapped_emotion', 'Unknown')} (强度: {result.get('intensity', 0):.2f})"
                print(f"音乐生成成功: {music_info}")
                return music_info
            return None
    except Exception as e:
        print(f"Error generating music: {str(e)}")
        print(f"音乐生成异常 - 情绪值: {emotion_value}")
    return None

def process_parallel_generation(story_content, emotion):
    """并行处理图片和音乐生成"""
    print(f"并行生成开始 - 故事长度: {len(story_content)}, 情绪值: {emotion}")
    image_url = None
    music_url = None
    
    def generate_image_task():
        nonlocal image_url
        prompt = generate_image_prompt(story_content)
        print(f"图片生成提示词: {prompt}")
        result = generate_image(prompt=prompt, api_key=DOUBAO_API_KEY)
        print(f"图片生成结果: {result.get('success', False)}")
        if result.get("success"):
            image_url = result["image_url"]
            
    def generate_music_task():
        nonlocal music_url
        print(f"开始生成音乐，情绪值: {emotion}")
        music_url = generate_music(emotion)
        print(f"音乐生成完成: {music_url is not None}")
    
    # 创建并启动线程
    image_thread = threading.Thread(target=generate_image_task)
    music_thread = threading.Thread(target=generate_music_task)
    
    image_thread.start()
    music_thread.start()
    
    # 等待所有线程完成
    image_thread.join()
    music_thread.join()
    
    print(f"并行生成完成 - 图片: {image_url is not None}, 音乐: {music_url is not None}")
    return image_url, music_url

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
    emotion = data.get('emotion', 0.5)  # 接收情绪参数，默认为中性 0.5
    
    # 详细的情绪日志记录
    print(f"\n=== 情绪调试日志 ===")
    print(f"接收到的原始情绪值: {emotion} (类型: {type(emotion)})")
    print(f"用户输入: '{user_input}'")
    print(f"当前场景数: {story_state['scenes_count'] + 1}")
    
    if not user_input:
        return jsonify({'error': '消息不能为空'}), 400
        
    try:
        # 更新场景计数
        story_state["scenes_count"] += 1
        
        # 获取记忆上下文
        memory_context = get_memory_context(memory)
        
        # 根据情绪值调整故事基调
        emotion_guidance = ""
        emotion_category = ""
        if emotion < 0.3:
            emotion_guidance = "当前情绪偏消极，故事应该更温暖治愈，给予希望和力量"
            emotion_category = "消极"
        elif emotion < 0.7:
            emotion_guidance = "当前情绪平和，保持故事的平静流畅，适度推进剧情"
            emotion_category = "平和"
        else:
            emotion_guidance = "当前情绪愉悦，故事可以更加欢快明朗，增添一些有趣的元素"
            emotion_category = "愉悦"
        
        print(f"情绪分类: {emotion_category}")
        print(f"情绪指导文本: {emotion_guidance}")
        
        # 构建故事引导上下文
        story_guidance = f"""
当前场景数: {story_state["scenes_count"]}
故事状态: {"进行中" if story_state["story_active"] else "已结束"}
情绪基调: {emotion_guidance}

请遵循以下故事引导原则：
1. 回复字数限制在150字以内
2. 描述简洁明了，避免过多细节
3. 每次推进一个小情节
4. 每个场景持续约5分钟体验时间
5. 每10个场景后有20%概率触发BE结局
6. 玩家行为需符合当前世界观的人类能力范围
7. 根据剧情和当前情绪基调调整对话语气
8. 包含10%的随机事件增加不可预测性

用户偏好: {', '.join([f'{k}:{v}' for k, v in user_preferences.items()])}
"""
        
        enhanced_content = f"""
{memory_context}

{story_guidance}

用户输入: {user_input}

请基于上述引导原则和历史记忆，继续推进故事发展。记住要保持故事的连贯性和情感一致性。
"""
        
        print(f"构建的完整提示词长度: {len(enhanced_content)} 字符")
        print(f"提示词中的情绪部分: {emotion_guidance}")
        
        user_message = BaseMessage.make_user_message(
            role_name='User',
            content=enhanced_content
        )
        
        # 执行对话
        response = agent.step(user_message)
        full_reply = response.msgs[0].content if response.msgs else "抱歉，我现在无法回复。"
        
        print(f"AI回复原文长度: {len(full_reply)} 字符")
        
        # 提取故事内容
        story_content = extract_story_content(full_reply)
        print(f"提取的故事内容长度: {len(story_content)} 字符")
        print(f"故事内容预览: {story_content[:100]}...")
        
        # 检查是否应该生成图片和音乐
        image_url = None
        music_url = None
        should_generate = (
            story_state["scenes_count"] % 3 == 0 or  # 每3个场景生成一次
            "看到" in user_input or "风景" in user_input or  # 用户提到视觉内容
            len(story_content) > 80  # 故事内容较长时
        )
        
        print(f"是否触发媒体生成: {should_generate}")
        if should_generate:
            print(f"触发原因: 场景数%3={story_state['scenes_count'] % 3}, 用户提到视觉={'看到' in user_input or '风景' in user_input}, 故事长度={len(story_content)}>80")
        
        if should_generate and story_content:
            print(f"开始并行生成图片和音乐...")
            print(f"传递给音乐生成的情绪值: {emotion}")
            image_url, music_url = process_parallel_generation(story_content, emotion)
            print(f"生成结果 - 图片URL: {image_url is not None}, 音乐URL: {music_url}")
        
        # 检查是否达到结局条件
        if story_state["scenes_count"] >= 10 and story_state["scenes_count"] % 10 == 0:
            import random
            ending_chance = random.random()
            print(f"结局检查: 场景数={story_state['scenes_count']}, 随机值={ending_chance:.3f}, 触发概率=0.2")
            if ending_chance < 0.2:
                story_state["story_active"] = False
                story_content += "\n\n[故事在此刻戛然而止...]"
                print("触发BE结局!")
        
        print(f"=== 最终响应 ===")
        print(f"故事激活状态: {story_state['story_active']}")
        print(f"场景计数: {story_state['scenes_count']}")
        print(f"情绪分类: {emotion_category}")
        print(f"包含图片: {image_url is not None}")
        print(f"包含音乐: {music_url is not None}")
        print(f"==================\n")
        
        return jsonify({
            'reply': story_content,
            'image_url': image_url,
            'music_url': music_url,
            'status': 'success',
            'scene_count': story_state["scenes_count"],
            'story_active': story_state["story_active"],
            # 添加调试信息到响应中
            'debug_info': {
                'emotion_value': emotion,
                'emotion_category': emotion_category,
                'emotion_guidance': emotion_guidance,
                'should_generate_media': should_generate,
                'story_length': len(story_content)
            }
        })
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        print(f"Error details - emotion: {emotion}, user_input: {user_input}")
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

# 在文件末尾添加测试端点
@app.route('/api/test-debug', methods=['GET'])
def test_debug():
    print("=== 测试调试输出 ===")
    print("这是一个测试调试信息")
    print("如果你能看到这个，说明调试输出正常工作")
    print("=====================")
    return jsonify({'message': '调试测试成功'})

@app.route('/api/test-emotion', methods=['POST'])
def test_emotion():
    """专门用于测试情绪调试的端点"""
    data = request.json if request.json else {}
    emotion = data.get('emotion', 0.5)
    user_input = data.get('message', '测试情绪调试')
    
    print(f"\n=== 情绪调试测试 ===")
    print(f"接收到的原始情绪值: {emotion} (类型: {type(emotion)})")
    print(f"用户输入: '{user_input}'")
    
    # 情绪分类测试
    emotion_category = ""
    emotion_guidance = ""
    if emotion < 0.3:
        emotion_guidance = "当前情绪偏消极，故事应该更温暖治愈，给予希望和力量"
        emotion_category = "消极"
    elif emotion < 0.7:
        emotion_guidance = "当前情绪平和，保持故事的平静流畅，适度推进剧情"
        emotion_category = "平和"
    else:
        emotion_guidance = "当前情绪愉悦，故事可以更加欢快明朗，增添一些有趣的元素"
        emotion_category = "愉悦"
    
    print(f"情绪分类: {emotion_category}")
    print(f"情绪指导文本: {emotion_guidance}")
    print(f"========================\n")
    
    return jsonify({
        'emotion_value': emotion,
        'emotion_category': emotion_category,
        'emotion_guidance': emotion_guidance,
        'status': 'debug_success'
    })

if __name__ == '__main__':
    # 添加启动时的调试测试
    print("\n=== 调试功能测试 ===")
    print("服务器启动成功，调试日志功能已激活")
    print("测试调试输出: curl http://localhost:8000/api/test-debug")
    print("测试情绪调试: curl -X POST http://localhost:8000/api/test-emotion -H 'Content-Type: application/json' -d '{\"emotion\": 0.8, \"message\": \"测试\"}'")
    print("完整聊天测试: curl -X POST http://localhost:8000/api/chat -H 'Content-Type: application/json' -d '{\"message\": \"开始冒险\", \"emotion\": 0.8}'")
    print("========================\n")
    
    app.run(host='0.0.0.0', port=8000)
