<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
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

const groupColors = {
  username: { color: '#ff00ff', highlight: '#ff00ff', border: '#ff00ff' },
  email: { color: '#ffff00', highlight: '#ffff00', border: '#ffff00' },
  domain: { color: '#00ff00', highlight: '#00ff00', border: '#00ff00' },
  phone: { color: '#ff00ff', highlight: '#ff00ff', border: '#ff00ff' },
  google: { color: '#ffff00', highlight: '#ffff00', border: '#ffff00' },
  subdomains: { color: '#00ff00', highlight: '#00ff00', border: '#00ff00' },
  harvest: { color: '#00ff00', highlight: '#00ff00', border: '#00ff00' },
  dns: { color: '#00ff00', highlight: '#00ff00', border: '#00ff00' },
  github: { color: '#64748b', highlight: '#64748b', border: '#64748b' }
}

const buildGraph = (results, queryType, queryValue) => {
  const nodes = new DataSet()
  const edges = new DataSet()
  const color = groupColors[queryType] || groupColors.username

  nodes.add({
    id: 'search',
    label: queryValue || 'search',
    group: queryType,
    color: { color: '#00ffff', highlight: '#00ffff', border: '#00ffff' },
    shape: 'circle',
    font: { color: '#00ffff', size: 16, face: 'Share Tech Mono' },
    title: queryValue || 'search'
  })

  if (results && Array.isArray(results)) {
    results.forEach((r, i) => {
      if (!r || typeof r !== 'object') return
      const id = `node_${i}`
      const siteName = String(r.site || r.username || r.url || 'Unknown')
      const rawUrl = r.url || r.site_url || ''
      const url = /^https?:\/\//.test(rawUrl) ? rawUrl : ''

      nodes.add({
        id,
        label: siteName.length > 20 ? siteName.substring(0, 20) + '...' : siteName,
        group: 'found',
        color: { color: color.color, highlight: color.highlight, border: color.border },
        shape: 'box',
        font: { color: '#e2e8f0', size: 12, face: 'Share Tech Mono' },
        url,
        title: `${siteName}${url ? '\n' + url : ''}`
      })

      if (url) {
        edges.add({
          from: 'search',
          to: id,
          color: { color: '#38bdf8', highlight: '#38bdf8' },
          width: 2,
          dashes: [5, 5]
        })
      }
    })
  }

  const data = { nodes, edges }
  const options = {
    nodes: {
      shape: 'box',
      font: { face: 'Share Tech Mono', size: 12 },
      scaling: { label: { min: 8, max: 16 } }
    },
    edges: {
      font: { face: 'Share Tech Mono', size: 10, color: '#64748b' },
      smooth: { type: 'cubicBezier' }
    },
    physics: {
      forceAtlas2Based: {
        gravitationalConstant: -26,
        centralGravity: 0.005,
        springLength: 230,
        springConstant: 0.18
      },
      solver: 'forceAtlas2Based',
      timestep: 0.5,
      stabilization: { iterations: 150 }
    },
    layout: { improvedLayout: true },
    interaction: { hover: true, tooltipDelay: 200 },
    levels: {
      useLevelConstraint: true,
      levelSeparation: 150
    },
    manipulation: { enabled: false }
  }

  if (network) { network.destroy(); network = null }
  network = new Network(containerRef.value, data, options)

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

  network.on('hoverNode', (params) => {
    if (params.nodes.length > 0) {
      const node = nodes.get(params.nodes[0])
      if (node) {
        network.selectNodes([node.id])
      }
    }
  })
}

const rebuildGraph = () => {
  if (props.results && Array.isArray(props.results) && props.results.length > 0) {
    buildGraph(props.results, props.queryType, props.queryValue)
  } else {
    const nodes = new DataSet([{
      id: 'empty',
      label: 'Sin resultados',
      font: { color: '#64748b', size: 14, face: 'Share Tech Mono' }
    }])
    const edges = new DataSet()
    const data = { nodes, edges }
    if (network) network.destroy()
    network = new Network(containerRef.value, data, {
      physics: { enabled: false },
      nodes: { font: { face: 'Share Tech Mono', size: 14 } }
    })
  }
}

watch(() => props.results, rebuildGraph, { deep: true })

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
      <span class="glitch-text">ENTITY GRAPH</span>
      <span class="status-badge">LIVE</span>
    </div>
    <div ref="containerRef" class="graph-canvas"></div>
    <div class="graph-legend">
      <span class="legend-item"><span class="legend-dot" style="background: #ff00ff;"></span> Target</span>
      <span class="legend-item"><span class="legend-dot" style="background: #38bdf8;"></span> Connection</span>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

.graph-container {
  background: var(--bg-card);
  border: 1px solid var(--border-cyan);
  border-radius: 8px;
  overflow: hidden;
  height: 100%;
  min-height: 400px;
  position: relative;
}
.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(90deg, #00ffff11, #ff00ff11);
  border-bottom: 1px solid #00ffff22;
  z-index: 2;
}
.graph-canvas { width: 100%; height: calc(100% - 50px); }
.graph-legend {
  position: absolute;
  bottom: 12px;
  left: 12px;
  display: flex;
  gap: 12px;
  background: #0a0e1aee;
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid var(--border);
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-muted);
  z-index: 3;
}
.legend-item { display: flex; align-items: center; gap: 4px; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
</style>
