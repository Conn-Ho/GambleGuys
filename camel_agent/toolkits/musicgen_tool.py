import math
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

# 尝试导入 CAMEL 框架的基础类，如果失败则创建兼容类
try:
    from camel.toolkits.base import BaseToolkit
    from camel.toolkits.openai_function import OpenAIFunction
    from camel.toolkits import FunctionTool
    CAMEL_AVAILABLE = True
except ImportError:
    # 如果无法导入CAMEL框架，创建基础类
    CAMEL_AVAILABLE = False
    
    class BaseToolkit:
        """基础工具包类的兼容实现"""
        def get_tools(self):
            raise NotImplementedError("Subclasses must implement this method.")
    
    class OpenAIFunction:
        """OpenAI函数包装器的兼容实现"""
        def __init__(self, func):
            self.func = func
            
    class FunctionTool:
        """函数工具的兼容实现"""
        def __init__(self, func):
            self.func = func

# ========================================================================================
# EEG 情绪分析核心模块
# ========================================================================================

# Cortex API 'met' 流返回的7个数值指标的顺序
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

# 情绪计算权重
WEIGHTS = {
    'arousal': {
        'exc': 0.4, 'str': 0.3, 'lex': 0.2, 'int': 0.15, 'eng': 0.1, 'foc': 0.05, 'rel': -0.4
    },
    'valence': {
        'rel': 0.35, 'int': 0.25, 'eng': 0.2, 'lex': 0.2, 'foc': 0.1, 'exc': 0.1, 'str': -0.5
    }
}

def normalize_to_neg_one_to_one(value: float, min_val: float, max_val: float) -> float:
    """将值归一化到 -1 到 1 的范围"""
    if max_val == min_val: 
        return 0
    return 2 * ((value - min_val) / (max_val - min_val)) - 1

def calculate_emotion_scores(metrics: Dict[str, float], weights: Dict[str, Dict[str, float]]) -> Tuple[float, float]:
    """计算情绪得分（valence 和 arousal）"""
    arousal = sum(weights['arousal'][key] * metrics[key] for key in API_METRIC_ORDER)
    valence = sum(weights['valence'][key] * metrics[key] for key in API_METRIC_ORDER)
    return max(-1, min(1, valence)), max(-1, min(1, arousal))

def get_precise_emotion(valence: float, arousal: float, neutral_threshold: float = 0.1) -> Tuple[str, float]:
    """根据 valence 和 arousal 值确定精确的情绪类型和强度"""
    intensity_raw = math.sqrt(valence**2 + arousal**2)
    intensity_normalized = min(100, (intensity_raw / math.sqrt(2)) * 100)

    if intensity_raw < neutral_threshold:
        return "中性 (Neutral)", intensity_normalized

    angle = math.degrees(math.atan2(arousal, valence))
    if angle < 0: 
        angle += 360

    if 22.5 <= angle < 67.5: 
        emotion_label = "开心 (Happy)"
    elif 67.5 <= angle < 112.5: 
        emotion_label = "惊喜 (Surprised)"
    elif 112.5 <= angle < 157.5: 
        emotion_label = "愤怒 (Angry)"
    elif 157.5 <= angle < 202.5: 
        emotion_label = "厌恶 (Disgust)"
    elif 202.5 <= angle < 247.5: 
        emotion_label = "悲伤 (Sad)"
    elif 247.5 <= angle < 292.5: 
        emotion_label = "疲倦 (Tired)"
    elif 292.5 <= angle < 337.5: 
        emotion_label = "放松 (Relaxed)"
    else: 
        emotion_label = "平静 (Pleased)"
    
    return emotion_label, intensity_normalized

