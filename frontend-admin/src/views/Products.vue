<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>商品管理</span>
          <div style="display:flex;gap:8px">
            <el-button @click="exportProducts">导出Excel</el-button>
            <el-button type="primary" @click="openAdd">新增商品</el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="10" style="margin-bottom:15px">
        <el-col :span="8">
          <el-input v-model="keyword" placeholder="搜索商品名称或条码" clearable @input="loadProducts">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-select v-model="categoryId" placeholder="选择分类" clearable @change="loadProducts">
            <el-option v-for="c in categories" :key="c.id" :value="c.id">
              <div style="display:flex;justify-content:space-between;align-items:center;width:100%">
                <span>{{ c.name }}</span>
                <el-badge :value="c.product_count" :max="999" type="primary" style="margin-left:8px" />
              </div>
            </el-option>
            <template #footer>
              <el-button text style="width:100%;padding:8px 0" @click="categoryDialogVisible = true">
                ✏️ 编辑分类
              </el-button>
            </template>
          </el-select>
        </el-col>
      </el-row>

      <div style="display:flex;flex-wrap:wrap;gap:16px">
        <div
          v-for="p in products" :key="p.id"
          style="width:200px;border:1px solid #e4e7ed;border-radius:8px;overflow:hidden;cursor:pointer;transition:box-shadow 0.2s"
          @mouseenter="e => e.currentTarget.style.boxShadow='0 4px 16px rgba(0,0,0,0.12)'"
          @mouseleave="e => e.currentTarget.style.boxShadow='none'"
        >
          <div style="width:200px;height:150px;background:#f5f7fa;display:flex;align-items:center;justify-content:center;overflow:hidden" @click="openDetail(p)">
            <img v-if="p.image" :src="'http://127.0.0.1:8000'+p.image" style="width:100%;height:100%;object-fit:cover" />
            <el-icon v-else style="font-size:48px;color:#c0c4cc"><Picture /></el-icon>
          </div>
          <div style="padding:10px" @click="openDetail(p)">
            <div style="font-weight:bold;font-size:13px;margin-bottom:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" :title="p.name">{{ p.name }}</div>
            <div style="font-size:12px;color:#666">规格：{{ p.spec || '-' }}</div>
            <div style="font-size:12px;color:#666">货号：{{ p.item_no || p.barcode || '-' }}</div>
            <div style="font-size:12px;color:#666">库存：{{ p.stock }}</div>
            <div style="font-size:12px;color:#e6a23c">进价：¥{{ p.cost_price ?? '-' }}</div>
            <div style="font-size:12px;color:#67c23a">售价：¥{{ p.sell_price ?? '-' }}</div>
          </div>
          <div style="padding:0 10px 10px">
            <el-button size="small" type="success" style="width:100%" @click.stop="openStockIn(p)">商品入库</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 商品详情弹窗 -->
    <el-dialog v-model="detailVisible" title="商品详情" width="750px">
      <div style="display:flex;gap:24px">
        <div style="width:260px;flex-shrink:0">
          <div style="width:260px;height:195px;background:#f5f7fa;border-radius:8px;overflow:hidden;display:flex;align-items:center;justify-content:center;margin-bottom:12px">
            <img v-if="detailProduct.image" :src="'http://127.0.0.1:8000'+detailProduct.image" style="width:100%;height:100%;object-fit:cover" />
            <el-icon v-else style="font-size:64px;color:#c0c4cc"><Picture /></el-icon>
          </div>
          <el-upload :auto-upload="false" :on-change="handleImageChange" :show-file-list="false" accept="image/*">
            <el-button size="small" style="width:100%">上传图片</el-button>
          </el-upload>
          <el-button size="small" type="success" style="width:100%;margin-top:8px" @click="openStockIn(detailProduct)">商品入库</el-button>
        </div>
        <div style="flex:1">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="商品名称">{{ detailProduct.name }}</el-descriptions-item>
            <el-descriptions-item label="条码">{{ detailProduct.barcode || '-' }}</el-descriptions-item>
            <el-descriptions-item label="货号">{{ detailProduct.item_no || '-' }}</el-descriptions-item>
            <el-descriptions-item label="分类">{{ detailProduct.category_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="规格">{{ detailProduct.spec || '-' }}</el-descriptions-item>
            <el-descriptions-item label="每包数量">{{ detailProduct.middle_pack ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="每件数量">{{ detailProduct.piece ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="进价">¥{{ detailProduct.cost_price ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="售价">¥{{ detailProduct.sell_price ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="库存">{{ detailProduct.stock }}</el-descriptions-item>
            <el-descriptions-item label="备注">{{ detailProduct.remark || '-' }}</el-descriptions-item>
          </el-descriptions>
          <div style="margin-top:16px">
            <div style="font-weight:bold;margin-bottom:8px">入库历史</div>
            <el-table :data="stockHistory" size="small" max-height="180">
              <el-table-column prop="created_at" label="入库时间" width="150" />
              <el-table-column prop="quantity" label="数量" width="70" />
              <el-table-column label="类型" width="90">
                <template #default="{ row }">
                  <el-tag v-if="row.source==='manual_new'" type="success" size="small">新增商品</el-tag>
                  <el-tag v-else-if="row.source==='manual_add'" type="primary" size="small">库存增加</el-tag>
                  <el-tag v-else-if="row.source==='import'" type="warning" size="small">导入添加</el-tag>
                  <el-tag v-else size="small">-</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="cost_price" label="进价" width="70" />
            </el-table>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="openEdit(detailProduct)">编辑</el-button>
        <el-button type="danger" @click="deleteProduct(detailProduct.id)">删除</el-button>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑商品' : '新增商品'" width="540px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="条形码"><el-input v-model="form.barcode" /></el-form-item>
        <el-form-item label="货号"><el-input v-model="form.item_no" /></el-form-item>
        <el-form-item label="商品名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category_id" placeholder="选择分类" style="width:100%">
            <el-option v-for="c in categories" :key="c.id" :value="c.id">
              <div style="display:flex;justify-content:space-between;align-items:center;width:100%">
                <span>{{ c.name }}</span>
                <el-badge :value="c.product_count" :max="999" type="primary" style="margin-left:8px" />
              </div>
            </el-option>
            <template #footer>
              <el-button text style="width:100%;padding:8px 0" @click="categoryDialogVisible = true">
                ✏️ 编辑分类
              </el-button>
            </template>
          </el-select>
        </el-form-item>
        <el-form-item label="规格"><el-input v-model="form.spec" /></el-form-item>
        <el-form-item label="每包数量"><el-input-number v-model="form.middle_pack" :min="1" /></el-form-item>
        <el-form-item label="每件数量"><el-input-number v-model="form.piece" :min="0" /></el-form-item>
        <el-form-item label="进价"><el-input-number v-model="form.cost_price" :precision="2" :min="0" @change="recalcSellPrice" /></el-form-item>
        <el-form-item label="售价">
          <div style="display:flex;gap:8px;align-items:center">
            <el-input-number v-model="form.sell_price" :precision="2" :min="0" style="width:130px" />
            <span style="color:#999;font-size:12px">利润率</span>
            <el-input-number
              v-model="form._margin"
              :precision="0" :min="0" :max="999" :step="5" style="width:130px"
              @change="val => { if(form.cost_price) form.sell_price = +(form.cost_price * (1 + (val||0) / 100)).toFixed(2) }"
            />
            <span style="color:#999;font-size:12px">%</span>
          </div>
        </el-form-item>
        <el-form-item v-if="!isEdit" label="初始库存"><el-input-number v-model="form.stock" :min="0" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProduct">保存</el-button>
      </template>
    </el-dialog>

    <!-- 商品入库弹窗 -->
    <el-dialog v-model="stockInVisible" title="商品入库" width="400px">
      <el-form :model="stockInForm" label-width="90px">
        <el-form-item label="商品名称"><span>{{ stockInProduct.name }}</span></el-form-item>
        <el-form-item label="当前库存"><span>{{ stockInProduct.stock }}</span></el-form-item>
        <el-form-item label="入库数量"><el-input-number v-model="stockInForm.quantity" :min="1" /></el-form-item>
        <el-form-item label="进价"><el-input-number v-model="stockInForm.cost_price" :precision="2" :min="0" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="stockInForm.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockInVisible = false">取消</el-button>
        <el-button type="primary" @click="submitStockIn">确认入库</el-button>
      </template>
    </el-dialog>

    <!-- 裁剪弹窗 -->
    <el-dialog v-model="cropperVisible" title="裁剪图片" width="620px" :close-on-click-modal="false">
      <div style="height:400px">
        <VueCropper
          ref="cropperRef"
          :img="cropperImg"
          :fixed="true"
          :fixed-number="[4, 3]"
          :auto-crop="true"
          :center-box="true"
          output-type="jpeg"
        />
      </div>
      <template #footer>
        <el-button @click="cropperVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCrop">确认裁剪并上传</el-button>
      </template>
    </el-dialog>

    <!-- 分类管理弹窗 -->
    <el-dialog v-model="categoryDialogVisible" title="分类管理" width="450px">
      <div style="display:flex;gap:8px;margin-bottom:16px">
        <el-input v-model="newCategoryName" placeholder="输入新分类名称" style="flex:1" @keyup.enter="addCategory" />
        <el-button type="primary" @click="addCategory">添加</el-button>
      </div>
      <el-table :data="categories" stripe>
        <el-table-column label="分类名称">
          <template #default="{ row }">
            <el-input v-if="row._editing" v-model="row._editName" size="small" />
            <span v-else>{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="商品数" width="80" align="center">
          <template #default="{ row }">
            <el-badge :value="row.product_count" :max="999" type="primary" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <template v-if="row._editing">
              <el-button size="small" type="success" @click="saveEditCategory(row)">保存</el-button>
              <el-button size="small" @click="row._editing = false">取消</el-button>
            </template>
            <template v-else>
              <el-button size="small" @click="row._editing = true; row._editName = row.name">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteCategory(row)">删除</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Picture } from '@element-plus/icons-vue'
import request from '../utils/request'
import axios from 'axios'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import 'vue-cropper/dist/index.css'
import { VueCropper } from 'vue-cropper'

const products = ref([])
const categories = ref([])
const keyword = ref('')
const categoryId = ref(null)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const stockInVisible = ref(false)
const cropperVisible = ref(false)
const categoryDialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const detailProduct = ref({})
const stockHistory = ref([])
const cropperImg = ref('')
const cropperRef = ref(null)
const uploadingProductId = ref(null)
const stockInProduct = ref({})
const stockInForm = ref({ quantity: 1, cost_price: 0, remark: '' })
const newCategoryName = ref('')

const form = ref({
  barcode: '', item_no: '', name: '', category_id: null,
  spec: '', middle_pack: 1, piece: null,
  cost_price: 0, sell_price: 0, stock: 0, remark: '', _margin: null
})

const recalcSellPrice = (val) => {
  if (form.value._margin && val) {
    form.value.sell_price = +(val * (1 + form.value._margin / 100)).toFixed(2)
  }
}

const loadProducts = async () => {
  const params = {}
  if (keyword.value) params.keyword = keyword.value
  if (categoryId.value) params.category_id = categoryId.value
  products.value = await request.get('/products/', { params })
}

const loadCategories = async () => {
  categories.value = await request.get('/categories/')
}

const exportProducts = () => {
  const data = products.value.map(p => ({
    '商品名称': p.name,
    '条码': p.barcode || '',
    '货号': p.item_no || '',
    '分类': p.category_name || '',
    '规格': p.spec || '',
    '每包数量': p.middle_pack ?? '',
    '每件数量': p.piece ?? '',
    '进价': p.cost_price ?? '',
    '售价': p.sell_price ?? '',
    '库存': p.stock,
    '备注': p.remark || ''
  }))
  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '商品列表')
  const buf = XLSX.write(wb, { type: 'array', bookType: 'xlsx' })
  saveAs(new Blob([buf], { type: 'application/octet-stream' }), `商品列表_${new Date().toLocaleDateString()}.xlsx`)
}

const addCategory = async () => {
  if (!newCategoryName.value.trim()) { ElMessage.warning('请输入分类名称'); return }
  await request.post('/categories/', { name: newCategoryName.value.trim() })
  ElMessage.success('添加成功')
  newCategoryName.value = ''
  loadCategories()
}

const saveEditCategory = async (row) => {
  if (!row._editName.trim()) { ElMessage.warning('分类名称不能为空'); return }
  await request.put(`/categories/${row.id}`, { name: row._editName.trim() })
  ElMessage.success('更新成功')
  row._editing = false
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

const openDetail = async (p) => {
  detailProduct.value = { ...p }
  cropperImg.value = ''
  detailVisible.value = true
  stockHistory.value = await request.get(`/products/${p.id}/stock-history`)
}

const handleImageChange = (file) => {
  uploadingProductId.value = detailProduct.value.id
  const reader = new FileReader()
  reader.onload = (e) => {
    cropperImg.value = e.target.result
    cropperVisible.value = true
  }
  reader.readAsDataURL(file.raw)
}

const submitCrop = () => {
  cropperRef.value.getCropBlob(async (blob) => {
    const formData = new FormData()
    formData.append('file', blob, 'image.jpg')
    const token = localStorage.getItem('token')
    const res = await axios.post(`http://127.0.0.1:8000/api/products/${uploadingProductId.value}/image`, formData, {
      headers: { Authorization: `Bearer ${token}` }
    })
    detailProduct.value.image = res.data.image
    ElMessage.success('图片上传成功')
    cropperVisible.value = false
    loadProducts()
  })
}

const openStockIn = (p) => {
  stockInProduct.value = p
  stockInForm.value = { quantity: 1, cost_price: p.cost_price || 0, remark: '' }
  stockInVisible.value = true
}

const submitStockIn = async () => {
  if (!stockInForm.value.quantity || stockInForm.value.quantity < 1) {
    ElMessage.warning('请输入入库数量')
    return
  }
  const res = await request.post(`/products/${stockInProduct.value.id}/stockin`, stockInForm.value)
  ElMessage.success(`入库成功，当前库存：${res.new_stock}`)
  stockInVisible.value = false
  detailVisible.value = false
  loadProducts()
}

const openAdd = () => {
  isEdit.value = false
  form.value = { barcode: '', item_no: '', name: '', category_id: null, spec: '', middle_pack: 1, piece: null, cost_price: 0, sell_price: 0, stock: 0, remark: '', _margin: null }
  dialogVisible.value = true
}

const openEdit = (row) => {
  isEdit.value = true
  editId.value = row.id
  form.value = { ...row, _margin: null }
  detailVisible.value = false
  dialogVisible.value = true
}

const saveProduct = async () => {
  if (!form.value.name) { ElMessage.warning('请输入商品名称'); return }
  const payload = { ...form.value }
  delete payload._margin
  if (isEdit.value) {
    await request.put(`/products/${editId.value}`, payload)
  } else {
    await request.post('/products/', payload)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadProducts()
}

const deleteProduct = async (id) => {
  await ElMessageBox.confirm('确定删除该商品？', '提示', { type: 'warning' })
  await request.delete(`/products/${id}`)
  ElMessage.success('删除成功')
  detailVisible.value = false
  loadProducts()
}

onMounted(() => {
  loadProducts()
  loadCategories()
})
</script>