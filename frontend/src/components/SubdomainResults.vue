<script setup>
import { defineProps, ref } from 'vue'

const props = defineProps({
  results: { type: Array, default: () => [] },
  raw: { type: String, default: '' }
})

const filter = ref('')
const sorted = ref([])

function getSubdomains() {
  if (!props.raw && !props.results.length) return []
  if (props.raw) {
    return props.raw.split('\n').filter(l => l.trim() && !l.startsWith('#') && !l.includes('Subdomain'))
  }
  return props.results
}

function getDisplay() {
  const list = typeof sorted.value === 'string' ? sorted.value.split('\n').filter(l => l.trim()) : sorted.value
  if (!filter.value) return list
  return list.filter(l => typeof l === 'string' ? l.toLowerCase().includes(filter.value.toLowerCase()) : String(l).toLowerCase().includes(filter.value.toLowerCase()))
}
</script>

<template>
  <div class="subdomain-results">
    <div class="section-title">SUBDOMAINS</div>
    <input v-model="filter" placeholder="filter..." class="cyber-input" style="margin-bottom: var(--spacing-md); max-width: 400px;" />
    <div v-if="getDisplay().length > 0" class="cards">
      <div v-for="(item, i) in getDisplay()" :key="i" class="cyber-card">
        <div class="card-glow"></div>
        <div class="card-body">
          <strong>{{ typeof item === 'string' ? item : item.domain || item.subdomain || item }}</strong>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">No subdomains found.</div>
  </div>
</template>

<style scoped>
</style>
