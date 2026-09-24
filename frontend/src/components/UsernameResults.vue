<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  results: { type: Array, default: () => [] },
  total: { type: Number, default: 0 }
})
</script>

<template>
  <div class="username-results">
    <div class="section-title">{{ total }} RESULTS</div>
    <div class="cards">
      <div v-for="(r, i) in results" :key="i" class="cyber-card">
        <div class="card-glow"></div>
        <div class="card-body">
          <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
            <strong>{{ r.site || 'Unknown' }}</strong>
            <span class="status-found" v-if="r.found">FOUND</span>
            <span class="status-notfound" v-else>NOT FOUND</span>
          </div>
          <a v-if="r.url" :href="r.url" target="_blank" rel="noopener">{{ r.url }}</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.status-found { color: #00ff00; font-family: var(--font-mono); font-size: 0.7rem; font-weight: bold; letter-spacing: 1px; }
.status-notfound { color: #64748b; font-family: var(--font-mono); font-size: 0.7rem; font-weight: bold; letter-spacing: 1px; }
</style>
