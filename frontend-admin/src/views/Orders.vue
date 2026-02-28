<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>订单管理</span>
          <el-button type="primary" @click="openAdd">新建订单</el-button>
        </div>
      </template>

      <!-- 筛选 -->
      <el-select v-model="filterStatus" placeholder="筛选状态" clearable style="margin-bottom:15px" @change="loadOrders">
        <el-option label="待确认" :value="1" />
        <el-option label="已确认待配货" :value="2" />
        <el-option label="已配货待发货" :value="3" />
        <el-option label="已发货待付款" :value="4" />
        <el-option label="已付款完成" :value="5" />
      </el-select>

      <el-table :data="orders" stripe>
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="supermarket_name" label="客户" width="130" />
        <el-table-column prop="total_amount" label="金额" width="100" />
        <el-table-column label="状态" width="130">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ row.status_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tracking_number" label="物流单号" width="130" />
        <el-table-column prop="created_at" label="下单时间" width="160" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
            <el-button size="small" type="primary" @click="openUpdateStatus(row)" v-if="row.status < 5">
              更新状态
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建订单弹窗 -->
    <el-dialog v-model="addDialogVisible" title="新建订单" width="650px">
      <el-form :model="orderForm" label-width="90px">
        <el-form-item label="选择客户">
          <el-select v-model="orderForm.supermarket_id" placeholder="请选择客户" style="width:100%">
            <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="orderForm.remark" type="textarea" />
        </el-form-item>
        <el-divider>商品明细</el-divider>
        <div v-for="(item, index) in orderForm.items" :key="index" style="display:flex;gap:10px;margin-bottom:10px;align-items:center">
          <el-select v-model="item.product_id" placeholder="选择商品" filterable style="flex:2" @change="fillPrice(item)">
            <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
          <el-input-number v-model="item.quantity" :min="1" style="flex:1" placeholder="数量" />
          <el-input-number v-model="item.unit_price" :precision="2" :min="0" style="flex:1" placeholder="单价" />
          <el-button type="danger" circle @click="removeItem(index)"><el-icon><Delete /></el-icon></el-button>
        </div>
        <el-button @click="addItem" style="width:100%">+ 添加商品</el-button>
        <div style="text-align:right;margin-top:10px;font-weight:bold">
          合计：{{ totalAmount }}
        </div>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveOrder">提交订单</el-button>
      </template>
    </el-dialog>

    <!-- 更新状态弹窗 -->
    <el-dialog v-model="statusDialogVisible" title="更新订单状态" width="450px">
      <el-form :model="statusForm" label-width="90px">
        <el-form-item label="新状态">
          <el-select v-model="statusForm.status" style="width:100%">
            <el-option label="已确认待配货" :value="2" />
            <el-option label="已配货待发货" :value="3" />
            <el-option label="已发货待付款" :value="4" />
            <el-option label="已付款完成" :value="5" />
          </el-select>
        </el-form-item>
        <el-form-item label="物流公司" v-if="statusForm.status === 4">
          <el-input v-model="statusForm.logistics_company" />
        </el-form-item>
        <el-form-item label="物流单号" v-if="statusForm.status === 4">
          <el-input v-model="statusForm.tracking_number" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="statusForm.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveStatus">确认更新</el-button>
      </template>
    </el-dialog>

    <!-- 订单详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="订单详情" width="600px">
      <div v-if="currentOrder">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ currentOrder.order_no }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ currentOrder.supermarket_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ currentOrder.status_text }}</el-descriptions-item>
          <el-descriptions-item label="总金额">{{ currentOrder.total_amount }}</el-descriptions-item>
          <el-descriptions-item label="物流公司">{{ currentOrder.logistics_company }}</el-descriptions-item>
          <el-descriptions-item label="物流单号">{{ currentOrder.tracking_number }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>商品明细</el-divider>
        <el-table :data="currentOrder.items" size="small">
          <el-table-column prop="product_name" label="商品" />
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column prop="unit_price" label="单价" width="90" />
          <el-table-column prop="total_price" label="小计" width="90" />
        </el-table>

        <el-divider>操作记录</el-divider>
        <el-timeline>
          <el-timeline-item
            v-for="log in currentOrder.logs"
            :key="log.created_at"
            :timestamp="log.created_at"
          >
            {{ log.status_text }} - {{ log.operator_name }}
            <div v-if="log.remark" style="color:#999;font-size:12px">{{ log.remark }}</div>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const orders = ref([])
const customers = ref([])
const products = ref([])
const filterStatus = ref(null)
const addDialogVisible = ref(false)
const statusDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const currentOrder = ref(null)
const currentOrderId = ref(null)

const orderForm = ref({
  supermarket_id: null,
  remark: '',
  items: [{ product_id: null, quantity: 1, unit_price: 0 }]
})

const statusForm = ref({
  status: 2,
  remark: '',
  tracking_number: '',
  logistics_company: ''
})

const totalAmount = computed(() => {
  return orderForm.value.items.reduce((sum, item) => {
    return sum + (item.quantity || 0) * (item.unit_price || 0)
  }, 0).toFixed(2)
})

const statusType = (status) => {
  const map = { 1: 'warning', 2: 'info', 3: 'primary', 4: '', 5: 'success' }
  return map[status] || ''
}

const loadOrders = async () => {
  const params = {}
  if (filterStatus.value) params.status = filterStatus.value
  orders.value = await request.get('/orders/', { params })
}

const loadCustomers = async () => {
  customers.value = await request.get('/customers/')
}

const loadProducts = async () => {
  products.value = await request.get('/products/')
}

const openAdd = () => {
  orderForm.value = {
    supermarket_id: null,
    remark: '',
    items: [{ product_id: null, quantity: 1, unit_price: 0 }]
  }
  addDialogVisible.value = true
}

const addItem = () => {
  orderForm.value.items.push({ product_id: null, quantity: 1, unit_price: 0 })
}

const removeItem = (index) => {
  orderForm.value.items.splice(index, 1)
}

const fillPrice = (item) => {
  const product = products.value.find(p => p.id === item.product_id)
  if (product) item.unit_price = product.sell_price || 0
}

const saveOrder = async () => {
  if (!orderForm.value.supermarket_id) {
    ElMessage.warning('请选择客户')
    return
  }
  if (orderForm.value.items.some(i => !i.product_id)) {
    ElMessage.warning('请选择商品')
    return
  }
  await request.post('/orders/', orderForm.value)
  ElMessage.success('订单创建成功')
  addDialogVisible.value = false
  loadOrders()
}

const openUpdateStatus = (row) => {
  currentOrderId.value = row.id
  statusForm.value = { status: row.status + 1, remark: '', tracking_number: '', logistics_company: '' }
  statusDialogVisible.value = true
}

const saveStatus = async () => {
  await request.put(`/orders/${currentOrderId.value}/status`, statusForm.value)
  ElMessage.success('状态更新成功')
  statusDialogVisible.value = false
  loadOrders()
}

const viewDetail = async (row) => {
  currentOrder.value = await request.get(`/orders/${row.id}`)
  detailDialogVisible.value = true
}

onMounted(() => {
  loadOrders()
  loadCustomers()
  loadProducts()
})
</script>