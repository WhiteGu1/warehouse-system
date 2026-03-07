<template>
  <div style="min-height:100vh;background:#f0f7ff">
    <header style="background:#fff;box-shadow:0 2px 12px rgba(64,158,255,0.1);position:sticky;top:0;z-index:100">
      <div v-if="user && user.discount < 1"
        style="background:linear-gradient(90deg,#e8f4fd,#c3dff7);text-align:center;padding:6px;font-size:13px;color:#2b7fc4;font-weight:500">
        🎉 {{ t.discountBanner }} <b>-{{ ((1 - user.discount) * 100).toFixed(0) }}%</b> {{ t.off }}
      </div>
      <div style="max-width:1300px;margin:0 auto;padding:0 12px;height:56px;display:flex;align-items:center;gap:10px">
        <div style="font-size:22px;font-weight:800;color:#409eff;letter-spacing:2px;flex-shrink:0;cursor:pointer" @click="$router.push('/')">
          {{ t.appName }}
        </div>
        <div style="flex:1;min-width:0">
          <el-autocomplete
            v-model="searchKeyword"
            :fetch-suggestions="fetchSuggestions"
            :placeholder="t.search"
            size="default"
            clearable
            style="width:100%"
            @select="onSelectSuggestion"
            @keyup.enter="doSearch"
            @clear="doSearch"
          >
            <template #suffix>
              <el-icon style="cursor:pointer;color:#409eff" @click="doSearch"><Search /></el-icon>
            </template>
            <template #default="{ item }">
              <div style="display:flex;align-items:center;justify-content:space-between">
                <div style="display:flex;align-items:center;gap:6px">
                  <el-icon style="color:#aaa;font-size:12px"><Clock /></el-icon>
                  <span>{{ item.value }}</span>
                </div>
                <el-icon style="color:#ccc;font-size:12px;cursor:pointer" @click.stop="removeHistory(item.value)"><Close /></el-icon>
              </div>
            </template>
          </el-autocomplete>
        </div>

        <div class="desktop-nav" style="display:flex;align-items:center;gap:8px;flex-shrink:0">
          <el-button size="small" round @click="switchLang" style="font-weight:bold;min-width:48px">
            {{ lang === 'zh' ? 'ES' : '中文' }}
          </el-button>
          <el-badge :value="cartCount" :hidden="cartCount === 0" type="danger">
            <el-button :icon="ShoppingCart" circle @click="$router.push('/cart')" />
          </el-badge>
          <el-button size="small" @click="$router.push('/orders')">{{ t.myOrders }}</el-button>
          <el-button size="small" @click="$router.push('/favorites')">
            <el-icon style="margin-right:4px"><Star /></el-icon>{{ t.favorites }}
          </el-button>
          <el-dropdown @command="handleCommand">
            <div style="display:flex;align-items:center;gap:4px;cursor:pointer;color:#555;font-size:13px">
              <el-icon><User /></el-icon>
              <span style="max-width:80px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ user?.name || user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="changePassword"><el-icon><Lock /></el-icon> {{ t.changePassword }}</el-dropdown-item>
                <el-dropdown-item command="logout" divided style="color:#f56c6c"><el-icon><SwitchButton /></el-icon> {{ t.logout }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <div class="mobile-nav" style="display:none;align-items:center;gap:6px;flex-shrink:0">
          <el-badge :value="cartCount" :hidden="cartCount === 0" type="danger">
            <el-button :icon="ShoppingCart" circle size="small" @click="$router.push('/cart')" />
          </el-badge>
          <el-button :icon="Menu" circle size="small" @click="mobileMenuVisible = true" />
        </div>
      </div>
    </header>

    <el-drawer v-model="mobileMenuVisible" direction="rtl" size="70%" :with-header="false">
      <div style="padding:20px">
        <div style="font-size:18px;font-weight:800;color:#409eff;margin-bottom:24px">{{ t.appName }}</div>
        <div style="display:flex;flex-direction:column;gap:12px">
          <el-button size="large" style="width:100%;justify-content:flex-start" @click="navTo('/')">🏠 {{ lang === 'zh' ? '首页' : 'Inicio' }}</el-button>
          <el-button size="large" style="width:100%;justify-content:flex-start" @click="navTo('/orders')">📦 {{ t.myOrders }}</el-button>
          <el-button size="large" style="width:100%;justify-content:flex-start" @click="navTo('/favorites')">⭐ {{ t.favorites }}</el-button>
          <el-divider />
          <el-button size="large" style="width:100%;justify-content:flex-start" @click="switchLang">🌐 {{ lang === 'zh' ? 'Español' : '中文' }}</el-button>
          <el-button size="large" style="width:100%;justify-content:flex-start" @click="openPwd">🔒 {{ t.changePassword }}</el-button>
          <el-button size="large" type="danger" plain style="width:100%;justify-content:flex-start" @click="logout">🚪 {{ t.logout }}</el-button>
        </div>
        <div style="margin-top:24px;font-size:12px;color:#bbb">{{ user?.name || user?.username }}</div>
      </div>
    </el-drawer>

<main style="max-width:1300px;margin:0 auto" class="main-content">
      <router-view :search-keyword="activeKeyword" @search-clear="activeKeyword=''" />
    </main>

    <el-dialog v-model="pwdDialogVisible" :title="t.changePassword" width="min(380px, 92vw)">
      <el-form :model="pwdForm" label-width="80px">
        <el-form-item :label="t.oldPassword">
          <el-input v-model="pwdForm.old_password" type="password" show-password :placeholder="t.oldPassword" />
        </el-form-item>
        <el-form-item :label="t.newPassword">
          <el-input v-model="pwdForm.new_password" type="password" show-password :placeholder="t.newPassword" />
        </el-form-item>
        <el-form-item :label="t.confirmPassword">
          <el-input v-model="pwdForm.confirm_password" type="password" show-password :placeholder="t.confirmPassword" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialogVisible = false">{{ t.cancel }}</el-button>
        <el-button type="primary" :loading="pwdLoading" @click="submitChangePassword">{{ t.confirm }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, ShoppingCart, User, Lock, SwitchButton, ArrowDown, Clock, Close, Star, Menu } from '@element-plus/icons-vue'
import { useCartStore } from '../stores/cart'
import request from '../utils/request'
import { useLang } from '../composables/useLang'

const router = useRouter()
const cart = useCartStore()
const { lang, t, switchLang } = useLang()
const searchKeyword = ref('')
const activeKeyword = ref('')
const user = ref(null)
const cartCount = computed(() => cart.count)
const pwdDialogVisible = ref(false)
const pwdLoading = ref(false)
const pwdForm = ref({ old_password: '', new_password: '', confirm_password: '' })
const mobileMenuVisible = ref(false)

const HISTORY_KEY = 'search_history'
const MAX_HISTORY = 10

const getHistory = () => {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]') } catch { return [] }
}
const saveToHistory = (kw) => {
  if (!kw.trim()) return
  let h = getHistory().filter(x => x !== kw)
  h.unshift(kw)
  if (h.length > MAX_HISTORY) h = h.slice(0, MAX_HISTORY)
  localStorage.setItem(HISTORY_KEY, JSON.stringify(h))
}
const removeHistory = (kw) => {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(getHistory().filter(h => h !== kw)))
}
const fetchSuggestions = (q, cb) => {
  const h = getHistory()
  cb((q ? h.filter(x => x.toLowerCase().includes(q.toLowerCase())) : h).map(x => ({ value: x })))
}
const onSelectSuggestion = (item) => { searchKeyword.value = item.value; doSearch() }
const doSearch = () => {
  if (searchKeyword.value.trim()) saveToHistory(searchKeyword.value.trim())
  activeKeyword.value = searchKeyword.value
  router.push('/')
}

