

import os
import sys
from typing import List, Optional
from camel.models import AzureOpenAIModel
from camel.types import ModelType
from camel.messages import BaseMessage

# 添加库路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libs.imgen import generate_image

from camel.toolkits.base import BaseToolkit
from camel.toolkits.openai_function import OpenAIFunction

class ImageGenerationToolkit(BaseToolkit):
    """图像生成工具包，使用豆包API提供文本到图像的生成功能。"""
    
    def __init__(self, api_key: Optional[str] = None):
        # 使用统一的API Key
        self.api_key = api_key or os.getenv("ARK_API_KEY") or "9184e6fa-3267-4188-bf11-094bc753682"
        
        self.llm_model = self._init_azure_openai()
    
    def _init_azure_openai(self) -> Optional[AzureOpenAIModel]:
        """初始化Azure OpenAI模型"""
        try:
            if not os.getenv("AZURE_OPENAI_ENDPOINT") or not os.getenv("AZURE_OPENAI_API_KEY"):
                return None
                
            model_config = {
                "temperature": 0.7,
                "max_tokens": 200,
                "top_p": 0.9,
                "stream": False
            }
            return AzureOpenAIModel(
                model_type=ModelType.GPT_4O_MINI,
                model_config_dict=model_config
            )
        except Exception as e:
            print(f"初始化Azure OpenAI模型失败: {str(e)}")
            return None
    
    def _optimize_prompt(self, story_content: str) -> str:
        """优化图片提示词"""
        if not self.llm_model:
  
            return f"pixel art dreamcore scene, {story_content[:100]}, nostalgic atmosphere, soft colors"
        
        try:
            system_prompt = "根据故事内容生成英文图像提示词。要求：梦核+像素风格，蓝紫调，低饱和，怀旧感。"
            
            user_message = BaseMessage.make_user_message(
                role_name='User',
                content=f"请为以下故事生成图像提示词：{story_content}"
            )
            
            system_message = BaseMessage.make_assistant_message(
                role_name='System',
                content=system_prompt
            )
            
            response = self.llm_model.run([system_message, user_message])
            
            if response and response.msgs:
                return response.msgs[0].content.strip()
            else:
                return f"pixel art dreamcore scene, {story_content[:100]}, nostalgic atmosphere, soft colors"
                
        except Exception as e:
            print(f"提示词优化失败: {str(e)}")
            return f"pixel art dreamcore scene, {story_content[:100]}, nostalgic atmosphere, soft colors"
    
    def generate_image(self, story_content: str) -> str:
        """根据故事内容生成图像。

        Args:
            story_content (str): 故事内容，将被优化为图片提示词

        Returns:
            str: 生成结果描述，包含图片URL或错误信息
        """
        try:
            # 优化提示词
            optimized_prompt = self._optimize_prompt(story_content)
            print(f"优化后的提示词: {optimized_prompt}")
            
            # 生成图片
            result = generate_image(
                prompt=optimized_prompt,
                api_key=self.api_key
            )
            
            if result["success"]:
                return f"图片生成成功: {result['image_url']}"
            else:
                return f"图片生成失败: {result['error']}"
                
        except Exception as e:
            return f"生成过程出错: {str(e)}"
    
    def get_tools(self) -> List[OpenAIFunction]:
        """获取工具列表"""
        image_tool = OpenAIFunction(self.generate_image)
        image_tool.set_function_name("generate_image")
        image_tool.set_function_description("根据故事内容生成梦核+像素风格图像")
        image_tool.set_paramter_description("story_content", "故事内容")
        
        return [image_tool]

# 导出
__all__ = ["ImageGenerationToolkit"]
