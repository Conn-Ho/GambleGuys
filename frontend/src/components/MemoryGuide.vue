<template>
  <div class="memory-guide-overlay">
    <div class="memory-guide-container">
   
      <!-- 主要内容 -->
      <div class="guide-content">
  

        <div class="guide-body">
          <!-- 记忆输入区域 -->
          <div class="memory-input-area">
            <!-- AI输出框 -->
            <div v-if="aiResponse" class="ai-output-box">
              <div class="output-content">{{ aiResponse }}</div>
            </div>
            
            <!-- 加载状态显示在输出框位置 -->
            <div v-if="loading && !aiResponse" class="ai-output-box loading-box">
              <Loading :inline="true" :text="''" />
            </div>
            
            <div class="input-container">
              <textarea 
                v-model="memoryInput"
                class="memory-textarea"
                :disabled="loading"
                @keydown.enter.ctrl="sendMemory"
                placeholder="在这里输入您的记忆..."
              ></textarea>
              <button 
                class="send-memory-btn" 
                @click="sendMemory"
                :disabled="loading || !memoryInput.trim()"
              >
                {{ loading ? '发送中...' : '发送记忆' }}
              </button>
            </div>
          </div>
        </div>

        <div class="guide-footer">
          <button v-if="hasInteracted" class="start-button" @click="startGame">
            <span class="button-text">开始游戏</span>
            <div class="button-effect"></div>
          </button>
       
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import Loading from './Loading.vue';

// 定义emits
const emit = defineEmits(['completed']);

// 记忆相关状态
const memoryInput = ref('');
const aiResponse = ref('');
const loading = ref(false);
const hasInteracted = ref(false); // 跟踪是否已经发送过记忆

// 初始化获取AI引导词
const initializeAIGuide = async () => {
  loading.value = true;
  
  try {
    const response = await fetch('http://localhost:5001/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: '请作为一个友好的AI伙伴，生成一段欢迎用户的引导词，引导用户分享一个对他们来说意义深刻的回忆。语调要温暖友好，让用户感到舒适和被理解。',
      }),
    });

    const data = await response.json();

    if (data.status === 'success') {
      aiResponse.value = data.reply;
    } else {
      // 如果API调用失败，使用备用引导词
      aiResponse.value = '欢迎来到记忆之旅！\n\n我是你的AI伙伴，很高兴认识你。在我们开始这段奇妙的冒险之前，我想了解一些关于你的特别记忆。\n\n请分享一个对你来说意义深刻的回忆，可以是快乐的、感动的，或是让你印象深刻的任何经历。这将帮助我更好地为你定制独特的游戏体验。';
    }
  } catch (error) {
    console.error('初始化AI引导词失败:', error);
    // 如果网络错误，使用备用引导词
    aiResponse.value = '欢迎来到记忆之旅！\n\n我是你的AI伙伴，很高兴认识你。在我们开始这段奇妙的冒险之前，我想了解一些关于你的特别记忆。\n\n请分享一个对你来说意义深刻的回忆，可以是快乐的、感动的，或是让你印象深刻的任何经历。这将帮助我更好地为你定制独特的游戏体验。';
  } finally {
    loading.value = false;
  }
};

// 初始化时调用AI引导词生成
onMounted(() => {
  initializeAIGuide();
});

// 发送记忆到AI工作流
const sendMemory = async () => {
  if (!memoryInput.value.trim() || loading.value) return;

  const userMemory = memoryInput.value.trim();
  loading.value = true;
  aiResponse.value = '';

  try {
    const response = await fetch('http://localhost:5001/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: `这是我的记忆分享: ${userMemory}`,
      }),
    });

    const data = await response.json();

    if (data.status === 'success') {
      aiResponse.value = data.reply;
      hasInteracted.value = true; // 标记已经交互过
    } else {
      aiResponse.value = '抱歉，处理记忆时出现问题：' + (data.error || '未知错误');
      hasInteracted.value = true;
    }
  } catch (error) {
    aiResponse.value = '连接失败，请检查网络连接。';
    hasInteracted.value = true;
    console.error('Error:', error);
  } finally {
    loading.value = false;
  }
};

// 开始游戏
const startGame = () => {
  const memoryData = {
    userMemory: memoryInput.value,
    aiResponse: aiResponse.value
  };
  console.log('🧠 Memory data:', memoryData);
  console.log('🎮 准备进入主游戏界面（带背景更新功能）');
  emit('completed', memoryData);
};
</script>

