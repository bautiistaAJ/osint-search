<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { Network } from 'vis-network/standalone'
import 'vis-network/styles/vis-network.css'
import { DataSet } from 'vis-data/peer'

const props = defineProps({
  results: { type: Array, default: () => [] },
  queryType: { type: String, default: 'username' },
  queryValue: { type: String, default: '' },
  breachData: { type: Object, default: null }
})

const TOP_K = 24

const containerRef = ref(null)
let network = null
let resizeObserver = null
let nodes = null
let edges = null

const shownCount = ref(0)
const frozen = ref(false)
const findOpen = ref(false)
const findQuery = ref('')
const selected = ref(null)

const typeBorders = {
  username: '#ff00ff',
  email: '#ffff00',
  domain: '#00ff00',
  phone: '#ff00ff',
  google: '#ffff00',
  subdomains: '#00ff00',
  harvest: '#00ff00',
  dns: '#00ff00',
  github: '#64748b'
}

const borderColor = computed(() => typeBorders[props.queryType] || '#ff00ff')
const totalCount = computed(() => props.results.length)
const withUrlCount = computed(() =>
  props.results.filter(r => r && typeof r === 'object' && /^https?:\/\//.test(r.url || r.site_url || r.profile_url || r.html_url || '')).length
)
const withoutUrlCount = computed(() => totalCount.value - withUrlCount.value)
const hasMore = computed(() => shownCount.value < totalCount.value)

const breachChip = computed(() => {
  const b = props.breachData
  if (!b) return null
  if (b.checked === false) return { text: 'BREACH: NO CONFIGURADO', cls: 'chip-warn' }
  if (b.found) return { text: `BREACH: ${b.breaches?.length || 0} HIT`, cls: 'chip-danger' }
  return { text: 'BREACH: LIMPIO', cls: 'chip-ok' }
})

const FA_PLATFORMS = [
  { re: /github/i, code: '\uf09b' },
  { re: /gitlab/i, code: '\uf296' },
  { re: /bitbucket/i, code: '\uf171' },
  { re: /(twitter|x\.com)/i, code: '\uf099' },
  { re: /instagram/i, code: '\uf16d' },
  { re: /facebook/i, code: '\uf09a' },
  { re: /linkedin/i, code: '\uf08c' },
  { re: /reddit/i, code: '\uf1a2' },
  { re: /youtube/i, code: '\uf167' },
  { re: /twitch/i, code: '\uf1e8' },
  { re: /tumblr/i, code: '\uf173' },
  { re: /pinterest/i, code: '\uf0d2' },
  { re: /medium/i, code: '\uf23a' },
  { re: /stackoverflow/i, code: '\uf16c' },
  { re: /spotify/i, code: '\uf1bc' },
  { re: /soundcloud/i, code: '\uf1be' },
  { re: /slack/i, code: '\uf198' },
  { re: /whatsapp/i, code: '\uf232' },
  { re: /dropbox/i, code: '\uf16b' },
  { re: /paypal/i, code: '\uf1ed' },
  { re: /apple|icloud/i, code: '\uf179' },
  { re: /android/i, code: '\uf17b' },
  { re: /google/i, code: '\uf1a0' },
  { re: /yahoo/i, code: '\uf19e' },
  { re: /flickr/i, code: '\uf16e' },
  { re: /dribbble/i, code: '\uf17d' },
  { re: /behance/i, code: '\uf1b4' },
  { re: /skype/i, code: '\uf17e' },
  { re: /steam/i, code: '\uf1b6' },
  { re: /vk/i, code: '\uf189' }
]

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
}

function truncateLabel(s) {
  return s.length > 20 ? s.substring(0, 20) + '…' : s
}

function makeTitle(html) {
  const el = document.createElement('div')
  el.innerHTML = html
  return el
}

function hostname(url) {
  try { return new URL(url).hostname.replace(/^www\./, '') } catch { return '' }
}

function platformIcon(url, siteName) {
  const hay = `${url || ''} ${siteName || ''}`
  const hit = FA_PLATFORMS.find(p => p.re.test(hay))
  return hit ? hit.code : null
}

