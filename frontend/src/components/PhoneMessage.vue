<template>
  <div class="phone-container" v-if="visible">
    <div class="phone-frame">
      <div class="phone-screen">
        <div class="phone-header">
          <div class="phone-status-bar">
            <span class="carrier">•••○○ AT&T</span>
            <span class="time">9:42 AM</span>
            <span class="battery">🔋</span>
          </div>
          <div class="app-header">
            <span class="back-arrow">←</span>
            <span class="app-title">故事</span>
            <span class="menu-dots">⋯</span>
          </div>
        </div>

        <div class="phone-content">
          <div class="colorful-background">
            <!-- 更深沉的彩色方块背景 -->
            <div class="color-grid">
              <div
                v-for="n in 42"
                :key="n"
                class="color-block"
                :style="getVintageColor()"
              ></div>
            </div>
          </div>

          <div class="input-popup">
            <div class="input-header">
              <span class="input-count">{{ messageCount }} of 27</span>
              <h3>From A Friend</h3>
              <p>A Message For You</p>
              <div class="timestamp">Today, 10:15 AM</div>
            </div>

            <div class="input-area">
              <textarea
                v-model="inputValue"
                @keyup.enter="handleSend"
                placeholder="请输入你的故事想法..."
                :disabled="loading || !storyActive"
                rows="3"
              ></textarea>
            </div>

            <div class="input-actions">
              <button
                @click="handleSend"
                :disabled="loading || !inputValue.trim() || !storyActive"
                class="send-btn"
              >
                {{
                  !storyActive
                    ? "故事已结束"
                    : loading
                    ? "发送中..."
                    : "发送"
                }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";

// 定义 props
const props = defineProps({
  visible: {
    type: Boolean,
    default: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  storyActive: {
    type: Boolean,
    default: true,
  },
  messageCount: {
    type: Number,
    default: 1,
  },
});

// 定义 emits
const emit = defineEmits(["send"]);

// 内部状态
const inputValue = ref("");

// 生成更深沉复古的颜色
const getVintageColor = () => {
  const vintageColors = [
    "#8B4513",
    "#A0522D",
    "#CD853F",
    "#D2B48C",
    "#DEB887", // 棕色系
    "#556B2F",
    "#6B8E23",
    "#9ACD32",
    "#32CD32",
    "#228B22", // 深绿系
    "#191970",
    "#000080",
    "#0000CD",
    "#4169E1",
    "#1E90FF", // 深蓝系
    "#8B0000",
    "#B22222",
    "#DC143C",
    "#FF0000",
    "#FF6347", // 深红系
    "#4B0082",
    "#483D8B",
    "#6A5ACD",
    "#7B68EE",
    "#9370DB", // 紫色系
    "#B8860B",
    "#DAA520",
    "#FF8C00",
    "#FF7F50",
    "#CD5C5C", // 金黄系
    "#2F4F4F",
    "#708090",
    "#778899",
    "#696969",
    "#808080", // 灰色系
    "#8B4513",
    "#A0522D",
    "#D2691E",
    "#FF4500",
    "#FF6347", // 橙棕系
  ];
  return {
    backgroundColor:
      vintageColors[Math.floor(Math.random() * vintageColors.length)],
  };
};

// 处理发送消息
const handleSend = () => {
  if (!inputValue.value.trim() || props.loading) return;
  
  const message = inputValue.value;
  inputValue.value = "";
  emit("send", message);
};
</script>

<style scoped>
/* 复古手机界面样式 */
.phone-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
}

.phone-frame {
  width: 280px;
  height: 520px;
  background: linear-gradient(145deg, #1a1a1a, #0d0d0d); /* 更深的渐变 */
  border-radius: 20px; /* 更圆润的边角 */
  padding: 6px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.9),
    inset 0 1px 0 rgba(255, 255, 255, 0.1); /* 添加内阴影 */
  border: 2px solid #333; /* 添加边框 */
}

.phone-screen {
  width: 100%;
  height: 100%;
  background: #000;
  border-radius: 15px;
  overflow: hidden;
  position: relative;
  border: 1px solid #222;
}

.phone-header {
  background: rgba(0, 0, 0, 0.95);
  color: white;
  padding: 6px 10px;
  font-family: "SF Pro Text", -apple-system, sans-serif;
}

.phone-status-bar {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  margin-bottom: 6px;
  font-weight: 600;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 500;
}

.phone-content {
  height: calc(100% - 55px);
  position: relative;
}

.colorful-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  grid-template-rows: repeat(7, 1fr);
  width: 100%;
  height: 100%;
  gap: 1px;
}

.color-block {
  border: 0.5px solid rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.input-popup {
  position: absolute;
  bottom: 25px;
  left: 15px;
  right: 15px;
  background: rgba(255, 255, 255, 0.97);
  border-radius: 10px;
  padding: 12px;
  backdrop-filter: blur(20px);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  border: 0.5px solid rgba(0, 0, 0, 0.1);
}

.input-header {
  text-align: center;
  margin-bottom: 10px;
}

.input-count {
  font-size: 11px;
  color: #666;
  font-weight: 500;
}

.input-header h3 {
  margin: 2px 0 1px 0;
  font-size: 15px;
  color: #333;
  font-weight: 600;
}

.input-header p {
  margin: 0 0 4px 0;
  font-size: 11px;
  color: #666;
}

.timestamp {
  font-size: 10px;
  color: #999;
  margin-top: 4px;
}

.input-area {
  margin-bottom: 10px;
}

.input-area textarea {
  width: 100%;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 6px;
  font-size: 13px;
  resize: none;
  outline: none;
  font-family: inherit;
  background: rgba(255, 255, 255, 0.9);
}

.input-area textarea:focus {
  border-color: #007aff;
  box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.2);
}

.input-actions {
  text-align: center;
}

.send-btn {
  background: #007aff;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
  font-weight: 500;
}

.send-btn:hover:not(:disabled) {
  background: #0056cc;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .phone-container {
    position: fixed;
    bottom: 10px;
    right: 10px;
  }

  .phone-frame {
    width: 240px;
    height: 450px;
  }
}
</style> 