<template>
  <div>
    <el-card style="margin-bottom:20px">
      <template #header><span>Excel 导入商品</span></template>
      <el-alert type="info" :closable="false" style="margin-bottom:15px">
        上传Excel后选择每个字段对应的列（A、B、C...），数量为0或名称为空则导入失败，售价为空则进入待确认价格库。嵌入图片将自动按4:3居中裁剪导入。
      </el-alert>
      <el-upload :auto-upload="false" :on-change="handleFileChange" :show-file-list="true" accept=".xlsx,.xls" :limit="1">
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
          <template #default="{ row }"><el-tag type="success">{{ row.success }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="failed" label="失败" width="80">
          <template #default="{ row }"><el-tag type="danger">{{ row.failed }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="pending_price" label="待确认价格" width="110">
          <template #default="{ row }"><el-tag type="warning">{{ row.pending_price }}</el-tag></template>
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

    <!-- 待确认价格 -->
    <el-card style="margin-bottom:20px">
      <template #header><span>待确认价格</span></template>
      <el-table :data="pendingPrices" stripe>
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="spec" label="规格" width="100" />
        <el-table-column prop="cost_price" label="进价" width="90" />
        <el-table-column label="售价 / 利润率" width="320">
          <template #default="{ row }">
            <div style="display:flex;gap:6px;align-items:center">
              <el-input-number v-model="row.sell_price" :precision="2" :min="0" size="small" style="width:120px" />
              <span style="color:#999;font-size:12px;white-space:nowrap">利润率</span>
              <el-input-number
                v-model="row._margin"
                :precision="0" :min="0" :max="999" :step="5" size="small" style="width:120px"
                @change="val => { if(row.cost_price) row.sell_price = +(row.cost_price * (1 + (val||0) / 100)).toFixed(2) }"
              />
              <span style="color:#999;font-size:12px">%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="confirmPrice(row)">确认</el-button>
            <el-button size="small" type="danger" @click="deletePending(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 列映射弹窗 -->
    <el-dialog v-model="mapDialogVisible" title="设置列映射" width="480px">
      <el-alert type="warning" :closable="false" style="margin-bottom:15px">
        商品名称、进价、数量为必填，其余选填。
      </el-alert>
      <el-form label-width="110px">
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

    <!-- 失败记录弹窗 -->
    <el-dialog v-model="failedDialogVisible" title="导入失败记录" width="800px">
      <div style="margin-bottom:10px">
        <el-button type="danger" size="small" @click="clearFailed">清空失败记录</el-button>
      </div>
      <el-table :data="failedRecords" stripe>
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="reason" label="失败原因" width="260" />
        <el-table-column label="原始数据" show-overflow-tooltip>
          <template #default="{ row }">{{ row.row_data }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="openFixDialog(row)">修正</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 修正并入库弹窗 -->
    <el-dialog v-model="fixDialogVisible" title="修正并入库" width="540px">
      <el-alert type="info" :closable="false" style="margin-bottom:15px">
        修正数据后点击确认入库，将直接添加该商品。
      </el-alert>
      <el-form :model="fixForm" label-width="90px">
        <el-form-item label="商品名称"><el-input v-model="fixForm.name" /></el-form-item>
        <el-form-item label="条码"><el-input v-model="fixForm.barcode" /></el-form-item>
        <el-form-item label="规格"><el-input v-model="fixForm.spec" /></el-form-item>
        <el-form-item label="进价"><el-input-number v-model="fixForm.cost_price" :precision="2" :min="0" @change="recalcFix" /></el-form-item>
        <el-form-item label="售价">
          <div style="display:flex;gap:8px;align-items:center">
            <el-input-number v-model="fixForm.sell_price" :precision="2" :min="0" style="width:130px" />
            <span style="color:#999;font-size:12px">利润率</span>
            <el-input-number
              v-model="fixForm._margin"
              :precision="0" :min="0" :max="999" :step="5" style="width:130px"
              @change="val => { if(fixForm.cost_price) fixForm.sell_price = +(fixForm.cost_price * (1 + (val||0) / 100)).toFixed(2) }"
            />
            <span style="color:#999;font-size:12px">%</span>
          </div>
        </el-form-item>
        <el-form-item label="数量"><el-input-number v-model="fixForm.stock" :min="1" /></el-form-item>
        <el-form-item label="每包数量"><el-input-number v-model="fixForm.middle_pack" :min="1" /></el-form-item>
        <el-form-item label="每件数量"><el-input-number v-model="fixForm.piece" :min="0" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="fixForm.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="fixDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitFix">确认入库</el-button>
      </template>
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
const fixDialogVisible = ref(false)
const uploading = ref(false)
const selectedFile = ref(null)
const currentBatchId = ref(null)
const currentFailedId = ref(null)