function resultLabel(r) {
  return String(r.site || r.username || r.url || r.login || r.name || 'Unknown')
}

function resultUrl(r) {
  const raw = r.url || r.site_url || r.profile_url || r.html_url || ''
  return /^https?:\/\//.test(raw) ? raw : ''
}

function addCenterNode() {
  nodes.add({
    id: 'search',
    label: props.queryValue || 'search',
    color: {
      background: '#0a0e1a',
      highlight: { background: '#0f1524', border: '#00ffff' },
      border: '#00ffff'
    },
    borderWidth: 2,
    shape: 'database',
    mass: 4,
    font: { color: '#00ffff', size: 15, face: 'Share Tech Mono' },
    title: makeTitle(`<b>CONSULTA</b><br>${escapeHtml(props.queryValue || 'search')}`)
  })
}

function addResultNode(r, i) {
  if (!r || typeof r !== 'object') return false
  const id = `node_${i}`
  if (nodes.get(id)) return false
  const siteName = resultLabel(r)
  const url = resultUrl(r)
  const border = borderColor.value
  const icon = platformIcon(url, siteName)
  const host = hostname(url)

  const base = {
    id,
    label: `**${truncateLabel(siteName)}**`,
    searchText: `${siteName} ${host}`.toLowerCase(),
    siteName,
    font: { color: '#e2e8f0', size: 12, face: 'Share Tech Mono', multi: 'md' },
    url,
    title: makeTitle(
      url
        ? `<b>${escapeHtml(siteName)}</b><br>${escapeHtml(url)}<br>↗ seleccioná y ABRIR`
        : `<b>${escapeHtml(siteName)}</b><br>sin URL`
    )
  }

  if (icon) {
    nodes.add({
      ...base,
      shape: 'icon',
      icon: { face: "'FontAwesome'", code: icon, size: 28, color: border }
    })
  } else {
    nodes.add({
      ...base,
      shape: 'box',
      widthConstraint: { maximum: 160 },
      margin: 6,
      borderWidth: 1.5,
      color: {
        background: '#0a0e1aee',
        highlight: { background: '#0f1524', border: '#ffffff' },
        border
      }
    })
  }

  edges.add({
    from: 'search',
    to: id,
    label: host || '',
    arrows: { to: { enabled: true, scaleFactor: 0.5 } },
    font: { size: 10, color: '#94a3b8', background: '#0a0e1a', align: 'middle' },
    color: url
      ? { color: '#00ffff', highlight: '#00ffff' }
      : { color: '#334155', highlight: '#475569' },
    width: url ? 2 : 1,
    dashes: url ? false : [4, 6]
  })
  return true
}

function addRange(from, to) {
  let added = 0
  for (let i = from; i < to && i < props.results.length; i++) {
    if (addResultNode(props.results[i], i)) added++
  }
  return added
}

function graphOptions() {
  return {
    nodes: {
      shape: 'box',
      font: { face: 'Share Tech Mono', size: 12, multi: 'md' }
    },
    edges: {
      smooth: { type: 'cubicBezier' },
      font: { size: 10, color: '#94a3b8', background: '#0a0e1a', align: 'middle' },
      arrows: { to: { enabled: true, scaleFactor: 0.5 } }
    },
    physics: {
      forceAtlas2Based: {
        gravitationalConstant: -40,
        centralGravity: 0.04,
        springLength: 130,
        springConstant: 0.12,
        damping: 0.4,
        avoidOverlap: 0.5
      },
      solver: 'forceAtlas2Based',
      stabilization: { iterations: 350, fit: true, updateInterval: 50 },
      adaptiveTimestep: true
    },
    layout: { improvedLayout: false, randomSeed: 42 },
    interaction: {
      hover: true,
      tooltipDelay: 200,
      highlightNearest: { enabled: true, degree: 1, hover: true },
      selectConnectedEdges: true
    },
    manipulation: { enabled: false }
  }
}

