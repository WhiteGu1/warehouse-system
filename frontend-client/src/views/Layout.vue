<template>
  <div style="min-height:100vh;background:#f0f7ff">
    <!-- 顶部导航 -->
    <header style="background:#fff;box-shadow:0 2px 12px rgba(64,158,255,0.1);position:sticky;top:0;z-index:100">
      <!-- 折扣提示横幅 -->
      <div v-if="user && user.discount < 1"
        style="background:linear-gradient(90deg,#e8f4fd,#c3dff7);text-align:center;padding:6px;font-size:13px;color:#2b7fc4;font-weight:500">
        🎉 您享有专属优惠：所有商品 <b>-{{ ((1 - user.discount) * 100).toFixed(0) }}%</b> 折扣
      </div>
      <div style="max-width:1300px;margin:0 auto;padding:0 20px;height:64px;display:flex;align-items:center;gap:20px">
        <div style="font-size:26px;font-weight:800;color:#409eff;letter-spacing:2px;flex-shrink:0;cursor:pointer" @click="$router.push('/')">
          HOMES
        </div>
        <!-- 搜索框 -->
        <div style="flex:1;max-width:500px">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索商品名称、条码..."
            size="large"
            clearable
            @keyup.enter="doSearch"
            @clear="doSearch"
          >
            <template #suffix>
              <el-icon style="cursor:pointer;color:#409eff" @click="doSearch"><Search /></el-icon>
            </template>
          </el-input>
        </div>
        <div style="flex:1" />
        <!-- 用户信息 -->
        <div style="display:flex;align-items:center;gap:16px">
          <span style="font-size:13px;color:#666">{{ user?.name || user?.username }}</span>
          <!-- 购物车 -->
          <el-badge :value="cartCount" :hidden="cartCount === 0" type="danger">
            <el-button :icon="ShoppingCart" circle size="large" @click="$router.push('/cart')" />
          </el-badge>
          <!-- 我的订单 -->
          <el-button size="default" @click="$router.push('/orders')">我的订单</el-button>
          <el-button size="default" type="danger" plain @click="logout">退出</el-button>
        </div>
      </div>
    </header>

    <!-- 主内容 -->
    <main style="max-width:1300px;margin:0 auto;padding:24px 20px">
      <router-view :search-keyword="activeKeyword" @search-clear="activeKeyword=''" />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, ShoppingCart } from '@element-plus/icons-vue'
import { useCartStore } from '../stores/cart'

const router = useRouter()
const cart = useCartStore()
const searchKeyword = ref('')
const activeKeyword = ref('')
const user = ref(null)
const cartCount = computed(() => cart.count)

const doSearch = () => {
  activeKeyword.value = searchKeyword.value
  router.push('/')
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