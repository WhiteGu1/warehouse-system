import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/login',
            name: 'login',
            component: () => import('../views/Login.vue')
        },
        {
            path: '/',
            component: () => import('../views/Layout.vue'),
            redirect: '/dashboard',
            children: [
                {
                    path: 'dashboard',
                    name: 'dashboard',
                    component: () => import('../views/Dashboard.vue')
                },
                {
                    path: 'products',
                    name: 'products',
                    component: () => import('../views/Products.vue')
                },
                {
                    path: 'stock-in',
                    name: 'stock-in',
                    component: () => import('../views/StockIn.vue')
                },
                {
                    path: 'stock-out',
                    name: 'stock-out',
                    component: () => import('../views/StockOut.vue')
                },
                {
                    path: 'orders',
                    name: 'orders',
                    component: () => import('../views/Orders.vue')
                },
                {
                    path: 'customers',
                    name: 'customers',
                    component: () => import('../views/Customers.vue')
                },
                {
                    path: 'stats',
                    name: 'stats',
                    component: () => import('../views/Stats.vue')
                },
                {
                    path: 'stats/flow',
                    name: 'stats-flow',
                    component: () => import('../views/StatsFlow.vue')
                },
                {
                    path: 'stats/products',
                    name: 'stats-products',
                    component: () => import('../views/StatsProducts.vue')
                },
                {
                    path: 'import',
                    name: 'import',
                    component: () => import('../views/Import.vue')
                }
            ]
        },
        {
            path: '/:pathMatch(.*)*',
            redirect: '/'
        }
    ]
})

router.beforeEach((to) => {
    const token = localStorage.getItem('token')
    if (to.path !== '/login' && !token) {
        return '/login'
    }
})

export default router