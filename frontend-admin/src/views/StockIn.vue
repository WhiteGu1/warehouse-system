<template>
  <div>
    <el-card>
      <template #header><span>入库记录</span></template>
      <el-row :gutter="10" style="margin-bottom:15px">
        <el-col :span="8">
          <el-input v-model="keyword" placeholder="搜索商品名称或条码" clearable @input="loadRecords">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
      </el-row>
      <el-table :data="records" stripe>
        <el-table-column prop="created_at" label="入库时间" width="160" />
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="product_barcode" label="条码" width="120" />
        <el-table-column prop="product_spec" label="规格" width="100" />
        <el-table-column prop="quantity" label="入库数量" width="90" />
        <el-table-column prop="cost_price" label="进价" width="90" />
        <el-table-column prop="total_amount" label="总金额" width="100" />
        <el-table-column label="类型" width="110">
          <template #default="{ row }">
            <el-tag v-if="row.source==='manual_new'" type="success" size="small">手动-新增</el-tag>
            <el-tag v-else-if="row.source==='manual_add'" type="primary" size="small">手动-库存增加</el-tag>
            <el-tag v-else-if="row.source==='import'" type="warning" size="small">导入添加</el-tag>
            <el-tag v-else-if="row.source==='cancel'" type="danger" size="small">取消退回</el-tag>
            <el-tag v-else size="small">-</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" show-overflow-tooltip />
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
  records.value = await request.get('/stock/', { params })
}

onMounted(() => {
  loadRecords()
})
</script>