function wireEvents() {
  network.once('stabilizationIterationsDone', () => {
    if (!network) return
    network.fit({ animation: { duration: 400, easingFunction: 'easeInOutQuad' } })
    if (!frozen.value) network.stopSimulation()
  })

  network.on('click', (params) => {
    if (params.nodes.length > 0) {
      const node = nodes.get(params.nodes[0])
      if (node) {
        selected.value = {
          id: node.id,
          label: node.id === 'search'
            ? (props.queryValue || 'search')
            : String(node.siteName || node.label || '').replace(/\*\*/g, ''),
          url: node.url || ''
        }
      }
    } else {
      selected.value = null
    }
  })

  network.on('hoverNode', (params) => {
    if (!params.node) return
    nodes.update({
      id: params.node,
      shadow: { enabled: true, color: 'rgba(0,255,255,0.55)', size: 15, x: 0, y: 0 }
    })
  })

  network.on('blurNode', (params) => {
    if (!params.node) return
    nodes.update({ id: params.node, shadow: false })
  })
}

function populate() {
  nodes.clear()
  edges.clear()
  addCenterNode()
  const end = Math.min(TOP_K, props.results.length)
  shownCount.value = addRange(0, end)
}

function rebuildGraph() {
  selected.value = null
  frozen.value = false
  findOpen.value = false
  findQuery.value = ''
  if (network) { network.destroy(); network = null }
  nodes = null
  edges = null
  shownCount.value = 0
  if (!props.results || !Array.isArray(props.results) || props.results.length === 0) return

  nodes = new DataSet()
  edges = new DataSet()
  network = new Network(containerRef.value, { nodes, edges }, graphOptions())
  wireEvents()
  populate()
}

function loadMore() {
  if (!network || !hasMore.value) return
  const from = shownCount.value
  const to = Math.min(from + TOP_K, props.results.length)
  shownCount.value += addRange(from, to)
  if (!frozen.value) {
    network.startSimulation()
    network.once('stabilized', () => {
      if (network && !frozen.value) network.stopSimulation()
    })
  }
}

function toggleFreeze() {
  if (!network) return
  frozen.value = !frozen.value
  network.setOptions({ physics: { enabled: !frozen.value } })
  if (!frozen.value) {
    network.startSimulation()
    network.once('stabilized', () => {
      if (network && !frozen.value) network.stopSimulation()
    })
  }
}

function fitView() {
  if (!network) return
  network.fit({ animation: { duration: 400, easingFunction: 'easeInOutQuad' } })
}

function exportPng() {
  const canvas = containerRef.value?.querySelector('canvas')
  if (!canvas) return
  try {
    const url = canvas.toDataURL('image/png')
    const a = document.createElement('a')
    a.href = url
    a.download = 'osint-graph.png'
    a.click()
  } catch (e) {
    console.error(e)
  }
}

function toggleFind() {
  findOpen.value = !findOpen.value
  if (!findOpen.value) {
    findQuery.value = ''
    if (network) network.unselectAll()
    selected.value = null
  }
}

function runFind() {
  if (!network || !nodes) return
  const q = findQuery.value.trim().toLowerCase()
  if (!q) {
    network.unselectAll()
    selected.value = null
    return
  }
  const hits = nodes
    .get({ filter: n => n.id !== 'search' && String(n.searchText || '').includes(q) })
    .map(n => n.id)
  if (hits.length) {
    network.selectNodes(hits)
    network.fit({ nodes: ['search', ...hits], animation: { duration: 300, easingFunction: 'easeInOutQuad' } })
    const first = nodes.get(hits[0])
    if (first) {
      selected.value = {
        id: first.id,
        label: String(first.siteName || first.label || '').replace(/\*\*/g, ''),
        url: first.url || ''
      }
    }
  } else {
    network.unselectAll()
    selected.value = null
  }
}

function selectBy(hasUrl) {
  if (!network || !nodes) return
  const hits = nodes
    .get({ filter: n => n.id !== 'search' && (!!n.url === hasUrl) })
    .map(n => n.id)
  if (hits.length) {
    network.selectNodes(hits)
    network.fit({ nodes: ['search', ...hits], animation: { duration: 300, easingFunction: 'easeInOutQuad' } })
  }
}

function openSelected() {
  const url = selected.value?.url
  if (!url) return
  try {
    const u = new URL(url, window.location.origin)
    if (u.protocol === 'http:' || u.protocol === 'https:') {
      window.open(u.href, '_blank', 'noopener,noreferrer')
    }
  } catch {}
}

