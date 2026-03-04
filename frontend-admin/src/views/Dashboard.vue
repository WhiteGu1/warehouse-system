<template>
  <div>
    <h2 style="margin-bottom:20px">系统首页</h2>

    <!-- 新订单提醒 -->
    <el-alert
      v-if="newOrders.length > 0"
      type="warning"
      :closable="false"
      style="margin-bottom:20px;cursor:pointer"
      @click="newOrderDialogVisible = true"
    >
      <template #title>
        <span style="font-size:15px;font-weight:bold">🔔 有 {{ newOrders.length }} 条新订单待确认，点击查看</span>
      </template>
    </el-alert>

    <el-row :gutter="20" style="margin-bottom:24px">
      <el-col :span="6">
        <el-card shadow="hover" style="cursor:pointer" @click="$router.push('/products')">
          <div style="text-align:center">
            <div style="font-size:32px;color:#409eff;font-weight:bold">{{ stats.products }}</div>
            <div style="color:#666;margin-top:8px">商品总数</div>
            <div style="color:#aaa;font-size:12px;margin-top:4px">点击进入商品管理</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" style="cursor:pointer" @click="$router.push('/customers')">
          <div style="text-align:center">
            <div style="font-size:32px;color:#67c23a;font-weight:bold">{{ stats.supermarkets }}</div>
            <div style="color:#666;margin-top:8px">客户数量</div>
            <div style="color:#aaa;font-size:12px;margin-top:4px">点击进入客户管理</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" style="cursor:pointer" @click="pendingOrderDialogVisible = true">
          <div style="text-align:center">
            <div style="font-size:32px;color:#e6a23c;font-weight:bold">{{ stats.pending_orders }}</div>
            <div style="color:#666;margin-top:8px">待处理订单</div>
            <div style="color:#aaa;font-size:12px;margin-top:4px">点击查看详情</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" style="cursor:pointer" @click="lowStockDialogVisible = true">
          <div style="text-align:center">
            <div style="font-size:32px;color:#f56c6c;font-weight:bold">{{ stats.low_stock }}</div>
            <div style="color:#666;margin-top:8px">库存不足</div>
            <div style="color:#aaa;font-size:12px;margin-top:4px">点击查看详情</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近订单 -->
    <el-card>
      <template #header><span>最近订单</span></template>
      <el-table :data="recentOrders" stripe>
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="supermarket_name" label="客户" width="150" />
        <el-table-column prop="total_amount" label="金额" width="100">
          <template #default="{ row }">${{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.status_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="下单时间" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push('/orders')">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新订单弹窗 -->
    <el-dialog v-model="newOrderDialogVisible" title="🔔 新订单待确认" width="700px">
      <el-table :data="newOrders" stripe>
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="supermarket_name" label="客户" width="150" />
        <el-table-column prop="total_amount" label="金额" width="100">
          <template #default="{ row }">${{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="下单时间" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="confirmOrder(row)">确认</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="newOrderDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 待处理订单弹窗 -->
    <el-dialog v-model="pendingOrderDialogVisible" title="待处理订单" width="700px">
      <el-table :data="pendingOrders" stripe>
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="supermarket_name" label="客户" width="150" />
        <el-table-column prop="total_amount" label="金额" width="100">
          <template #default="{ row }">${{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.status_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="下单时间" />
      </el-table>
      <template #footer>
        <el-button @click="$router.push('/orders');pendingOrderDialogVisible=false">前往订单管理</el-button>
        <el-button @click="pendingOrderDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 库存不足弹窗 -->
    <el-dialog v-model="lowStockDialogVisible" title="库存不足商品" width="600px">
      <el-table :data="lowStockProducts" stripe>
        <el-table-column prop="name" label="商品名称" />
        <el-table-column prop="spec" label="规格" width="100" />
        <el-table-column prop="barcode" label="条码" width="130" />
        <el-table-column prop="stock" label="当前库存" width="90">
          <template #default="{ row }">
            <el-tag type="danger" size="small">{{ row.stock }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="$router.push('/products');lowStockDialogVisible=false">前往商品管理</el-button>
        <el-button @click="lowStockDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const stats = ref({ products: 0, supermarkets: 0, pending_orders: 0, low_stock: 0 })
const recentOrders = ref([])
const pendingOrders = ref([])
const lowStockProducts = ref([])
const newOrders = ref([])

const newOrderDialogVisible = ref(false)
const pendingOrderDialogVisible = ref(false)
const lowStockDialogVisible = ref(false)

let pollTimer = null

const statusType = (status) => {
  const map = { 1: 'warning', 2: 'primary', 3: 'primary', 4: 'success', 5: 'info' }
  return map[status] || 'info'
}

const loadStats = async () => {
  stats.value = await request.get('/orders/stats/overview')
}

const loadRecentOrders = async () => {
  const all = await request.get('/orders/')
  recentOrders.value = all.slice(0, 10)
  pendingOrders.value = all.filter(o => o.status < 5)
}

const loadLowStock = async () => {
  const all = await request.get('/products/')
  lowStockProducts.value = all.filter(p => p.stock < 10)
}

const loadNewOrders = async () => {
  const all = await request.get('/orders/')
  const incoming = all.filter(o => o.status === 1)
  if (incoming.length > newOrders.value.length) {
    ElMessage.warning(`有新订单待确认！`)
  }
  newOrders.value = incoming
}

const confirmOrder = async (row) => {
  await request.put(`/orders/${row.id}/status`, { status: 2, remark: '管理员已确认' })
  ElMessage.success('订单已确认')
  newOrders.value = newOrders.value.filter(o => o.id !== row.id)
  loadStats()
  loadRecentOrders()
}

const startPolling = () => {
  pollTimer = setInterval(() => {
    loadNewOrders()
    loadStats()
  }, 15000)
}

onMounted(() => {
  loadStats()
  loadRecentOrders()
  loadLowStock()
  loadNewOrders()
  startPolling()
})

onUnmounted(() => {
  clearInterval(pollTimer)
})
</script>