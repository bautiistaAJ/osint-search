<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="cyber-body">
    <div class="container">
      <header class="cyber-header">
        <div class="glitch-container">
          <h1 class="glitch-text" data-text="OSINT SEARCH">OSINT SEARCH</h1>
        </div>
        <p class="cyber-subtitle">Busca perfiles, emails, dominios, teléfonos y más</p>
        <div class="header-indicator" v-if="false"></div>
      </header>

      <RouterView />

      <nav class="bottom-nav">
        <router-link to="/">INICIO</router-link>
        <router-link to="/history">HISTORIAL</router-link>
        <router-link to="/favorites">FAVORITOS</router-link>
      </nav>
    </div>
  </div>
</template>

<style scoped>

.cyber-body { background: var(--bg-primary); min-height: 100vh; position: relative; }
.container { max-width: 1000px; margin: 0 auto; padding: var(--spacing-md); position: relative; z-index: 1; }

.cyber-header { text-align: center; margin-bottom: var(--spacing-lg); padding: var(--spacing-lg); }

.header-indicator {
  width: 8px; height: 8px;
  background: var(--green);
  border-radius: 50%;
  margin: var(--spacing-sm) auto 0;
  box-shadow: 0 0 8px var(--green);
  animation: pulse 2s infinite;
}

</style>
