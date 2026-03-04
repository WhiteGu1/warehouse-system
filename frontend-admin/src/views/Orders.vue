<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>订单管理</span>
          <div style="display:flex;gap:8px">
            <el-button @click="exportOrders">导出Excel</el-button>
            <el-button type="primary" @click="openAdd">新建订单</el-button>
          </div>
        </div>
      </template>

      <el-select v-model="filterStatus" placeholder="筛选状态" clearable style="margin-bottom:15px" @change="loadOrders">
        <el-option label="待确认" :value="1" />
        <el-option label="已确认待配货" :value="2" />
        <el-option label="已配货待发货" :value="3" />
        <el-option label="已发货待付款" :value="4" />
        <el-option label="已付款完成" :value="5" />
        <el-option label="已取消" :value="6" />
        <el-option label="已退款" :value="7" />
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
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
            <el-button size="small" type="success" @click="printInvoice(row)">打印</el-button>
            <el-button size="small" type="primary" @click="openUpdateStatus(row)" v-if="row.status >= 1 && row.status <= 4">更新状态</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建订单弹窗 -->
    <el-dialog v-model="addDialogVisible" title="新建订单" width="700px">
      <el-form :model="orderForm" label-width="90px">
        <el-form-item label="选择客户">
          <el-select v-model="orderForm.supermarket_id" placeholder="请选择客户" style="width:100%" @change="onCustomerChange">
            <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id">
              <span>{{ c.name }}</span>
              <el-tag v-if="c.discount < 1" type="warning" size="small" style="margin-left:8px">
                -{{ ((1 - c.discount) * 100).toFixed(0) }}%
              </el-tag>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="折扣" v-if="currentDiscount < 1">
          <el-tag type="warning">该客户享有 -{{ ((1 - currentDiscount) * 100).toFixed(0) }}% 优惠，将在总价中体现</el-tag>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="orderForm.remark" type="textarea" />
        </el-form-item>
        <el-divider>商品明细</el-divider>
        <div v-for="(item, index) in orderForm.items" :key="index" style="display:flex;gap:10px;margin-bottom:10px;align-items:center">
          <el-select v-model="item.product_id" placeholder="选择商品" filterable style="flex:2" @change="fillPrice(item)">
            <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
          <el-input-number v-model="item.quantity" :min="1" style="width:100px" />
          <el-input-number v-model="item.unit_price" :precision="2" :min="0" style="width:120px" />
          <el-button type="danger" circle @click="removeItem(index)"><el-icon><Delete /></el-icon></el-button>
        </div>
        <el-button @click="addItem" style="width:100%">+ 添加商品</el-button>
        <div style="text-align:right;margin-top:12px">
          <span style="color:#999;font-size:13px">原价合计：${{ originalTotal }}</span>
          <template v-if="currentDiscount < 1">
            <span style="margin:0 10px;color:#e6a23c;font-size:13px">折扣：-{{ ((1 - currentDiscount) * 100).toFixed(0) }}%</span>
            <span style="font-weight:bold;font-size:16px;color:#f56c6c">折后合计：${{ totalAmount }}</span>
          </template>
          <template v-else>
            <span style="font-weight:bold;font-size:16px;margin-left:12px">合计：${{ totalAmount }}</span>
          </template>
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
    <el-dialog v-model="detailDialogVisible" title="订单详情" width="700px">
      <div v-if="currentOrder">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ currentOrder.order_no }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ currentOrder.supermarket_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusType(currentOrder.status)">{{ currentOrder.status_text }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总金额">
            <span>${{ currentOrder.total_amount }}</span>
            <el-tooltip v-if="getCustomerDiscount(currentOrder) < 1" placement="top">
              <template #content>客户折扣：-{{ ((1 - getCustomerDiscount(currentOrder)) * 100).toFixed(0) }}%</template>
              <el-tag type="warning" size="small" style="margin-left:8px;cursor:pointer">
                -{{ ((1 - getCustomerDiscount(currentOrder)) * 100).toFixed(0) }}%
              </el-tag>
            </el-tooltip>
          </el-descriptions-item>
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
          <!-- 待确认时：删除单个商品 -->
          <el-table-column v-if="currentOrder.status === 1" label="操作" width="75">
            <template #default="{ row }">
              <el-button size="small" type="danger" @click="removeOrderItem(row)">删除</el-button>
            </template>
          </el-table-column>
          <!-- 已发货后：选择退货数量 -->
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

        <!-- 操作按钮区 -->
        <div style="margin-top:16px;display:flex;gap:10px;flex-wrap:wrap">
          <!-- 待确认：取消整单 -->
          <el-button v-if="currentOrder.status === 1" type="danger" @click="cancelOrder">
            取消订单
          </el-button>
          <!-- 已确认及以后：退款并归还库存 -->
          <el-button v-if="currentOrder.status >= 2 && currentOrder.status <= 5" type="warning" @click="refundOrder">
            退款（归还库存）
          </el-button>
          <!-- 已发货后：退货（仅退款，库存不归还） -->
          <el-button v-if="currentOrder.status >= 4 && currentOrder.status <= 5" type="danger" @click="returnOrder">
            确认退货（仅退款）
          </el-button>
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

    <!-- 打印发票弹窗 -->
    <el-dialog v-model="invoiceDialogVisible" title="订单发票" width="700px">
      <div id="invoice-content" style="padding:30px;font-family:'Microsoft YaHei',sans-serif;color:#000;max-width:640px;margin:0 auto">
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
            <tr v-if="invoiceData.discount && invoiceData.discount < 1">
              <td colspan="4" style="border:1px solid #ddd;padding:8px;text-align:right;color:#999">原价合计</td>
              <td style="border:1px solid #ddd;padding:8px;text-align:right;color:#999">${{ invoiceData.original_total }}</td>
            </tr>
            <tr v-if="invoiceData.discount && invoiceData.discount < 1">
              <td colspan="4" style="border:1px solid #ddd;padding:8px;text-align:right;color:#e6a23c">折扣</td>
              <td style="border:1px solid #ddd;padding:8px;text-align:right;color:#e6a23c">
                -{{ ((1 - invoiceData.discount) * 100).toFixed(0) }}%
              </td>
            </tr>
            <tr style="font-weight:bold;background:#f5f7fa">
              <td colspan="4" style="border:1px solid #ddd;padding:8px;text-align:right">
                {{ invoiceData.discount && invoiceData.discount < 1 ? '折后合计' : '合计' }}
              </td>
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import request from '../utils/request'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

