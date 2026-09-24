<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  results: { type: Array, default: () => [] },
  breachData: { type: Object, default: null }
})
</script>

<template>
  <div class="email-results">
    <div class="section-title">ACCOUNTS FOUND</div>
    <div v-if="results.length > 0" class="cards">
      <div v-for="(r, i) in results" :key="i" class="cyber-card">
        <div class="card-glow"></div>
        <div class="card-body">
          <strong>{{ r.site || 'Unknown' }}</strong>
          <span class="status-found" v-if="r.found">FOUND</span>
          <span class="status-notfound" v-else>NOT FOUND</span>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">No accounts found.</div>

    <div v-if="breachData" class="breach-panel" style="margin-top: var(--spacing-lg);">
      <div class="section-title">BREACH CHECK</div>
      <div v-if="breachData.found" class="breach-found">
        <p style="margin-bottom: 8px;">Found in {{ breachData.breaches?.length || 0 }} breach(es).</p>
        <div v-for="(b, i) in breachData.breaches" :key="i" class="breach-item">
          <strong>{{ b.Title || b.Name || b.name }}</strong> - {{ b.BreachDate || 'Fecha desconocida' }}
        </div>
      </div>
      <div v-else-if="breachData.error" class="breach-found">
        <p>HIBP unavailable: {{ breachData.error }}</p>
      </div>
      <div v-else class="breach-ok">
        <p>No breaches found.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
</style>
