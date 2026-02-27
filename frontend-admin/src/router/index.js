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
                    path: 'orders',
                    name: 'orders',
                    component: () => import('../views/Orders.vue')
                },
                {
path: 'customers',
name: 'customers',
component: () => import('../views/Customers.vue')
                }
            ]
        },
        {
            path: '/:pathMatch(.*)*',
            redirect: '/'
        }
    ]
})

// 路由守卫：未登录跳转到登录页
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    if (to.path !== '/login' && !token) {
        next('/login')
    } else {
        next()
    }
})

export default router