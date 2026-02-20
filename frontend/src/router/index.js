import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Overview', component: () => import('@/views/Overview.vue') },
  { path: '/settings', name: 'Settings', component: () => import('@/views/Settings.vue') },
  { path: '/rules', name: 'Rules', component: () => import('@/views/Rules.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
