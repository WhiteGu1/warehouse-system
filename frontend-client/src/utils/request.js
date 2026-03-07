import axios from 'axios'

export const BASE_URL = 'http://192.168.0.109:8000'

const instance = axios.create({
  baseURL: BASE_URL + '/api',
  timeout: 10000
})

instance.interceptors.request.use(config => {
  const token = localStorage.getItem('client_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

instance.interceptors.response.use(
  res => res.data,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('client_token')
      localStorage.removeItem('client_user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default instance