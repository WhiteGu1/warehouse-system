<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>订单管理</span>
          <div style="display:flex;gap:8px">
            <el-button @click="openExportDialog">导出Excel</el-button>
            <el-button type="primary" @click="openAdd">新建订单</el-button>
          </div>
        </div>
      </template>

<!-- 筛选栏 -->
<div style="display:flex;gap:8px;margin-bottom:15px;flex-wrap:wrap">
  <el-select v-model="filterStatus" placeholder="筛选状态" clearable style="flex:1;min-width:130px" @change="loadOrders">
    <el-option label="待确认" :value="1" />
    <el-option label="已确认待配货" :value="2" />
    <el-option label="已配货待发货" :value="3" />
    <el-option label="已发货待付款" :value="4" />
    <el-option label="已付款完成" :value="5" />
    <el-option label="已取消" :value="6" />
    <el-option label="已退款" :value="7" />
  </el-select>
  <el-select v-model="filterCustomer" placeholder="筛选客户" clearable style="flex:1;min-width:130px" @change="loadOrders">
    <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
  </el-select>
  <el-date-picker
    v-model="filterDateRange"
    type="daterange"
    range-separator="至"
    start-placeholder="开始日期"
    end-placeholder="结束日期"
    style="flex:1;min-width:220px"
    @change="loadOrders"
  />
</div>

<!-- PC端表格 -->
<el-table :data="orders" stripe v-loading="loading" style="width:100%" class="desktop-table">
  <el-table-column prop="order_no" label="订单号" min-width="165" />
  <el-table-column prop="supermarket_name" label="客户" min-width="100" />
  <el-table-column label="金额" min-width="110">
    <template #default="{ row }">
      <span style="color:#409eff;font-weight:bold;white-space:nowrap">${{ row.total_amount }}</span>
    </template>
  </el-table-column>
  <el-table-column label="状态" min-width="120">
    <template #default="{ row }">
      <el-tag :type="statusType(row.status)" style="white-space:nowrap">{{ row.status_text }}</el-tag>
    </template>
  </el-table-column>
  <el-table-column prop="tracking_number" label="物流单号" min-width="120" show-overflow-tooltip />
  <el-table-column prop="created_at" label="下单时间" min-width="155" />
  <el-table-column label="操作" min-width="240" fixed="right">
    <template #default="{ row }">
      <div style="display:flex;gap:4px;align-items:center">
        <el-button size="small" @click="viewDetail(row)">详情</el-button>
        <el-button size="small" type="success" @click="printInvoice(row)">打印</el-button>
        <el-button size="small" type="primary" @click="openUpdateStatus(row)" v-if="row.status >= 1 && row.status <= 4">更新状态</el-button>
      </div>
    </template>
  </el-table-column>
</el-table>

<!-- 手机端卡片列表 -->
<div class="mobile-list" v-loading="loading">
  <div
    v-for="row in orders" :key="row.id"
    style="border:1px solid #e4e7ed;border-radius:8px;padding:12px;margin-bottom:10px;background:#fff;cursor:pointer"
    @click="viewDetail(row)"
  >
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
      <div style="font-size:13px;color:#666;flex:1;margin-right:8px;word-break:break-all">{{ row.order_no }}</div>
      <el-tag :type="statusType(row.status)" size="small" style="flex-shrink:0">{{ row.status_text }}</el-tag>
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
      <span style="font-size:14px;font-weight:bold">{{ row.supermarket_name }}</span>
      <span style="color:#409eff;font-weight:bold;font-size:16px">${{ row.total_amount }}</span>
    </div>
    <div style="font-size:12px;color:#888;margin-bottom:8px">{{ row.created_at }}</div>
    <div v-if="row.tracking_number" style="font-size:12px;color:#666;margin-bottom:8px">物流：{{ row.tracking_number }}</div>
    <div style="display:flex;gap:6px" @click.stop>
      <el-button size="small" type="success" @click="printInvoice(row)">打印</el-button>
      <el-button size="small" type="primary" @click="openUpdateStatus(row)" v-if="row.status >= 1 && row.status <= 4">更新状态</el-button>
    </div>
  </div>
  <div v-if="orders.length === 0 && !loading" style="text-align:center;color:#aaa;padding:40px 0">暂无订单</div>
</div>

