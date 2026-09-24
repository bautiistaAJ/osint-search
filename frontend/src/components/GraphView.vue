<script setup>
import { ref, onMounted, watch } from 'vue'
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

const buildGraph = (results, queryType, queryValue) => {
  const nodes = new DataSet()
  const edges = new DataSet()

  // Central node - the searched entity
  nodes.add({
    id: 'search',
    label: queryValue,
    group: queryType,
    color: { color: '#00ffff', highlight: '#00ffff', border: '#00ffff' },
    shape: 'circle',
    font: { color: '#00ffff', size: 16, face: 'Share Tech Mono' }
  })

  const groupColors = {
    username: { color: '#ff00ff', highlight: '#ff00ff', border: '#ff00ff' },
    email: { color: '#ffff00', highlight: '#ffff00', border: '#ffff00' },
    domain: { color: '#00ff00', highlight: '#00ff00', border: '#00ff00' }
  }

  if (results && results.length > 0) {
    results.forEach((r, i) => {
      const id = `node_${i}`
      const siteName = r.site || r.username || r.url || 'Unknown'
      const url = r.url || r.site_url || ''
      const color = groupColors[queryType] || groupColors.username

      nodes.add({
        id,
        label: siteName.length > 20 ? siteName.substring(0, 20) + '...' : siteName,
        group: 'found',
        color,
        shape: 'box',
        font: { color: '#e2e8f0', size: 12, face: 'Share Tech Mono' },
        url
      })

      edges.add({
        from: 'search',
        to: id,
        color: { color: '#38bdf8', highlight: '#38bdf8' },
        width: 2,
        dashes: [5, 5]
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
    groups: {
      search: { color: { border: '#00ffff', background: '#00ffff' }, font: { color: '#00ffff' } },
      found: { color: { border: '#ff00ff', background: '#1e293b' }, font: { color: '#e2e8f0' } }
    },
    layout: {
      improvedLayout: true
    },
    interaction: {}
  }

  

  if (network) {
    network.destroy()
  }

  network = new Network(containerRef.value, data, options)

  network.on('click', (params) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      const node = nodes.get(nodeId)
      if (node && node.url) {
        window.open(node.url, '_blank', 'noopener')
      }
    }
  })
}

watch(() => props.results, (newVal) => {
  if (newVal && newVal.length > 0) {
    buildGraph(newVal, props.queryType, props.queryValue)
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
}, { deep: true })

onMounted(() => {
  if (props.results && props.results.length > 0) {
    buildGraph(props.results, props.queryType, props.queryValue)
  } else {
    const nodes = new DataSet([{
      id: 'empty',
      label: 'Ejecutá una búsqueda para ver el grafo',
      font: { color: '#64748b', size: 14, face: 'Share Tech Mono' }
    }])
    const edges = new DataSet()
    const data = { nodes, edges }
    network = new Network(containerRef.value, data, {
      physics: { enabled: false },
      nodes: { font: { face: 'Share Tech Mono', size: 14 } }
    })
  }
})
</script>

<template>
  <div class="graph-container">
    <div class="graph-header">
      <span class="glitch-text">ENTITY GRAPH</span>
      <span class="status-badge">LIVE</span>
    </div>
    <div ref="containerRef" class="graph-canvas"></div>
  </div>
</template>

<style scoped>
.graph-container {
  background: #0a0e1a;
  border: 1px solid #00ffff33;
  border-radius: 8px;
  overflow: hidden;
  height: 100%;
  min-height: 400px;
}
.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(90deg, #00ffff11, #ff00ff11);
  border-bottom: 1px solid #00ffff22;
}
.glitch-text {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.9rem;
  color: #00ffff;
  text-shadow: 0 0 10px #00ffff66;
  letter-spacing: 2px;
}
.status-badge {
  background: #00ff0022;
  color: #00ff00;
  padding: 2px 10px;
  border-radius: 4px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.75rem;
  border: 1px solid #00ff0044;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
.graph-canvas {
  width: 100%;
  height: calc(100% - 50px);
}
</style>
