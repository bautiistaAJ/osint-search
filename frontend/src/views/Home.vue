<script setup>
import { ref } from 'vue'
import axios from 'axios'
import GraphView from '../components/GraphView.vue'

const query = ref('')
const queryType = ref('username')
const results = ref([])
const breachData = ref(null)
const loading = ref(false)
const error = ref('')
const showGraph = ref(false)
const searched = ref(false)

async function search() {
  if (!query.value.trim()) return
  loading.value = true
  error.value = ''
  showGraph.value = false
  results.value = []
  searched.value = true
  try {
    const endpoint = getEndpoint(queryType.value)
    const res = await axios.get(`${endpoint}?q=${encodeURIComponent(query.value)}`)
    const data = res.data
    if (data.results) {
      results.value = Array.isArray(data.results) ? data.results : [data.results]
    } else {
      results.value = []
    }
    breachData.value = data.breach || null
    if (Array.isArray(results.value) && results.value.length > 0) {
      showGraph.value = true
    }
  } catch (e) {
    error.value = 'Error en la búsqueda. Verificá que el backend esté corriendo.'
    results.value = []
    showGraph.value = false
    console.error(e)
  } finally {
    loading.value = false
  }
}

function getEndpoint(type) {
  const map = {
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
  return map[type] || '/api/search/username'
}

function formatResult(r) {
  if (typeof r === 'string') return r
  if (!r || typeof r !== 'object') return 'Resultado'
  return r.site || r.username || r.url || r.email || r.login || r.name || r.raw || 'Resultado'
}

function getUrl(r) {
  if (!r || typeof r !== 'object') return ''
  return r.url || r.site_url || r.profile_url || r.html_url || r[0]?.url || ''
}

function getPlaceholder(type) {
  const placeholders = {
    username: 'ingresá un handle o nombre de usuario...',
    email: 'ingresá un email...',
    domain: 'ingresá un dominio (ej: example.com)...',
    phone: 'ingresá un número de teléfono (ej: +1234567890)...',
    google: 'ingresá un email para buscar su cuenta Google...',
    subdomains: 'ingresá un dominio para buscar subdominios...',
    harvest: 'ingresá un dominio para recolectar emails...',
    dns: 'ingresá un dominio para ver sus registros DNS...',
    github: 'ingresá un username de GitHub...'
  }
  return placeholders[type] || 'ingresá un valor...'
}

function isRawType() {
  return ['phone', 'google', 'subdomains', 'harvest', 'domain'].includes(queryType.value)
}

function isRawResult() {
  return isRawType() && results.value && results.value.raw
}

function isDnsResult() {
  return queryType.value === 'dns' && results.value && results.value.A !== undefined && !results.value.error
}

function isGithubResult() {
  return queryType.value === 'github' && results.value && results.value.login
}

function getDnsRecords() {
  if (!isDnsResult()) return {}
  return results.value
}
</script>

<template>
  <div class="search-section">
    <div class="search-box">
      <select v-model="queryType" class="cyber-select">
        <option value="username">👤 USUARIO / HANDLE</option>
        <option value="email">📧 EMAIL</option>
        <option value="domain">🌐 DOMINIO</option>
        <option value="phone">📱 TELÉFONO</option>
        <option value="google">🔍 GOOGLE ACCOUNT</option>
        <option value="subdomains">🕸️ SUBDOMINIOS</option>
        <option value="harvest">🎯 RECOLECCIÓN EMAIL</option>
        <option value="dns">📋 REGISTROS DNS</option>
        <option value="github">🐙 GITHUB</option>
      </select>
      <input
        v-model="query"
        class="cyber-input"
        :placeholder="getPlaceholder(queryType)"
        @keyup.enter="search"
      />
      <button @click="search" :disabled="loading" class="cyber-btn">
        <span v-if="loading" class="scanning">SCANNING...</span>
        <span v-else>▶ INICIAR SCAN</span>
      </button>
    </div>

    <div v-if="error" class="cyber-error">{{ error }}</div>

    <div v-if="showGraph && results.length > 0" class="graph-section">
      <GraphView :results="results" :queryType="queryType" :queryValue="query" />
    </div>

    <div v-if="searched && !showGraph && results.length > 0" class="results">
      <h2 class="section-title">RESULTADOS</h2>

      <div v-if="isRawResult()" class="raw-result">
        <pre>{{ results.raw }}</pre>
      </div>

      <div v-else-if="isDnsResult()" class="dns-result">
        <div v-for="(vals, type) in getDnsRecords()" :key="type" class="dns-card" v-if="Array.isArray(vals) && vals.length > 0">
          <strong>{{ type }}</strong>
          <ul>
            <li v-for="v in vals" :key="v">{{ v }}</li>
          </ul>
        </div>
        <div v-if="results.error" class="cyber-error">{{ results.error }}</div>
      </div>

      <div v-else-if="isGithubResult()" class="github-card">
        <div class="card-glow"></div>
        <div class="card-body">
          <strong>{{ results.name || results.login }}</strong>
          <p>{{ results.bio }}</p>
          <a :href="results.html_url" target="_blank" rel="noopener">{{ results.html_url }}</a>
          <div class="github-meta">
            <span>Repos: {{ results.public_repos }}</span>
            <span>Followers: {{ results.followers }}</span>
            <span>Location: {{ results.location || 'N/A' }}</span>
          </div>
        </div>
      </div>

      <div v-else-if="queryType === 'email' && results.length === 0 && breachData" class="breach-extra">
        <h2 class="section-title">🔒 BRECHAS</h2>
        <div v-if="breachData.found" class="breach-found">
          <p>Se encontraron {{ breachData.breaches?.length || 0 }} brechas.</p>
          <ul>
            <li v-for="(b, i) in breachData.breaches" :key="i">
              {{ b.Title || b.Name || b.name }} - {{ b.BreachDate || 'Fecha desconocida' }}
            </li>
          </ul>
        </div>
        <div v-else-if="breachData.error" class="breach-found">
          <p>⚠ Error al consultar HIBP: {{ breachData.error }}</p>
        </div>
        <div v-else class="breach-ok">
          <p>✅ No se encontraron brechas.</p>
        </div>
      </div>

      <div v-else class="cards">
        <div v-for="(r, i) in results" :key="i" class="cyber-card">
          <div class="card-glow"></div>
          <div class="card-body">
            <strong>{{ formatResult(r) }}</strong>
            <a v-if="getUrl(r)" :href="getUrl(r)" target="_blank" rel="noopener">{{ getUrl(r) }}</a>
          </div>
        </div>
      </div>
    </div>

    <div v-if="searched && !showGraph && results.length === 0 && !error" class="results">
      <h2 class="section-title">RESULTADOS</h2>
      <p class="no-results">Sin resultados encontrados.</p>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

.search-section {
  max-width: 1000px;
  margin: 0 auto;
}

.search-box {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.cyber-select {
  padding: 12px 16px;
  border-radius: 0;
  border: 1px solid #00ffff44;
  background: #0a0e1a;
  color: #00ffff;
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.85rem;
  outline: none;
  cursor: pointer;
  transition: all 0.3s;
}
.cyber-select:focus {
  border-color: #00ffff;
  box-shadow: 0 0 10px #00ffff33;
}

.cyber-input {
  flex: 1;
  min-width: 200px;
  padding: 12px 16px;
  border-radius: 0;
  border: 1px solid #334155;
  background: #0a0e1a;
  color: #e2e8f0;
  font-family: 'Share Tech Mono', monospace;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s;
}
.cyber-input:focus {
  border-color: #00ffff;
  box-shadow: 0 0 15px #00ffff22;
}

.cyber-btn {
  padding: 12px 28px;
  border-radius: 0;
  background: linear-gradient(135deg, #00ffff, #ff00ff);
  color: #0a0e1a;
  font-family: 'Share Tech Mono', monospace;
  font-weight: bold;
  font-size: 0.9rem;
  border: none;
  cursor: pointer;
  letter-spacing: 1px;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}
.cyber-btn:hover:not(:disabled) {
  box-shadow: 0 0 20px #00ffff66;
  transform: translateY(-1px);
}
.cyber-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.scanning {
  animation: blink 0.8s infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.cyber-error {
  background: #7f1d1d;
  color: #fca5a5;
  padding: 12px;
  border-left: 4px solid #ff0000;
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.85rem;
  margin-bottom: 20px;
}

.section-title {
  font-family: 'Share Tech Mono', monospace;
  font-size: 1.2rem;
  color: #00ffff;
  margin-bottom: 16px;
  text-shadow: 0 0 10px #00ffff44;
  border-bottom: 1px solid #00ffff22;
  padding-bottom: 8px;
}

.results {
  margin-top: 20px;
}

.no-results {
  color: #64748b;
  font-family: 'Share Tech Mono', monospace;
  font-size: 1rem;
}

.cards { display: grid; gap: 12px; }

.cyber-card {
  background: #0a0e1a;
  border: 1px solid #334155;
  border-radius: 0;
  padding: 16px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}
.cyber-card:hover {
  border-color: #00ffff66;
  box-shadow: 0 0 15px #00ffff11;
}
.card-glow {
  position: absolute;
  top: 0; left: -100%;
  width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(0,255,255,0.05), transparent);
  transition: left 0.5s;
}
.cyber-card:hover .card-glow {
  left: 100%;
}
.card-body strong { color: #00ffff; font-family: 'Share Tech Mono', monospace; }
.card-body a { display: block; margin-top: 8px; color: #94a3b8; font-size: 0.85rem; font-family: 'Share Tech Mono', monospace; word-break: break-all; }

.breach-extra, .breach-section { background: #0a0e1a; border-radius: 0; padding: 16px; margin-bottom: 16px; border: 1px solid #334155; }
.breach-found { background: #7f1d1d; padding: 12px; border-left: 4px solid #ff0000; }
.breach-ok { background: #14532d; padding: 12px; border-left: 4px solid #00ff00; color: #4ade80; }
.breach-found p, .breach-ok p { font-family: 'Share Tech Mono', monospace; }
.breach-found ul, .breach-ok ul { margin-top: 8px; padding-left: 20px; }
.breach-found li, .breach-ok li { font-family: 'Share Tech Mono', monospace; font-size: 0.9rem; color: #e2e8f0; }

.graph-section { margin-top: 20px; }

.raw-result pre {
  background: #0a0e1a;
  border: 1px solid #334155;
  border-radius: 0;
  padding: 16px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.85rem;
  color: #00ff00;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 400px;
  overflow-y: auto;
}

.dns-result { display: grid; gap: 12px; }
.dns-card { background: #0a0e1a; border: 1px solid #334155; padding: 12px; }
.dns-card strong { color: #00ffff; font-family: 'Share Tech Mono', monospace; }
.dns-card ul { list-style: none; padding: 0; margin-top: 8px; }
.dns-card li { color: #e2e8f0; font-family: 'Share Tech Mono', monospace; font-size: 0.9rem; padding: 2px 0; }

.github-card { background: #0a0e1a; border: 1px solid #334155; padding: 16px; position: relative; overflow: hidden; }
.github-card:hover { border-color: #ff00ff44; box-shadow: 0 0 15px #ff00ff11; }
.github-card .card-body { font-family: 'Share Tech Mono', monospace; }
.github-card .card-body strong { color: #00ffff; font-size: 1.2rem; }
.github-card .card-body p { color: #94a3b8; margin: 8px 0; }
.github-card .card-body a { color: #94a3b8; font-size: 0.85rem; display: block; margin-top: 8px; }
.github-meta { display: flex; gap: 20px; margin-top: 12px; flex-wrap: wrap; }
.github-meta span { color: #64748b; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; }
</style>
