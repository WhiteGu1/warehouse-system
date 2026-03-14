<template>
  <div>
    <el-card>
      <template #header><span>出库记录</span></template>
      <el-input v-model="keyword" placeholder="搜索商品名称或条码" clearable @input="loadRecords" style="margin-bottom:15px">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>

      <!-- PC端表格 -->
      <el-table :data="records" stripe class="desktop-table">
        <el-table-column prop="created_at" label="出库时间" width="160" />
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="product_barcode" label="条码" width="120" />
        <el-table-column prop="product_spec" label="规格" width="100" />
        <el-table-column prop="order_no" label="订单号" width="160" />
        <el-table-column prop="quantity" label="出库数量" width="90" />
        <el-table-column prop="sell_price" label="售价" width="90" />
        <el-table-column prop="reason" label="原因" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status==='deleted'" type="danger" size="small">商品删除</el-tag>
            <el-tag v-else-if="row.status==='已退回'" type="info" size="small">已退回</el-tag>
            <el-tag v-else-if="row.status==='仅退款'" type="warning" size="small">仅退款</el-tag>
            <el-tag v-else-if="row.status==='已取消'" type="info" size="small">已取消</el-tag>
            <el-tag v-else-if="row.status==='待确认'" type="info" size="small">待确认</el-tag>
            <el-tag v-else-if="row.status==='待配货'" type="warning" size="small">待配货</el-tag>
            <el-tag v-else-if="row.status==='待发货'" type="warning" size="small">待发货</el-tag>
            <el-tag v-else-if="row.status==='待付款'" type="primary" size="small">待付款</el-tag>
            <el-tag v-else-if="row.status==='已完成'" type="success" size="small">已完成</el-tag>
            <el-tag v-else size="small">{{ row.status || '-' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- 手机端卡片列表 -->
      <div class="mobile-list">
        <div v-for="row in records" :key="row.id" style="border:1px solid #e4e7ed;border-radius:8px;padding:12px;margin-bottom:10px;background:#fff">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
            <div style="font-weight:bold;font-size:14px;flex:1;margin-right:8px">{{ row.product_name }}</div>
            <el-tag v-if="row.status==='deleted'" type="danger" size="small">商品删除</el-tag>
            <el-tag v-else-if="row.status==='已退回'" type="info" size="small">已退回</el-tag>
            <el-tag v-else-if="row.status==='仅退款'" type="warning" size="small">仅退款</el-tag>
            <el-tag v-else-if="row.status==='已取消'" type="info" size="small">已取消</el-tag>
            <el-tag v-else-if="row.status==='待确认'" type="info" size="small">待确认</el-tag>
            <el-tag v-else-if="row.status==='待配货'" type="warning" size="small">待配货</el-tag>
            <el-tag v-else-if="row.status==='待发货'" type="warning" size="small">待发货</el-tag>
            <el-tag v-else-if="row.status==='待付款'" type="primary" size="small">待付款</el-tag>
            <el-tag v-else-if="row.status==='已完成'" type="success" size="small">已完成</el-tag>
            <el-tag v-else size="small">{{ row.status || '-' }}</el-tag>
          </div>
          <div style="font-size:12px;color:#888;margin-bottom:4px">{{ row.created_at }}</div>
          <div style="font-size:12px;color:#666;margin-bottom:4px">订单号：{{ row.order_no || '-' }}</div>
          <div style="display:flex;gap:16px;flex-wrap:wrap;font-size:13px">
            <span>条码：<b>{{ row.product_barcode || '-' }}</b></span>
            <span>规格：<b>{{ row.product_spec || '-' }}</b></span>
            <span>数量：<b style="color:#f56c6c">{{ row.quantity }}</b></span>
            <span>售价：<b style="color:#67c23a">${{ row.sell_price }}</b></span>
          </div>
          <div v-if="row.reason" style="font-size:12px;color:#aaa;margin-top:4px">原因：{{ row.reason }}</div>
        </div>
        <div v-if="records.length === 0" style="text-align:center;color:#aaa;padding:40px 0">暂无记录</div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import request from '../utils/request'

const records = ref([])
const keyword = ref('')

const loadRecords = async () => {
  const params = {}
  if (keyword.value) params.keyword = keyword.value
  records.value = await request.get('/stock-out/', { params })
}

onMounted(() => {
  loadRecords()
})
</script>

<style scoped>
.mobile-list { display: none; }

@media (max-width: 768px) {
  .desktop-table { display: none; }
  .mobile-list { display: block; }
}
</style>