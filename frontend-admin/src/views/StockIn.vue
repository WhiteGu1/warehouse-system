<template>
  <div>
    <el-card>
      <template #header><span>入库记录</span></template>
      <el-input v-model="keyword" placeholder="搜索商品名称或条码" clearable @input="onSearch" style="margin-bottom:15px">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>

      <!-- PC端表格 -->
      <el-table :data="records" stripe v-loading="loading" class="desktop-table">
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

      <!-- 手机端卡片列表 -->
      <div class="mobile-list" v-loading="loading">
        <div v-for="row in records" :key="row.id" style="border:1px solid #e4e7ed;border-radius:8px;padding:12px;margin-bottom:10px;background:#fff">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
            <div style="font-weight:bold;font-size:14px;flex:1;margin-right:8px">{{ row.product_name }}</div>
            <el-tag v-if="row.source==='manual_new'" type="success" size="small">新增</el-tag>
            <el-tag v-else-if="row.source==='manual_add'" type="primary" size="small">补货</el-tag>
            <el-tag v-else-if="row.source==='import'" type="warning" size="small">导入</el-tag>
            <el-tag v-else-if="row.source==='cancel'" type="danger" size="small">退回</el-tag>
            <el-tag v-else size="small">-</el-tag>
          </div>
          <div style="font-size:12px;color:#888;margin-bottom:4px">{{ row.created_at }}</div>
          <div style="display:flex;gap:16px;flex-wrap:wrap;font-size:13px">
            <span>条码：<b>{{ row.product_barcode || '-' }}</b></span>
            <span>规格：<b>{{ row.product_spec || '-' }}</b></span>
            <span>数量：<b style="color:#409eff">{{ row.quantity }}</b></span>
            <span>进价：<b style="color:#e6a23c">${{ row.cost_price }}</b></span>
            <span>总额：<b style="color:#67c23a">${{ row.total_amount }}</b></span>
          </div>
          <div v-if="row.remark" style="font-size:12px;color:#aaa;margin-top:4px">备注：{{ row.remark }}</div>
        </div>
        <div v-if="records.length === 0 && !loading" style="text-align:center;color:#aaa;padding:40px 0">暂无记录</div>
      </div>

      <div style="display:flex;justify-content:center;margin-top:12px">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          background
          @current-change="loadRecords"
          class="mobile-pagination"
        />
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next, jumper"
          background
          @current-change="loadRecords"
          class="desktop-pagination"
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

<style scoped>
.mobile-list { display: none; }
.mobile-pagination { display: none; }
.desktop-pagination { display: flex; }

@media (max-width: 768px) {
  .desktop-table { display: none; }
  .mobile-list { display: block; }
  .mobile-pagination { display: flex; }
  .desktop-pagination { display: none; }
}
</style>