const fixForm = ref({
  name: '', barcode: '', spec: '', cost_price: 0,
  sell_price: 0, stock: 1, middle_pack: 1, piece: null, remark: '', _margin: null
})

const columnMap = ref({
  name: null, cost_price: null, sell_price: null, stock: null,
  spec: null, barcode: null, remark: null, middle_pack: null, piece: null, image_col: null
})

const fields = [
  { key: 'name', label: '商品名称', required: true },
  { key: 'cost_price', label: '进价', required: true },
  { key: 'stock', label: '数量/库存', required: true },
  { key: 'sell_price', label: '售价', required: false },
  { key: 'spec', label: '规格', required: false },
  { key: 'barcode', label: '条码', required: false },
  { key: 'middle_pack', label: '每包数量', required: false },
  { key: 'piece', label: '每件数量', required: false },
  { key: 'remark', label: '备注', required: false },
  { key: 'image_col', label: '图片列', required: false },
]

const columnOptions = (() => {
  const cols = []
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  for (let i = 0; i < 26; i++) cols.push({ label: letters[i], value: i })
  for (let j = 0; j < 26; j++) cols.push({ label: 'A' + letters[j], value: 26 + j })
  for (let j = 0; j < 26; j++) cols.push({ label: 'B' + letters[j], value: 52 + j })
  return cols
})()

const recalcFix = (val) => {
  if (fixForm.value._margin && val) {
    fixForm.value.sell_price = +(val * (1 + fixForm.value._margin / 100)).toFixed(2)
  }
}

const handleFileChange = (file) => { selectedFile.value = file.raw }

const openMapDialog = () => {
  columnMap.value = {
    name: null, cost_price: null, sell_price: null, stock: null,
    spec: null, barcode: null, remark: null, middle_pack: null, piece: null, image_col: null
  }
  mapDialogVisible.value = true
}

const uploadFile = async () => {
  if (columnMap.value.name === null) { ElMessage.warning('请选择商品名称对应的列'); return }
  if (columnMap.value.cost_price === null) { ElMessage.warning('请选择进价对应的列'); return }
  if (columnMap.value.stock === null) { ElMessage.warning('请选择数量对应的列'); return }
  uploading.value = true
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('column_map', JSON.stringify(columnMap.value))
  try {
    const token = localStorage.getItem('token')
    const res = await axios.post('http://127.0.0.1:8000/api/imports/upload', formData, {
      headers: { Authorization: `Bearer ${token}` },
      timeout: 120000
    })
    ElMessage.success(res.data.message)
    mapDialogVisible.value = false
    loadBatches()
    loadPendingPrices()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '导入失败，请检查文件格式')
  } finally {
    uploading.value = false
  }
}

const loadBatches = async () => { batches.value = await request.get('/imports/batches') }
const loadPendingPrices = async () => { pendingPrices.value = await request.get('/imports/pending-price') }

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

const openFixDialog = (row) => {
  currentFailedId.value = row.id
  fixForm.value = {
    name: '', barcode: '', spec: '', cost_price: 0,
    sell_price: 0, stock: 1, middle_pack: 1, piece: null, remark: '', _margin: null
  }
  fixDialogVisible.value = true
}

const submitFix = async () => {
  if (!fixForm.value.name) { ElMessage.warning('请输入商品名称'); return }
  if (!fixForm.value.stock || fixForm.value.stock < 1) { ElMessage.warning('请输入数量'); return }
  const payload = { ...fixForm.value }
  delete payload._margin
  await request.post('/products/', payload)
  await request.delete(`/imports/failed-single/${currentFailedId.value}`)
  ElMessage.success('入库成功')
  fixDialogVisible.value = false
  failedRecords.value = failedRecords.value.filter(r => r.id !== currentFailedId.value)
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
  if (!row.sell_price) { ElMessage.warning('请输入售价'); return }
  await request.put(`/imports/pending-price/${row.id}`, { sell_price: row.sell_price })
  ElMessage.success('价格已确认')
  loadPendingPrices()
}

const deletePending = async (row) => {
  await ElMessageBox.confirm('确定删除该待确认记录？', '提示', { type: 'warning' })
  await request.delete(`/imports/pending-price/${row.id}`)
  ElMessage.success('已删除')
  loadPendingPrices()
}

onMounted(() => {
  loadBatches()
  loadPendingPrices()
})
</script>