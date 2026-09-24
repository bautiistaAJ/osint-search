<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import GraphView from '../components/GraphView.vue'
import TerminalView from '../components/TerminalView.vue'
import UsernameResults from '../components/UsernameResults.vue'
import EmailResults from '../components/EmailResults.vue'
import DnsResults from '../components/DnsResults.vue'
import SubdomainResults from '../components/SubdomainResults.vue'
import PhoneDossier from '../components/PhoneDossier.vue'
import GithubDossier from '../components/GithubDossier.vue'
import ScanConsole from '../components/ScanConsole.vue'

const query = ref('')
const queryType = ref('username')
const results = ref([])
const breachData = ref(null)
const rawData = ref('')
const rawFound = ref(false)
const dnsRecords = ref({})
const dnsError = ref('')
const dnsFound = ref(false)
const githubData = ref(null)
const loading = ref(false)
const error = ref('')
const showGraph = ref(false)
const searched = ref(false)
const viewMode = ref('graph')
const total = computed(() => results.value.length)
const scanSteps = ref([])
const currentStep = ref(-1)

const GRAPH_TYPES = ['username', 'email']

const scanStepLabels = {
  username: ['Running maigret...', 'Running whatsmyname...', 'Merging results'],
  email: ['Querying holehe...', 'Checking HIBP...'],
  phone: ['Running phoneinfoga...'],
  google: ['Running ghunt...'],
  subdomains: ['Running sublist3r...'],
  harvest: ['Running theHarvester...'],
  dns: ['Resolving DNS records...'],
  github: ['Fetching GitHub API...'],
  domain: ['Querying WHOIS...']
}

