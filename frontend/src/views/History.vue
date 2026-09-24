<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const history = ref([])
const loading = ref(false)

function relativeTime(dateStr) {
  const now = new Date()
  const d = new Date(dateStr)
  const diff = Math.floor((now - d) / 1000)
  if (diff < 60) return 'hace un momento'
  if (diff < 3600) return `hace ${Math.floor(diff / 60)}m`
  if (diff < 86400) return `hace ${Math.floor(diff / 3600)}h`
  if (diff < 604800) return `hace ${Math.floor(diff / 86400)}d`
  return d.toLocaleDateString()
}

async function loadHistory() {
  loading.value = true
  try {
    const res = await axios.get('/api/history')
    history.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function rerun(item) {
  try {
    const typeMap = {
      username: '/api/search/username',
      email: '/api/search/email',
      domain: '/api/search/domain',
      phone: '/api/search/phone',
      google: '/api/search/google',
      subdomains: '/api/search/subdomains',
      harvest: '/api/search/harvest',
      dns: '/api/search/dns',
      github: '/api/search/github'
    }
    const endpoint = typeMap[item.query_type]
    if (endpoint) {
      await axios.get(`${endpoint}?q=${encodeURIComponent(item.query_value)}`)
    }
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadHistory)
</script>

<template>
  <div class="cyber-body">
    <div class="cyber-grid"></div>
    <div class="container">
      <header class="cyber-header">
        <h1 class="glitch-text" data-text="HISTORIAL">HISTORIAL</h1>
        <p class="cyber-subtitle">Últimas búsquedas ejecutadas</p>
      </header>

      <div v-if="loading" class="loading-state">SCANNING...</div>

      <div v-if="history.length === 0 && !loading" class="empty-state">
        <p>No tenés búsquedas previas.</p>
      </div>

      <div v-else class="list">
        <div v-for="item in history" :key="item.id" class="cyber-card">
          <div class="card-glow"></div>
          <div class="card-body">
            <span class="badge">{{ item.query_type }}</span>
            <span class="date">{{ relativeTime(item.created_at) }}</span>
            <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
              <p class="query">{{ item.query_value }}</p>
              <button @click="rerun(item)" class="cyber-btn" style="padding: 6px 14px; font-size: 0.75rem; flex-shrink: 0;">RE-RUN</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

.cyber-body { background: var(--bg-primary); min-height: 100vh; position: relative; }
.container { max-width: 900px; margin: 0 auto; padding: var(--spacing-md); position: relative; z-index: 1; }
.cyber-header { text-align: center; margin-bottom: var(--spacing-lg); padding: var(--spacing-lg); }
.list { display: grid; gap: var(--spacing-md); }
.cyber-card { background: var(--bg-card); border: 1px solid var(--border); padding: var(--spacing-md); position: relative; overflow: hidden; transition: all 0.3s; }
.cyber-card:hover { border-color: var(--border-cyan); box-shadow: var(--glow-cyan-soft); }
.card-glow { position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(0,255,255,0.05), transparent); transition: left 0.5s; }
.cyber-card:hover .card-glow { left: 100%; }
.card-body { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: var(--spacing-sm); }
.query { font-family: var(--font-mono); font-size: 1rem; color: var(--text-primary); margin-top: var(--spacing-sm); }
.date { color: var(--text-muted); font-family: var(--font-mono); font-size: 0.8rem; }
</style>