def analyze_emotion_from_sample(sample_list: List[float]) -> Tuple[str, float, float, float]:
    """
    情绪分析流程的入口函数
    
    Args:
        sample_list: 包含7个EEG指标的列表 [eng, exc, lex, str, rel, int, foc]
    
    Returns:
        Tuple[emotion, intensity, valence, arousal]
    """
    raw_data = dict(zip(API_METRIC_ORDER, sample_list))
    
    # 如果注意力过低，设为0
    if raw_data['foc'] <= 0.1:
        raw_data['foc'] = 0.0
    
    # 归一化指标
    normalized_metrics = {}
    for key, value in raw_data.items():
        min_val, max_val = METRIC_RANGES[key]
        normalized_metrics[key] = normalize_to_neg_one_to_one(value, min_val, max_val)
    
    # 计算情绪坐标
    v, a = calculate_emotion_scores(normalized_metrics, WEIGHTS)
    emotion, intensity = get_precise_emotion(v, a)
    
    return emotion, intensity, v, a

# ========================================================================================
# 音乐生成工具类
# ========================================================================================

@dataclass
class MusicGenToolArguments:
    """音乐生成工具参数"""
    emotion: str
    intensity: float
    valence: float
    arousal: float

@dataclass
class EEGMusicGenArguments:
    """从 EEG 数据生成音乐的参数"""
    eeg_data: List[float]  # 7个EEG指标值

class MusicGenTool:
    """音乐生成工具"""
    name = "music_gen"
    description = "Generate music based on emotional state from EEG data"
    args_schema = MusicGenToolArguments

    def _emotion_to_prompt(self, emotion: str, intensity: float, valence: float, arousal: float) -> str:
        """将情绪指标转换为音乐生成提示词"""
        # 基础音乐风格映射
        emotion_to_style = {
            "开心 (Happy)": "upbeat and cheerful",
            "惊喜 (Surprised)": "dramatic and energetic",
            "愤怒 (Angry)": "intense and powerful",
            "厌恶 (Disgust)": "dissonant and tense",
            "悲伤 (Sad)": "melancholic and slow",
            "疲倦 (Tired)": "ambient and calm",
            "放松 (Relaxed)": "peaceful and flowing",
            "平静 (Pleased)": "gentle and harmonious",
            "中性 (Neutral)": "balanced and moderate"
        }

        base_style = emotion_to_style.get(emotion, "balanced and moderate")
        
        # 根据情绪强度调整描述
        intensity_desc = ""
        if intensity > 80:
            intensity_desc = "very "
        elif intensity > 60:
            intensity_desc = "quite "
        elif intensity < 30:
            intensity_desc = "slightly "

        # 根据valence和arousal添加额外的音乐特征
        extra_features = []
        if valence > 0.5:
            extra_features.append("major key")
        elif valence < -0.5:
            extra_features.append("minor key")
            
        if arousal > 0.5:
            extra_features.append("fast tempo")
        elif arousal < -0.5:
            extra_features.append("slow tempo")

        extra_desc = ", ".join(extra_features)
        if extra_desc:
            prompt = f"Generate a {intensity_desc}{base_style} music piece in {extra_desc}"
        else:
            prompt = f"Generate a {intensity_desc}{base_style} music piece"

        return prompt

    def __call__(self, args: MusicGenToolArguments) -> str:
        """基于情绪状态生成音乐"""
        prompt = self._emotion_to_prompt(
            args.emotion,
            args.intensity,
            args.valence,
            args.arousal
        )
        # TODO: 在这里添加实际的音乐生成逻辑
        # 这里应该调用实际的音乐生成模型API
        return prompt

