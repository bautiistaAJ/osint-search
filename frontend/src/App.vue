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
      </header>

      <RouterView />

      <nav class="bottom-nav">
        <router-link to="/">🔍 INICIO</router-link>
        <router-link to="/history">📜 HISTORIAL</router-link>
        <router-link to="/favorites">⭐ FAVORITOS</router-link>
      </nav>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

.cyber-body {
  background: #0a0e1a;
  min-height: 100vh;
  overflow-x: hidden;
  position: relative;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  position: relative;
  z-index: 1;
}

.cyber-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  position: relative;
}

.glitch-container {
  position: relative;
  display: inline-block;
}

.glitch-text {
  font-family: 'Share Tech Mono', monospace;
  font-size: 2.5rem;
  color: #00ffff;
  text-shadow:
    0 0 7px #00ffffaa,
    0 0 15px #00ffff66,
    0 0 30px #00ffff33;
  letter-spacing: 4px;
  animation: glitch 3s infinite;
}

@keyframes glitch {
  0%, 93%, 100% { transform: translate(0); }
  94% { transform: translate(-2px, 1px); text-shadow: 2px 0 #ff00ff, -2px 0 #00ff00; }
  95% { transform: translate(2px, -1px); text-shadow: -2px 0 #ff00ff, 2px 0 #00ff00; }
  96% { transform: translate(-1px, 2px); text-shadow: 1px 0 #ff00ff, -1px 0 #00ff00; }
}

.cyber-subtitle {
  color: #94a3b8;
  font-family: 'Share Tech Mono', monospace;
  margin-top: 10px;
  font-size: 0.9rem;
  letter-spacing: 1px;
}

.bottom-nav {
  display: flex; gap: 20px; justify-content: center;
  margin-top: 40px; padding-top: 20px;
  border-top: 1px solid #334155;
}
.bottom-nav a {
  color: #00ffff; text-decoration: none;
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.85rem;
  letter-spacing: 1px;
}
.bottom-nav a:hover { text-shadow: 0 0 10px #00ffff66; }
</style>
