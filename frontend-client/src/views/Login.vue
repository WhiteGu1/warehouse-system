<template>
  <div style="min-height:100vh;background:linear-gradient(135deg,#e8f4fd 0%,#c3dff7 100%);display:flex;align-items:center;justify-content:center">
    <div style="background:#fff;border-radius:16px;box-shadow:0 8px 32px rgba(64,158,255,0.15);padding:48px 40px;width:380px;position:relative">
      <!-- 语言切换 -->
      <el-button size="small" round @click="switchLang" style="position:absolute;top:16px;right:16px;font-weight:bold">
        {{ lang === 'zh' ? 'ES' : '中文' }}
      </el-button>

      <div style="text-align:center;margin-bottom:36px">
        <div style="font-size:32px;font-weight:800;color:#409eff;letter-spacing:2px">{{ t.appName }}</div>
        <div style="font-size:13px;color:#aaa;margin-top:6px">{{ lang === 'zh' ? '批发商城 · 客户登录' : 'Tienda Mayorista · Cliente' }}</div>
      </div>
      <el-form @submit.prevent="handleLogin">
        <el-form-item>
          <el-input
            v-model="form.username"
            :placeholder="t.username"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            :placeholder="t.password"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          style="width:100%;margin-top:8px;border-radius:8px;font-size:15px"
          :loading="loading"
          @click="handleLogin"
        >
          {{ t.loginBtn }}
        </el-button>
      </el-form>
      <div v-if="error" style="color:#f56c6c;text-align:center;margin-top:16px;font-size:13px">{{ error }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import request from '../utils/request'
import { useLang } from '../composables/useLang'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const form = ref({ username: '', password: '' })
const { lang, t, switchLang } = useLang()

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    error.value = lang.value === 'zh' ? '请输入账号和密码' : 'Ingrese usuario y contraseña'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await request.post('/auth/client-login', form.value)
    localStorage.setItem('client_token', res.access_token)
    localStorage.setItem('client_user', JSON.stringify(res.user))
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || t.value.loginFailed
  } finally {
    loading.value = false
  }
}
</script>