import requests
import json
from typing import Dict, Any, Optional

def generate_image(
    prompt: str,
    api_key: str,
    image_size: str = "1024x1024",
    batch_size: int = 1,
    num_inference_steps: int = 20,
    guidance_scale: float = 7.5,
    model: str = "Kwai-Kolors/Kolors"
) -> Dict[str, Any]:
    """
    使用硅基流动API生成图像
    
    Args:
        prompt: 图像描述提示词
        api_key: API密钥
        image_size: 图像尺寸，默认"1024x1024"
        batch_size: 批次大小，默认1
        num_inference_steps: 推理步数，默认20
        guidance_scale: 引导强度，默认7.5
        model: 使用的模型，默认"Kwai-Kolors/Kolors"
    
    Returns:
        Dict包含success, image_url, error等信息
    """
    url = "https://api.siliconflow.cn/v1/images/generations"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "image_size": image_size,
        "batch_size": batch_size,
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if "data" in data and len(data["data"]) > 0:
            return {
                "success": True,
                "image_url": data["data"][0]["url"],
                "response_data": data,
                "prompt": prompt,
                "error": None
            }
        else:
            return {
                "success": False,
                "image_url": None,
                "response_data": data,
                "prompt": prompt,
                "error": "No image data returned"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "image_url": None,
            "response_data": None,
            "prompt": prompt,
            "error": f"Request error: {str(e)}"
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "image_url": None,
            "response_data": None,
            "prompt": prompt,
            "error": f"JSON decode error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "image_url": None,
            "response_data": None,
            "prompt": prompt,
            "error": f"Unexpected error: {str(e)}"
        }

# 测试代码（仅在直接运行时执行）
if __name__ == "__main__":
    # 示例用法
    test_prompt = "an island near sea, with seagulls, moon shining over the sea, light house, boats in the background, fish flying over the sea"
    test_api_key = "sk-rpbdfcumdlwdfssveutdyweficaabukciujbkoltmdsnjiba"
    
    result = generate_image(test_prompt, test_api_key)
    print(json.dumps(result, indent=2, ensure_ascii=False))