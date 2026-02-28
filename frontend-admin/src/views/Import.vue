<template>
  <div>
    <el-card style="margin-bottom:20px">
      <template #header>
        <span>Excel 导入商品</span>
      </template>
      <el-alert type="info" :closable="false" style="margin-bottom:15px">
        上传Excel后选择每个字段对应的列（A、B、C...），数量为0或名称为空则导入失败，售价为空则进入待确认价格库。
      </el-alert>
      <el-upload
        :auto-upload="false"
        :on-change="handleFileChange"
        :show-file-list="true"
        accept=".xlsx,.xls"
        :limit="1"
      >
        <el-button type="primary">选择 Excel 文件</el-button>
      </el-upload>
      <el-button type="success" style="margin-top:15px" @click="openMapDialog" :disabled="!selectedFile">
        下一步：设置列映射
      </el-button>
    </el-card>

    <el-card style="margin-bottom:20px">
      <template #header><span>导入批次记录</span></template>
      <el-table :data="batches" stripe>
        <el-table-column prop="batch_name" label="文件名" />
        <el-table-column prop="total" label="总条数" width="80" />
        <el-table-column prop="success" label="成功" width="80">
          <template #default="{ row }">
            <el-tag type="success">{{ row.success }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="failed" label="失败" width="80">
          <template #default="{ row }">
            <el-tag type="danger">{{ row.failed }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pending_price" label="待确认价格" width="110">
          <template #default="{ row }">
            <el-tag type="warning">{{ row.pending_price }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="导入时间" width="160" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="viewFailed(row)">失败记录</el-button>
            <el-button size="small" type="warning" @click="rollback(row.id)">撤回</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card style="margin-bottom:20px">
      <template #header><span>待确认价格</span></template>
      <el-table :data="pendingPrices" stripe>
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="spec" label="规格" width="100" />
        <el-table-column prop="cost_price" label="进价" width="100" />
        <el-table-column label="售价" width="160">
          <template #default="{ row }">
            <el-input-number v-model="row.sell_price" :precision="2" :min="0" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="confirmPrice(row)">确认</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="mapDialogVisible" title="设置列映射" width="450px">
      <el-alert type="warning" :closable="false" style="margin-bottom:15px">
        商品名称、进价、数量为必填，其余选填。
      </el-alert>
      <el-form label-width="100px">
        <el-form-item v-for="field in fields" :key="field.key" :label="field.label + (field.required ? ' *' : '')">
          <el-select v-model="columnMap[field.key]" placeholder="选择列" clearable style="width:100%">
            <el-option v-for="col in columnOptions" :key="col.value" :label="col.label" :value="col.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="mapDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="uploadFile">开始导入</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="failedDialogVisible" title="导入失败记录" width="600px">
      <el-button type="danger" size="small" style="margin-bottom:10px" @click="clearFailed">清空失败记录</el-button>
      <el-table :data="failedRecords" stripe>
        <el-table-column prop="reason" label="失败原因" />
        <el-table-column prop="row_data" label="原始数据" show-overflow-tooltip />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../utils/request'
import axios from 'axios'

const batches = ref([])
const pendingPrices = ref([])
const failedRecords = ref([])
const failedDialogVisible = ref(false)
const mapDialogVisible = ref(false)
const uploading = ref(false)
const selectedFile = ref(null)
const currentBatchId = ref(null)

const columnMap = ref({
  name: null,
  cost_price: null,
  sell_price: null,
  stock: null,
  spec: null,
  barcode: null,
  remark: null
})

const fields = [
  { key: 'name', label: '商品名称', required: true },
  { key: 'cost_price', label: '进价', required: true },
  { key: 'stock', label: '数量/库存', required: true },
  { key: 'sell_price', label: '售价', required: false },
  { key: 'spec', label: '规格', required: false },
  { key: 'barcode', label: '条码', required: false },
  { key: 'remark', label: '备注', required: false },
]

const columnOptions = (() => {
  const cols = []
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  for (let i = 0; i < 26; i++) {
    cols.push({ label: letters[i], value: i })
  }
  for (let j = 0; j < 26; j++) {
    cols.push({ label: 'A' + letters[j], value: 26 + j })
  }
  for (let j = 0; j < 26; j++) {
    cols.push({ label: 'B' + letters[j], value: 52 + j })
  }
  return cols
})()

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const openMapDialog = () => {
  columnMap.value = { name: null, cost_price: null, sell_price: null, stock: null, spec: null, barcode: null, remark: null }
  mapDialogVisible.value = true
}

const uploadFile = async () => {
  if (columnMap.value.name === null) {
    ElMessage.warning('请选择商品名称对应的列')
    return
  }
  if (columnMap.value.cost_price === null) {
    ElMessage.warning('请选择进价对应的列')
    return
  }
  if (columnMap.value.stock === null) {
    ElMessage.warning('请选择数量对应的列')
    return
  }
  uploading.value = true
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('column_map', JSON.stringify(columnMap.value))
  try {
    const token = localStorage.getItem('token')
    const res = await axios.post('http://127.0.0.1:8000/api/imports/upload', formData, {
      headers: { Authorization: `Bearer ${token}` }
    })
    ElMessage.success(res.data.message)
    mapDialogVisible.value = false
    loadBatches()
    loadPendingPrices()
  } catch (e) {
    ElMessage.error('导入失败，请检查文件格式')
  } finally {
    uploading.value = false
  }
}

const loadBatches = async () => {
  batches.value = await request.get('/imports/batches')
}

const loadPendingPrices = async () => {
  pendingPrices.value = await request.get('/imports/pending-price')
}

const viewFailed = async (row) => {
  currentBatchId.value = row.id
  failedRecords.value = await request.get(`/imports/failed/${row.id}`)
  failedDialogVisible.value = true
}

const clearFailed = async () => {
  await ElMessageBox.confirm('确定清空该批次的失败记录？', '提示', { type: 'warning' })
  await request.delete(`/imports/failed/${currentBatchId.value}`)
  ElMessage.success('已清空')
  failedDialogVisible.value = false
  loadBatches()
}

const rollback = async (batchId) => {
  await ElMessageBox.confirm('确定撤回该批次？将删除该批次导入的所有商品！', '警告', { type: 'error' })
  await request.delete(`/imports/batches/${batchId}`)
  ElMessage.success('已撤回')
  loadBatches()
  loadPendingPrices()
}

const confirmPrice = async (row) => {
  if (!row.sell_price) {
    ElMessage.warning('请输入售价')
    return
  }
  await request.put(`/imports/pending-price/${row.id}`, { sell_price: row.sell_price })
  ElMessage.success('价格已确认')
  loadPendingPrices()
}

onMounted(() => {
  loadBatches()
  loadPendingPrices()
})
</script>