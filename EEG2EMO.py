"""Example program to show how to read a multi-channel time series from LSL."""
import time
from pylsl import StreamInlet, resolve_streams
import math

def process_stream(stream_type):
    streams = resolve_streams()
    for s in streams:
        if s.type() == stream_type:
            return s
    return None

stream_types = {
    1: "EEG",
    2: "Motion",
    3: "Contact-Quality",
    4: "EEG-Quality",
    5: "Performance-Metrics",
    6: "Band-Power"
}

print("Choose a stream type:")
for i, stream_type in stream_types.items():
    print(f"{i}. {stream_type}")

stream_type_choice = int(input("Enter the number corresponding to the stream type: "))
stream_type = list(stream_types.values())[stream_type_choice - 1]
selected_stream = process_stream(stream_type)

if selected_stream:
    print(f"Selected stream: {selected_stream.name()}")
else:
    print("No matching stream found.")
    exit(1)

inlet = StreamInlet(selected_stream)
info = inlet.info()
print(f"\nThe manufacturer is: {info.desc().child_value('manufacturer')}")
print("The channel labels are listed below:")
ch = info.desc().child("channels").child("channel")
labels = []
for _ in range(info.channel_count()):
    labels.append(ch.child_value('label'))
    ch = ch.next_sibling()
print(f"  {', '.join(labels)}")

metric_labels = ["Attention", "Engagement", "Excitement", "Interest", "Relaxation", "Stress"]

print("Now pulling samples...")

# 1. 归一化函数、范围和权重定义
# -------------------------------------------------------------------------

METRIC_RANGES = {
    'Attention': (0, 100),
    'Engagement': (0, 100),
    'Excitement': (0, 100),
    'Interest': (0, 100),
    'Relaxation': (0, 100),
    'Stress': (0, 100) 
}

WEIGHTS = {
    'arousal': {
        'Excitement': 0.5, 'Stress': 0.2, 'Interest': 0.1, 
        'Engagement': 0.1, 'Attention': 0.1, 'Relaxation': -0.3
    },
    'valence': {
        'Relaxation': 0.4, 'Interest': 0.3, 'Engagement': 0.2, 
        'Attention': 0.1, 'Stress': -0.6
    }
}

def normalize_to_neg_one_to_one(value, min_val, max_val):
    if max_val == min_val: return 0
    return 2 * ((value - min_val) / (max_val - min_val)) - 1

# 2. Valence/Arousal 计算函数
# -------------------------------------------------------------------------

def calculate_emotion_scores(metrics, weights):
    arousal = (weights['arousal']['Excitement'] * metrics['Excitement'] +
               weights['arousal']['Stress']     * metrics['Stress'] +
               weights['arousal']['Interest']   * metrics['Interest'] +
               weights['arousal']['Engagement'] * metrics['Engagement'] +
               weights['arousal']['Attention']  * metrics['Attention'] +
               weights['arousal']['Relaxation'] * metrics['Relaxation'])

    valence = (weights['valence']['Relaxation'] * metrics['Relaxation'] +
               weights['valence']['Interest']   * metrics['Interest'] +
               weights['valence']['Engagement'] * metrics['Engagement'] +
               weights['valence']['Attention']  * metrics['Attention'] +
               weights['valence']['Stress']     * metrics['Stress'])
    
    return max(-1, min(1, valence)), max(-1, min(1, arousal))

# 3. 精确情绪判断函数
# -------------------------------------------------------------------------

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

# 4. 主分析流程封装
# -------------------------------------------------------------------------

def analyze_emotion_from_sample(sample_list):
    """
    接收原始的LSL样本列表(list)，完成从数据处理到情绪输出的全过程。
    """
    # 步骤 A: 将数据列表和标签组合成字典
    raw_data = dict(zip(metric_labels, sample_list))
    
    # 步骤 B: 数据归一化
    normalized_metrics = {}
    for key, value in raw_data.items():
        min_val, max_val = METRIC_RANGES[key]
        normalized_metrics[key] = normalize_to_neg_one_to_one(value, min_val, max_val)
    
    # 步骤 C: 计算V/A坐标
    v, a = calculate_emotion_scores(normalized_metrics, WEIGHTS)
    
    # 步骤 D: 获取最终情绪和强度
    emotion, intensity = get_precise_emotion(v, a)
    
    return emotion, intensity

try:
    while True:
        sample, timestamp = inlet.pull_sample()
        if timestamp is not None:
            if stream_type == "Performance-Metrics":
                # 格式化输出
                output = []
                for name, value in zip(metric_labels, sample):
                    output.append(f"{name}: {value:.2f}")
                print(", ".join(output))
                # 调用在文件末尾定义的函数来处理数据
                emotion, intensity = analyze_emotion_from_sample(sample)
                # 打印情绪分析结果
                print(f"--> 情绪分析: {emotion}, 强度: {intensity:.2f} / 100\n")
            else:
                print(sample)
except KeyboardInterrupt:
    print("接收已手动终止。")