function copySelected() {
  const url = selected.value?.url
  if (url) navigator.clipboard.writeText(url).catch(() => {})
}

watch(() => props.results, rebuildGraph)

onMounted(() => {
  rebuildGraph()
  resizeObserver = new ResizeObserver(() => {
    if (network) network.redraw()
  })
  if (containerRef.value) resizeObserver.observe(containerRef.value)
})

onUnmounted(() => {
  if (resizeObserver) resizeObserver.disconnect()
  if (network) { network.destroy(); network = null }
  nodes = null
  edges = null
})
</script>

<template>
  <div class="graph-container">
    <div class="scanlines" aria-hidden="true"></div>
    <div class="graph-header">
      <span class="glitch-text graph-title">ENTITY GRAPH</span>
      <div class="graph-meta">
        <span v-if="breachChip" class="breach-chip" :class="breachChip.cls">{{ breachChip.text }}</span>
        <div class="graph-legend">
          <span class="legend-item legend-static"><span class="legend-dot dot-query"></span> CONSULTA</span>
          <button class="legend-item legend-btn" title="Seleccionar nodos con URL" @click="selectBy(true)">
            <span class="legend-dot" :style="{ borderColor: borderColor }"></span> CON URL ({{ withUrlCount }})
          </button>
          <button class="legend-item legend-btn" title="Seleccionar nodos sin URL" @click="selectBy(false)">
            <span class="legend-dot dot-no-url"></span> SIN URL ({{ withoutUrlCount }})
          </button>
        </div>
        <span class="status-badge" :style="{ borderColor: borderColor, color: borderColor }">{{ shownCount }}/{{ totalCount }} ENTIDADES</span>
        <div class="graph-toolbar">
          <button class="tool-btn" title="Ajustar vista" @click="fitView">AJUSTAR</button>
          <button class="tool-btn" :class="{ active: frozen }" :aria-pressed="frozen" @click="toggleFreeze">
            {{ frozen ? 'REANUDAR' : 'CONGELAR' }}
          </button>
          <button class="tool-btn" title="Exportar PNG" @click="exportPng">PNG</button>
          <button class="tool-btn" :class="{ active: findOpen }" :aria-pressed="findOpen" @click="toggleFind">BUSCAR</button>
          <button v-if="hasMore" class="tool-btn tool-more" @click="loadMore">
            +{{ Math.min(TOP_K, totalCount - shownCount) }} MAS
          </button>
        </div>
      </div>
    </div>
    <div v-if="findOpen" class="graph-find">
      <input
        v-model="findQuery"
        class="cyber-input find-input"
        placeholder="buscar en el grafo..."
        @input="runFind"
        @keyup.enter="runFind"
      />
    </div>
    <div ref="containerRef" class="graph-canvas"></div>
    <div v-if="selected" class="node-panel">
      <div class="node-panel-header">
        <span class="node-panel-title">{{ selected.label }}</span>
        <button class="panel-x" title="Cerrar" @click="selected = null; network && network.unselectAll()">�</button>
      </div>
      <div v-if="selected.url" class="node-panel-url">{{ selected.url }}</div>
      <div v-else class="node-panel-url muted">sin URL asociada</div>
      <div class="node-panel-actions">
        <button v-if="selected.url" class="tool-btn tool-action" @click="openSelected">ABRIR ?</button>
        <button v-if="selected.url" class="tool-btn tool-action" @click="copySelected">COPIAR</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.graph-container {
  background: var(--bg-card);
  border: 1px solid var(--border-cyan);
  border-radius: 0;
  overflow: hidden;
  height: 100%;
  min-height: 400px;
  position: relative;
  display: flex;
  flex-direction: column;
}

.graph-container::before,
.graph-container::after {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  border-color: var(--cyan);
  border-style: solid;
  z-index: 5;
  pointer-events: none;
  transition: transform 0.15s ease;
}
.graph-container::before { top: 0; left: 0; border-width: 2px 0 0 2px; }
.graph-container::after { bottom: 0; right: 0; border-width: 0 2px 2px 0; }
.graph-container:hover::before { transform: translate(3px, 3px); }
.graph-container:hover::after { transform: translate(-3px, -3px); }

