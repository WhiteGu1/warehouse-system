<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>客户管理</span>
          <el-button type="primary" @click="openAdd">新增客户</el-button>
        </div>
      </template>

      <el-table :data="customers" stripe>
        <el-table-column prop="name" label="客户名称" />
        <el-table-column prop="contact_person" label="联系人" width="100" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="address" label="地址" />
        <el-table-column prop="username" label="登录账号" width="120" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="110" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="warning" @click="resetPassword(row.id)">重置密码</el-button>
            <el-button size="small" :type="row.is_active ? 'danger' : 'success'" @click="toggleStatus(row)">
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑客户' : '新增客户'" width="500px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="客户名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="form.contact_person" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" />
        </el-form-item>
        <el-form-item label="登录账号" v-if="!isEdit">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="登录密码" v-if="!isEdit">
          <el-input v-model="form.password" type="password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCustomer">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../utils/request'

const customers = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const form = ref({
  name: '', contact_person: '', phone: '',
  address: '', username: '', password: ''
})

const loadCustomers = async () => {
  customers.value = await request.get('/customers/')
}

const openAdd = () => {
  isEdit.value = false
  form.value = { name: '', contact_person: '', phone: '', address: '', username: '', password: '' }
  dialogVisible.value = true
}

const openEdit = (row) => {
  isEdit.value = true
  editId.value = row.id
  form.value = { name: row.name, contact_person: row.contact_person, phone: row.phone, address: row.address, is_active: row.is_active }
  dialogVisible.value = true
}

const saveCustomer = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入客户名称')
    return
  }
  if (isEdit.value) {
    await request.put(`/customers/${editId.value}`, form.value)
  } else {
    if (!form.value.username || !form.value.password) {
      ElMessage.warning('请输入账号和密码')
      return
    }
    await request.post('/customers/', form.value)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadCustomers()
}

const resetPassword = async (id) => {
  await ElMessageBox.confirm('确定重置该客户密码为 123456？', '提示', { type: 'warning' })
  await request.put(`/customers/${id}/reset-password`)
  ElMessage.success('密码已重置为123456')
}

const toggleStatus = async (row) => {
  const action = row.is_active ? '禁用' : '启用'
  await ElMessageBox.confirm(`确定${action}该客户？`, '提示', { type: 'warning' })
  await request.put(`/customers/${row.id}`, { ...row, is_active: row.is_active ? 0 : 1 })
  ElMessage.success(`${action}成功`)
  loadCustomers()
}

onMounted(() => {
  loadCustomers()
})
</script>