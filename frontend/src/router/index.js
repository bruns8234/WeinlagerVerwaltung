import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/weine',
    name: 'WeinUebersicht',
    component: () => import('../views/WeinUebersicht.vue')
  },
  {
    path: '/weine/neu',
    name: 'WeinAnlegen',
    component: () => import('../views/WeinAnlegen.vue')
  },
  {
    path: '/weine/:id',
    name: 'WeinBearbeiten',
    component: () => import('../views/WeinBearbeiten.vue')
  },
  {
    path: '/lager',
    name: 'Lagerstatus',
    component: () => import('../views/Lagerstatus.vue')
  },
  {
    path: '/lagerung',
    name: 'Lagerung',
    component: () => import('../views/Lagerung.vue')
  },
  {
    path: '/stammdaten',
    name: 'Stammdaten',
    component: () => import('../views/Stammdaten.vue')
  },
  {
    path: '/backup',
    name: 'Backup',
    component: () => import('../views/Backup.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router