import os
from typing import Dict, Any, Optional
from volcenginesdkarkruntime import Ark

def generate_image(prompt: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    # 使用传入的API Key，如果没有则使用环境变量或默认值
    actual_api_key = api_key or os.getenv("ARK_API_KEY") or "9184e6fa-3267-4188-bf11-094bc7536823"
    
    if not actual_api_key:
        return {"success": False, "error": "未提供API密钥"}
    
    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=actual_api_key,
    )
    
    try:
        response = client.images.generate(
            model="doubao-seedream-3-0-t2i-250415",
            prompt=prompt,
        )
        return {
            "success": True,
            "image_url": response.data[0].url,
        }
    except Exception as e:
        print(f"图片生成错误: {str(e)}")  # 添加错误日志
        return {
            "success": False,
            "error": str(e)
        }