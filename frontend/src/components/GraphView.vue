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

const containerRef = ref(null)
let network = null
let resizeObserver = null
let nodeDataSet = null
let edgeDataSet = null

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
const drawnCount = ref(0)

const breachChip = computed(() => {
  const b = props.breachData
  if (!b) return null
  if (b.checked === false) return { text: 'BREACH: NO CONFIGURADO', cls: 'chip-warn' }
  if (b.found) return { text: `BREACH: ${b.breaches?.length || 0} HIT`, cls: 'chip-danger' }
  return { text: 'BREACH: LIMPIO', cls: 'chip-ok' }
})

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

const buildGraph = (results, queryType, queryValue) => {
  const nodes = new DataSet()
  const edges = new DataSet()
  const border = typeBorders[queryType] || typeBorders.username
  let count = 0

  nodes.add({
    id: 'search',
    label: queryValue || 'search',
    color: {
      background: '#0a0e1a',
      highlight: { background: '#0f1524', border: '#00ffff' },
      border: '#00ffff'
    },
    borderWidth: 2,
    shape: 'ellipse',
    font: { color: '#00ffff', size: 16, face: 'Share Tech Mono' },
    title: makeTitle(`<b>QUERY</b><br>${escapeHtml(queryValue || 'search')}`)
  })

  if (results && Array.isArray(results)) {
    results.forEach((r, i) => {
      if (!r || typeof r !== 'object') return
      const id = `node_${i}`
      const siteName = String(r.site || r.username || r.url || r.login || r.name || 'Unknown')
      const rawUrl = r.url || r.site_url || r.profile_url || r.html_url || ''
      const url = /^https?:\/\//.test(rawUrl) ? rawUrl : ''

      nodes.add({
        id,
        label: truncateLabel(siteName),
        color: {
          background: '#0a0e1aee',
          highlight: { background: '#0f1524', border: '#ffffff' },
          border
        },
        borderWidth: 1.5,
        shape: 'box',
        font: { color: '#e2e8f0', size: 12, face: 'Share Tech Mono' },
        url,
        title: makeTitle(
          url
            ? `<b>${escapeHtml(siteName)}</b><br>${escapeHtml(url)}<br>↗ click para abrir`
            : `<b>${escapeHtml(siteName)}</b><br>sin URL`
        )
      })
      count++

      edges.add({
        from: 'search',
        to: id,
        color: url
          ? { color: '#00ffff', highlight: '#00ffff' }
          : { color: '#334155', highlight: '#475569' },
        width: url ? 2 : 1,
        dashes: url ? false : [4, 6]
      })
    })
  }
  drawnCount.value = count

  const data = { nodes, edges }
  const options = {
    nodes: {
      shape: 'box',
      font: { face: 'Share Tech Mono', size: 12 }
    },
    edges: {
      smooth: { type: 'cubicBezier' }
    },
    physics: {
      forceAtlas2Based: {
        gravitationalConstant: -26,
        centralGravity: 0.01,
        springLength: 140,
        springConstant: 0.18
      },
      solver: 'forceAtlas2Based',
      stabilization: { iterations: 400 }
    },
    layout: { improvedLayout: true },
    interaction: { hover: true, tooltipDelay: 200 },
    manipulation: { enabled: false }
  }

  if (network) { network.destroy(); network = null }
  network = new Network(containerRef.value, data, options)
  nodeDataSet = nodes
  edgeDataSet = edges

  network.once('stabilizationIterationsDone', () => {
    if (!network) return
    network.fit({ animation: { duration: 300 } })
    network.stopSimulation()
  })

  network.on('click', (params) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      const node = nodes.get(nodeId)
      if (node && node.url) {
        try {
          const u = new URL(node.url, window.location.origin)
          if (u.protocol === 'http:' || u.protocol === 'https:') {
            window.open(u.href, '_blank', 'noopener,noreferrer')
          }
        } catch {}
      }
    }
  })
}

const rebuildGraph = () => {
  if (network) { network.destroy(); network = null }
  nodeDataSet = null
  edgeDataSet = null
  if (props.results && Array.isArray(props.results) && props.results.length > 0) {
    buildGraph(props.results, props.queryType, props.queryValue)
  } else {
    drawnCount.value = 0
  }
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
  nodeDataSet = null
  edgeDataSet = null
})
</script>

<template>
  <div class="graph-container">
    <div class="graph-header">
      <span class="glitch-text graph-title">ENTITY GRAPH</span>
      <div class="graph-meta">
        <span v-if="breachChip" class="breach-chip" :class="breachChip.cls">{{ breachChip.text }}</span>
        <div class="graph-legend">
          <span class="legend-item"><span class="legend-dot dot-query"></span> QUERY</span>
          <span class="legend-item"><span class="legend-dot" :style="{ borderColor: borderColor }"></span> FOUND</span>
          <span class="legend-item"><span class="legend-dot dot-no-url"></span> SIN URL</span>
        </div>
        <span class="status-badge" :style="{ borderColor: borderColor, color: borderColor }">{{ drawnCount }} ENTIDADES</span>
      </div>
    </div>
    <div ref="containerRef" class="graph-canvas"></div>
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
  z-index: 2;
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
.graph-canvas { flex: 1 1 auto; width: 100%; min-height: 0; }
.graph-legend {
  display: flex;
  gap: 12px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-secondary);
}
.legend-item { display: flex; align-items: center; gap: 5px; }
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
</style>
