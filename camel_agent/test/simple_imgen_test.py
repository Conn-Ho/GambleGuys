#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的图像生成测试脚本
只需要输入提示词即可生成图片
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from toolkits.imgen_tool import simple_generate_image


def main():
    """主测试函数"""
    print("🎨 简单图像生成测试")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        "一只可爱的小猫",
        "beautiful sunset over mountains",
        "古代中国建筑",
        "科幻城市夜景"
    ]
    
    for i, prompt in enumerate(test_cases, 1):
        print(f"\n📝 测试 {i}: {prompt}")
        print("-" * 30)
        
        # 调用简化接口
        result = simple_generate_image(prompt)
        
        if result["success"]:
            print(f"✅ 成功生成!")
            print(f"🔗 图像链接: {result['image_url']}")
        else:
            print(f"❌ 生成失败: {result['message']}")
    
    print("\n" + "=" * 50)
    print("🎯 交互式测试 - 输入你自己的提示词")
    
    while True:
        try:
            user_prompt = input("\n请输入图像描述 (输入 'quit' 退出): ").strip()
            
            if user_prompt.lower() in ['quit', 'exit', 'q']:
                print("👋 再见!")
                break
                
            if not user_prompt:
                print("⚠️  请输入有效的提示词")
                continue
            
            print("🔄 正在生成图像...")
            result = simple_generate_image(user_prompt)
            
            if result["success"]:
                print(f"✅ 生成成功! 图像链接: {result['image_url']}")
            else:
                print(f"❌ 生成失败: {result['message']}")
                
        except KeyboardInterrupt:
            print("\n👋 程序中断，再见!")
            break
        except Exception as e:
            print(f"❌ 程序错误: {e}")


if __name__ == "__main__":
    main() 