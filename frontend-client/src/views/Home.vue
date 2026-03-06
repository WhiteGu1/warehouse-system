<template>
  <div>
    <!-- 分类栏 -->
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:16px">
      <el-button :type="selectedCategory === null ? 'primary' : ''" size="small" round @click="selectedCategory = null">{{ t.allCategories }}</el-button>
      <el-button
        v-for="c in categories" :key="c.id"
        :type="selectedCategory === c.id ? 'primary' : ''"
        size="small" round @click="selectedCategory = c.id"
      >{{ lang === 'es' && c.name_es ? c.name_es : c.name }}</el-button>
    </div>

    <!-- 排序/筛选栏 -->
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;flex-wrap:wrap">
      <div style="font-size:13px;color:#999">{{ filteredProducts.length }} {{ t.products }}</div>
      <div style="flex:1" />
      <el-checkbox v-model="filterSpecial" :label="t.specialOnly" border size="small" />
      <el-checkbox v-model="filterInStock" :label="t.inStockOnly" border size="small" />
      <el-checkbox v-model="filterFav" :label="t.favOnly" border size="small" />
      <el-button
        :type="filterNew ? 'warning' : ''"
        size="small" round
        @click="filterNew = !filterNew"
        style="font-weight:bold"
      >NEW! {{ t.filterNew }}</el-button>
      <el-select v-model="sortBy" size="small" style="width:140px" :placeholder="lang === 'es' ? 'Ordenar' : '排序方式'">
        <el-option :label="t.sortDefault" value="" />
        <el-option :label="t.sortPriceAsc" value="price_asc" />
        <el-option :label="t.sortPriceDesc" value="price_desc" />
        <el-option :label="t.sortNameAsc" value="name_asc" />
        <el-option :label="t.sortNameDesc" value="name_desc" />
      </el-select>
    </div>

    <!-- 新商品提示栏 -->
    <div v-if="filterNew" style="margin-bottom:12px;background:linear-gradient(90deg,#fff7e6,#fffbe6);border:1px solid #ffe58f;border-radius:8px;padding:8px 14px;font-size:13px;color:#d48806;display:flex;align-items:center;gap:8px">
      NEW! {{ t.newProductsTitle }}（{{ filteredProducts.length }} {{ t.products }}）
    </div>

    <!-- 商品网格 -->
    <div class="product-grid">
      <div
        v-for="p in pagedProducts" :key="p.id"
        class="product-card"
        @mouseenter="e => e.currentTarget.style.boxShadow='0 8px 24px rgba(64,158,255,0.18)'"
        @mouseleave="e => e.currentTarget.style.boxShadow='0 2px 12px rgba(64,158,255,0.08)'"
      >
        <!-- 收藏按钮 -->
        <div
          style="position:absolute;top:8px;right:42px;z-index:10;background:rgba(255,255,255,0.9);border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,0.15)"
          @click.stop="toggleFav(p)"
        >
          <el-icon :style="isFav(p.id) ? 'color:#f56c6c' : 'color:#ccc'"><Star /></el-icon>
        </div>
        <!-- 购物车气泡 -->
        <div
          v-if="cart.getQty(p.id) > 0"
          style="position:absolute;top:8px;right:8px;z-index:10;background:#409eff;color:#fff;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,0.2)"
          @click.stop="openQtyEdit(p)"
        >{{ cart.getQty(p.id) }}</div>

        <!-- 商品图 -->
        <div class="product-img" @click="openDetail(p)">
          <img v-if="p.image" :src="'http://127.0.0.1:8000'+p.image" style="width:100%;height:100%;object-fit:cover" />
          <el-icon v-else style="font-size:48px;color:#c3dff7"><Picture /></el-icon>
          <div v-if="p.special_price" style="position:absolute;top:8px;left:8px;background:#f56c6c;color:#fff;font-size:11px;padding:2px 8px;border-radius:10px;font-weight:bold">{{ t.special }}</div>
          <div v-else-if="p.stock <= 0" style="position:absolute;top:8px;left:8px;background:#909399;color:#fff;font-size:11px;padding:2px 8px;border-radius:10px">{{ t.outOfStock }}</div>
          <div v-else-if="p.stock < 10" style="position:absolute;top:8px;left:8px;background:#e6a23c;color:#fff;font-size:11px;padding:2px 8px;border-radius:10px">{{ t.lowStock }}</div>
          <!-- 新商品标签 -->
          <div v-if="isNewProduct(p)" style="position:absolute;bottom:8px;left:8px;background:#fa8c16;color:#fff;font-size:10px;padding:1px 6px;border-radius:8px;font-weight:bold">🆕 NEW</div>
        </div>

        <!-- 商品信息 -->
        <div style="padding:10px;cursor:pointer" @click="openDetail(p)">
          <div style="font-weight:bold;font-size:13px;margin-bottom:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#333" :title="p.name">
            {{ lang === 'es' && p.name_es ? p.name_es : p.name }}
          </div>
          <div style="font-size:11px;color:#999;margin-bottom:2px">{{ t.barcode }}：{{ p.barcode || '-' }}</div>
          <div style="font-size:11px;color:#999;margin-bottom:2px">{{ t.spec }}：{{ p.spec || '-' }}</div>
          <div style="font-size:11px;color:#777;margin-bottom:2px;background:#f5f7fa;border-radius:4px;padding:2px 6px;display:inline-block">
            bulto: {{ p.piece || 1 }} | paquete: {{ p.middle_pack || 1 }}
          </div>
          <!-- 最后入库时间 -->
          <div v-if="p.last_stock_in" style="font-size:10px;color:#bbb;margin-top:2px">
            {{ t.lastStockIn }}：{{ p.last_stock_in.slice(0,10) }}
          </div>
          <div style="margin-top:6px">
            <template v-if="p.special_price">
              <div style="font-size:11px;color:#aaa;text-decoration:line-through">${{ p.sell_price }}</div>
              <div style="display:flex;align-items:center;gap:4px">
                <span style="font-size:15px;font-weight:bold;color:#f56c6c">${{ p.special_price }}</span>
                <span v-if="p.sell_price" style="font-size:10px;background:#f56c6c;color:#fff;padding:1px 5px;border-radius:8px">
                  -{{ ((1 - p.special_price / p.sell_price) * 100).toFixed(0) }}%
                </span>
              </div>
            </template>
            <template v-else>
              <div style="font-size:15px;font-weight:bold;color:#409eff">${{ p.sell_price }}</div>
            </template>
          </div>
        </div>

        <!-- 加购区 -->
        <div style="padding:0 10px 10px;display:flex;gap:4px;align-items:center">
          <el-input-number
            v-model="qtyMap[p.id]"
            :min="p.middle_pack || 1"
            :step="p.middle_pack || 1"
            :max="p.stock || 9999"
            size="small" style="flex:1"
            controls-position="right"
          />
          <el-button type="primary" size="small" :disabled="p.stock <= 0" @click.stop="addToCart(p)">{{ t.addToCart }}</el-button>
          <el-button
            v-if="p.middle_pack && p.middle_pack > 1"
            size="small" style="padding:0 5px;font-size:11px"
            @click.stop="addPack(p)"
          >+{{ p.middle_pack }}</el-button>
        </div>
      </div>
    </div>

    <div v-if="filteredProducts.length === 0" style="text-align:center;color:#aaa;padding:60px 0;font-size:15px">{{ t.noProducts }}</div>

    <!-- 分页 -->
    <div v-if="filteredProducts.length > pageSize" style="display:flex;justify-content:center;margin-top:32px;padding-bottom:16px">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="filteredProducts.length"
        layout="prev, pager, next, jumper"
        background
        @current-change="onPageChange"
      />
    </div>

    <!-- 商品详情弹窗 -->
    <el-dialog v-model="detailVisible" width="min(520px,95vw)" :title="lang === 'es' && detailProduct.name_es ? detailProduct.name_es : detailProduct.name">
      <div style="display:flex;gap:16px;flex-wrap:wrap">
        <div style="width:180px;height:135px;background:#f0f7ff;border-radius:8px;overflow:hidden;flex-shrink:0;display:flex;align-items:center;justify-content:center">
          <img v-if="detailProduct.image" :src="'http://127.0.0.1:8000'+detailProduct.image" style="width:100%;height:100%;object-fit:cover" />
          <el-icon v-else style="font-size:48px;color:#c3dff7"><Picture /></el-icon>
        </div>
        <div style="flex:1;min-width:160px;font-size:13px;line-height:2">
          <div><b>{{ t.barcode }}：</b>{{ detailProduct.barcode || '-' }}</div>
          <div><b>{{ t.spec }}：</b>{{ detailProduct.spec || '-' }}</div>
          <div><b>bulto：</b>{{ detailProduct.piece || 1 }}</div>
          <div><b>paquete：</b>{{ detailProduct.middle_pack || 1 }}</div>
          <div><b>{{ t.stock }}：</b>{{ detailProduct.stock }}</div>
          <div v-if="detailProduct.last_stock_in"><b>{{ t.lastStockIn }}：</b>{{ detailProduct.last_stock_in.slice(0,10) }}</div>
          <template v-if="detailProduct.special_price">
            <div><b>{{ t.originalPrice }}：</b><span style="text-decoration:line-through;color:#aaa">${{ detailProduct.sell_price }}</span></div>
            <div>
              <b>{{ t.special }}：</b>
              <span style="color:#f56c6c;font-weight:bold;font-size:16px">${{ detailProduct.special_price }}</span>
              <span v-if="detailProduct.sell_price" style="font-size:12px;background:#f56c6c;color:#fff;padding:1px 6px;border-radius:8px;margin-left:6px">
                -{{ ((1 - detailProduct.special_price / detailProduct.sell_price) * 100).toFixed(0) }}%
              </span>
            </div>
          </template>
          <template v-else>
            <div><b>{{ t.price }}：</b><span style="color:#409eff;font-weight:bold;font-size:16px">${{ detailProduct.sell_price }}</span></div>
          </template>
        </div>
      </div>
      <div style="margin-top:16px;display:flex;gap:10px;align-items:center">
        <el-input-number v-model="detailQty" :min="detailProduct.middle_pack || 1" :step="detailProduct.middle_pack || 1" :max="detailProduct.stock || 9999" size="large" style="flex:1" />
        <el-button type="primary" size="large" :disabled="detailProduct.stock <= 0" @click="addDetailToCart">{{ t.addToCart }}</el-button>
      </div>
    </el-dialog>

    <!-- 气泡修改数量弹窗 -->
    <el-dialog v-model="qtyEditVisible" width="min(340px,92vw)" :title="`${t.cartQty} - ${lang === 'es' && qtyEditProduct.name_es ? qtyEditProduct.name_es : qtyEditProduct.name}`">
      <div style="font-size:13px;color:#999;margin-bottom:12px">
        {{ t.currentStock }}：{{ qtyEditProduct.stock }}
        <span v-if="qtyEditProduct.middle_pack"> · paquete {{ qtyEditProduct.middle_pack }}</span>
      </div>
      <el-input-number v-model="qtyEditVal" :min="0" :step="qtyEditProduct.middle_pack || 1" :max="qtyEditProduct.stock || 9999" size="large" style="width:100%" />
      <div style="font-size:12px;color:#aaa;margin-top:8px">{{ t.deleteIfZero }}</div>
      <template #footer>
        <el-button @click="qtyEditVisible = false">{{ t.cancel }}</el-button>
        <el-button type="primary" @click="confirmQtyEdit">{{ t.confirm }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Picture, Star } from '@element-plus/icons-vue'
