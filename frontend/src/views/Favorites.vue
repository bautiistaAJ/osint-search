<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const favorites = ref([])
const loading = ref(false)
const label = ref('')
const selectedFav = ref(null)

async function loadFavorites() {
  loading.value = true
  try {
    const res = await axios.get('/api/favorites')
    favorites.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function addFavorite() {
  if (!selectedFav.value) return
  try {
    await axios.post('/api/favorites', null, {
      params: {
        query_type: selectedFav.value.query_type,
        query_value: selectedFav.value.query_value,
        label: label.value || selectedFav.value.query_value
      }
    })
    label.value = ''
    loadFavorites()
  } catch (e) {
    console.error(e)
  }
}

async function removeFav(id) {
  await axios.delete(`/api/favorites/${id}`)
  loadFavorites()
}

onMounted(loadFavorites)
</script>

<template>
  <div class="cyber-body">
    <div class="cyber-grid"></div>
    <div class="container">
      <header class="cyber-header">
        <h1 class="glitch-text" data-text="FAVORITOS">FAVORITOS</h1>
        <p class="cyber-subtitle">Busquedas guardadas para investigar despues</p>
      </header>

      <div v-if="selectedFav" class="add-form">
        <input v-model="label" placeholder="etiqueta (opcional)..." class="cyber-input" />
        <button @click="addFavorite" class="cyber-btn">GUARDAR</button>
      </div>

      <div v-if="loading" class="loading">SCANNING...</div>

      <div v-if="favorites.length === 0 && !loading" class="empty">
        <p>No tenes favoritos guardados.</p>
      </div>

      <div v-else class="list">
        <div v-for="fav in favorites" :key="fav.id" class="cyber-card">
          <div class="card-glow"></div>
          <div class="card-body">
            <span class="badge">{{ fav.query_type }}</span>
            <span class="label">{{ fav.label }}</span>
            <p class="query">{{ fav.query_value }}</p>
            <span class="date">{{ fav.created_at }}</span>
            <button class="delete-btn" @click="removeFav(fav.id)">X</button>
          </div>
        </div>
      </div>

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

.cyber-body { background: #0a0e1a; min-height: 100vh; position: relative; }
.cyber-grid {
  position: fixed; top:0; left:0; width:100%; height:100%;
  background-image: linear-gradient(rgba(0,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,255,255,0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none; z-index: 0;
}
.container { max-width: 900px; margin: 0 auto; padding: 20px; position: relative; z-index: 1; }
.cyber-header { text-align: center; margin-bottom: 30px; padding: 20px; }
.glitch-text { font-family: 'Share Tech Mono', monospace; font-size: 2rem; color: #00ffff; text-shadow: 0 0 7px #00ffffaa; letter-spacing: 4px; animation: glitch 3s infinite; }
@keyframes glitch { 0%,93%,100%{transform:translate(0)} 94%{transform:translate(-2px,1px)} 95%{transform:translate(2px,-1px)} 96%{transform:translate(-1px,2px)} }
.cyber-subtitle { color: #94a3b8; font-family: 'Share Tech Mono', monospace; margin-top: 10px; font-size: 0.9rem; }
.add-form { display: flex; gap: 10px; margin-bottom: 20px; }
.cyber-input { flex: 1; padding: 12px; border: 1px solid #334155; background: #0a0e1a; color: #e2e8f0; font-family: 'Share Tech Mono', monospace; outline: none; }
.cyber-input:focus { border-color: #00ffff; box-shadow: 0 0 10px #00ffff33; }
.cyber-btn { padding: 12px 20px; background: linear-gradient(135deg, #00ffff, #ff00ff); color: #0a0e1a; border: none; font-family: 'Share Tech Mono', monospace; font-weight: bold; cursor: pointer; }
.loading, .empty { text-align: center; padding: 40px; color: #00ffff; font-family: 'Share Tech Mono', monospace; letter-spacing: 2px; }
.list { display: grid; gap: 12px; }
.cyber-card { background: #0a0e1a; border: 1px solid #334155; padding: 16px; position: relative; overflow: hidden; }
.cyber-card:hover { border-color: #00ffff44; box-shadow: 0 0 15px #00ffff11; }
.card-glow { position: absolute; top:0; left:-100%; width:100%; height:100%; background: linear-gradient(90deg, transparent, rgba(0,255,255,0.05), transparent); transition: left 0.5s; }
.cyber-card:hover .card-glow { left: 100%; }
.card-body { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.badge { background: #00ffff22; color: #00ffff; padding: 2px 10px; font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; border: 1px solid #00ffff33; }
.label { color: #00ffff; font-family: 'Share Tech Mono', monospace; }
.query { font-family: 'Share Tech Mono', monospace; font-size: 1rem; color: #e2e8f0; width: 100%; margin-top: 4px; }
.date { color: #64748b; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; }
.delete-btn { background: #7f1d1d; color: #fca5a5; border: 1px solid #ff0000; padding: 4px 12px; cursor: pointer; font-family: 'Share Tech Mono', monospace; }
.bottom-nav { display: flex; gap: 20px; justify-content: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #334155; }
.bottom-nav a { color: #00ffff; text-decoration: none; font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; letter-spacing: 1px; }
.bottom-nav a:hover { text-shadow: 0 0 10px #00ffff66; }
</style>
