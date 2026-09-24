<script setup>
import { onMounted, ref } from 'vue'

const props = defineProps({
  raw: { type: String, default: '' },
  title: { type: String, default: 'TERMINAL OUTPUT' },
  path: { type: String, default: '' }
})

const lines = ref([])
const visible = ref(false)

function parseOutput(raw) {
  if (!raw) return []
  return raw.split('\n').filter(l => l.trim() !== '')
}

function copyOutput() {
  if (props.raw) {
    navigator.clipboard.writeText(props.raw).catch(() => {})
  }
}

onMounted(() => {
  lines.value = parseOutput(props.raw)
  visible.value = true
})
</script>

<template>
  <div class="terminal" v-if="visible">
    <div class="terminal-header">
      <div class="terminal-dot red"></div>
      <div class="terminal-dot yellow"></div>
      <div class="terminal-dot green"></div>
      <span class="terminal-title">{{ title }}</span>
    </div>
    <div class="terminal-body">
      <div v-if="path" class="terminal-line info">
        <span class="terminal-path">{{ path }}</span>
      </div>
      <div v-for="(line, i) in lines" :key="i" class="terminal-line">
        <span class="timestamp">{{ i + 1 }}</span>{{ line }}
      </div>
      <div v-if="lines.length === 0" class="terminal-line error">No output generated.</div>
    </div>
    <div style="padding: 8px 12px; border-top: 1px solid var(--border); display: flex; gap: 8px; justify-content: flex-end;">
      <button @click="copyOutput" class="cyber-btn" style="padding: 6px 14px; font-size: 0.75rem;">COPY</button>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
</style>