import request from '../utils/request'
import { useCartStore } from '../stores/cart'
import { useLang } from '../composables/useLang'

const props = defineProps({ searchKeyword: String })
const cart = useCartStore()
const { lang, t } = useLang()
const products = ref([])
const categories = ref([])
const selectedCategory = ref(null)
const filterSpecial = ref(false)
const filterInStock = ref(false)
const filterFav = ref(false)
const filterNew = ref(false)
const sortBy = ref('')
const qtyMap = ref({})
const detailVisible = ref(false)
const detailProduct = ref({})
const detailQty = ref(1)
const discount = ref(1.0)
const qtyEditVisible = ref(false)
const qtyEditProduct = ref({})
const qtyEditVal = ref(0)
const favorites = ref(JSON.parse(localStorage.getItem('favorites') || '[]'))
const currentPage = ref(1)
const pageSize = 50

// 近2个月判断（用 created_at 商品创建时间）
const twoMonthsAgo = new Date()
twoMonthsAgo.setMonth(twoMonthsAgo.getMonth() - 2)

const isNewProduct = (p) => {
  if (!p.created_at) return false
  return new Date(p.created_at) >= twoMonthsAgo
}

const isFav = (id) => favorites.value.includes(id)
const toggleFav = (p) => {
  const idx = favorites.value.indexOf(p.id)
  if (idx === -1) { favorites.value.push(p.id); ElMessage.success(t.value.collected) }
  else { favorites.value.splice(idx, 1); ElMessage.info(t.value.uncollected) }
  localStorage.setItem('favorites', JSON.stringify(favorites.value))
}

