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
              <el-button text style="width:100%;padding:8px 0" @click="categoryDialogVisible = true">✏️ 编辑分类</el-button>
            </template>
          </el-select>
        </el-col>
      </el-row>

      <!-- 批量操作栏 -->
      <div v-if="selectedIds.length > 0" style="margin-bottom:12px;display:flex;align-items:center;gap:10px;background:#e8f4fd;padding:10px 14px;border-radius:8px">
        <span style="font-size:13px;color:#409eff;font-weight:bold">已选 {{ selectedIds.length }} 件商品</span>
        <el-button size="small" @click="selectedIds = []">取消选择</el-button>
        <el-button size="small" type="primary" @click="openBatchPrice">批量改售价</el-button>
        <el-button size="small" type="danger" @click="openBatchSpecial">批量设特价</el-button>
        <el-button size="small" type="warning" @click="openBatchCategory">批量改分类</el-button>
      </div>

      <div style="display:flex;flex-wrap:wrap;gap:16px">
        <div
          v-for="p in products" :key="p.id"
          :style="`width:200px;border:2px solid ${selectedIds.includes(p.id) ? '#409eff' : '#e4e7ed'};border-radius:8px;overflow:hidden;cursor:pointer;transition:box-shadow 0.2s;position:relative`"
          @mouseenter="e => e.currentTarget.style.boxShadow='0 4px 16px rgba(0,0,0,0.12)'"
          @mouseleave="e => e.currentTarget.style.boxShadow='none'"
        >
          <div style="width:200px;height:150px;background:#f5f7fa;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative">
            <div style="position:absolute;top:6px;left:6px;z-index:10" @click.stop="toggleSelect(p.id)">
              <el-checkbox :model-value="selectedIds.includes(p.id)" />
            </div>
            <img v-if="p.image" :src="'http://127.0.0.1:8000'+p.image" style="width:100%;height:100%;object-fit:cover;cursor:pointer" @click="openDetail(p)" />
            <el-icon v-else style="font-size:48px;color:#c0c4cc;cursor:pointer" @click="openDetail(p)"><Picture /></el-icon>
          </div>
          <div style="padding:10px" @click="openDetail(p)">
            <div style="font-weight:bold;font-size:13px;margin-bottom:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" :title="p.name">{{ p.name }}</div>
            <div v-if="p.name_es" style="font-size:11px;color:#888;margin-bottom:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">🇪🇸 {{ p.name_es }}</div>
            <div style="font-size:12px;color:#666">规格：{{ p.spec || '-' }}</div>
            <div style="font-size:12px;color:#666">货号：{{ p.item_no || p.barcode || '-' }}</div>
            <div style="font-size:12px;color:#666">库存：{{ p.stock }}</div>
            <div style="font-size:12px;color:#e6a23c">进价：${{ p.cost_price ?? '-' }}</div>
            <div style="font-size:12px;color:#67c23a">售价：${{ p.sell_price ?? '-' }}</div>
            <div v-if="p.special_price" style="font-size:12px;color:#f56c6c;font-weight:bold">特价：${{ p.special_price }}</div>
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
            <el-descriptions-item label="🇪🇸 西语名称">{{ detailProduct.name_es || '-' }}</el-descriptions-item>
            <el-descriptions-item label="条码">{{ detailProduct.barcode || '-' }}</el-descriptions-item>
            <el-descriptions-item label="货号">{{ detailProduct.item_no || '-' }}</el-descriptions-item>
            <el-descriptions-item label="分类">{{ detailProduct.category_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="规格">{{ detailProduct.spec || '-' }}</el-descriptions-item>
            <el-descriptions-item label="每包数量">{{ detailProduct.middle_pack ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="每件数量">{{ detailProduct.piece ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="进价">${{ detailProduct.cost_price ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="售价">${{ detailProduct.sell_price ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="特价">
              <span v-if="detailProduct.special_price" style="color:#f56c6c;font-weight:bold">${{ detailProduct.special_price }}</span>
              <span v-else style="color:#aaa">无</span>
            </el-descriptions-item>
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
      <el-form :model="form" label-width="100px">
        <el-form-item label="条形码"><el-input v-model="form.barcode" /></el-form-item>
        <el-form-item label="货号"><el-input v-model="form.item_no" /></el-form-item>
        <el-form-item label="商品名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="🇪🇸 西语名称">
          <el-input v-model="form.name_es" placeholder="西班牙语名称（选填）" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category_id" placeholder="选择分类" style="width:100%">
            <el-option v-for="c in categories" :key="c.id" :value="c.id">
              <div style="display:flex;justify-content:space-between;align-items:center;width:100%">
                <span>{{ c.name }}</span>
                <el-badge :value="c.product_count" :max="999" type="primary" style="margin-left:8px" />
              </div>
            </el-option>
            <template #footer>
              <el-button text style="width:100%;padding:8px 0" @click="categoryDialogVisible = true">✏️ 编辑分类</el-button>
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
            <el-input-number v-model="form._margin" :precision="0" :min="0" :max="999" :step="5" style="width:130px"
              @change="val => { if(form.cost_price) form.sell_price = +(form.cost_price * (1 + (val||0) / 100)).toFixed(2) }" />
            <span style="color:#999;font-size:12px">%</span>
          </div>
        </el-form-item>
        <el-form-item label="特价">
          <div style="display:flex;gap:8px;align-items:center">
            <el-input-number v-model="form.special_price" :precision="2" :min="0" style="width:150px" />
            <el-button size="small" type="danger" @click="form.special_price = null" v-if="form.special_price">清除特价</el-button>
            <span style="font-size:12px;color:#aaa">不填则无特价</span>
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
        <VueCropper ref="cropperRef" :img="cropperImg" :fixed="true" :fixed-number="[4, 3]" :auto-crop="true" :center-box="true" output-type="jpeg" />
      </div>
      <template #footer>
        <el-button @click="cropperVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCrop">确认裁剪并上传</el-button>
      </template>
    </el-dialog>

    <!-- 批量改售价弹窗 -->
    <el-dialog v-model="batchPriceVisible" title="批量修改售价" width="360px">
      <el-form label-width="80px">
        <el-form-item label="修改方式">
          <el-radio-group v-model="batchPriceMode">
            <el-radio value="fixed">固定金额</el-radio>
            <el-radio value="margin">利润率</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="batchPriceMode === 'fixed'" label="售价">
          <el-input-number v-model="batchPriceVal" :precision="2" :min="0" style="width:100%" />
        </el-form-item>
        <el-form-item v-else label="利润率">
          <div style="display:flex;align-items:center;gap:8px">
            <el-input-number v-model="batchMarginVal" :precision="0" :min="0" :max="999" style="width:150px" />
            <span>%</span>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchPriceVisible = false">取消</el-button>
        <el-button type="primary" @click="submitBatchPrice">确认修改 {{ selectedIds.length }} 件</el-button>
      </template>
    </el-dialog>

    <!-- 批量设特价弹窗 -->
    <el-dialog v-model="batchSpecialVisible" title="批量设置特价" width="360px">
      <el-form label-width="80px">
        <el-form-item label="特价金额">
          <el-input-number v-model="batchSpecialVal" :precision="2" :min="0" style="width:100%" />
        </el-form-item>
        <div style="font-size:12px;color:#aaa;margin-left:80px">设为 0 则清除特价</div>
      </el-form>
      <template #footer>
        <el-button @click="batchSpecialVisible = false">取消</el-button>
        <el-button type="danger" @click="submitBatchSpecial">确认设置 {{ selectedIds.length }} 件</el-button>
      </template>
    </el-dialog>

    <!-- 批量改分类弹窗 -->
    <el-dialog v-model="batchCategoryVisible" title="批量修改分类" width="360px">
      <el-form label-width="80px">
        <el-form-item label="目标分类">
          <el-select v-model="batchCategoryVal" placeholder="选择分类" style="width:100%">
            <el-option v-for="c in categories" :key="c.id" :value="c.id" :label="c.name" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchCategoryVisible = false">取消</el-button>
        <el-button type="warning" @click="submitBatchCategory">确认修改 {{ selectedIds.length }} 件</el-button>
      </template>
    </el-dialog>

    <!-- 分类管理弹窗 -->
    <el-dialog v-model="categoryDialogVisible" title="分类管理" width="550px">
      <div style="display:flex;gap:8px;margin-bottom:16px;align-items:flex-start">
        <div style="flex:1;display:flex;flex-direction:column;gap:6px">
          <el-input v-model="newCategoryName" placeholder="中文名称" @keyup.enter="addCategory" />
          <el-input v-model="newCategoryNameEs" placeholder="🇪🇸 西语名称（选填）" @keyup.enter="addCategory" />
        </div>
        <el-button type="primary" @click="addCategory" style="height:72px">添加</el-button>
      </div>
      <el-table :data="categories" stripe>
        <el-table-column label="中文名称">
          <template #default="{ row }">
            <el-input v-if="row._editing" v-model="row._editName" size="small" placeholder="中文" />
            <span v-else>{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="🇪🇸 西语名称">
          <template #default="{ row }">
            <el-input v-if="row._editing" v-model="row._editNameEs" size="small" placeholder="Español" />
            <span v-else style="color:#888">{{ row.name_es || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="商品数" width="70" align="center">
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
              <el-button size="small" @click="row._editing = true; row._editName = row.name; row._editNameEs = row.name_es || ''">编辑</el-button>
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
const newCategoryNameEs = ref('')
const selectedIds = ref([])
const batchPriceVisible = ref(false)
const batchSpecialVisible = ref(false)
const batchCategoryVisible = ref(false)
const batchPriceMode = ref('fixed')
const batchPriceVal = ref(0)
const batchMarginVal = ref(30)
const batchSpecialVal = ref(0)
const batchCategoryVal = ref(null)

const form = ref({
  barcode: '', item_no: '', name: '', name_es: '', category_id: null,
  spec: '', middle_pack: 1, piece: null,
  cost_price: 0, sell_price: 0, special_price: null, stock: 0, remark: '', _margin: null
})

const recalcSellPrice = (val) => {
  if (form.value._margin && val) {
    form.value.sell_price = +(val * (1 + form.value._margin / 100)).toFixed(2)
  }
}

const toggleSelect = (id) => {
  const idx = selectedIds.value.indexOf(id)
  if (idx === -1) selectedIds.value.push(id)
  else selectedIds.value.splice(idx, 1)
}

const openBatchPrice = () => { batchPriceVal.value = 0; batchMarginVal.value = 30; batchPriceVisible.value = true }
const openBatchSpecial = () => { batchSpecialVal.value = 0; batchSpecialVisible.value = true }
const openBatchCategory = () => { batchCategoryVal.value = null; batchCategoryVisible.value = true }

const submitBatchPrice = async () => {
  const selected = products.value.filter(p => selectedIds.value.includes(p.id))
  for (const p of selected) {
    let newPrice
    if (batchPriceMode.value === 'fixed') newPrice = batchPriceVal.value
    else newPrice = p.cost_price ? +(p.cost_price * (1 + batchMarginVal.value / 100)).toFixed(2) : null
    if (newPrice !== null) await request.put(`/products/${p.id}`, { sell_price: newPrice })
  }
  ElMessage.success(`已更新 ${selected.length} 件商品售价`)
  batchPriceVisible.value = false; selectedIds.value = []; loadProducts()
}

const submitBatchSpecial = async () => {
  for (const id of selectedIds.value) {
    const val = batchSpecialVal.value > 0 ? batchSpecialVal.value : null
    await request.put(`/products/${id}`, { special_price: val })
  }
  ElMessage.success(`已更新 ${selectedIds.value.length} 件商品特价`)
  batchSpecialVisible.value = false; selectedIds.value = []; loadProducts()
}

const submitBatchCategory = async () => {
  if (!batchCategoryVal.value) { ElMessage.warning('请选择分类'); return }
  for (const id of selectedIds.value) {
    await request.put(`/products/${id}`, { category_id: batchCategoryVal.value })
  }
  ElMessage.success(`已更新 ${selectedIds.value.length} 件商品分类`)
  batchCategoryVisible.value = false; selectedIds.value = []; loadProducts()
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
    '商品名称': p.name, '西语名称': p.name_es || '', '条码': p.barcode || '',
    '货号': p.item_no || '', '分类': p.category_name || '', '规格': p.spec || '',
    '每包数量': p.middle_pack ?? '', '每件数量': p.piece ?? '',
    '进价': p.cost_price ?? '', '售价': p.sell_price ?? '',
    '特价': p.special_price ?? '', '库存': p.stock, '备注': p.remark || ''
  }))
  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '商品列表')
  const buf = XLSX.write(wb, { type: 'array', bookType: 'xlsx' })
  saveAs(new Blob([buf], { type: 'application/octet-stream' }), `商品列表_${new Date().toLocaleDateString()}.xlsx`)
}

const addCategory = async () => {
  if (!newCategoryName.value.trim()) { ElMessage.warning('请输入分类名称'); return }
  await request.post('/categories/', { name: newCategoryName.value.trim(), name_es: newCategoryNameEs.value.trim() || null })
  ElMessage.success('添加成功')
  newCategoryName.value = ''; newCategoryNameEs.value = ''
  loadCategories()
}

const saveEditCategory = async (row) => {
  if (!row._editName.trim()) { ElMessage.warning('分类名称不能为空'); return }
  await request.put(`/categories/${row.id}`, { name: row._editName.trim(), name_es: row._editNameEs?.trim() || null })
  ElMessage.success('更新成功')
  row._editing = false
  loadCategories()
}

const deleteCategory = async (row) => {
  if (row.product_count > 0) { ElMessage.warning(`该分类下有 ${row.product_count} 个商品，无法删除`); return }
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
  reader.onload = (e) => { cropperImg.value = e.target.result; cropperVisible.value = true }
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
  if (!stockInForm.value.quantity || stockInForm.value.quantity < 1) { ElMessage.warning('请输入入库数量'); return }
  const res = await request.post(`/products/${stockInProduct.value.id}/stockin`, stockInForm.value)
  ElMessage.success(`入库成功，当前库存：${res.new_stock}`)
  stockInVisible.value = false; detailVisible.value = false
  loadProducts()
}

const openAdd = () => {
  isEdit.value = false
  form.value = { barcode: '', item_no: '', name: '', name_es: '', category_id: null, spec: '', middle_pack: 1, piece: null, cost_price: 0, sell_price: 0, special_price: null, stock: 0, remark: '', _margin: null }
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
  if (isEdit.value) await request.put(`/products/${editId.value}`, payload)
  else await request.post('/products/', payload)
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

onMounted(() => { loadProducts(); loadCategories() })
</script>