<style scoped>
.memory-guide-overlay {
  position: fixed;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  background-image: url('../assets/bg/image.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 9999;
  overflow-y: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.memory-guide-container {
  position: relative;
  max-width: 800px;
  width: 100%;
  min-height: 600px;
}

.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.floating-orb {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  animation: float 6s ease-in-out infinite;
}

.orb-1 {
  width: 100px;
  height: 100px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.orb-2 {
  width: 150px;
  height: 150px;
  top: 60%;
  right: 15%;
  animation-delay: 2s;
}

.orb-3 {
  width: 80px;
  height: 80px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

.guide-content {
  background: transparent;
  padding: 40px;
  position: relative;
  z-index: 1;
}

.guide-header {
  text-align: center;
  margin-bottom: 30px;
}

.memory-icon {
  font-size: 64px;
  margin-bottom: 16px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.guide-title {
  font-size: 36px;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.guide-subtitle {
  font-size: 18px;
  color: #718096;
  margin: 0;
}





.response-content {
  font-size: 16px;
  color: #2d3748;
  line-height: 1.6;
}

/* 加载状态 */
.loading-display {
  text-align: center;
  padding: 20px;
  margin-bottom: 25px;
}

.loading-text {
  font-size: 16px;
  color: #718096;
  font-style: italic;
}

/* 记忆输入区域 */
.memory-input-area {
  position: fixed;
  bottom: 50px;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  max-width: 600px;
  background: transparent;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* AI输出框 */
.ai-output-box {
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(15px);
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  padding: 15px;
  max-height: 200px;
  overflow-y: auto;
  animation: slideUp 0.3s ease-out;
}

.ai-output-box.loading-box {
  border-color: rgba(255, 255, 255, 0.3);
  text-align: center;
}

.output-header {
  font-size: 14px;
  font-weight: 600;
  color: rgba(102, 126, 234, 0.8);
  margin-bottom: 8px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.2);
  padding-bottom: 5px;
}

.output-content {
  font-size: 16px;
  color: #ffffff;
  line-height: 1.6;
  white-space: pre-wrap;
}

.loading-text {
  font-size: 16px;
  color: #ffffff;
  font-style: italic;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 输入框样式调整 */
.input-container {
  position: relative;
  background: transparent;
}

.memory-textarea {
  width: 100%;
  min-height: 120px;
  padding: 15px;
  padding-bottom: 60px; /* 为按钮留出空间 */
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  font-size: 16px;
  line-height: 1.5;
  resize: vertical;
  transition: all 0.3s ease;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  box-sizing: border-box;
  color: #ffffff;
}

.memory-textarea::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.memory-textarea:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(0, 0, 0, 0.7);
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
}

.memory-textarea:disabled {
  opacity: 0.6;
  color: #94a3b8;
}

.send-memory-btn {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: linear-gradient(135deg, #6b7280, #4b5563);
  color: white;
  border: none;
  border-radius: 25px;
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 1;
}

.send-memory-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(107, 114, 128, 0.3);
  background: linear-gradient(135deg, #4b5563, #374151);
}

.send-memory-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.input-hint {
  font-size: 12px;
  color: #a0aec0;
  text-align: center;
  margin: 5px 0 0 0;
}

.guide-footer {
  text-align: center;
}

.start-button {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: linear-gradient(135deg, #6b7280, #4b5563);
  color: white;
  border: none;
  border-radius: 50px;
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  z-index: 9998;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.start-button:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 12px 30px rgba(107, 114, 128, 0.4);
  background: linear-gradient(135deg, #4b5563, #374151);
}

.start-button:active {
  transform: translateY(-1px) scale(1.02);
}

.button-text {
  position: relative;
  z-index: 2;
}

.button-effect {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.start-button:hover .button-effect {
  left: 100%;
}

.privacy-note {
  font-size: 12px;
  color: #a0aec0;
  margin: 0;
  max-width: 400px;
  margin: 0 auto;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .memory-guide-overlay {
    padding: 10px;
  }

  .guide-content {
    padding: 30px 20px;
  }

  .guide-title {
    font-size: 28px;
  }

  .memory-input-area {
    width: 90%;
    bottom: 20px;
  }
  
  .ai-output-box {
    max-height: 150px;
    padding: 12px;
  }
  
  .memory-textarea {
    min-height: 100px;
    font-size: 14px;
  }

  .start-button {
    bottom: 20px;
    right: 20px;
    padding: 12px 24px;
    font-size: 14px;
  }
}
</style>