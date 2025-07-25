

import os
import sys
from typing import List, Optional, Dict, Any

# 添加库路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libs.imgen import generate_image

try:
    from camel.toolkits.base import BaseToolkit
    from camel.toolkits.openai_function import OpenAIFunction
    from camel.toolkits import FunctionTool
except ImportError:
    # 如果无法导入CAMEL框架，创建基础类
    class BaseToolkit:
        def get_tools(self):
            raise NotImplementedError("Subclasses must implement this method.")
    
    class OpenAIFunction:
        def __init__(self, func):
            self.func = func
            
    class FunctionTool:
        def __init__(self, func):
            self.func = func


def create_image(prompt: str, size: str = "1024x1024", steps: int = 20, guidance: float = 7.5) -> Dict[str, Any]:
    """Generate an image using text prompt.
    
    Args:
        prompt: Text description of the desired image
        size: Image size in format 'widthxheight'
        steps: Number of inference steps
        guidance: Guidance scale for stable diffusion
        
    Returns:
        Dict containing generation result with keys:
        - success: bool indicating if generation succeeded
        - image_url: URL of generated image if successful
        - error: Error message if failed
    """
    try:
        api_key = os.getenv("SILICONFLOW_API_KEY", "sk-rpbdfcumdlwdfssveutdyweficaabukciujbkoltmdsnjiba")
        result = generate_image(
            prompt=prompt,
            api_key=api_key,
            image_size=size,
            num_inference_steps=steps,
            guidance_scale=guidance
        )
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# 使用 FunctionTool 包装函数
create_image_tool = FunctionTool(create_image)


class ImageGenerationToolkit(BaseToolkit):
    """Image generation toolkit that provides text-to-image generation capabilities."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv(
            "SILICONFLOW_API_KEY", 
            "sk-rpbdfcumdlwdfssveutdyweficaabukciujbkoltmdsnjiba"
        )
    
    def generate_image(self, prompt: str) -> str:
        try:
            result = generate_image(
                prompt=prompt,
                api_key=self.api_key,
                image_size="1024x1024",
                num_inference_steps=20,
                guidance_scale=7.5
            )
            
            if result["success"]:
                return f"\n提示词: {prompt}\n图像URL: {result['image_url']}"
            else:
                return f"\n提示词: {prompt}\n错误: {result['error']}"
                
        except Exception as e:
            return f"生成过程出错: {str(e)}"
    
    def get_tools(self) -> List[OpenAIFunction]:
        return [OpenAIFunction(self.generate_image), create_image_tool]


# 导出
__all__ = ["ImageGenerationToolkit", "create_image", "create_image_tool"]
