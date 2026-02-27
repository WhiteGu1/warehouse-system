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
          <span>入库管理</span>
        </el-menu-item>
        <el-menu-item index="/orders">
          <el-icon><List /></el-icon>
          <span>订单管理</span>
        </el-menu-item>
        <el-menu-item index="/supermarkets">
          <el-icon><Shop /></el-icon>
          <span>客户管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background:white;display:flex;align-items:center;justify-content:space-between;box-shadow:0 1px 4px rgba(0,0,0,0.1)">
        <span style="font-size:16px">欢迎，{{ name }}</span>
        <el-button type="danger" plain size="small" @click="logout">退出登录</el-button>
      </el-header>
      <el-main style="background:#f0f2f5">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const name = ref(localStorage.getItem('name') || '管理员')

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('name')
  router.push('/login')
}
</script>