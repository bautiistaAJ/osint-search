<script setup>
const props = defineProps({
  results: { type: Array, default: () => [] },
  breachData: { type: Object, default: null }
})

function confBadge(r) {
  if (r.confidence === 'low') return { label: 'SIN CONFIAR', cls: 'chip-low' }
  if (r.method === 'both') return { label: 'VERIFICADO', cls: 'chip-verified' }
  if (r.method === 'native') return { label: 'NATIVE', cls: 'chip-native' }
  if (r.method === 'holehe') return { label: 'HOLEHE', cls: 'chip-holehe' }
  return null
}

function badgeTitle(r) {
  const map = {
    low: 'Detección no confiable (falló el canary check) — verificar manualmente',
    both: 'Confirmado por el checker nativo y por holehe',
    native: 'Detectado por el checker nativo',
    holehe: 'Detectado solo por holehe'
  }
  return map[r.confidence === 'low' ? 'low' : r.method] || ''
}
</script>

<template>
  <div class="email-results">
    <div class="section-title">CUENTAS ENCONTRADAS</div>
    <div v-if="results.length > 0" class="cards">
      <div v-for="(r, i) in results" :key="i" class="cyber-card">
        <div class="card-glow"></div>
        <div class="card-body">
          <strong>{{ r.site || 'Unknown' }}</strong>
          <span v-if="confBadge(r)" class="conf-badge" :class="confBadge(r).cls" :title="badgeTitle(r)">{{ confBadge(r).label }}</span>
          <a v-if="r.url" class="card-link" :href="r.url" target="_blank" rel="noopener noreferrer">ABRIR ↗</a>
          <span class="status-found" v-if="r.found">FOUND</span>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">No se encontraron cuentas.</div>

    <div v-if="breachData" class="breach-panel" style="margin-top: var(--spacing-lg);">
      <div class="section-title">BREACH CHECK</div>
      <div v-if="breachData.checked === false" class="breach-unchecked">
        <p>NO CONFIGURADO — HIBP no está conectado. Los resultados de breach no son confiables.</p>
      </div>
      <div v-else-if="breachData.found" class="breach-found">
        <p style="margin-bottom: 8px;">Encontrado en {{ breachData.breaches?.length || 0 }} brecha(s).</p>
        <div v-for="(b, i) in breachData.breaches" :key="i" class="breach-item">
          <strong>{{ b.Title || b.Name || b.name }}</strong> - {{ b.BreachDate || 'Fecha desconocida' }}
        </div>
      </div>
      <div v-else-if="breachData.error" class="breach-found">
        <p>HIBP no disponible: {{ breachData.error }}</p>
      </div>
      <div v-else class="breach-ok">
        <p>Sin brechas encontradas.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.conf-badge {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  letter-spacing: 1px;
  padding: 2px 6px;
  border: 1px solid;
  white-space: nowrap;
}
.chip-verified { color: var(--cyan); border-color: var(--cyan); background: #00ffff11; }
.chip-native { color: var(--green); border-color: var(--green); background: #00ff0011; }
.chip-holehe { color: var(--text-secondary); border-color: var(--border); background: var(--bg-primary); }
.chip-low { color: #fbbf24; border-color: #fbbf24; background: #fbbf2411; }

.card-link {
  font-size: 0.7rem;
  color: var(--cyan);
  text-decoration: none;
  letter-spacing: 1px;
  border: 1px solid var(--border);
  padding: 2px 6px;
  transition: all 0.15s;
}
.card-link:hover {
  border-color: var(--cyan);
  box-shadow: var(--glow-cyan);
}
</style>
