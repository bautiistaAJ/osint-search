<script setup>
const props = defineProps({
  results: { type: Array, default: () => [] },
  total: { type: Number, default: 0 }
})
</script>

<template>
  <div class="username-results">
    <div class="section-title">{{ total }} RESULTADOS</div>
    <div class="cards">
      <div v-for="(r, i) in results" :key="i" class="cyber-card">
        <div class="card-glow"></div>
        <div class="card-body">
          <strong>{{ r.site || 'Unknown' }}</strong>
          <span class="status-found" v-if="r.found">FOUND</span>
        </div>
        <a v-if="r.url" :href="r.url" target="_blank" rel="noopener">{{ r.url }}</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
