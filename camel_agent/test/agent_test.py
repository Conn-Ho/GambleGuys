from camel.models import AzureOpenAIModel
from camel.types import ModelType
from camel.agents import ChatAgent
from camel.messages import BaseMessage
import os

# 设置Azure OpenAI环境变量
os.environ["AZURE_OPENAI_API_KEY"] = "ES3vLOAy8MUTMui8udIAk2vZO1Fo7qCBHKlaAvcprOXicYTkjzwbJQQJ99BDACHYHv6XJ3w3AAAAACOG4FT8"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://ai-philxia4932ai122623990161.openai.azure.com/"
os.environ["AZURE_API_VERSION"] = "2024-02-15-preview"
os.environ["AZURE_DEPLOYMENT_NAME"] = "gpt-4.1"

# Azure OpenAI配置
model_config = {
    "temperature": 0.7,
    "max_tokens": 800,
    "top_p": 0.95,
    "stream": False
}

# 初始化Azure OpenAI模型
model = AzureOpenAIModel(
    model_type=ModelType.GPT_4O_MINI,
    model_config_dict=model_config
)

# 创建系统消息
sys_msg = BaseMessage.make_assistant_message(
    role_name='Assistant', 
    content='你是一个友好的助手。'
)

# 创建聊天代理
agent = ChatAgent(
    system_message=sys_msg,
    model=model
)

# 创建用户消息
user_message = BaseMessage.make_user_message(
    role_name='User',
    content="你好，CAMEL‑AI 在 Azure OpenAI 环境中可以做什么？"
)

# 测试对话
response = agent.step(user_message)
print(response.msgs[0].content)
