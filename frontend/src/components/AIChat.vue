<template>
  <div class="ai-chat">
    <div class="messages" ref="messagesContainer">
      <div v-for="(msg, idx) in messages" :key="idx" :class="msg.role">
        <template v-if="msg.role === 'ai'">
          <span></span>{{ msg.text }}
        </template>
        <template v-else> <span>我：</span>{{ msg.text }} </template>
      </div>
      <div v-if="loading" class="loading">正在思考...</div>
    </div>
    <div class="input-row">
      <input
        v-model="input"
        @keyup.enter="send"
        placeholder="输入你的问题..."
        :disabled="loading"
      />
      <button @click="send" :disabled="loading">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from "vue";

const input = ref("");
const loading = ref(false);
const messagesContainer = ref(null);
const messages = ref([
  {
    role: "ai",
    text: "你好，我是AI故事助手，可以为你创作故事和生成配图。请告诉我你想要什么样的故事？",
  },
]);

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
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
    await scrollToBottom();
  }
}

onMounted(() => {
  scrollToBottom();
});
</script>

<style scoped>
.ai-chat {
  position: fixed;
  right: 32px;
  bottom: 32px;
  width: 360px;
  height: 600px;
  max-height: 70vh;
  background: rgba(30, 30, 30, 0.8);
  border-radius: 18px;
  display: flex;
  flex-direction: column;
  z-index: 10;
  color: #fff;
  overflow: hidden;
}
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.user,
.ai {
  max-width: 80%;
  padding: 10px 16px;
  border-radius: 18px;
  word-break: break-all;
  display: inline-block;
}
.user {
  align-self: flex-end;
  color: #fff;
  text-align: right;
  background: #2563eb;
}

.ai {
  display: flex;
  align-items: flex-start;
  background: #222;
  color: #ffd580;
  text-align: left;
  padding-left: 4px;
}
.input-row {
  display: flex;
  border-top: 1px solid #444;
  padding: 12px 8px;
  background: #222c;
  box-shadow: 0 -2px 8px #0004;
}
input {
  flex: 1;
  border: none;
  outline: none;
  padding: 10px;
  border-radius: 8px;
  margin-right: 8px;
  background: #333;
  color: #fff;
  font-size: 16px;
}
input:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
button {
  background: linear-gradient(90deg, #4e8cff, #2563eb);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
}
button:hover:not(:disabled) {
  background: linear-gradient(90deg, #2563eb, #4e8cff);
}
button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
.messages::-webkit-scrollbar {
  width: 6px;
}
.messages::-webkit-scrollbar-thumb {
  background: #444a;
  border-radius: 3px;
}
.loading {
  align-self: center;
  color: #666;
  margin: 10px 0;
  font-style: italic;
}
</style>
