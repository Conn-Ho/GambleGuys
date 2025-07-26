<template>
  <div class="chat-container">
    <!-- 故事状态显示 -->
    <div class="story-status" v-if="storyState.scene_count > 0">
      <div class="status-info">
        <span class="scene-count">场景 {{ storyState.scene_count }}</span>
        <span
          class="story-state"
          :class="{ 'story-ended': !storyState.story_active }"
        >
          {{ storyState.story_active ? "故事进行中" : "故事已结束" }}
        </span>
      </div>
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: `${(storyState.scene_count % 10) * 10}%` }"
        ></div>
      </div>
    </div>

    <!-- AI回复对话框 (只显示最新的一个，透明样式) -->
    <div v-if="latestAiMessage" class="ai-dialog-wrapper">
      <div class="ai-dialog">
        <div class="ai-dialog-header">
          <span class="ai-dialog-title">???</span>
        </div>
        <div class="ai-dialog-content">
          <p class="ai-response">{{ latestAiMessage.text }}</p>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="ai-dialog-wrapper">
      <div class="ai-dialog">
        <div class="ai-dialog-header">
          <span class="ai-dialog-title">???</span>
        </div>
        <div class="ai-dialog-content">
          <p class="ai-response loading-text">正在思考...</p>
        </div>
      </div>
    </div>

    <!-- 用户输入手机界面 (更复古风格) -->
    <div class="phone-container">
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
                <span class="input-count"
                  >{{ messages.filter((m) => m.role === "user").length + 1 }} of
                  27</span
                >
                <h3>From A Friend</h3>
                <p>A Message For You</p>
                <div class="timestamp">Today, 10:15 AM</div>
              </div>

              <div class="input-area">
                <textarea
                  v-model="input"
                  @keyup.enter="send"
                  placeholder="请输入你的故事想法..."
                  :disabled="loading || !storyState.story_active"
                  rows="3"
                ></textarea>
              </div>

              <div class="input-actions">
                <button
                  @click="send"
                  :disabled="
                    loading || !input.trim() || !storyState.story_active
                  "
                  class="send-btn"
                >
                  {{
                    !storyState.story_active
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
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed } from "vue";

// 定义发射事件
const emit = defineEmits(["backgroundUpdate"]);

const input = ref("");
const loading = ref(false);
const storyState = ref({
  scene_count: 0,
  story_active: true,
});

const messages = ref([
  {
    role: "ai",
    text: "你终于来了",
  },
]);

// 计算最新的AI消息
const latestAiMessage = computed(() => {
  const aiMessages = messages.value.filter((m) => m.role === "ai");
  return aiMessages.length > 0 ? aiMessages[aiMessages.length - 1] : null;
});

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

async function send() {
  if (!input.value.trim() || loading.value) return;

  const userMessage = input.value;
  messages.value.push({ role: "user", text: userMessage });
  input.value = "";
  loading.value = true;

  try {
    const response = await fetch("http://localhost:5000/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: userMessage,
      }),
    });

    const data = await response.json();

    if (data.status === "success") {
      messages.value.push({ role: "ai", text: data.reply });

      // 更新故事状态
      if (data.scene_count !== undefined) {
        storyState.value.scene_count = data.scene_count;
      }
      if (data.story_active !== undefined) {
        storyState.value.story_active = data.story_active;
      }

      // 如果有图片URL，发射背景更新事件
      if (data.image_url) {
        emit("backgroundUpdate", data.image_url);
      }

      // 如果故事结束，显示提示
      if (!data.story_active) {
        setTimeout(() => {
          messages.value.push({
            role: "ai",
            text: "故事已达到结局。感谢您的参与！",
          });
        }, 1500);
      }
    } else {
      messages.value.push({
        role: "ai",
        text: "抱歉，出现了一些问题：" + (data.error || "未知错误"),
      });
    }
  } catch (error) {
    messages.value.push({
      role: "ai",
      text: "抱歉，连接服务器失败，请检查后端服务是否正常运行。",
    });
    console.error("Error:", error);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  // 初始化
});
</script>

<style scoped>
.chat-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  z-index: 10;
}

/* 故事状态样式 */
.story-status {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  border-radius: 12px;
  padding: 10px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  backdrop-filter: blur(10px);
  z-index: 15;
  min-width: 200px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
}

.status-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.scene-count {
  color: #ffd700;
  font-size: 14px;
  font-weight: bold;
}

.story-state {
  color: #4caf50;
  font-size: 12px;
  font-weight: bold;
}

.story-state.story-ended {
  color: #ff6b6b;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(to right, #ffd700, #ffa500);
  border-radius: 2px;
  transition: width 0.3s ease-in-out;
}

/* AI对话框样式 (透明设计) */
.ai-dialog-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.ai-dialog {
  background: rgba(20, 20, 30, 0.7); /* 更透明 */
  border-radius: 12px;
  min-width: 400px;
  max-width: 600px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(15px); /* 增强模糊效果 */
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.ai-dialog-header {
  background: rgba(10, 10, 20, 0.6); /* 更透明 */
  padding: 12px 20px;
  border-radius: 12px 12px 0 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.ai-dialog-title {
  color: #ffffff;
  font-size: 16px;
  font-weight: bold;
  letter-spacing: 2px;
}

.ai-dialog-content {
  padding: 20px;
}

.ai-response {
  color: #ffffff;
  font-size: 16px;
  line-height: 1.6;
  margin: 0;
  text-align: center;
}

.loading-text {
  color: #888;
  font-style: italic;
}

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
  .ai-dialog {
    min-width: 300px;
    max-width: 90vw;
  }

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
