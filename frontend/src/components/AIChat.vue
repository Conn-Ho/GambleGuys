<template>
  <div class="ai-chat">
    <div class="messages">
      <div v-for="(msg, idx) in messages" :key="idx" :class="msg.role">
        <template v-if="msg.role === 'ai'">
          <span></span>{{ msg.text }}
        </template>
        <template v-else>
          <span>我：</span>{{ msg.text }}
        </template>
      </div>
    </div>
    <div class="input-row">
      <input v-model="input" @keyup.enter="send" placeholder="输入你的问题..." />
      <button @click="send">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const input = ref('')
const messages = ref([
  { role: 'ai', text: '你好，我是AI，有什么可以帮你？' }
])
function send() {
  if (!input.value.trim()) return
  messages.value.push({ role: 'user', text: input.value })
  // 这里模拟AI回复，实际可接API
  setTimeout(() => {
    messages.value.push({ role: 'ai', text: 'AI回复：' + input.value })
  }, 500)
  input.value = ''
}
</script>

<style scoped>
.ai-chat {
  position: fixed;
  right: 32px;
  bottom: 32px;
  width: 360px;
  max-height: 70vh;
  background: rgba(30,30,30,0.8);
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
.user, .ai {
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
button:hover {
  background: linear-gradient(90deg, #2563eb, #4e8cff);
}
.messages::-webkit-scrollbar {
  width: 6px;
}
.messages::-webkit-scrollbar-thumb {
  background: #444a;
  border-radius: 3px;
}
</style> 