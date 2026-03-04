<template>
  <div style="max-width:700px;margin:0 auto">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
      <el-button :icon="ArrowLeft" @click="$router.push('/orders')">返回</el-button>
      <h2 style="margin:0;color:#333">订单详情</h2>
    </div>

    <el-card v-if="order" style="margin-bottom:16px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ order.order_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(order.status)">{{ order.status_text }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="总金额">
          <span style="color:#409eff;font-weight:bold;font-size:16px">${{ order.total_amount }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="下单时间">{{ order.created_at }}</el-descriptions-item>
        <el-descriptions-item label="物流公司">{{ order.logistics_company || '-' }}</el-descriptions-item>
        <el-descriptions-item label="物流单号">{{ order.tracking_number || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ order.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card v-if="order" style="margin-bottom:16px">
      <template #header><span style="font-weight:bold">商品明细</span></template>
      <el-table :data="order.items" size="small">
        <el-table-column prop="product_name" label="商品" />
        <el-table-column prop="product_barcode" label="条码" width="130" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="unit_price" label="单价" width="90">
          <template #default="{ row }">${{ row.unit_price }}</template>
        </el-table-column>
        <el-table-column prop="total_price" label="小计" width="90">
          <template #default="{ row }">
            <span style="color:#409eff;font-weight:bold">${{ row.total_price }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card v-if="order">
      <template #header><span style="font-weight:bold">物流进度</span></template>
      <el-timeline>
        <el-timeline-item
          v-for="log in order.logs" :key="log.created_at"
          :timestamp="log.created_at"
          :type="log.status === 5 ? 'success' : 'primary'"
        >
          {{ log.status_text }}
          <div v-if="log.remark" style="color:#999;font-size:12px">{{ log.remark }}</div>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import request from '../utils/request'

const route = useRoute()
const order = ref(null)

const statusType = (status) => {
  const map = { 1: 'warning', 2: 'info', 3: 'primary', 4: '', 5: 'success', 6: 'danger', 7: 'danger' }
  return map[status] || ''
}

onMounted(async () => {
  order.value = await request.get(`/orders/${route.params.id}`)
})
</script>