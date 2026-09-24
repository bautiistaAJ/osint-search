<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { Network } from 'vis-network/standalone'
import 'vis-network/styles/vis-network.css'
import { DataSet } from 'vis-data/peer'

const props = defineProps({
  results: { type: Array, default: () => [] },
  queryType: { type: String, default: 'username' },
  queryValue: { type: String, default: '' }
})

const containerRef = ref(null)
let network = null
let resizeObserver = null

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
const entityCount = computed(() => props.results.length)

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
}

function truncateLabel(s) {
  return s.length > 20 ? s.substring(0, 20) + '…' : s
}

const buildGraph = (results, queryType, queryValue) => {
  const nodes = new DataSet()
  const edges = new DataSet()
  const border = typeBorders[queryType] || typeBorders.username

  nodes.add({
    id: 'search',
    label: queryValue || 'search',
    color: {
      color: '#0a0e1a',
      highlight: '#0f1524',
      border: '#00ffff',
      highlightBorder: '#00ffff'
    },
    borderWidth: 2,
    shape: 'ellipse',
    font: { color: '#00ffff', size: 16, face: 'Share Tech Mono' },
    title: `<b>QUERY</b><br>${escapeHtml(queryValue || 'search')}`
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
          color: '#0a0e1aee',
          highlight: '#0f1524',
          border,
          highlightBorder: '#ffffff'
        },
        borderWidth: 1.5,
        shape: 'box',
        font: { color: '#e2e8f0', size: 12, face: 'Share Tech Mono' },
        url,
        title: url
          ? `<b>${escapeHtml(siteName)}</b><br>${escapeHtml(url)}<br>↗ click para abrir`
          : `<b>${escapeHtml(siteName)}</b><br>sin URL`
      })

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
  if (props.results && Array.isArray(props.results) && props.results.length > 0) {
    buildGraph(props.results, props.queryType, props.queryValue)
  }
}

watch(() => props.results, rebuildGraph, { deep: true })
watch(() => props.queryType, rebuildGraph)
watch(() => props.queryValue, rebuildGraph)

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
})
</script>

<template>
  <div class="graph-container">
    <div class="graph-header">
      <span class="glitch-text graph-title">ENTITY GRAPH</span>
      <div class="graph-meta">
        <div class="graph-legend">
          <span class="legend-item"><span class="legend-dot dot-query"></span> QUERY</span>
          <span class="legend-item"><span class="legend-dot" :style="{ borderColor: borderColor }"></span> FOUND</span>
          <span class="legend-item"><span class="legend-dot dot-no-url"></span> SIN URL</span>
        </div>
        <span class="status-badge">{{ entityCount }} ENTIDADES</span>
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
  color: var(--text-muted);
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
</style>
