<template>
  <div style="max-width:780px;margin:0 auto">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
      <el-button :icon="ArrowLeft" size="small" @click="$router.push('/orders')">{{ t.back }}</el-button>
      <h2 style="margin:0;color:#333;font-size:clamp(16px,4vw,22px)">{{ lang === 'zh' ? '订单详情' : 'Detalle del Pedido' }}</h2>
    </div>

    <div v-if="!order" style="text-align:center;padding:60px;color:#aaa">
      <el-icon style="font-size:48px;color:#c3dff7"><Loading /></el-icon>
      <div style="margin-top:12px">{{ t.loading }}</div>
    </div>

    <template v-if="order">
      <!-- 状态横幅 -->
      <el-card style="margin-bottom:16px;background:linear-gradient(135deg,#e8f4fd,#f0f9ff)">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
          <div>
            <div style="font-size:13px;color:#888;margin-bottom:4px">{{ t.orderNo }}</div>
            <div style="font-size:16px;font-weight:bold;color:#333">{{ order.order_no }}</div>
          </div>
          <div style="text-align:center">
            <div style="font-size:13px;color:#888;margin-bottom:4px">{{ t.orderTime }}</div>
            <div style="font-size:14px;color:#555">{{ order.created_at }}</div>
          </div>
          <div style="text-align:center">
            <div style="font-size:13px;color:#888;margin-bottom:6px">{{ t.orderStatus }}</div>
            <el-tag :type="statusType(order.status)" size="large" style="font-size:14px;padding:8px 16px">
              {{ statusText(order.status) || order.status_text }}
            </el-tag>
          </div>
          <div style="text-align:right">
            <div style="font-size:13px;color:#888;margin-bottom:4px">{{ t.orderAmount }}</div>
            <div style="font-size:24px;font-weight:bold;color:#409eff">${{ order.total_amount }}</div>
          </div>
        </div>
      </el-card>

      <!-- 物流信息 -->
      <el-card v-if="order.tracking_number || order.logistics_company" style="margin-bottom:16px">
        <template #header>
          <div style="display:flex;align-items:center;gap:8px">
            <el-icon style="color:#409eff"><Van /></el-icon>
            <span style="font-weight:bold">{{ t.logistics }}</span>
          </div>
        </template>
        <div style="display:flex;gap:40px;font-size:14px;flex-wrap:wrap">
          <div>
            <span style="color:#888">{{ t.logisticsCompany }}：</span>
            <span style="font-weight:bold">{{ order.logistics_company || '-' }}</span>
          </div>
          <div>
            <span style="color:#888">{{ t.trackingNo }}：</span>
            <span style="font-weight:bold;color:#409eff">{{ order.tracking_number || '-' }}</span>
          </div>
        </div>
      </el-card>

      <!-- 商品明细 -->
      <el-card style="margin-bottom:16px">
        <template #header>
          <div style="display:flex;align-items:center;gap:8px">
            <el-icon style="color:#409eff"><ShoppingBag /></el-icon>
            <span style="font-weight:bold">{{ t.orderItems }}</span>
            <el-tag type="info" size="small">{{ order.items.length }} {{ t.kinds }}</el-tag>
          </div>
        </template>
        <el-table :data="order.items" size="default">
          <el-table-column :label="lang === 'zh' ? '商品' : 'Producto'" min-width="160">
            <template #default="{ row }">
              <div style="font-weight:bold;font-size:13px">{{ row.product_name }}</div>
              <div style="font-size:11px;color:#aaa">{{ row.product_barcode || '' }}</div>
            </template>
          </el-table-column>
          <el-table-column :label="t.qty" width="80" align="center">
            <template #default="{ row }">
              <el-tag type="info" size="small">× {{ row.quantity }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="t.unitPrice" width="100" align="right">
            <template #default="{ row }">
              <span style="color:#555">${{ row.unit_price }}</span>
            </template>
          </el-table-column>
          <el-table-column :label="t.subtotal" width="110" align="right">
            <template #default="{ row }">
              <span style="color:#409eff;font-weight:bold;font-size:15px">${{ row.total_price }}</span>
            </template>
          </el-table-column>
        </el-table>
        <div style="display:flex;justify-content:flex-end;padding:16px 0 0;border-top:1px solid #f0f0f0;margin-top:12px">
          <div style="font-size:15px;color:#888;margin-right:16px">{{ t.total }}</div>
          <div style="font-size:20px;font-weight:bold;color:#409eff">${{ order.total_amount }}</div>
        </div>
        <div v-if="order.remark" style="margin-top:8px;font-size:13px;color:#888">
          {{ t.remark }}：{{ order.remark }}
        </div>
      </el-card>

      <!-- 订单进度 -->
      <el-card>
        <template #header>
          <div style="display:flex;align-items:center;gap:8px">
            <el-icon style="color:#409eff"><Clock /></el-icon>
            <span style="font-weight:bold">{{ t.orderProgress }}</span>
          </div>
        </template>
        <div v-if="order.logs && order.logs.length > 0">
          <el-timeline>
            <el-timeline-item
              v-for="(log, idx) in order.logs"
              :key="idx"
              :timestamp="log.created_at"
              :type="idx === 0 ? 'primary' : 'info'"
              :hollow="idx !== 0"
              placement="top"
            >
              <div style="font-weight:bold;font-size:14px;color:#333">{{ statusText(log.status) || log.status_text }}</div>
              <div v-if="log.remark" style="font-size:12px;color:#999;margin-top:4px">{{ log.remark }}</div>
            </el-timeline-item>
          </el-timeline>
        </div>
        <div v-else style="color:#aaa;font-size:13px;padding:12px 0">{{ t.noProgress }}</div>
      </el-card>

      <!-- 取消按钮 -->
      <div v-if="order.status === 1" style="margin-top:16px;text-align:center">
        <el-button type="danger" size="large" @click="cancelOrder">{{ t.cancelOrder }}</el-button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Loading, Van, ShoppingBag, Clock } from '@element-plus/icons-vue'
import request from '../utils/request'
import { useCartStore } from '../stores/cart'
import { useLang } from '../composables/useLang'

const route = useRoute()
const router = useRouter()
const cart = useCartStore()
const { lang, t } = useLang()
const order = ref(null)

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

const cancelOrder = async () => {
  await ElMessageBox.confirm(t.value.confirmCancel, t.value.confirm, { type: 'warning' })
  const user = JSON.parse(localStorage.getItem('client_user') || '{}')
  const discount = user.discount ?? 1.0
  order.value.items.forEach(item => {
    cart.addItem({
      id: item.product_id, name: item.product_name, barcode: item.product_barcode,
      sell_price: +(item.unit_price / discount).toFixed(2),
      image: null, spec: null, middle_pack: null, piece: null, stock: 9999
    }, item.quantity, discount)
  })
  await request.post(`/orders/${order.value.id}/client-cancel`)
  ElMessage.success(t.value.cancelSuccess)
  router.push('/orders')
}

onMounted(async () => {
  order.value = await request.get(`/orders/${route.params.id}`)
})
</script>