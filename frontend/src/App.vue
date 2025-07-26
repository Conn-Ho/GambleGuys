<script setup>
import { ref, onMounted } from 'vue'
import Loading from './components/Loading.vue'
import TheWelcome from './components/TheWelcome.vue'

const loading = ref(true)

onMounted(() => {
  // 模拟加载2秒
  setTimeout(() => {
    loading.value = false
  }, 2000)
})
</script>

<template>
  <Loading v-if="loading" />
  <main v-else>
    <TheWelcome />
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
