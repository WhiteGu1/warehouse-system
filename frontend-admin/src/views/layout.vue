<template>
  <el-container style="height: 100vh">
    <el-aside width="200px" style="background:#001529">
      <div style="color:white;text-align:center;padding:20px;font-size:16px;font-weight:bold">
        出入库管理
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#001529"
        text-color="#ccc"
        active-text-color="#fff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataLine /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/products">
          <el-icon><Goods /></el-icon>
          <span>商品管理</span>
        </el-menu-item>
        <el-menu-item index="/stock-in">
          <el-icon><Download /></el-icon>
          <span>入库记录</span>
        </el-menu-item>
        <el-menu-item index="/stock-out">
          <el-icon><Upload /></el-icon>
          <span>出库记录</span>
        </el-menu-item>
        <el-menu-item index="/orders">
          <el-icon><List /></el-icon>
          <span>订单管理</span>
        </el-menu-item>
        <el-menu-item index="/customers">
          <el-icon><Shop /></el-icon>
          <span>客户管理</span>
        </el-menu-item>
        <el-menu-item index="/stats">
          <el-icon><TrendCharts /></el-icon>
          <span>统计分析</span>
        </el-menu-item>
        <el-menu-item index="/import">
          <el-icon><Folder /></el-icon>
          <span>Excel导入</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background:white;display:flex;align-items:center;justify-content:space-between;box-shadow:0 1px 4px rgba(0,0,0,0.1)">
        <div style="display:flex;align-items:center;gap:16px">
          <span style="font-size:16px">欢迎，{{ name }}</span>
          <el-badge v-if="newOrderCount > 0" :value="newOrderCount" type="danger">
            <el-button size="small" type="warning" @click="$router.push('/dashboard')">新订单</el-button>
          </el-badge>
        </div>
        <el-button type="danger" plain size="small" @click="logout">退出登录</el-button>
      </el-header>
      <el-main style="background:#f0f2f5">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { DataLine, Goods, Download, Upload, List, Shop, Folder, TrendCharts } from '@element-plus/icons-vue'
import request from '../utils/request'

const router = useRouter()
const name = ref(localStorage.getItem('name') || '管理员')
const newOrderCount = ref(0)
let pollTimer = null

const checkNewOrders = async () => {
  try {
    const all = await request.get('/orders/')
    newOrderCount.value = all.filter(o => o.status === 1).length
  } catch {}
}

const logout = () => {
  clearInterval(pollTimer)
  localStorage.removeItem('token')
  localStorage.removeItem('name')
  router.push('/login')
}

onMounted(() => {
  checkNewOrders()
  pollTimer = setInterval(checkNewOrders, 15000)
})

onUnmounted(() => {
  clearInterval(pollTimer)
})
</script>