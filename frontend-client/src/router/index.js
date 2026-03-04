import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: () => import('../views/Login.vue') },
    {
      path: '/',
      component: () => import('../views/Layout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', component: () => import('../views/Home.vue') },
        { path: 'cart', component: () => import('../views/Cart.vue') },
        { path: 'orders', component: () => import('../views/Orders.vue') },
        { path: 'order/:id', component: () => import('../views/OrderDetail.vue') },
      ]
    }
  ]
})

router.beforeEach((to) => {
  const token = localStorage.getItem('client_token')
  if (to.meta.requiresAuth && !token) return '/login'
  if (to.path === '/login' && token) return '/'
})

export default router