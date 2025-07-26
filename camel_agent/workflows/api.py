from flask import Flask, request, jsonify
from flask_cors import CORS
from main import init_model, init_tools, create_agent, get_memory_context
from camel.messages import BaseMessage
from camel_agent.memory.memory import memory

app = Flask(__name__)
CORS(app)  # 启用CORS以允许前端访问

# 初始化AI组件
model = init_model()
tools = init_tools()
agent = create_agent(model, tools, memory)

# 用户偏好（可以后续改为数据库存储）
user_preferences = {
    "故事类型": "温暖、治愈的故事",
    "图片风格": "像素风+梦核风的风景画",
    "主角偏好": "喜欢回忆往事",
    "音乐风格要求": "梦核+像素风格"
}

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('message', '')
        
        if not user_input:
            return jsonify({'error': '消息不能为空'}), 400
            
        # 获取记忆上下文
        memory_context = get_memory_context(memory)
        
        # 构建增强的用户消息
        preference_context = f"\n用户偏好: {', '.join([f'{k}:{v}' for k, v in user_preferences.items()])}"
        
        enhanced_content = f"""
{memory_context}

{preference_context}

用户输入: {user_input}

重要提示: 请首先调用 get_memory 工具获取历史记忆，然后基于历史记忆承接上文继续故事，不要重新开始故事。
"""
        
        # 创建用户消息
        user_message = BaseMessage.make_user_message(
            role_name='User',
            content=enhanced_content
        )
        
        # 执行对话
        response = agent.step(user_message)
        
        # 提取回复内容
        reply_content = response.msgs[0].content if response.msgs else "抱歉，我现在无法回复。"
        
        return jsonify({
            'reply': reply_content,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 