async function search() {
  if (!query.value.trim()) return
  loading.value = true
  error.value = ''
  showGraph.value = false
  results.value = []
  breachData.value = null
  rawData.value = ''
  rawFound.value = false
  dnsRecords.value = {}
  dnsError.value = ''
  dnsFound.value = false
  githubData.value = null
  searched.value = true
  viewMode.value = 'graph'
  currentStep.value = -1
  scanSteps.value = scanStepLabels[queryType.value] || ['Searching...']
  try {
    const endpoint = getEndpoint(queryType.value)
    const res = await axios.get(`${endpoint}?q=${encodeURIComponent(query.value)}`)
    const data = res.data
    currentStep.value = scanSteps.value.length - 1
    await processResponse(data)
  } catch (e) {
    error.value = 'Error en la búsqueda. Verificá que el backend esté corriendo.'
    results.value = []
    showGraph.value = false
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function processResponse(data) {
  if (data.results) {
    results.value = Array.isArray(data.results) ? data.results : [data.results]
  } else {
    results.value = []
  }
  breachData.value = data.breach || null
  rawData.value = data.results?.raw || data.raw || ''
  rawFound.value = data.results?.found || data.found || false

  if (queryType.value === 'dns') {
    dnsRecords.value = (typeof data.results === 'object' && !Array.isArray(data.results)) ? data.results : {}
    dnsError.value = data.results?.error || ''
    dnsFound.value = data.found || false
  }

  if (queryType.value === 'github') {
    githubData.value = (typeof data.results === 'object' && !Array.isArray(data.results) && data.results.login) ? data.results : null
  }

  showGraph.value =
    GRAPH_TYPES.includes(queryType.value) &&
    Array.isArray(data.results) &&
    results.value.length > 0
}

function onTypeChange() {
  query.value = ''
  results.value = []
  showGraph.value = false
  searched.value = false
  error.value = ''
  breachData.value = null
  rawData.value = ''
  rawFound.value = false
  dnsRecords.value = {}
  dnsError.value = ''
  dnsFound.value = false
  githubData.value = null
  viewMode.value = 'graph'
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

function isDnsType() {
  return queryType.value === 'dns'
}

function isGithubType() {
  return queryType.value === 'github'
}
</script>

<template>
  <div class="search-section">
    <div class="search-box">
      <select v-model="queryType" class="cyber-select" @change="onTypeChange">
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

    <ScanConsole
      v-if="loading && scanSteps.length > 0"
      :steps="scanSteps"
      :currentStep="currentStep"
      :queryType="queryType"
    />

    <div v-if="searched && !loading && !error" class="results-block">
      <div v-if="showGraph" class="graph-section">
        <div class="view-toggle">
          <button :class="{ active: viewMode === 'graph' }" @click="viewMode = 'graph'">◧ GRAPH</button>
          <button :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'">☰ LIST</button>
        </div>
        <div v-show="viewMode === 'graph'" class="graph-frame">
          <GraphView :results="results" :queryType="queryType" :queryValue="query" />
        </div>
        <div v-show="viewMode === 'list'" class="results">
          <UsernameResults v-if="queryType === 'username'" :results="results" :total="total" />
          <EmailResults v-else :results="results" :breachData="breachData" />
        </div>
      </div>

      <div v-else-if="isRawType() && rawData" class="results">
        <h2 class="section-title">RAW OUTPUT</h2>
        <PhoneDossier v-if="queryType === 'phone'" :raw="rawData" :found="rawFound" />
        <SubdomainResults v-else-if="queryType === 'subdomains' || queryType === 'harvest'" :results="results" :raw="rawData" />
        <TerminalView v-else :raw="rawData" :path="query" :title="queryType.toUpperCase()" />
      </div>

      <div v-else-if="isRawType()" class="results">
        <h2 class="section-title">RESULTADOS</h2>
        <PhoneDossier v-if="queryType === 'phone'" :raw="rawData" :found="rawFound" />
        <SubdomainResults v-else-if="queryType === 'subdomains' || queryType === 'harvest'" :results="results" :raw="rawData" />
        <TerminalView v-else :raw="rawData" :path="query" :title="queryType.toUpperCase()" />
      </div>

      <div v-else-if="isDnsType()" class="results">
        <h2 class="section-title">RESULTADOS</h2>
        <DnsResults :records="dnsRecords" :error="dnsError" :found="dnsFound" />
      </div>

      <div v-else-if="isGithubType()" class="results">
        <h2 class="section-title">RESULTADOS</h2>
        <GithubDossier :data="githubData" :raw="rawData" />
      </div>

      <div v-else-if="queryType === 'email'" class="results">
        <h2 class="section-title">EMAIL / BREACHES</h2>
        <EmailResults :results="results" :breachData="breachData" />
      </div>

      <div v-else class="results">
        <h2 class="section-title">RESULTADOS</h2>
        <p class="no-results">Sin resultados encontrados.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-section { max-width: 1000px; margin: 0 auto; }

.search-box { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }

.section-title {
  font-family: var(--font-mono);
  font-size: 1.2rem;
  color: var(--cyan);
  margin-bottom: var(--spacing-md);
  text-shadow: 0 0 10px #00ffff44;
  border-bottom: 1px solid #00ffff22;
  padding-bottom: var(--spacing-sm);
}

.results { margin-top: 20px; }
.results-block { margin-top: 20px; }

.graph-section { display: flex; flex-direction: column; }
.graph-frame { height: clamp(400px, 60vh, 700px); }

.view-toggle {
  display: flex;
  justify-content: flex-end;
  gap: 0;
  margin-bottom: 10px;
}
.view-toggle button {
  background: var(--bg-primary);
  border: 1px solid var(--border);
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 0.75rem;
  letter-spacing: 1px;
  padding: 6px 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.view-toggle button + button { border-left: none; }
.view-toggle button.active {
  background: var(--cyan);
  color: var(--bg-primary);
  border-color: var(--cyan);
  box-shadow: var(--glow-cyan);
}

.no-results { color: var(--text-muted); font-family: var(--font-mono); font-size: 1rem; }
</style>
