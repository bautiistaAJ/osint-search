<script setup>
import { ref } from 'vue'

const props = defineProps({
  raw: { type: String, default: '' },
  found: { type: Boolean, default: false }
})

const metrics = ref([])

function parseMetrics(raw) {
  if (!raw) return []
  return raw.split('\n').filter(l => l.trim() && !l.startsWith('#') && l.includes(':'))
}

metrics.value = parseMetrics(props.raw)
</script>

<template>
  <div class="phone-dossier">
    <div class="section-title">PHONE DOSSIER</div>
    <div v-if="found && metrics.length > 0" class="dossier-grid">
      <div v-for="(m, i) in metrics" :key="i" class="dossier-panel">
        <div class="phone-metric" v-if="m.includes(':')">
          <span class="phone-metric-label">{{ m.split(':')[0].trim() }}</span>
          <span class="phone-metric-value">{{ m.split(':')[1].trim() }}</span>
        </div>
        <div v-else class="cyber-card">
          <div class="card-body"><strong>{{ m }}</strong></div>
        </div>
      </div>
    </div>
    <div v-else-if="raw" class="terminal">
      <div class="terminal-header">
        <div class="terminal-dot red"></div>
        <div class="terminal-dot yellow"></div>
        <div class="terminal-dot green"></div>
        <span class="terminal-title">OUTPUT</span>
      </div>
      <div class="terminal-body">
        <div v-for="(line, i) in raw.split('\n').filter(l => l.trim())" :key="i" class="terminal-line">
          {{ line }}
        </div>
      </div>
    </div>
    <div v-else class="empty-state">No phone data found.</div>
  </div>
</template>

<style scoped>
.phone-metric-label { color: var(--text-muted); font-family: var(--font-mono); font-size: 0.8rem; }
.phone-metric-value { color: var(--text-primary); font-family: var(--font-mono); font-size: 0.8rem; font-weight: bold; }
</style>
