<template>
  <div>
    <h2 style="margin-bottom:20px">系统首页</h2>

    <!-- 新订单提醒 -->
    <el-alert
      v-if="newOrders.length > 0"
      type="warning"
      :closable="false"
      style="margin-bottom:20px;cursor:pointer"
      @click="newOrderDialogVisible = true"
    >
      <template #title>
        <span style="font-size:15px;font-weight:bold">🔔 有 {{ newOrders.length }} 条新订单待确认，点击查看</span>
      </template>
    </el-alert>

    <el-row :gutter="20" style="margin-bottom:24px">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" style="cursor:pointer" @click="$router.push('/products')">
          <div style="text-align:center">
            <div style="font-size:32px;color:#409eff;font-weight:bold">{{ stats.products }}</div>
            <div style="color:#666;margin-top:8px">商品总数</div>
            <div style="color:#aaa;font-size:12px;margin-top:4px">点击进入商品管理</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" style="cursor:pointer" @click="$router.push('/customers')">
          <div style="text-align:center">
            <div style="font-size:32px;color:#67c23a;font-weight:bold">{{ stats.supermarkets }}</div>
            <div style="color:#666;margin-top:8px">客户数量</div>
            <div style="color:#aaa;font-size:12px;margin-top:4px">点击进入客户管理</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-row :gutter="20" style="margin-bottom:24px;row-gap:16px"></el-row>
        <el-card shadow="hover" style="cursor:pointer" @click="pendingOrderDialogVisible = true">
          <div style="text-align:center">
            <div style="font-size:32px;color:#e6a23c;font-weight:bold">{{ stats.pending_orders }}</div>
            <div style="color:#666;margin-top:8px">待处理订单</div>
            <div style="color:#aaa;font-size:12px;margin-top:4px">点击查看详情</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-row :gutter="20" style="margin-bottom:24px;row-gap:16px"></el-row>
        <el-card shadow="hover" style="cursor:pointer" @click="lowStockDialogVisible = true">
          <div style="text-align:center">
            <div style="font-size:32px;color:#f56c6c;font-weight:bold">{{ stats.low_stock }}</div>
            <div style="color:#666;margin-top:8px">库存不足</div>
            <div style="color:#aaa;font-size:12px;margin-top:4px">点击查看详情</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 未完成订单 -->
    <el-card>
      <template #header><span>未完成订单（待处理）</span></template>
      <el-table
        :data="recentOrders" stripe
        row-style="cursor:pointer"
        @row-click="viewDetail"
      >
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="supermarket_name" label="客户" width="130" />
        <el-table-column label="金额" width="110">
          <template #default="{ row }">
            <span style="color:#409eff;font-weight:bold;white-space:nowrap">${{ row.total_amount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="130">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.status_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tracking_number" label="物流单号" width="130" show-overflow-tooltip />
        <el-table-column prop="created_at" label="下单时间" width="160" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <div style="display:flex;gap:4px" @click.stop>
              <el-button size="small" type="success" @click="printInvoice(row)">打印</el-button>
              <el-button size="small" type="primary" @click="openUpdateStatus(row)" v-if="row.status >= 1 && row.status <= 4">更新状态</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新订单弹窗 -->
    <el-dialog v-model="newOrderDialogVisible" title="🔔 新订单待确认" width="700px">
      <el-table :data="newOrders" stripe>
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="supermarket_name" label="客户" width="150" />
        <el-table-column prop="total_amount" label="金额" width="100">
          <template #default="{ row }">${{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="下单时间" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="confirmOrder(row)">确认</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="newOrderDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 待处理订单弹窗 -->
    <el-dialog v-model="pendingOrderDialogVisible" title="待处理订单" width="700px">
      <el-table :data="pendingOrders" stripe>
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="supermarket_name" label="客户" width="150" />
        <el-table-column prop="total_amount" label="金额" width="100">
          <template #default="{ row }">${{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.status_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="下单时间" />
      </el-table>
      <template #footer>
        <el-button @click="$router.push('/orders');pendingOrderDialogVisible=false">前往订单管理</el-button>
        <el-button @click="pendingOrderDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 库存不足弹窗 -->
    <el-dialog v-model="lowStockDialogVisible" title="库存不足商品" width="600px">
      <el-table :data="lowStockProducts" stripe>
        <el-table-column prop="name" label="商品名称" />
        <el-table-column prop="spec" label="规格" width="100" />
        <el-table-column prop="barcode" label="条码" width="130" />
        <el-table-column prop="stock" label="当前库存" width="90">
          <template #default="{ row }">
            <el-tag type="danger" size="small">{{ row.stock }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="$router.push('/products');lowStockDialogVisible=false">前往商品管理</el-button>
        <el-button @click="lowStockDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 订单详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="订单详情" width="700px">
      <div v-if="currentOrder">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ currentOrder.order_no }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ currentOrder.supermarket_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusType(currentOrder.status)">{{ currentOrder.status_text }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总金额">${{ currentOrder.total_amount }}</el-descriptions-item>
          <el-descriptions-item label="物流公司">{{ currentOrder.logistics_company || '-' }}</el-descriptions-item>
          <el-descriptions-item label="物流单号">{{ currentOrder.tracking_number || '-' }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>商品明细</el-divider>
        <el-table :data="currentOrder.items" size="small">
          <el-table-column prop="product_name" label="商品" />
          <el-table-column prop="product_barcode" label="条码" width="120" />
          <el-table-column prop="quantity" label="数量" width="60" />
          <el-table-column prop="returned_quantity" label="已退" width="55">
            <template #default="{ row }">
              <span v-if="row.returned_quantity > 0" style="color:#f56c6c">{{ row.returned_quantity }}</span>
              <span v-else style="color:#ccc">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="unit_price" label="单价" width="75" />
          <el-table-column prop="total_price" label="小计" width="75" />
          <el-table-column v-if="currentOrder.status === 1" label="操作" width="75">
            <template #default="{ row }">
              <el-button size="small" type="danger" @click="removeOrderItem(row)">删除</el-button>
            </template>
          </el-table-column>
          <el-table-column v-if="currentOrder.status >= 4 && currentOrder.status <= 5" label="退货数量" width="110">
            <template #default="{ row }">
              <el-input-number
                v-model="returnQtyMap[row.id]"
                :min="0" :max="row.quantity - (row.returned_quantity || 0)"
                size="small" style="width:90px"
              />
            </template>
          </el-table-column>
        </el-table>

        <div style="margin-top:16px;display:flex;gap:10px;flex-wrap:wrap">
          <el-button v-if="currentOrder.status === 1" type="danger" @click="cancelOrder">取消订单</el-button>
          <el-button v-if="currentOrder.status >= 2 && currentOrder.status <= 5" type="warning" @click="refundOrder">退款（归还库存）</el-button>
          <el-button v-if="currentOrder.status >= 4 && currentOrder.status <= 5" type="danger" @click="returnOrder">确认退货（仅退款）</el-button>
        </div>

        <el-divider>操作记录</el-divider>
        <el-timeline>
          <el-timeline-item v-for="log in currentOrder.logs" :key="log.created_at" :timestamp="log.created_at">
            {{ log.status_text }} - {{ log.operator_name }}
            <div v-if="log.remark" style="color:#999;font-size:12px">{{ log.remark }}</div>
          </el-timeline-item>
        </el-timeline>
      </div>
      <template #footer>
        <el-button type="success" @click="printInvoice(currentOrder)">打印发票</el-button>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
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

    <!-- 打印发票弹窗 -->
    <el-dialog v-model="invoiceDialogVisible" title="订单发票" width="700px">
      <div id="invoice-content-dash" style="padding:30px;font-family:'Microsoft YaHei',sans-serif;color:#000;max-width:640px;margin:0 auto">
        <div style="text-align:center;margin-bottom:24px">
          <div style="font-size:24px;font-weight:bold;letter-spacing:4px">销售发票</div>
          <div style="font-size:12px;color:#999;margin-top:4px">SALES INVOICE</div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:10px;font-size:13px">
          <span><b>订单号：</b>{{ invoiceData.order_no }}</span>
          <span><b>开票日期：</b>{{ invoiceData.created_at }}</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:10px;font-size:13px">
          <span><b>客户名称：</b>{{ invoiceData.supermarket_name }}</span>
          <span><b>税号：</b>{{ invoiceData.tax_no || '-' }}</span>
        </div>
        <div style="margin-bottom:20px;font-size:13px">
          <b>地址：</b>{{ invoiceData.address || '-' }}
        </div>
        <div style="border-top:2px solid #000" />
        <table style="width:100%;border-collapse:collapse;font-size:13px">
          <thead>
            <tr style="background:#f5f7fa">
              <th style="border:1px solid #ddd;padding:8px;text-align:left">商品名称</th>
              <th style="border:1px solid #ddd;padding:8px;text-align:left;width:120px">条码</th>
              <th style="border:1px solid #ddd;padding:8px;text-align:center;width:60px">数量</th>
              <th style="border:1px solid #ddd;padding:8px;text-align:right;width:80px">单价</th>
              <th style="border:1px solid #ddd;padding:8px;text-align:right;width:80px">小计</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in invoiceData.items" :key="item.id">
              <td style="border:1px solid #ddd;padding:8px">{{ item.product_name }}</td>
              <td style="border:1px solid #ddd;padding:8px;color:#666">{{ item.product_barcode || '-' }}</td>
              <td style="border:1px solid #ddd;padding:8px;text-align:center">{{ item.quantity }}</td>
              <td style="border:1px solid #ddd;padding:8px;text-align:right">${{ item.unit_price }}</td>
              <td style="border:1px solid #ddd;padding:8px;text-align:right">${{ item.total_price }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr style="font-weight:bold;background:#f5f7fa">
              <td colspan="4" style="border:1px solid #ddd;padding:8px;text-align:right">合计</td>
              <td style="border:1px solid #ddd;padding:8px;text-align:right;font-size:15px">${{ invoiceData.total_amount }}</td>
            </tr>
          </tfoot>
        </table>
        <div style="border-top:2px solid #000;margin-bottom:20px" />
      </div>
      <template #footer>
        <el-button type="primary" @click="doPrint">🖨️ 打印</el-button>
        <el-button @click="invoiceDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../utils/request'

const stats = ref({ products: 0, supermarkets: 0, pending_orders: 0, low_stock: 0 })
const recentOrders = ref([])
const pendingOrders = ref([])
const lowStockProducts = ref([])
const newOrders = ref([])

const newOrderDialogVisible = ref(false)
const pendingOrderDialogVisible = ref(false)
const lowStockDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const statusDialogVisible = ref(false)
const invoiceDialogVisible = ref(false)

const currentOrder = ref(null)
const currentOrderId = ref(null)
const returnQtyMap = ref({})
const invoiceData = ref({})

const statusForm = ref({ status: 2, remark: '', tracking_number: '', logistics_company: '' })

let pollTimer = null

const statusType = (status) => {
  const map = { 1: 'warning', 2: 'info', 3: 'primary', 4: '', 5: 'success', 6: 'danger', 7: 'danger' }
  return map[status] || ''
}

const loadStats = async () => {
  stats.value = await request.get('/orders/stats/overview')
}

const loadRecentOrders = async () => {
  const pending = await request.get('/orders/', { params: { page: 1, page_size: 99999 } })
  const allPending = (pending.items || []).filter(o => o.status >= 1 && o.status <= 4)
  allPending.sort((a, b) => {
    if (a.status === 4 && b.status !== 4) return -1
    if (b.status === 4 && a.status !== 4) return 1
    return new Date(b.created_at) - new Date(a.created_at)
  })
  recentOrders.value = allPending.slice(0, 10)
  pendingOrders.value = allPending
}

const loadLowStock = async () => {
  const res = await request.get('/products/', { params: { filter_low_stock: true, page: 1, page_size: 99999 } })
  lowStockProducts.value = (res.items || []).filter(p => p.stock < 10)
}

const loadNewOrders = async () => {
  const res = await request.get('/orders/', { params: { status: 1, page: 1, page_size: 99999 } })
  const incoming = res.items || []
  if (incoming.length > newOrders.value.length) {
    ElMessage.warning('有新订单待确认！')
  }
  newOrders.value = incoming
}

const confirmOrder = async (row) => {
  await request.put(`/orders/${row.id}/status`, { status: 2, remark: '管理员已确认' })
  ElMessage.success('订单已确认')
  newOrders.value = newOrders.value.filter(o => o.id !== row.id)
  loadStats()
  loadRecentOrders()
}

const viewDetail = async (row) => {
  currentOrder.value = await request.get(`/orders/${row.id}`)
  returnQtyMap.value = {}
  currentOrder.value.items.forEach(item => { returnQtyMap.value[item.id] = 0 })
  detailDialogVisible.value = true
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
  loadStats()
  loadRecentOrders()
  loadNewOrders()
}

const removeOrderItem = async (row) => {
  try {
    await ElMessageBox.confirm(`确定从订单中删除"${row.product_name}"？`, '提示', { type: 'warning' })
  } catch { return }
  await request.delete(`/orders/${currentOrder.value.id}/items/${row.id}`)
  ElMessage.success('已删除，库存已归还')
  currentOrder.value = await request.get(`/orders/${currentOrder.value.id}`)
  loadRecentOrders()
}

const cancelOrder = async () => {
  try {
    await ElMessageBox.confirm('确定取消该订单？库存将归还。', '提示', { type: 'warning' })
  } catch { return }
  await request.post(`/orders/${currentOrder.value.id}/cancel`)
  ElMessage.success('订单已取消，库存已归还')
  detailDialogVisible.value = false
  loadStats()
  loadRecentOrders()
  loadNewOrders()
}

const refundOrder = async () => {
  try {
    await ElMessageBox.confirm('确定退款？库存将归还。', '提示', { type: 'warning' })
  } catch { return }
  await request.post(`/orders/${currentOrder.value.id}/refund`)
  ElMessage.success('退款成功，库存已归还')
  currentOrder.value = await request.get(`/orders/${currentOrder.value.id}`)
  loadStats()
  loadRecentOrders()
}

const returnOrder = async () => {
  const items = Object.entries(returnQtyMap.value)
    .filter(([, qty]) => qty > 0)
    .map(([id, qty]) => ({ item_id: parseInt(id), quantity: qty }))
  if (items.length === 0) { ElMessage.warning('请填写退货数量'); return }
  try {
    await ElMessageBox.confirm('确定退货？库存不归还，出库记录标记仅退款。', '提示', { type: 'warning' })
  } catch { return }
  await request.post(`/orders/${currentOrder.value.id}/return`, { items })
  ElMessage.success('退货登记成功')
  currentOrder.value = await request.get(`/orders/${currentOrder.value.id}`)
  returnQtyMap.value = {}
  currentOrder.value.items.forEach(item => { returnQtyMap.value[item.id] = 0 })
  loadRecentOrders()
}

const printInvoice = async (row) => {
  const order = row.items ? row : await request.get(`/orders/${row.id}`)
  invoiceData.value = { ...order, tax_no: '', address: '' }
  invoiceDialogVisible.value = true
}

const doPrint = () => {
  const content = document.getElementById('invoice-content-dash').innerHTML
  const win = window.open('', '_blank')
  win.document.write(`
    <html>
      <head>
        <title>订单发票</title>
        <style>
          body { font-family: 'Microsoft YaHei', sans-serif; padding: 30px; color: #000; }
          table { width: 100%; border-collapse: collapse; font-size: 13px; }
          th, td { border: 1px solid #ddd; padding: 8px; }
          @media print { body { padding: 0; } }
        </style>
      </head>
      <body>${content}</body>
    </html>
  `)
  win.document.close()
  win.focus()
  setTimeout(() => { win.print(); win.close() }, 300)
}

const startPolling = () => {
  pollTimer = setInterval(() => {
    loadNewOrders()
    loadStats()
  }, 15000)
}

onMounted(() => {
  loadStats()
  loadRecentOrders()
  loadLowStock()
  loadNewOrders()
  startPolling()
})

onUnmounted(() => {
  clearInterval(pollTimer)
})
</script>