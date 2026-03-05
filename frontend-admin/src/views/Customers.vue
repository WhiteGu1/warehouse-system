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
        <el-table-column prop="tax_no" label="税号" width="160" />
        <el-table-column label="折扣" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.discount < 1" type="warning">{{ (row.discount * 100).toFixed(0) }}折</el-tag>
            <el-tag v-else type="success">无折扣</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="登录账号" width="120" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '正常' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="110" />
        <el-table-column label="操作" width="240">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="info" @click="openStats(row)">统计</el-button>
            <el-button size="small" type="warning" @click="resetPassword(row.id)">重置密码</el-button>
            <el-button size="small" :type="row.is_active ? 'danger' : 'success'" @click="toggleStatus(row)">
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑客户' : '新增客户'" width="500px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="客户名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="form.contact_person" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="税号"><el-input v-model="form.tax_no" placeholder="纳税人识别号" /></el-form-item>
        <el-form-item label="折扣">
          <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
            <el-button
              v-for="d in discountOptions" :key="d.value"
              :type="form.discount === d.value ? 'primary' : ''"
              size="small"
              @click="form.discount = d.value"
            >{{ d.label }}</el-button>
            <el-input-number
              v-model="form.discount"
              :precision="2" :min="0.01" :max="1" :step="0.05"
              style="width:120px"
            />
            <span style="color:#999;font-size:12px">（1=无折扣，0.9=九折）</span>
          </div>
        </el-form-item>
        <el-form-item label="登录账号" v-if="!isEdit"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="登录密码" v-if="!isEdit"><el-input v-model="form.password" type="password" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCustomer">保存</el-button>
      </template>
    </el-dialog>

    <!-- 客户订单统计弹窗 -->
    <el-dialog v-model="statsVisible" :title="`客户统计 - ${statsCustomer.name}`" width="780px">
      <div v-if="statsLoading" style="text-align:center;padding:40px;color:#aaa">加载中...</div>
      <div v-else>
        <!-- 概览卡片 -->
        <div style="display:flex;gap:12px;margin-bottom:20px">
          <div style="flex:1;background:linear-gradient(135deg,#e8f4fd,#c3dff7);border-radius:10px;padding:16px;text-align:center">
            <div style="font-size:13px;color:#666;margin-bottom:6px">累计订单</div>
            <div style="font-size:28px;font-weight:bold;color:#409eff">{{ statsData.total_orders }}</div>
          </div>
          <div style="flex:1;background:linear-gradient(135deg,#f0f9eb,#d4edda);border-radius:10px;padding:16px;text-align:center">
            <div style="font-size:13px;color:#666;margin-bottom:6px">累计消费</div>
            <div style="font-size:28px;font-weight:bold;color:#67c23a">${{ statsData.total_amount }}</div>
          </div>
          <div style="flex:1;background:linear-gradient(135deg,#fdf6ec,#fde8c8);border-radius:10px;padding:16px;text-align:center">
            <div style="font-size:13px;color:#666;margin-bottom:6px">平均客单价</div>
            <div style="font-size:28px;font-weight:bold;color:#e6a23c">${{ statsData.avg_amount }}</div>
          </div>
          <div style="flex:1;background:linear-gradient(135deg,#fef0f0,#fdd);border-radius:10px;padding:16px;text-align:center">
            <div style="font-size:13px;color:#666;margin-bottom:6px">完成订单</div>
            <div style="font-size:28px;font-weight:bold;color:#f56c6c">{{ statsData.completed_orders }}</div>
          </div>
        </div>

        <!-- 最近订单 -->
        <div style="font-weight:bold;font-size:14px;margin-bottom:10px;color:#333">
          最近订单
          <el-tag type="info" size="small" style="margin-left:8px">最近20笔</el-tag>
        </div>
        <el-table :data="statsData.recent_orders" size="small" max-height="220" stripe>
          <el-table-column prop="order_no" label="订单号" width="170" />
          <el-table-column label="金额" width="90">
            <template #default="{ row }">
              <span style="color:#409eff;font-weight:bold">${{ row.total_amount }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="110">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)" size="small">{{ row.status_text }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="下单时间" width="160" />
          <el-table-column label="操作" width="70">
            <template #default="{ row }">
              <el-button size="small" type="primary" text @click="viewOrder(row.id)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 常购商品 Top10 -->
        <div style="font-weight:bold;font-size:14px;margin:16px 0 10px;color:#333">
          常购商品 Top 10
        </div>
        <el-table :data="statsData.top_products" size="small" max-height="220" stripe>
          <el-table-column type="index" label="#" width="40" />
          <el-table-column prop="product_name" label="商品名称" />
          <el-table-column prop="product_barcode" label="条码" width="130" />
          <el-table-column label="累计购买" width="90" align="center">
            <template #default="{ row }">
              <el-tag type="primary" size="small">{{ row.total_qty }} 件</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="累计金额" width="100" align="right">
            <template #default="{ row }">
              <span style="color:#409eff;font-weight:bold">${{ row.total_amount }}</span>
            </template>
          </el-table-column>
          <el-table-column label="订单次数" width="80" align="center">
            <template #default="{ row }">
              {{ row.order_count }} 次
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button type="primary" @click="exportCustomerStats">导出统计</el-button>
        <el-button @click="statsVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

