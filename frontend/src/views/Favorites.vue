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
        <p class="cyber-subtitle">Busquedas guardadas para investigar después</p>
      </header>

      <div v-if="selectedFav" class="add-form">
        <input v-model="label" placeholder="etiqueta (opcional)..." class="cyber-input" />
        <button @click="addFavorite" class="cyber-btn">GUARDAR</button>
      </div>

      <div v-if="loading" class="loading-state">SCANNING...</div>

      <div v-if="favorites.length === 0 && !loading" class="empty-state">
        <p>No tenés favoritos guardados.</p>
      </div>

      <div v-else class="list">
        <div v-for="fav in favorites" :key="fav.id" class="cyber-card">
          <div class="card-glow"></div>
          <div class="card-body">
            <span class="badge">{{ fav.query_type }}</span>
            <span class="label">{{ fav.label }}</span>
            <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
              <p class="query">{{ fav.query_value }}</p>
              <div style="display: flex; gap: 8px; align-items: center;">
                <span class="date">{{ fav.created_at }}</span>
                <button class="delete-btn" @click="removeFav(fav.id)">X</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <nav class="bottom-nav">
        <router-link to="/">INICIO</router-link>
        <router-link to="/history">HISTORIAL</router-link>
        <router-link to="/favorites">FAVORITOS</router-link>
      </nav>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

.cyber-body { background: var(--bg-primary); min-height: 100vh; position: relative; }
.container { max-width: 900px; margin: 0 auto; padding: var(--spacing-md); position: relative; z-index: 1; }
.cyber-header { text-align: center; margin-bottom: var(--spacing-lg); padding: var(--spacing-lg); }
.add-form { display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-lg); }
.loading, .empty { text-align: center; padding: var(--spacing-xl); color: var(--cyan); font-family: var(--font-mono); letter-spacing: 2px; }
.list { display: grid; gap: var(--spacing-md); }
.cyber-card { background: var(--bg-card); border: 1px solid var(--border); padding: var(--spacing-md); position: relative; overflow: hidden; }
.cyber-card:hover { border-color: var(--border-cyan); box-shadow: var(--glow-cyan-soft); }
.card-glow { position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(0,255,255,0.05), transparent); transition: left 0.5s; }
.cyber-card:hover .card-glow { left: 100%; }
.card-body { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: var(--spacing-sm); }
.label { color: var(--cyan); font-family: var(--font-mono); }
.query { font-family: var(--font-mono); font-size: 1rem; color: var(--text-primary); width: 100%; margin-top: var(--spacing-sm); }
.date { color: var(--text-muted); font-family: var(--font-mono); font-size: 0.8rem; }
.delete-btn { background: #7f1d1d; color: #fca5a5; border: 1px solid var(--red); padding: var(--spacing-xs) var(--spacing-sm); cursor: pointer; font-family: var(--font-mono); font-size: 0.8rem; }
</style>
