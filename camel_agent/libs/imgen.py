import os
from typing import Dict, Any, Optional
from volcenginesdkarkruntime import Ark

def generate_image(prompt: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    actual_api_key = api_key or os.getenv("ARK_API_KEY")
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
        return {
            "success": False,
            "error": str(e)
        }