const router = useRouter()
const customers = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const statsVisible = ref(false)
const statsLoading = ref(false)
const statsCustomer = ref({})
const statsData = ref({
  total_orders: 0, total_amount: 0, avg_amount: 0, completed_orders: 0,
  recent_orders: [], top_products: []
})

const discountOptions = [
  { label: '无折扣', value: 1.0 },
  { label: '九五折', value: 0.95 },
  { label: '九折', value: 0.9 },
  { label: '八五折', value: 0.85 },
  { label: '八折', value: 0.8 },
]

const form = ref({
  name: '', contact_person: '', phone: '', address: '',
  tax_no: '', discount: 1.0, username: '', password: ''
})

const statusType = (status) => {
  const map = { 1: 'warning', 2: 'info', 3: 'primary', 4: '', 5: 'success', 6: 'danger', 7: 'danger' }
  return map[status] || ''
}

const loadCustomers = async () => {
  customers.value = await request.get('/customers/')
}

const openAdd = () => {
  isEdit.value = false
  form.value = { name: '', contact_person: '', phone: '', address: '', tax_no: '', discount: 1.0, username: '', password: '' }
  dialogVisible.value = true
}

const openEdit = (row) => {
  isEdit.value = true
  editId.value = row.id
  form.value = {
    name: row.name, contact_person: row.contact_person, phone: row.phone,
    address: row.address, tax_no: row.tax_no || '', discount: row.discount ?? 1.0, is_active: row.is_active
  }
  dialogVisible.value = true
}

const saveCustomer = async () => {
  if (!form.value.name) { ElMessage.warning('请输入客户名称'); return }
  if (isEdit.value) {
    await request.put(`/customers/${editId.value}`, form.value)
  } else {
    if (!form.value.username || !form.value.password) { ElMessage.warning('请输入账号和密码'); return }
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

const openStats = async (row) => {
  statsCustomer.value = row
  statsVisible.value = true
  statsLoading.value = true
  try {
    // 获取该客户所有订单
    const orders = await request.get('/orders/', { params: { supermarket_id: row.id } })
    const validOrders = orders.filter(o => o.status !== 6 && o.status !== 7)
    const total_orders = orders.length
    const completed_orders = orders.filter(o => o.status === 5).length
    const total_amount = validOrders.reduce((s, o) => s + parseFloat(o.total_amount || 0), 0).toFixed(2)
    const avg_amount = total_orders > 0 ? (parseFloat(total_amount) / total_orders).toFixed(2) : '0.00'

    // 最近20笔
    const recent_orders = [...orders]
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 20)

    // 常购商品：拉取每笔订单明细（最近50笔）
    const productMap = {}
    const recentForItems = [...orders]
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 50)
    for (const o of recentForItems) {
      if (o.status === 6 || o.status === 7) continue
      try {
        const detail = await request.get(`/orders/${o.id}`)
        if (detail.items) {
          for (const item of detail.items) {
            const key = item.product_id
            if (!productMap[key]) {
              productMap[key] = {
                product_name: item.product_name,
                product_barcode: item.product_barcode || '',
                total_qty: 0, total_amount: 0, order_count: 0
              }
            }
            productMap[key].total_qty += item.quantity
            productMap[key].total_amount += parseFloat(item.total_price || 0)
            productMap[key].order_count += 1
          }
        }
      } catch {}
    }
    const top_products = Object.values(productMap)
      .sort((a, b) => b.total_qty - a.total_qty)
      .slice(0, 10)
      .map(p => ({ ...p, total_amount: p.total_amount.toFixed(2) }))

    statsData.value = { total_orders, total_amount, avg_amount, completed_orders, recent_orders, top_products }
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    statsLoading.value = false
  }
}

const viewOrder = (id) => {
  statsVisible.value = false
  router.push('/orders')
}

const exportCustomerStats = () => {
  const wb = XLSX.utils.book_new()

  // 概览
  const overview = [{
    '客户名称': statsCustomer.value.name,
    '累计订单': statsData.value.total_orders,
    '累计消费': statsData.value.total_amount,
    '平均客单价': statsData.value.avg_amount,
    '完成订单': statsData.value.completed_orders
  }]
  const ws1 = XLSX.utils.json_to_sheet(overview)
  XLSX.utils.book_append_sheet(wb, ws1, '概览')

  // 最近订单
  const ordersData = statsData.value.recent_orders.map(o => ({
    '订单号': o.order_no,
    '金额': o.total_amount,
    '状态': o.status_text,
    '下单时间': o.created_at
  }))
  const ws2 = XLSX.utils.json_to_sheet(ordersData)
  XLSX.utils.book_append_sheet(wb, ws2, '最近订单')

  // 常购商品
  const productsData = statsData.value.top_products.map((p, i) => ({
    '排名': i + 1,
    '商品名称': p.product_name,
    '条码': p.product_barcode,
    '累计购买数量': p.total_qty,
    '累计金额': p.total_amount,
    '订单次数': p.order_count
  }))
  const ws3 = XLSX.utils.json_to_sheet(productsData)
  XLSX.utils.book_append_sheet(wb, ws3, '常购商品')

  const buf = XLSX.write(wb, { type: 'array', bookType: 'xlsx' })
  saveAs(new Blob([buf], { type: 'application/octet-stream' }), `${statsCustomer.value.name}_统计_${new Date().toLocaleDateString()}.xlsx`)
}

onMounted(() => {
  loadCustomers()
})
</script>