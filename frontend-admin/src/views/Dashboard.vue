<template>
  <div>
    <h2 style="margin-bottom:20px">系统首页</h2>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align:center">
            <div style="font-size:32px;color:#409eff;font-weight:bold">{{ stats.products }}</div>
            <div style="color:#666;margin-top:8px">商品总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align:center">
            <div style="font-size:32px;color:#67c23a;font-weight:bold">{{ stats.supermarkets }}</div>
            <div style="color:#666;margin-top:8px">超市数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align:center">
            <div style="font-size:32px;color:#e6a23c;font-weight:bold">{{ stats.pending_orders }}</div>
            <div style="color:#666;margin-top:8px">待处理订单</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align:center">
            <div style="font-size:32px;color:#f56c6c;font-weight:bold">{{ stats.low_stock }}</div>
            <div style="color:#666;margin-top:8px">库存不足</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const stats = ref({
  products: 0,
  supermarkets: 0,
  pending_orders: 0,
  low_stock: 0
})
</script>