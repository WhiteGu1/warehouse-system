<template>
  <div>
    <el-card>
      <template #header><span>入库记录</span></template>
      <el-row :gutter="10" style="margin-bottom:15px">
        <el-col :span="8">
          <el-input v-model="keyword" placeholder="搜索商品名称或条码" clearable @input="onSearch">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
      </el-row>
      <el-table :data="records" stripe v-loading="loading">
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
      <div style="display:flex;justify-content:flex-end;margin-top:12px">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next, jumper"
          background
          @current-change="loadRecords"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import request from '../utils/request'

const records = ref([])
const keyword = ref('')
const currentPage = ref(1)
const pageSize = 50
const total = ref(0)
const loading = ref(false)

const onSearch = () => {
  currentPage.value = 1
  loadRecords()
}

const loadRecords = async () => {
  loading.value = true
  try {
    const res = await request.get('/stock/', {
      params: { keyword: keyword.value || undefined, page: currentPage.value, page_size: pageSize }
    })
    records.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

loadRecords()
</script>