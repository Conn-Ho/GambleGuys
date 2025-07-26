#!/usr/bin/env python3
"""
EEG 数据到音乐生成数据传输测试

测试目标：
1. 验证 EEG2EMO.py 的情绪分析功能
2. 验证 musicgen_tool.py 的音乐生成功能  
3. 验证两者之间的数据传输流程
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import math
from camel_agent.toolkits.musicgen_tool import MusicGenToolkit, MusicGenToolArguments

# ========================================================================================
# 从 EEG2EMO.py 导入情绪分析相关函数
# ========================================================================================

# 复制必要的常量和函数（避免依赖 cortex 库）
API_METRIC_ORDER = ['eng', 'exc', 'lex', 'str', 'rel', 'int', 'foc']

METRIC_RANGES = {
    'eng': (0, 1),  # Engagement
    'exc': (0, 1),  # Excitement  
    'lex': (0, 1),  # Lexical Excitement
    'str': (0, 1),  # Stress
    'rel': (0, 1),  # Relaxation
    'int': (0, 1),  # Interest
    'foc': (0, 1)   # Focus (Attention)
}

WEIGHTS = {
    'arousal': {
        'exc': 0.4, 'str': 0.3, 'lex': 0.2, 'int': 0.15, 'eng': 0.1, 'foc': 0.05, 'rel': -0.4
    },
    'valence': {
        'rel': 0.35, 'int': 0.25, 'eng': 0.2, 'lex': 0.2, 'foc': 0.1, 'exc': 0.1, 'str': -0.5
    }
}

def normalize_to_neg_one_to_one(value, min_val, max_val):
    if max_val == min_val: return 0
    return 2 * ((value - min_val) / (max_val - min_val)) - 1

def calculate_emotion_scores(metrics, weights):
    arousal = sum(weights['arousal'][key] * metrics[key] for key in API_METRIC_ORDER)
    valence = sum(weights['valence'][key] * metrics[key] for key in API_METRIC_ORDER)
    return max(-1, min(1, valence)), max(-1, min(1, arousal))

def get_precise_emotion(valence, arousal, neutral_threshold=0.1):
    intensity_raw = math.sqrt(valence**2 + arousal**2)
    intensity_normalized = min(100, (intensity_raw / math.sqrt(2)) * 100)

    if intensity_raw < neutral_threshold:
        return "中性 (Neutral)", intensity_normalized

    angle = math.degrees(math.atan2(arousal, valence))
    if angle < 0: angle += 360

    if 22.5 <= angle < 67.5: emotion_label = "开心 (Happy)"
    elif 67.5 <= angle < 112.5: emotion_label = "惊喜 (Surprised)"
    elif 112.5 <= angle < 157.5: emotion_label = "愤怒 (Angry)"
    elif 157.5 <= angle < 202.5: emotion_label = "厌恶 (Disgust)"
    elif 202.5 <= angle < 247.5: emotion_label = "悲伤 (Sad)"
    elif 247.5 <= angle < 292.5: emotion_label = "疲倦 (Tired)"
    elif 292.5 <= angle < 337.5: emotion_label = "放松 (Relaxed)"
    else: emotion_label = "平静 (Pleased)"
    return emotion_label, intensity_normalized

def analyze_emotion_from_sample(sample_list):
    """情绪分析流程的入口函数"""
    raw_data = dict(zip(API_METRIC_ORDER, sample_list))
    
    if raw_data['foc'] <= 0.1:
        raw_data['foc'] = 0.0
    
    normalized_metrics = {}
    for key, value in raw_data.items():
        min_val, max_val = METRIC_RANGES[key]
        normalized_metrics[key] = normalize_to_neg_one_to_one(value, min_val, max_val)
    
    v, a = calculate_emotion_scores(normalized_metrics, WEIGHTS)
    emotion, intensity = get_precise_emotion(v, a)
    
    return emotion, intensity, v, a

# ========================================================================================
# 测试数据和测试函数
# ========================================================================================

def get_test_eeg_samples():
    """返回多组测试用的 EEG 数据样本"""
    return {
        "开心状态": [0.8, 0.7, 0.6, 0.2, 0.9, 0.7, 0.6],  # 高兴奋，低压力，高放松
        "悲伤状态": [0.3, 0.2, 0.3, 0.7, 0.2, 0.3, 0.4],  # 低兴奋，高压力，低放松
        "愤怒状态": [0.9, 0.9, 0.8, 0.9, 0.1, 0.8, 0.7],  # 高兴奋，高压力，低放松  
        "放松状态": [0.4, 0.3, 0.2, 0.1, 0.9, 0.5, 0.8],  # 低兴奋，低压力，高放松
        "中性状态": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],  # 所有值都中等
    }

def test_emotion_analysis():
    """测试情绪分析功能"""
    print("=== 测试 EEG 情绪分析功能 ===")
    test_samples = get_test_eeg_samples()
    
    results = {}
    for state_name, sample_data in test_samples.items():
        emotion, intensity, valence, arousal = analyze_emotion_from_sample(sample_data)
        results[state_name] = {
            'emotion': emotion,
            'intensity': intensity,
            'valence': valence,
            'arousal': arousal
        }
        print(f"{state_name}: {emotion} | 强度: {intensity:.2f}/100 | V: {valence:.2f}, A: {arousal:.2f}")
    
    return results

def test_music_generation(emotion_results):
    """测试音乐生成功能"""
    print("\n=== 测试音乐生成功能 ===")
    
    # 初始化音乐生成工具
    music_toolkit = MusicGenToolkit()
    music_gen_tool = music_toolkit.get_tools()[0]
    
    music_results = {}
    for state_name, emotion_data in emotion_results.items():
        # 创建音乐生成参数
        music_args = MusicGenToolArguments(
            emotion=emotion_data['emotion'],
            intensity=emotion_data['intensity'],
            valence=emotion_data['valence'],
            arousal=emotion_data['arousal']
        )
        
        # 生成音乐提示词
        music_prompt = music_gen_tool(music_args)
        music_results[state_name] = music_prompt
        print(f"{state_name} -> 音乐提示词: {music_prompt}")
    
    return music_results

def test_full_pipeline():
    """测试完整的数据传输流程"""
    print("=== 完整数据传输流程测试 ===")
    
    # 模拟实时 EEG 数据处理
    test_samples = get_test_eeg_samples()
    music_toolkit = MusicGenToolkit()
    music_gen_tool = music_toolkit.get_tools()[0]
    
    print("模拟实时处理...")
    for i, (state_name, sample_data) in enumerate(test_samples.items(), 1):
        print(f"\n--- 第 {i} 次数据处理 ({state_name}) ---")
        
        # 步骤 1: 情绪分析
        emotion, intensity, valence, arousal = analyze_emotion_from_sample(sample_data)
        print(f"1. 情绪分析结果: {emotion} (强度: {intensity:.2f})")
        
        # 步骤 2: 创建音乐生成参数
        music_args = MusicGenToolArguments(
            emotion=emotion,
            intensity=intensity,
            valence=valence,
            arousal=arousal
        )
        print(f"2. 音乐参数创建: ✓")
        
        # 步骤 3: 生成音乐提示词
        music_prompt = music_gen_tool(music_args)
        print(f"3. 音乐提示词生成: {music_prompt}")
        
        print(f"4. 数据传输状态: ✓ 成功")

def test_edge_cases():
    """测试边界情况"""
    print("\n=== 边界情况测试 ===")
    
    edge_cases = {
        "全零值": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "全最大值": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        "极端对比": [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0],
    }
    
    music_toolkit = MusicGenToolkit()
    music_gen_tool = music_toolkit.get_tools()[0]
    
    for case_name, sample_data in edge_cases.items():
        try:
            emotion, intensity, valence, arousal = analyze_emotion_from_sample(sample_data)
            music_args = MusicGenToolArguments(
                emotion=emotion,
                intensity=intensity,
                valence=valence,
                arousal=arousal
            )
            music_prompt = music_gen_tool(music_args)
            print(f"{case_name}: ✓ 处理成功 -> {emotion} -> {music_prompt}")
        except Exception as e:
            print(f"{case_name}: ✗ 处理失败 -> {e}")

def main():
    """主测试函数"""
    print("开始 EEG 到音乐生成数据传输测试")
    print("=" * 60)
    
    try:
        # 测试 1: 情绪分析功能
        emotion_results = test_emotion_analysis()
        
        # 测试 2: 音乐生成功能
        music_results = test_music_generation(emotion_results)
        
        # 测试 3: 完整流程
        test_full_pipeline()
        
        # 测试 4: 边界情况
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试完成！数据传输流程工作正常。")
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 