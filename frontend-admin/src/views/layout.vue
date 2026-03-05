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
          <el-icon><DataLine /></el-icon><span>首页</span>
        </el-menu-item>
        <el-menu-item index="/products">
          <el-icon><Goods /></el-icon><span>商品管理</span>
        </el-menu-item>
        <el-menu-item index="/stock-in">
          <el-icon><Download /></el-icon><span>入库记录</span>
        </el-menu-item>
        <el-menu-item index="/stock-out">
          <el-icon><Upload /></el-icon><span>出库记录</span>
        </el-menu-item>
        <el-menu-item index="/orders">
          <el-icon><List /></el-icon>
          <span style="display:flex;align-items:center;justify-content:space-between;width:100%">
            订单管理
            <el-badge v-if="pendingCount > 0" :value="pendingCount" type="danger" style="margin-left:4px" />
          </span>
        </el-menu-item>
        <el-menu-item index="/customers">
          <el-icon><Shop /></el-icon><span>客户管理</span>
        </el-menu-item>
        <el-menu-item index="/stats">
          <el-icon><TrendCharts /></el-icon><span>统计分析</span>
        </el-menu-item>
        <el-menu-item index="/import">
          <el-icon><Folder /></el-icon><span>Excel导入</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header style="background:white;display:flex;align-items:center;justify-content:space-between;box-shadow:0 1px 4px rgba(0,0,0,0.1)">
        <div style="display:flex;align-items:center;gap:16px">
          <span style="font-size:16px">欢迎，{{ name }}</span>
          <el-badge v-if="pendingCount > 0" :value="pendingCount" type="danger">
            <el-button size="small" type="warning" @click="$router.push('/orders')">
              待处理订单
            </el-button>
          </el-badge>
          <!-- 通知权限提示 -->
          <el-tooltip v-if="notifPermission === 'default'" content="点击开启新订单桌面通知" placement="bottom">
            <el-button size="small" type="info" plain :icon="Bell" @click="requestNotifPermission">
              开启通知
            </el-button>
          </el-tooltip>
          <el-tooltip v-else-if="notifPermission === 'granted'" content="桌面通知已开启" placement="bottom">
            <el-icon style="color:#67c23a;font-size:18px"><Bell /></el-icon>
          </el-tooltip>
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
import { ElNotification } from 'element-plus'
import { DataLine, Goods, Download, Upload, List, Shop, Folder, TrendCharts, Bell } from '@element-plus/icons-vue'
import request from '../utils/request'

const router = useRouter()
const name = ref(localStorage.getItem('name') || '管理员')
const pendingCount = ref(0)
const notifPermission = ref(Notification.permission)
let pollTimer = null
let lastPendingCount = 0
let initialized = false

const requestNotifPermission = async () => {
  const result = await Notification.requestPermission()
  notifPermission.value = result
}

const sendBrowserNotif = (count) => {
  if (Notification.permission !== 'granted') return
  const n = new Notification('新订单提醒', {
    body: `您有 ${count} 笔待确认订单，请及时处理。`,
    icon: '/favicon.ico',
    tag: 'new-order'
  })
  n.onclick = () => {
    window.focus()
    router.push('/orders')
    n.close()
  }
}

const checkNewOrders = async () => {
  try {
    const all = await request.get('/orders/')
    const count = all.filter(o => o.status === 1).length
    pendingCount.value = count

    if (!initialized) {
      lastPendingCount = count
      initialized = true
      return
    }

    if (count > lastPendingCount) {
      const diff = count - lastPendingCount
      // 页面内通知
      ElNotification({
        title: '新订单',
        message: `收到 ${diff} 笔新订单，请及时处理`,
        type: 'warning',
        duration: 6000,
        onClick: () => router.push('/orders')
      })
      // 浏览器桌面通知
      sendBrowserNotif(count)
    }
    lastPendingCount = count
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
  pollTimer = setInterval(checkNewOrders, 30000)
})

onUnmounted(() => {
  clearInterval(pollTimer)
})
</script>