const filteredProducts = computed(() => {
  let list = products.value
  if (selectedCategory.value) list = list.filter(p => p.category_id === selectedCategory.value)
  if (props.searchKeyword) {
    const kw = props.searchKeyword.toLowerCase()
    list = list.filter(p =>
      (p.name || '').toLowerCase().includes(kw) ||
      (p.name_es || '').toLowerCase().includes(kw) ||
      (p.barcode || '').toLowerCase().includes(kw) ||
      (p.item_no || '').toLowerCase().includes(kw)
    )
  }
  if (filterSpecial.value) list = list.filter(p => p.special_price)
  if (filterInStock.value) list = list.filter(p => p.stock > 0)
  if (filterFav.value) list = list.filter(p => isFav(p.id))
  if (filterNew.value) list = list.filter(p => isNewProduct(p))
  list = [...list]
  if (sortBy.value === 'price_asc') list.sort((a, b) => (a.special_price || a.sell_price || 0) - (b.special_price || b.sell_price || 0))
  else if (sortBy.value === 'price_desc') list.sort((a, b) => (b.special_price || b.sell_price || 0) - (a.special_price || a.sell_price || 0))
  else if (sortBy.value === 'name_asc') list.sort((a, b) => (a.name || '').localeCompare(b.name || ''))
  else if (sortBy.value === 'name_desc') list.sort((a, b) => (b.name || '').localeCompare(a.name || ''))
  else if (sortBy.value === 'stock_in_desc') {
    list.sort((a, b) => {
      if (!a.last_stock_in && !b.last_stock_in) return 0
      if (!a.last_stock_in) return 1
      if (!b.last_stock_in) return -1
      return b.last_stock_in.localeCompare(a.last_stock_in)
    })
  }
  return list
})

