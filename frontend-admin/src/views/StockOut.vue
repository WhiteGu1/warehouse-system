<template>
  <div>
    <el-card>
      <template #header><span>出库记录</span></template>
      <el-row :gutter="10" style="margin-bottom:15px">
        <el-col :span="8">
          <el-input v-model="keyword" placeholder="搜索商品名称或条码" clearable @input="loadRecords">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
      </el-row>
      <el-table :data="records" stripe>
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