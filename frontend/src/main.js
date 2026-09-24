import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Home from './views/Home.vue'
import History from './views/History.vue'
import Favorites from './views/Favorites.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/history', component: History },
    { path: '/favorites', component: Favorites }
  ]
})

createApp(App).use(router).mount('#app')
