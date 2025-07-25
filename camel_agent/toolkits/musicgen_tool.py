from typing import Optional
from dataclasses import dataclass
from camel.types import BaseToolkit, BaseTool, BaseToolArguments

@dataclass
class MusicGenToolArguments(BaseToolArguments):
    emotion: str
    intensity: float
    valence: float
    arousal: float

class MusicGenTool(BaseTool):
    name = "music_gen"
    description = "Generate music based on emotional state from EEG data"
    args_schema = MusicGenToolArguments

    def _emotion_to_prompt(self, emotion: str, intensity: float, valence: float, arousal: float) -> str:
        """Convert emotion metrics to music generation prompt."""
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
        """Generate music based on emotional state."""
        prompt = self._emotion_to_prompt(
            args.emotion,
            args.intensity,
            args.valence,
            args.arousal
        )
        # TODO: 在这里添加实际的音乐生成逻辑
        # 这里应该调用实际的音乐生成模型API
        return prompt

class MusicGenToolkit(BaseToolkit):
    name = "music_gen_toolkit"
    description = "Toolkit for generating music based on emotional state"

    def get_tools(self) -> list[BaseTool]:
        return [MusicGenTool()]

    def get_env_keys(self) -> list[str]:
        return []  # 如果需要API密钥，在这里添加
