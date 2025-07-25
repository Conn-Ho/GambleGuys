"""Example program to show how to read a multi-channel time series from LSL."""
import time
from pylsl import StreamInlet, resolve_streams

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
            else:
                print(sample)
except KeyboardInterrupt:
    print("接收已手动终止。")