.scanlines {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(0deg, transparent 0 3px, rgba(255,255,255,0.012) 3px 4px);
  pointer-events: none;
  z-index: 3;
}

.graph-header {
  flex: 0 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding: 10px 16px;
  background: linear-gradient(90deg, #00ffff11, #ff00ff11);
  border-bottom: 1px solid #00ffff22;
  z-index: 4;
  position: relative;
}
.graph-title {
  font-size: 1.1rem !important;
  letter-spacing: 2px !important;
}
.graph-meta {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.graph-find {
  flex: 0 0 auto;
  padding: 8px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-secondary);
  z-index: 4;
  position: relative;
}
.find-input { font-size: 0.85rem; padding: 8px 12px; }

.graph-canvas { flex: 1 1 auto; width: 100%; min-height: 0; position: relative; z-index: 1; }

.graph-legend {
  display: flex;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-secondary);
}
.legend-item { display: flex; align-items: center; gap: 5px; }
.legend-static { opacity: 0.9; }
.legend-btn {
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  font-size: 0.7rem;
  padding: 2px 6px;
  cursor: pointer;
  transition: all 0.15s;
}
.legend-btn:hover { border-color: var(--border-cyan); color: var(--cyan); }
.legend-btn:focus-visible { outline: 1px solid var(--cyan); outline-offset: 1px; }
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  background: #0a0e1a;
  border: 2px solid var(--border);
}
.dot-query { border-color: #00ffff; }
.dot-no-url { border-style: dashed; border-color: #334155; }

.graph-toolbar { display: flex; gap: 6px; flex-wrap: wrap; }
.tool-btn {
  background: var(--bg-primary);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-family: var(--font-mono);
  font-size: 0.65rem;
  letter-spacing: 1px;
  padding: 4px 10px;
  cursor: pointer;
  transition: all 0.15s;
}
.tool-btn:hover { border-color: var(--cyan); color: var(--cyan); }
.tool-btn:focus-visible { outline: 1px solid var(--cyan); outline-offset: 1px; }
.tool-btn.active {
  background: var(--cyan);
  color: var(--bg-primary);
  border-color: var(--cyan);
  box-shadow: var(--glow-cyan);
}
.tool-more { border-color: var(--magenta); color: var(--magenta); }
.tool-more:hover { background: var(--magenta); color: var(--bg-primary); }

.breach-chip {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  letter-spacing: 1px;
  padding: 3px 8px;
  border: 1px solid;
  white-space: nowrap;
}
.chip-warn { color: #fbbf24; border-color: #fbbf24; background: #fbbf2411; }
.chip-danger { color: #f87171; border-color: #f87171; background: #f8717111; }
.chip-ok { color: var(--green); border-color: var(--green); background: #00ff0011; }

.node-panel {
  position: absolute;
  bottom: 14px;
  right: 14px;
  width: min(340px, calc(100% - 28px));
  background: #0a0e1af2;
  border: 1px solid var(--border-cyan);
  box-shadow: 0 0 20px #00ffff22, inset 0 0 30px #00ffff08;
  padding: 12px 14px;
  z-index: 6;
  font-family: var(--font-mono);
}
.node-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.node-panel-title {
  color: var(--cyan);
  font-size: 0.9rem;
  letter-spacing: 1px;
  word-break: break-all;
}
.panel-x {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-muted);
  width: 22px;
  height: 22px;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  flex-shrink: 0;
}
.panel-x:hover { border-color: var(--red); color: var(--red); }
.node-panel-url {
  color: var(--text-secondary);
  font-size: 0.75rem;
  word-break: break-all;
  margin-bottom: 10px;
  line-height: 1.4;
}
.node-panel-url.muted { color: var(--text-muted); font-style: italic; }
.node-panel-actions { display: flex; gap: 8px; }
.tool-action { font-size: 0.7rem; padding: 6px 12px; }

@media (prefers-reduced-motion: reduce) {
  .scanlines { display: none; }
  .graph-title { animation: none !important; }
  .graph-container::before,
  .graph-container::after { transition: none; }
}
</style>
