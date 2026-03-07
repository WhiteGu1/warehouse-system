<template>
  <div>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
      <el-button :icon="ArrowLeft" size="small" @click="$router.push('/')">{{ t.back }}</el-button>
      <h2 style="margin:0;color:#333;font-size:clamp(16px,4vw,22px)">{{ t.myOrders }}</h2>
    </div>

    <el-card>
<el-table :data="orders" stripe row-style="cursor:pointer" @row-click="(row) => $router.push(`/order/${row.id}`)">
  <el-table-column prop="order_no" :label="t.orderNo" min-width="150" />
  <el-table-column :label="t.orderAmount" width="120">
    <template #default="{ row }">
      <span style="color:#409eff;font-weight:bold;white-space:nowrap">${{ row.total_amount }}</span>
    </template>
  </el-table-column>
  <el-table-column :label="t.orderStatus" width="130">
    <template #default="{ row }">
      <el-tag :type="statusType(row.status)" size="small" style="white-space:nowrap">{{ statusText(row.status) || row.status_text }}</el-tag>
    </template>
  </el-table-column>
  <el-table-column prop="tracking_number" :label="t.trackingNo" min-width="120" show-overflow-tooltip />
  <el-table-column prop="created_at" :label="t.orderTime" width="155" />
  <el-table-column v-if="orders.some(o => o.status === 1)" :label="lang === 'zh' ? '操作' : 'Acción'" width="90">
    <template #default="{ row }">
      <div @click.stop>
        <el-button size="small" type="danger" plain v-if="row.status === 1" @click="cancelOrder(row)">{{ t.cancelOrder }}</el-button>
      </div>
    </template>
  </el-table-column>
</el-table>
      <div v-if="orders.length === 0" style="text-align:center;padding:40px;color:#aaa">
        {{ lang === 'zh' ? '暂无订单' : 'Sin pedidos' }}
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import request from '../utils/request'
import { useCartStore } from '../stores/cart'
import { useLang } from '../composables/useLang'

const cart = useCartStore()
const { lang, t } = useLang()
const orders = ref([])

const statusType = (status) => {
  const map = { 1: 'warning', 2: 'info', 3: 'primary', 4: '', 5: 'success', 6: 'danger', 7: 'danger' }
  return map[status] || ''
}

const statusText = (status) => {
  const map = {
    zh: { 1: '待确认', 2: '已确认待配货', 3: '已配货待发货', 4: '已发货待付款', 5: '已付款完成', 6: '已取消', 7: '已退款' },
    es: { 1: 'Pendiente', 2: 'Confirmado', 3: 'Preparando', 4: 'Enviado', 5: 'Completado', 6: 'Cancelado', 7: 'Reembolsado' }
  }
  return (map[lang.value] || map.zh)[status] || ''
}

const loadOrders = async () => {
  try {
    const res = await request.get('/orders/my')
    console.log('orders res:', res)
    orders.value = Array.isArray(res) ? res : (res.items || [])
  } catch (e) {
    console.log('orders error:', e)
    console.log('orders error response:', e.response)
  }
}

const cancelOrder = async (row) => {
  await ElMessageBox.confirm(
    `${t.value.confirmCancel} (${row.order_no})`,
    t.value.confirm,
    { type: 'warning' }
  )
  const detail = await request.get(`/orders/${row.id}`)
  await request.post(`/orders/${row.id}/client-cancel`)
  const user = JSON.parse(localStorage.getItem('client_user') || '{}')
  const discount = user.discount ?? 1.0
  detail.items.forEach(item => {
    cart.addItem({
      id: item.product_id, name: item.product_name, barcode: item.product_barcode,
      sell_price: +(item.unit_price / discount).toFixed(2),
      image: null, spec: null, middle_pack: null, piece: null
    }, item.quantity, discount)
  })
  ElMessage.success(t.value.cancelSuccess)
  loadOrders()
}

onMounted(() => { loadOrders() })
</script>