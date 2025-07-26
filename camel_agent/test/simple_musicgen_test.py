#!/usr/bin/env python3
"""
简化的音乐生成工具测试

测试移植到 musicgen_tool.py 中的核心功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from camel_agent.toolkits.musicgen_tool import (
    MusicGenToolkit,
    simple_eeg_to_music,
    get_test_eeg_samples,
    analyze_emotion_from_sample
)

def test_integrated_functionality():
    """测试移植后的集成功能"""
    print("=== 测试移植后的音乐生成工具 ===")
    
    # 初始化工具包
    toolkit = MusicGenToolkit()
    
    # 获取测试数据
    test_samples = get_test_eeg_samples()
    
    print("\n1. 测试基本情绪分析功能:")
    for state_name, eeg_data in test_samples.items():
        emotion, intensity, valence, arousal = analyze_emotion_from_sample(eeg_data)
        print(f"   {state_name}: {emotion} | 强度: {intensity:.2f} | V: {valence:.2f}, A: {arousal:.2f}")
    
    print("\n2. 测试 EEG 到音乐的完整流程:")
    for state_name, eeg_data in test_samples.items():
        result = toolkit.generate_music_from_eeg(eeg_data)
        if result["success"]:
            emotion_info = result["emotion_analysis"]
            print(f"   {state_name}:")
            print(f"     情绪: {emotion_info['emotion']} (强度: {emotion_info['intensity']:.2f})")
            print(f"     音乐: {result['music_prompt']}")
        else:
            print(f"   {state_name}: 失败 - {result['error']}")
    
    print("\n3. 测试便捷函数:")
    for state_name, eeg_data in test_samples.items():
        music_prompt = simple_eeg_to_music(eeg_data)
        print(f"   {state_name}: {music_prompt}")

def test_individual_functions():
    """测试各个独立功能"""
    print("\n=== 测试独立功能模块 ===")
    
    toolkit = MusicGenToolkit()
    
    # 测试单独的情绪分析
    print("\n1. 测试情绪分析:")
    test_eeg = [0.8, 0.7, 0.6, 0.2, 0.9, 0.7, 0.6]
    emotion_result = toolkit.analyze_eeg_emotion(test_eeg)
    print(f"   EEG 数据: {test_eeg}")
    print(f"   分析结果: {emotion_result}")
    
    # 测试根据情绪生成音乐
    print("\n2. 测试根据情绪生成音乐:")
    if emotion_result["success"]:
        music_prompt = toolkit.generate_music_from_emotion(
            emotion_result["emotion"],
            emotion_result["intensity"],
            emotion_result["valence"],
            emotion_result["arousal"]
        )
        print(f"   音乐提示词: {music_prompt}")

def main():
    """主测试函数"""
    print("开始测试移植后的音乐生成工具包")
    print("=" * 60)
    
    try:
        # 测试集成功能
        test_integrated_functionality()
        
        # 测试独立功能
        test_individual_functions()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试完成！核心功能移植成功。")
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 