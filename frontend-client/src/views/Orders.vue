<template>
  <div>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
      <el-button :icon="ArrowLeft" @click="$router.push('/')">返回</el-button>
      <h2 style="margin:0;color:#333">我的订单</h2>
    </div>

    <el-card>
      <el-table :data="orders" stripe>
        <el-table-column prop="order_no" label="订单号" width="190" />
        <el-table-column prop="total_amount" label="金额" width="100">
          <template #default="{ row }">
            <span style="color:#409eff;font-weight:bold">${{ row.total_amount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="130">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ row.status_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tracking_number" label="物流单号" width="140" />
        <el-table-column prop="created_at" label="下单时间" width="170" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="$router.push(`/order/${row.id}`)">详情</el-button>
            <el-button size="small" type="danger" plain v-if="row.status === 1" @click="cancelOrder(row)">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="orders.length === 0" style="text-align:center;padding:40px;color:#aaa">暂无订单</div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import request from '../utils/request'
import { useCartStore } from '../stores/cart'
const cart = useCartStore()

const orders = ref([])

const statusType = (status) => {
  const map = { 1: 'warning', 2: 'info', 3: 'primary', 4: '', 5: 'success', 6: 'danger', 7: 'danger' }
  return map[status] || ''
}

const loadOrders = async () => {
  orders.value = await request.get('/orders/my')
}

const cancelOrder = async (row) => {
  await ElMessageBox.confirm(`确定取消订单 ${row.order_no}？取消后商品将返回购物车。`, '提示', { type: 'warning' })
  // 先获取订单详情
  const detail = await request.get(`/orders/${row.id}`)
  await request.post(`/orders/${row.id}/client-cancel`)
  // 把订单商品加回购物车
  const user = JSON.parse(localStorage.getItem('client_user') || '{}')
  const discount = user.discount ?? 1.0
  detail.items.forEach(item => {
    cart.addItem({
      id: item.product_id,
      name: item.product_name,
      barcode: item.product_barcode,
      sell_price: +(item.unit_price / discount).toFixed(2),
      image: null,
      spec: null,
      middle_pack: null,
      piece: null
    }, item.quantity, discount)
  })
  ElMessage.success('订单已取消，商品已返回购物车')
  loadOrders()
}
onMounted(() => { loadOrders() })
</script>