<script setup>
const props = defineProps({
  records: { type: Object, default: () => ({}) },
  error: { type: String, default: '' },
  found: { type: Boolean, default: false }
})

const recordTypes = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME', 'CAA', 'SOA']
</script>

<template>
  <div class="dns-results">
    <div class="section-title">DNS RECORDS</div>
    <div v-if="error" class="cyber-error">{{ error }}</div>
    <div v-else-if="found && Object.keys(records).length > 0" class="dossier-grid">
      <div v-for="rt in recordTypes" :key="rt" class="dossier-panel" v-if="records[rt] && records[rt].length > 0">
        <h3>{{ rt }}</h3>
        <div v-for="(val, i) in records[rt]" :key="i" class="dossier-field">
          <span class="dossier-field-label">#{{ i + 1 }}</span>
          <span class="dossier-field-value" style="color: var(--green); word-break: break-all;">{{ val }}</span>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">No DNS records found.</div>
  </div>
</template>

<style scoped>
</style>