<div style="margin-top:12px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
  <el-pagination
    v-model:current-page="currentPage"
    :page-size="pageSize"
    :total="total"
    layout="prev, pager, next"
    background
    @current-change="fetchOrders"
    class="mobile-pagination"
  />
  <el-pagination
    v-model:current-page="currentPage"
    :page-size="pageSize"
    :total="total"
    layout="total, prev, pager, next, jumper"
    background
    @current-change="fetchOrders"
    class="desktop-pagination"
  />
  <div style="font-size:13px;color:#888">
    共 <b>{{ summaryCount }}</b> 笔订单，合计
    <span style="color:#409eff;font-weight:bold;font-size:15px">${{ summaryTotal.toFixed(2) }}</span>
  </div>
</div>


    </el-card>

    <!-- 导出弹窗 -->
    <el-dialog v-model="exportDialogVisible" title="导出订单Excel" width="420px">
      <el-form label-width="80px">
        <el-form-item label="客户">
          <el-select v-model="exportForm.customer_id" placeholder="全部客户" clearable style="width:100%">
            <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="exportForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width:100%"
          />
        </el-form-item>
        <el-form-item label="订单状态">
          <el-select v-model="exportForm.status" placeholder="全部状态" clearable style="width:100%">
            <el-option label="待确认" :value="1" />
            <el-option label="已确认待配货" :value="2" />
            <el-option label="已配货待发货" :value="3" />
            <el-option label="已发货待付款" :value="4" />
            <el-option label="已付款完成" :value="5" />
            <el-option label="已取消" :value="6" />
            <el-option label="已退款" :value="7" />
          </el-select>
        </el-form-item>
        <el-form-item label="导出内容">
          <el-checkbox-group v-model="exportForm.includes">
            <el-checkbox value="summary">订单汇总</el-checkbox>
            <el-checkbox value="items">商品明细</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="exporting" @click="doExport">导出</el-button>
      </template>
    </el-dialog>

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
const filterCustomer = ref(null)
const filterDateRange = ref(null)
const addDialogVisible = ref(false)
const statusDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const invoiceDialogVisible = ref(false)
const exportDialogVisible = ref(false)
const exporting = ref(false)
const currentOrder = ref(null)
const currentOrderId = ref(null)
const currentDiscount = ref(1.0)
const invoiceData = ref({})
const returnQtyMap = ref({})
const total = ref(0)
const currentPage = ref(1)
const pageSize = 50
const loading = ref(false)
const summaryTotal = ref(0)
const summaryCount = ref(0)

const exportForm = ref({
  customer_id: null, dateRange: null, status: null, includes: ['summary', 'items']
})

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

const statusText = (status) => {
  const map = { 1: '待确认', 2: '已确认待配货', 3: '已配货待发货', 4: '已发货待付款', 5: '已付款完成', 6: '已取消', 7: '已退款' }
  return map[status] || ''
}

const getCustomerDiscount = (order) => {
  if (!order) return 1.0
  const customer = customers.value.find(c => c.name === order.supermarket_name)
  return customer ? (customer.discount ?? 1.0) : 1.0
}

const buildFilterParams = () => {
  const params = {}
  if (filterStatus.value) params.status = filterStatus.value
  if (filterCustomer.value) params.supermarket_id = filterCustomer.value
  if (filterDateRange.value?.[0]) {
    params.date_from = filterDateRange.value[0].toISOString().split('T')[0]
    params.date_to = filterDateRange.value[1].toISOString().split('T')[0]
  }
  return params
}

const loadOrders = async () => {
  currentPage.value = 1
  await fetchOrders()
}

