<script setup>
const props = defineProps({
  steps: { type: Array, default: () => [] },
  currentStep: { type: Number, default: -1 },
  queryType: { type: String, default: 'username' }
})
</script>

<template>
  <div class="scan-console" v-if="steps.length > 0">
    <div class="scan-console-header">
      <span class="scan-label">SCAN: {{ queryType.toUpperCase() }}</span>
      <span class="scan-status">SCANNING...</span>
    </div>
    <div class="scan-console-body">
      <div v-for="(step, i) in steps" :key="i" class="scan-line" :class="i < currentStep ? 'ok' : i === currentStep ? '' : ''">
        <span class="step">{{ i <= currentStep ? '[OK]' : '[ ]' }}</span> {{ step }}
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
