<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>入库管理</span>
          <el-button type="primary" @click="dialogVisible = true">新增入库</el-button>
        </div>
      </template>

      <el-table :data="records" stripe>
        <el-table-column prop="created_at" label="入库时间" width="180" />
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="quantity" label="入库数量" width="100" />
        <el-table-column prop="cost_price" label="进价" width="100" />
        <el-table-column prop="total_amount" label="总金额" width="120" />
        <el-table-column prop="remark" label="备注" />
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新增入库" width="450px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="选择商品">
          <el-select v-model="form.product_id" placeholder="请选择商品" filterable style="width:100%">
            <el-option
              v-for="p in products"
              :key="p.id"
              :label="p.name + (p.spec ? ' (' + p.spec + ')' : '')"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="入库数量">
          <el-input-number v-model="form.quantity" :min="1" />
        </el-form-item>
        <el-form-item label="进价">
          <el-input-number v-model="form.cost_price" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveStockIn">确认入库</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const records = ref([])
const products = ref([])
const dialogVisible = ref(false)
const form = ref({ product_id: null, quantity: 1, cost_price: 0, remark: '' })

const loadRecords = async () => {
  records.value = await request.get('/stock/')
}

const loadProducts = async () => {
  products.value = await request.get('/products/')
}

const saveStockIn = async () => {
  if (!form.value.product_id) {
    ElMessage.warning('请选择商品')
    return
  }
  const res = await request.post('/stock/', form.value)
  ElMessage.success(`入库成功，当前库存：${res.new_stock}`)
  dialogVisible.value = false
  form.value = { product_id: null, quantity: 1, cost_price: 0, remark: '' }
  loadRecords()
}

onMounted(() => {
  loadRecords()
  loadProducts()
})
</script>