const navTo = (path) => { mobileMenuVisible.value = false; router.push(path) }
const openPwd = () => {
  mobileMenuVisible.value = false
  pwdForm.value = { old_password: '', new_password: '', confirm_password: '' }
  pwdDialogVisible.value = true
}

const handleCommand = (cmd) => {
  if (cmd === 'changePassword') openPwd()
  else if (cmd === 'logout') logout()
}

const submitChangePassword = async () => {
  if (!pwdForm.value.old_password) { ElMessage.warning(t.value.oldPassword); return }
  if (!pwdForm.value.new_password) { ElMessage.warning(t.value.newPassword); return }
  if (pwdForm.value.new_password.length < 6) { ElMessage.warning(t.value.pwdMinLength); return }
  if (pwdForm.value.new_password !== pwdForm.value.confirm_password) { ElMessage.warning(t.value.pwdMismatch); return }
  pwdLoading.value = true
  try {
    await request.post('/auth/client-change-password', {
      old_password: pwdForm.value.old_password,
      new_password: pwdForm.value.new_password
    })
    ElMessage.success(t.value.pwdSuccess)
    pwdDialogVisible.value = false
    setTimeout(() => logout(), 1500)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || t.value.pwdMismatch)
  } finally {
    pwdLoading.value = false
  }
}

const logout = () => {
  localStorage.removeItem('client_token')
  localStorage.removeItem('client_user')
  localStorage.removeItem('cart')
  cart.clear()
  router.push('/login')
}

onMounted(() => {
  const u = localStorage.getItem('client_user')
  if (u) user.value = JSON.parse(u)
})
</script>

<style scoped>
:global(body) {
  overflow-x: hidden;
}
:global(html) {
  overflow-x: hidden;
}
.main-content {
  padding: 16px 12px;
}
@media (max-width: 768px) {
  .main-content {
    padding: 10px 6px;
  }
}
@media (max-width: 400px) {
  .main-content {
    padding: 8px 4px;
  }
}
@media (max-width: 768px) {
  .desktop-nav { display: none !important; }
  .mobile-nav { display: flex !important; }
}
</style>