<template>
  <el-container style="height:100vh">

    <!-- 手机端遮罩 -->
    <div
      v-if="drawerOpen"
      class="mobile-overlay"
      @click="drawerOpen = false"
    />

    <!-- 侧边栏 -->
    <el-aside
      :width="asideWidth"
      class="aside"
      :class="{ 'aside-open': drawerOpen }"
      style="background:#001529;transition:all 0.3s;overflow:hidden"
    >
      <div style="color:white;text-align:center;padding:20px;font-size:16px;font-weight:bold;display:flex;align-items:center;justify-content:space-between">
        <span>出入库管理</span>
        <el-icon class="mobile-only" style="cursor:pointer;color:#ccc" @click="drawerOpen = false"><Close /></el-icon>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#001529"
        text-color="#ccc"
        active-text-color="#fff"
        @select="drawerOpen = false"
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
      <el-header style="background:white;display:flex;align-items:center;justify-content:space-between;box-shadow:0 1px 4px rgba(0,0,0,0.1);padding:0 12px">
        <div style="display:flex;align-items:center;gap:10px">
          <el-button class="mobile-only" :icon="Menu" circle size="small" @click="drawerOpen = true" />
          <span style="font-size:15px">欢迎，{{ name }}</span>
          <el-badge v-if="pendingCount > 0" :value="pendingCount" type="danger">
            <el-button size="small" type="warning" @click="$router.push('/orders')">
              待处理订单
            </el-button>
          </el-badge>
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

      <el-main style="background:#f0f2f5;overflow-x:hidden;padding:12px">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElNotification } from 'element-plus'
import { DataLine, Goods, Download, Upload, List, Shop, Folder, TrendCharts, Bell, Close, Menu } from '@element-plus/icons-vue'
import request from '../utils/request'

const router = useRouter()
const name = ref(localStorage.getItem('name') || '管理员')
const pendingCount = ref(0)
const notifPermission = ref(Notification.permission)
const drawerOpen = ref(false)
let pollTimer = null
let lastPendingCount = 0
let initialized = false

const isMobile = () => window.innerWidth <= 768
const asideWidth = computed(() => {
  if (isMobile()) return drawerOpen.value ? '200px' : '0px'
  return '200px'
})

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
  n.onclick = () => { window.focus(); router.push('/orders'); n.close() }
}

const checkNewOrders = async () => {
  try {
    const res = await request.get('/orders/', { params: { status: 1, page: 1, page_size: 99999 } })
    const count = (res.items || []).length
    pendingCount.value = count
    if (!initialized) { lastPendingCount = count; initialized = true; return }
    if (count > lastPendingCount) {
      const diff = count - lastPendingCount
      ElNotification({
        title: '新订单',
        message: `收到 ${diff} 笔新订单，请及时处理`,
        type: 'warning',
        duration: 6000,
        onClick: () => router.push('/orders')
      })
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

<style scoped>
.aside {
  position: relative;
  z-index: 100;
}
.mobile-only {
  display: none;
}
.mobile-overlay {
  display: none;
}

:deep(.el-container) {
  height: 100%;
}
:deep(.el-main) {
  height: calc(100vh - 60px);
  overflow-y: auto;
}
:deep(.el-main > *) {
  min-height: 100%;
}
:deep(.el-card) {
  min-height: 100%;
  box-sizing: border-box;
}
:deep(.el-card__body) {
  height: calc(100% - 55px);
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .mobile-only {
    display: flex !important;
  }
  .aside {
    position: fixed !important;
    top: 0;
    left: 0;
    height: 100vh;
    width: 0 !important;
    z-index: 200;
  }
  .aside-open {
    width: 200px !important;
  }
  .mobile-overlay {
    display: block;
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background: rgba(0,0,0,0.4);
    z-index: 199;
  }
}
</style>