<script setup>
const props = defineProps({
  data: { type: Object, default: null },
  raw: { type: String, default: '' }
})
</script>

<template>
  <div class="github-dossier">
    <div class="section-title">GITHUB DOSSIER</div>
    <div v-if="data && data.login" class="dossier-grid">
      <div class="dossier-panel" style="border-color: var(--border-cyan);">
        <h3>PROFILE</h3>
        <div class="dossier-field">
          <span class="dossier-field-label">USERNAME</span>
          <span class="dossier-field-value" style="color: var(--cyan);">{{ data.login }}</span>
        </div>
        <div class="dossier-field" v-if="data.name">
          <span class="dossier-field-label">NAME</span>
          <span class="dossier-field-value">{{ data.name }}</span>
        </div>
        <div class="dossier-field" v-if="data.bio">
          <span class="dossier-field-label">BIO</span>
          <span class="dossier-field-value">{{ data.bio }}</span>
        </div>
        <div class="dossier-field" v-if="data.location">
          <span class="dossier-field-label">LOCATION</span>
          <span class="dossier-field-value">{{ data.location }}</span>
        </div>
        <div class="dossier-field" v-if="data.company">
          <span class="dossier-field-label">COMPANY</span>
          <span class="dossier-field-value">{{ data.company }}</span>
        </div>
        <div class="dossier-field" v-if="data.email">
          <span class="dossier-field-label">EMAIL</span>
          <span class="dossier-field-value" style="color: var(--cyan);">{{ data.email }}</span>
        </div>
        <div class="dossier-field" v-if="data.twitter_username">
          <span class="dossier-field-label">TWITTER</span>
          <span class="dossier-field-value">{{ data.twitter_username }}</span>
        </div>
        <div class="dossier-field">
          <span class="dossier-field-label">REPOS</span>
          <span class="dossier-field-value">{{ data.public_repos || 0 }}</span>
        </div>
        <div class="dossier-field">
          <span class="dossier-field-label">FOLLOWERS</span>
          <span class="dossier-field-value">{{ data.followers || 0 }}</span>
        </div>
        <div class="dossier-field">
          <span class="dossier-field-label">FOLLOWING</span>
          <span class="dossier-field-value">{{ data.following || 0 }}</span>
        </div>
        <div class="dossier-field" v-if="data.created_at">
          <span class="dossier-field-label">CREATED</span>
          <span class="dossier-field-value">{{ new Date(data.created_at).toLocaleDateString() }}</span>
        </div>
        <a v-if="data.html_url" :href="data.html_url" target="_blank" rel="noopener" style="color: var(--cyan); font-family: var(--font-mono); font-size: 0.85rem; margin-top: var(--spacing-sm); display: block;">{{ data.html_url }}</a>
      </div>
    </div>
    <div v-else-if="raw" class="terminal">
      <div class="terminal-header">
        <div class="terminal-dot red"></div>
        <div class="terminal-dot yellow"></div>
        <div class="terminal-dot green"></div>
        <span class="terminal-title">OUTPUT</span>
      </div>
      <div class="terminal-body">
        <div v-for="(line, i) in raw.split('\n').filter(l => l.trim())" :key="i" class="terminal-line">
          {{ line }}
        </div>
      </div>
    </div>
    <div v-else class="empty-state">No GitHub data found.</div>
  </div>
</template>

<style scoped>
</style>