const orders = ref([])
const customers = ref([])
const products = ref([])
const filterStatus = ref(null)
const addDialogVisible = ref(false)
const statusDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const invoiceDialogVisible = ref(false)
const currentOrder = ref(null)
const currentOrderId = ref(null)
const currentDiscount = ref(1.0)
const invoiceData = ref({})
const returnQtyMap = ref({})

const orderForm = ref({
  supermarket_id: null, remark: '',
  items: [{ product_id: null, quantity: 1, unit_price: 0 }]
})

const statusForm = ref({
  status: 2, remark: '', tracking_number: '', logistics_company: ''
})

const originalTotal = computed(() => {
  return orderForm.value.items.reduce((sum, item) => {
    return sum + (item.quantity || 0) * (item.unit_price || 0)
  }, 0).toFixed(2)
})

const totalAmount = computed(() => {
  return (parseFloat(originalTotal.value) * currentDiscount.value).toFixed(2)
})

const statusType = (status) => {
  const map = { 1: 'warning', 2: 'info', 3: 'primary', 4: '', 5: 'success', 6: 'danger', 7: 'danger' }
  return map[status] || ''
}

const getCustomerDiscount = (order) => {
  if (!order) return 1.0
  const customer = customers.value.find(c => c.name === order.supermarket_name)
  return customer ? (customer.discount ?? 1.0) : 1.0
}

const loadOrders = async () => {
  const params = {}
  if (filterStatus.value) params.status = filterStatus.value
  orders.value = await request.get('/orders/', { params })
}

const loadCustomers = async () => { customers.value = await request.get('/customers/') }
const loadProducts = async () => { products.value = await request.get('/products/') }

const onCustomerChange = (id) => {
  const c = customers.value.find(x => x.id === id)
  currentDiscount.value = c ? (c.discount ?? 1.0) : 1.0
}

const fillPrice = (item) => {
  const p = products.value.find(x => x.id === item.product_id)
  if (p) item.unit_price = +(p.sell_price || 0)
}

