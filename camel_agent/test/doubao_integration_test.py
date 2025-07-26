#!/usr/bin/env python3
"""
豆包图片生成集成测试
演示如何使用重构后的简洁代码生成故事和图片
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 加载环境变量
load_dotenv()

def test_story_and_image_generation():
    """测试完整的故事生成和图片生成流程"""
    try:
        # 导入重构后的模块
        from main import StoryAndImageGenerator
        
        # 创建生成器实例
        generator = StoryAndImageGenerator()
        
        # 测试主题
        theme = "一个神奇的森林冒险"
        
        print("🎬 开始生成故事和图片...")
        print(f"📝 主题: {theme}")
        print("-" * 50)
        
        # 生成故事
        print("📖 生成故事中...")
        story = generator.generate_story(theme)
        print(f"✅ 故事生成完成:\n{story}\n")
        
        # 生成图片提示词
        print("🎨 生成图片提示词中...")
        image_prompt = generator.generate_image_prompt(story)
        print(f"✅ 图片提示词: {image_prompt}\n")
        
        # 生成图片
        print("🖼️ 使用豆包API生成图片中...")
        image_url = generator.generate_image(image_prompt)
        print(f"✅ 图片生成成功: {image_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_toolkit_integration():
    """测试工具包集成"""
    try:
        from camel_agent.toolkits.imgen_tool import ImageGenerationToolkit
        
        print("\n🔧 测试图片生成工具包...")
        
        # 创建工具包实例
        toolkit = ImageGenerationToolkit()
        
        # 测试故事内容
        story_content = "在一个充满魔法的森林里，有一只可爱的小狐狸正在寻找失落的宝石。阳光透过树叶洒下斑驳的光影。"
        
        # 生成图片
        result = toolkit.generate_image(story_content)
        print(f"🎯 工具包测试结果: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具包测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 豆包图片生成集成测试")
    print("=" * 60)
    
    # 检查必要的环境变量
    if not os.getenv("ARK_API_KEY"):
        print("⚠️  警告: ARK_API_KEY 环境变量未设置")
        print("💡 提示: 请设置 ARK_API_KEY 环境变量或在代码中直接指定API密钥")
    
    # 运行测试
    test1_success = test_story_and_image_generation()
    test2_success = test_toolkit_integration()
    
    print("\n" + "=" * 60)
    if test1_success and test2_success:
        print("✅ 所有测试通过! 豆包集成成功!")
    else:
        print("❌ 部分测试失败，请检查配置和网络连接")

if __name__ == "__main__":
    main() 