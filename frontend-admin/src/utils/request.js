import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const request = axios.create({
    baseURL: 'http://127.0.0.1:8000/api',
    timeout: 10000
})

// 请求拦截器：自动带上token
request.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// 响应拦截器：统一处理错误
request.interceptors.response.use(
    response => response.data,
    error => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token')
            router.push('/login')
            ElMessage.error('登录已过期，请重新登录')
        } else {
            ElMessage.error(error.response?.data?.detail || '请求失败')
        }
        return Promise.reject(error)
    }
)

export default request