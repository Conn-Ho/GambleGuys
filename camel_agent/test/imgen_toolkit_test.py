#!/usr/bin/env python3
"""
图像生成工具包测试示例

演示如何使用 ImageGenerationToolkit 生成图像
"""

import os
import sys
import json

# 添加项目路径到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from toolkits.imgen_tool import ImageGenerationToolkit


def test_basic_image_generation():
    """测试基本图像生成功能"""
    print("=" * 60)
    print("测试基本图像生成功能")
    print("=" * 60)
    
    # 初始化工具包
    toolkit = ImageGenerationToolkit()
    
    # 测试提示词
    test_prompt = "一只可爱的小猫坐在窗台上，阳光洒在它的毛发上"
    
    print(f"生成图像，提示词: {test_prompt}")
    print("-" * 40)
    
    # 生成图像
    result = toolkit.generate_image_from_prompt(prompt=test_prompt)
    print(result)
    print()


def test_prompt_optimization():
    """测试提示词优化功能"""
    print("=" * 60)
    print("测试提示词优化功能")
    print("=" * 60)
    
    # 初始化工具包
    toolkit = ImageGenerationToolkit()
    
    # 测试提示词
    test_prompt = "sunset over mountains"
    
    print(f"优化提示词: {test_prompt}")
    print("-" * 40)
    
    # 优化提示词
    result = toolkit.optimize_prompt_for_image_generation(test_prompt)
    print(result)
    print()


def test_available_sizes():
    """测试获取可用图像尺寸"""
    print("=" * 60)
    print("测试获取可用图像尺寸")
    print("=" * 60)
    
    # 初始化工具包
    toolkit = ImageGenerationToolkit()
    
    # 获取支持的图像尺寸
    result = toolkit.get_available_image_sizes()
    print(result)
    print()


def test_custom_parameters():
    """测试自定义参数图像生成"""
    print("=" * 60)
    print("测试自定义参数图像生成")
    print("=" * 60)
    
    # 初始化工具包
    toolkit = ImageGenerationToolkit()
    
    # 测试提示词
    test_prompt = "futuristic cityscape with flying cars"
    
    print(f"使用自定义参数生成图像")
    print(f"提示词: {test_prompt}")
    print(f"图像尺寸: 768x768")
    print(f"推理步数: 30")
    print(f"引导强度: 8.0")
    print("-" * 40)
    
    # 使用自定义参数生成图像
    result = toolkit.generate_image_from_prompt(
        prompt=test_prompt,
        image_size="768x768",
        num_inference_steps=30,
        guidance_scale=8.0,
        enhance_prompt=True
    )
    print(result)
    print()


def test_toolkit_functions():
    """测试工具包函数列表"""
    print("=" * 60)
    print("测试工具包函数列表")
    print("=" * 60)
    
    # 初始化工具包
    toolkit = ImageGenerationToolkit()
    
    # 获取可用工具
    tools = toolkit.get_tools()
    
    print(f"工具包包含 {len(tools)} 个函数:")
    for i, tool in enumerate(tools, 1):
        func_name = tool.func.__name__
        func_doc = tool.func.__doc__.strip().split('\n')[0] if tool.func.__doc__ else "无描述"
        print(f"{i}. {func_name}: {func_doc}")
    print()


def test_error_handling():
    """测试错误处理"""
    print("=" * 60)
    print("测试错误处理")
    print("=" * 60)
    
    # 使用无效的API密钥初始化工具包
    try:
        toolkit = ImageGenerationToolkit(api_key="invalid_key")
        
        # 尝试生成图像
        result = toolkit.generate_image_from_prompt("test prompt")
        print("错误处理测试结果:")
        print(result)
        
    except Exception as e:
        print(f"捕获到异常: {e}")
    print()


def main():
    """主测试函数"""
    print("硅基流动图像生成工具包 - 测试套件")
    print("=" * 60)
    print()
    
    try:
        # 运行各项测试
        test_available_sizes()
        test_prompt_optimization()
        test_toolkit_functions()
        test_basic_image_generation()
        test_custom_parameters()
        test_error_handling()
        
        print("=" * 60)
        print("所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 