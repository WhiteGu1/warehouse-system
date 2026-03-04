<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>分类管理</span>
          <el-button type="primary" @click="openAdd">新增分类</el-button>
        </div>
      </template>
      <el-table :data="categories" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="分类名称" />
        <el-table-column prop="product_count" label="商品数量" width="100" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteCategory(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑分类' : '新增分类'" width="400px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="分类名称"><el-input v-model="form.name" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCategory">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../utils/request'

const categories = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const form = ref({ name: '' })

const loadCategories = async () => {
  const data = await request.get('/categories/')
  categories.value = data
}

const openAdd = () => {
  isEdit.value = false
  form.value = { name: '' }
  dialogVisible.value = true
}

const openEdit = (row) => {
  isEdit.value = true
  editId.value = row.id
  form.value = { name: row.name }
  dialogVisible.value = true
}

const saveCategory = async () => {
  if (!form.value.name) { ElMessage.warning('请输入分类名称'); return }
  if (isEdit.value) {
    await request.put(`/categories/${editId.value}`, form.value)
  } else {
    await request.post('/categories/', form.value)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadCategories()
}

const deleteCategory = async (row) => {
  if (row.product_count > 0) {
    ElMessage.warning(`该分类下有 ${row.product_count} 个商品，无法删除`)
    return
  }
  await ElMessageBox.confirm(`确定删除分类"${row.name}"？`, '提示', { type: 'warning' })
  await request.delete(`/categories/${row.id}`)
  ElMessage.success('删除成功')
  loadCategories()
}

onMounted(() => {
  loadCategories()
})
</script>