watch(filteredProducts, () => { currentPage.value = 1 })

const pagedProducts = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredProducts.value.slice(start, start + pageSize)
})

const onPageChange = () => { window.scrollTo({ top: 0, behavior: 'smooth' }) }

const cartMsg = (result) => {
  if (result.code === 'insufficient_stock') return `${t.value.stockInsufficient} ${result.stock}`
  return t.value.correctNumber
}

const cartPrice = (p) => p.special_price ? p.special_price : p.sell_price

const loadProducts = async () => {
  products.value = await request.get('/products/')
  products.value.forEach(p => { qtyMap.value[p.id] = p.middle_pack || 1 })
}
const loadCategories = async () => { categories.value = await request.get('/categories/') }

const addToCart = (p) => {
  const qty = qtyMap.value[p.id]
  if (!Number.isInteger(qty) || qty <= 0) { ElMessage.warning(t.value.correctNumber); return }
  const result = cart.addItem({ ...p, sell_price: cartPrice(p) }, qty, discount.value)
  if (!result.success) { ElMessage.warning(cartMsg(result)); return }
  ElMessage.success(t.value.addedToCart)
}
const addPack = (p) => {
  const result = cart.addItem({ ...p, sell_price: cartPrice(p) }, p.middle_pack, discount.value)
  if (!result.success) { ElMessage.warning(cartMsg(result)); return }
  ElMessage.success(`${t.value.addedPacks} ${p.middle_pack}`)
}
const openDetail = (p) => { detailProduct.value = p; detailQty.value = p.middle_pack || 1; detailVisible.value = true }
const addDetailToCart = () => {
  const qty = detailQty.value
  if (!Number.isInteger(qty) || qty <= 0) { ElMessage.warning(t.value.correctNumber); return }
  const result = cart.addItem({ ...detailProduct.value, sell_price: cartPrice(detailProduct.value) }, qty, discount.value)
  if (!result.success) { ElMessage.warning(cartMsg(result)); return }
  ElMessage.success(t.value.addedToCart); detailVisible.value = false
}
const openQtyEdit = (p) => { qtyEditProduct.value = p; qtyEditVal.value = cart.getQty(p.id); qtyEditVisible.value = true }
const confirmQtyEdit = () => {
  const val = qtyEditVal.value
  if (val !== 0 && (!Number.isInteger(val) || val < 0)) { ElMessage.warning(t.value.correctNumber); return }
  const result = cart.updateQty(qtyEditProduct.value.id, val, qtyEditProduct.value.stock)
  if (!result.success) { ElMessage.warning(cartMsg(result)); return }
  ElMessage.success(val === 0 ? t.value.uncollected : t.value.addedToCart)
  qtyEditVisible.value = false
}
onMounted(() => {
  const u = localStorage.getItem('client_user')
  if (u) discount.value = JSON.parse(u).discount ?? 1.0
  loadProducts(); loadCategories()
})
</script>

<style scoped>
.product-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
.product-card {
  width: 220px;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(64,158,255,0.08);
  transition: box-shadow 0.2s;
  position: relative;
}
.product-img {
  width: 100%;
  height: 165px;
  background: #f0f7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
  cursor: pointer;
}
@media (max-width: 768px) {
  .product-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  .product-card { width: 100%; }
  .product-img { height: 130px; }
}
@media (max-width: 400px) {
  .product-grid { grid-template-columns: repeat(2, 1fr); gap: 8px; }
}
</style>