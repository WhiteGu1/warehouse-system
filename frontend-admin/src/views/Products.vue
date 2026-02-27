<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>商品管理</span>
          <el-button type="primary" @click="openAdd">新增商品</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-row :gutter="10" style="margin-bottom:15px">
        <el-col :span="8">
          <el-input v-model="keyword" placeholder="搜索商品名称" clearable @change="loadProducts">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-select v-model="categoryId" placeholder="选择分类" clearable @change="loadProducts">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-col>
      </el-row>

      <!-- 商品表格 -->
      <el-table :data="products" stripe>
        <el-table-column prop="barcode" label="条形码" width="130" />
        <el-table-column prop="name" label="商品名称" />
        <el-table-column prop="category_name" label="分类" width="100" />
        <el-table-column prop="spec" label="规格" width="100" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="cost_price" label="进价" width="90" />
        <el-table-column prop="sell_price" label="售价" width="90" />
        <el-table-column prop="stock" label="库存" width="80" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteProduct(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑商品' : '新增商品'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="条形码">
          <el-input v-model="form.barcode" />
        </el-form-item>
        <el-form-item label="商品名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category_id" placeholder="选择分类">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="规格">
          <el-input v-model="form.spec" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="form.unit" />
        </el-form-item>
        <el-form-item label="进价">
          <el-input-number v-model="form.cost_price" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="售价">
          <el-input-number v-model="form.sell_price" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="库存">
          <el-input-number v-model="form.stock" :min="0" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProduct">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../utils/request'

const products = ref([])
const categories = ref([])
const keyword = ref('')
const categoryId = ref(null)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const form = ref({
  barcode: '', name: '', category_id: null,
  spec: '', unit: '', cost_price: 0,
  sell_price: 0, stock: 0, remark: ''
})

const loadProducts = async () => {
  const params = {}
  if (keyword.value) params.keyword = keyword.value
  if (categoryId.value) params.category_id = categoryId.value
  products.value = await request.get('/products/', { params })
}

const loadCategories = async () => {
  categories.value = await request.get('/products/categories')
}

const openAdd = () => {
  isEdit.value = false
  form.value = {
    barcode: '', name: '', category_id: null,
    spec: '', unit: '', cost_price: 0,
    sell_price: 0, stock: 0, remark: ''
  }
  dialogVisible.value = true
}

const openEdit = (row) => {
  isEdit.value = true
  editId.value = row.id
  form.value = { ...row }
  dialogVisible.value = true
}

const saveProduct = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入商品名称')
    return
  }
  if (isEdit.value) {
    await request.put(`/products/${editId.value}`, form.value)
  } else {
    await request.post('/products/', form.value)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadProducts()
}

const deleteProduct = async (id) => {
  await ElMessageBox.confirm('确定删除该商品？', '提示', { type: 'warning' })
  await request.delete(`/products/${id}`)
  ElMessage.success('删除成功')
  loadProducts()
}

onMounted(() => {
  loadProducts()
  loadCategories()
})
</script>