const exportOrders = () => {
  const data = orders.value.map(o => ({
    '订单号': o.order_no, '客户': o.supermarket_name || '',
    '金额': o.total_amount, '状态': o.status_text,
    '物流公司': o.logistics_company || '', '物流单号': o.tracking_number || '',
    '备注': o.remark || '', '下单时间': o.created_at
  }))
  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '订单列表')
  const buf = XLSX.write(wb, { type: 'array', bookType: 'xlsx' })
  saveAs(new Blob([buf], { type: 'application/octet-stream' }), `订单列表_${new Date().toLocaleDateString()}.xlsx`)
}

const openAdd = () => {
  currentDiscount.value = 1.0
  orderForm.value = { supermarket_id: null, remark: '', items: [{ product_id: null, quantity: 1, unit_price: 0 }] }
  addDialogVisible.value = true
}

const addItem = () => { orderForm.value.items.push({ product_id: null, quantity: 1, unit_price: 0 }) }
const removeItem = (index) => { orderForm.value.items.splice(index, 1) }

const saveOrder = async () => {
  if (!orderForm.value.supermarket_id) { ElMessage.warning('请选择客户'); return }
  if (orderForm.value.items.some(i => !i.product_id)) { ElMessage.warning('请选择商品'); return }
  const payload = {
    ...orderForm.value,
    discount: currentDiscount.value,
    total_amount_override: parseFloat(totalAmount.value)
  }
  await request.post('/orders/', payload)
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
  returnQtyMap.value = {}
  currentOrder.value.items.forEach(item => { returnQtyMap.value[item.id] = 0 })
  detailDialogVisible.value = true
}

const removeOrderItem = async (row) => {
  await ElMessageBox.confirm(`确定从订单中删除"${row.product_name}"？`, '提示', { type: 'warning' })
  await request.delete(`/orders/${currentOrder.value.id}/items/${row.id}`)
  ElMessage.success('已删除，库存已归还')
  currentOrder.value = await request.get(`/orders/${currentOrder.value.id}`)
  loadOrders()
}

const cancelOrder = async () => {
  await ElMessageBox.confirm('确定取消该订单？库存将归还。', '提示', { type: 'warning' })
  await request.post(`/orders/${currentOrder.value.id}/cancel`)
  ElMessage.success('订单已取消，库存已归还')
  detailDialogVisible.value = false
  loadOrders()
}

const refundOrder = async () => {
  await ElMessageBox.confirm('确定退款？库存将归还。', '提示', { type: 'warning' })
  await request.post(`/orders/${currentOrder.value.id}/refund`)
  ElMessage.success('退款成功，库存已归还')
  currentOrder.value = await request.get(`/orders/${currentOrder.value.id}`)
  loadOrders()
}

const returnOrder = async () => {
  const items = Object.entries(returnQtyMap.value)
    .filter(([, qty]) => qty > 0)
    .map(([id, qty]) => ({ item_id: parseInt(id), quantity: qty }))
  if (items.length === 0) { ElMessage.warning('请填写退货数量'); return }
  await ElMessageBox.confirm('确定退货？库存不归还，出库记录标记仅退款。', '提示', { type: 'warning' })
  await request.post(`/orders/${currentOrder.value.id}/return`, { items })
  ElMessage.success('退货登记成功')
  currentOrder.value = await request.get(`/orders/${currentOrder.value.id}`)
  returnQtyMap.value = {}
  currentOrder.value.items.forEach(item => { returnQtyMap.value[item.id] = 0 })
  loadOrders()
}

const printInvoice = async (row) => {
  const order = row.items ? row : await request.get(`/orders/${row.id}`)
  const customer = customers.value.find(c => c.name === order.supermarket_name) || {}
  const discount = customer.discount ?? 1.0
  const originalTotal = order.items
    ? order.items.reduce((s, i) => s + (i.unit_price || 0) * (i.quantity || 0), 0).toFixed(2)
    : order.total_amount
  invoiceData.value = {
    ...order,
    tax_no: customer.tax_no || '',
    address: customer.address || '',
    discount,
    original_total: originalTotal,
  }
  invoiceDialogVisible.value = true
}

const doPrint = () => {
  const content = document.getElementById('invoice-content').innerHTML
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

onMounted(() => {
  loadOrders()
  loadCustomers()
  loadProducts()
})
</script>