const fetchOrders = async () => {
  loading.value = true
  try {
    const filterParams = buildFilterParams()
    const [res, summary] = await Promise.all([
      request.get('/orders/', { params: { ...filterParams, page: currentPage.value, page_size: pageSize } }),
      request.get('/orders/summary', { params: filterParams })
    ])
    orders.value = res.items
    total.value = res.total
    summaryCount.value = summary.count
    summaryTotal.value = summary.total
  } finally {
    loading.value = false
  }
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

const openExportDialog = () => {
  exportForm.value = { customer_id: null, dateRange: null, status: null, includes: ['summary', 'items'] }
  exportDialogVisible.value = true
}

const doExport = async () => {
  exporting.value = true
  try {
    const params = {}
    if (exportForm.value.customer_id) params.supermarket_id = exportForm.value.customer_id
    if (exportForm.value.status) params.status = exportForm.value.status
    if (exportForm.value.dateRange?.[0]) {
      params.date_from = exportForm.value.dateRange[0].toISOString().split('T')[0]
      params.date_to = exportForm.value.dateRange[1].toISOString().split('T')[0]
    }
    const res = await request.get('/orders/', { params: { ...params, page: 1, page_size: 99999 } })
    const exportOrders = res.items

    const wb = XLSX.utils.book_new()

    if (exportForm.value.includes.includes('summary')) {
      const summaryData = exportOrders.map(o => ({
        '订单号': o.order_no, '客户': o.supermarket_name || '', '金额': o.total_amount,
        '状态': o.status_text || statusText(o.status), '物流公司': o.logistics_company || '',
        '物流单号': o.tracking_number || '', '备注': o.remark || '', '下单时间': o.created_at
      }))
      const totalAmt = exportOrders.reduce((s, o) => s + parseFloat(o.total_amount || 0), 0).toFixed(2)
      summaryData.push({ '订单号': '合计', '客户': '', '金额': totalAmt, '状态': '', '物流公司': '', '物流单号': '', '备注': '', '下单时间': '' })
      const ws1 = XLSX.utils.json_to_sheet(summaryData)
      ws1['!cols'] = [{ wch: 20 }, { wch: 16 }, { wch: 10 }, { wch: 14 }, { wch: 14 }, { wch: 16 }, { wch: 20 }, { wch: 18 }]
      XLSX.utils.book_append_sheet(wb, ws1, '订单汇总')
    }

    if (exportForm.value.includes.includes('items')) {
      const itemRows = []
      for (const o of exportOrders) {
        const detail = await request.get(`/orders/${o.id}`)
        if (detail.items) {
          for (const item of detail.items) {
            itemRows.push({
              '订单号': o.order_no, '客户': o.supermarket_name || '', '下单时间': o.created_at,
              '订单状态': o.status_text || statusText(o.status), '商品名称': item.product_name,
              '条码': item.product_barcode || '', '数量': item.quantity, '单价': item.unit_price,
              '小计': item.total_price, '已退数量': item.returned_quantity || 0
            })
          }
        }
      }
      const ws2 = XLSX.utils.json_to_sheet(itemRows)
      ws2['!cols'] = [{ wch: 20 }, { wch: 16 }, { wch: 18 }, { wch: 14 }, { wch: 20 }, { wch: 14 }, { wch: 8 }, { wch: 10 }, { wch: 10 }, { wch: 10 }]
      XLSX.utils.book_append_sheet(wb, ws2, '商品明细')
    }

    const buf = XLSX.write(wb, { type: 'array', bookType: 'xlsx' })
    saveAs(new Blob([buf], { type: 'application/octet-stream' }), `订单导出_${new Date().toLocaleDateString().replace(/\//g, '-')}.xlsx`)
    ElMessage.success('导出成功')
    exportDialogVisible.value = false
  } catch (e) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
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
  await request.post('/orders/', { ...orderForm.value, discount: currentDiscount.value, total_amount_override: parseFloat(totalAmount.value) })
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
  try {
    await ElMessageBox.confirm(`确定从订单中删除"${row.product_name}"？`, '提示', { type: 'warning' })
  } catch { return }
  await request.delete(`/orders/${currentOrder.value.id}/items/${row.id}`)
  ElMessage.success('已删除，库存已归还')
  currentOrder.value = await request.get(`/orders/${currentOrder.value.id}`)
  loadOrders()
}

const cancelOrder = async () => {
  try {
    await ElMessageBox.confirm('确定取消该订单？库存将归还。', '提示', { type: 'warning' })
  } catch { return }
  await request.post(`/orders/${currentOrder.value.id}/cancel`)
  ElMessage.success('订单已取消，库存已归还')
  detailDialogVisible.value = false
  loadOrders()
}

const refundOrder = async () => {
  try {
    await ElMessageBox.confirm('确定退款？库存将归还。', '提示', { type: 'warning' })
  } catch { return }
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
  try {
    await ElMessageBox.confirm('确定退货？库存不归还，出库记录标记仅退款。', '提示', { type: 'warning' })
  } catch { return }
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
  invoiceData.value = { ...order, tax_no: customer.tax_no || '', address: customer.address || '', discount, original_total: originalTotal }
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