class EEGMusicGenTool:
    """从 EEG 数据直接生成音乐的工具"""
    name = "eeg_music_gen"
    description = "Generate music directly from EEG data by analyzing emotions first"
    args_schema = EEGMusicGenArguments

    def __init__(self):
        self.music_tool = MusicGenTool()

    def __call__(self, args: EEGMusicGenArguments) -> Dict[str, Any]:
        """
        从 EEG 数据直接生成音乐
        
        Args:
            args: 包含 EEG 数据的参数
            
        Returns:
            包含情绪分析结果和音乐提示词的字典
        """
        try:
            # 步骤 1: 分析 EEG 数据得到情绪
            emotion, intensity, valence, arousal = analyze_emotion_from_sample(args.eeg_data)
            
            # 步骤 2: 创建音乐生成参数
            music_args = MusicGenToolArguments(
                emotion=emotion,
                intensity=intensity,
                valence=valence,
                arousal=arousal
            )
            
            # 步骤 3: 生成音乐提示词
            music_prompt = self.music_tool(music_args)
            
            return {
                "success": True,
                "emotion_analysis": {
                    "emotion": emotion,
                    "intensity": intensity,
                    "valence": valence,
                    "arousal": arousal
                },
                "music_prompt": music_prompt,
                "eeg_data": args.eeg_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "eeg_data": args.eeg_data
            }

class MusicGenToolkit(BaseToolkit):
    """音乐生成工具包"""
    name = "music_gen_toolkit"
    description = "Toolkit for generating music based on emotional state from EEG data"

    def __init__(self):
        self.music_tool = MusicGenTool()
        self.eeg_music_tool = EEGMusicGenTool()

    def analyze_eeg_emotion(self, eeg_data: List[float]) -> Dict[str, Any]:
        """分析 EEG 数据得到情绪信息"""
        try:
            emotion, intensity, valence, arousal = analyze_emotion_from_sample(eeg_data)
            return {
                "success": True,
                "emotion": emotion,
                "intensity": intensity,
                "valence": valence,
                "arousal": arousal
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def generate_music_from_emotion(self, emotion: str, intensity: float, valence: float, arousal: float) -> str:
        """根据情绪参数生成音乐提示词"""
        args = MusicGenToolArguments(
            emotion=emotion,
            intensity=intensity,
            valence=valence,
            arousal=arousal
        )
        return self.music_tool(args)

    def generate_music_from_eeg(self, eeg_data: List[float]) -> Dict[str, Any]:
        """从 EEG 数据直接生成音乐（完整流程）"""
        args = EEGMusicGenArguments(eeg_data=eeg_data)
        return self.eeg_music_tool(args)

    def get_tools(self) -> List[Any]:
        """返回工具列表"""
        return [self.music_tool, self.eeg_music_tool]

    def get_env_keys(self) -> List[str]:
        """返回所需的环境变量键"""
        return []  # 如果需要API密钥，在这里添加

# ========================================================================================
# 便捷函数
# ========================================================================================

def simple_eeg_to_music(eeg_data: List[float]) -> str:
    """
    简单的 EEG 到音乐转换函数
    
    Args:
        eeg_data: 包含7个EEG指标的列表
        
    Returns:
        音乐生成提示词
    """
    toolkit = MusicGenToolkit()
    result = toolkit.generate_music_from_eeg(eeg_data)
    
    if result["success"]:
        return result["music_prompt"]
    else:
        return f"生成失败: {result['error']}"

def get_test_eeg_samples() -> Dict[str, List[float]]:
    """返回测试用的 EEG 数据样本"""
    return {
        "开心状态": [0.8, 0.7, 0.6, 0.2, 0.9, 0.7, 0.6],  # 高兴奋，低压力，高放松
        "悲伤状态": [0.3, 0.2, 0.3, 0.7, 0.2, 0.3, 0.4],  # 低兴奋，高压力，低放松
        "愤怒状态": [0.9, 0.9, 0.8, 0.9, 0.1, 0.8, 0.7],  # 高兴奋，高压力，低放松  
        "放松状态": [0.4, 0.3, 0.2, 0.1, 0.9, 0.5, 0.8],  # 低兴奋，低压力，高放松
        "中性状态": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],  # 所有值都中等
    }

# 导出主要类和函数
__all__ = [
    "MusicGenToolkit", 
    "MusicGenTool", 
    "EEGMusicGenTool",
    "MusicGenToolArguments",
    "EEGMusicGenArguments",
    "analyze_emotion_from_sample",
    "simple_eeg_to_music",
    "get_test_eeg_samples"
]
