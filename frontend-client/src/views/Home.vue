<template>
  <div>
    <!-- 分类栏 -->
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px">
      <el-button :type="selectedCategory === null ? 'primary' : ''" size="small" round @click="selectedCategory = null">全部</el-button>
      <el-button
        v-for="c in categories" :key="c.id"
        :type="selectedCategory === c.id ? 'primary' : ''"
        size="small" round @click="selectedCategory = c.id"
      >{{ c.name }}</el-button>
    </div>

    <div style="font-size:13px;color:#999;margin-bottom:16px">共 {{ filteredProducts.length }} 件商品</div>

    <!-- 商品网格 -->
    <div style="display:flex;flex-wrap:wrap;gap:16px">
      <div
        v-for="p in filteredProducts" :key="p.id"
        style="width:220px;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(64,158,255,0.08);transition:box-shadow 0.2s;position:relative"
        @mouseenter="e => e.currentTarget.style.boxShadow='0 8px 24px rgba(64,158,255,0.18)'"
        @mouseleave="e => e.currentTarget.style.boxShadow='0 2px 12px rgba(64,158,255,0.08)'"
      >
        <!-- 购物车气泡 -->
        <div
          v-if="cart.getQty(p.id) > 0"
          style="position:absolute;top:8px;right:8px;z-index:10;background:#409eff;color:#fff;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,0.2)"
          @click.stop="openQtyEdit(p)"
        >{{ cart.getQty(p.id) }}</div>

        <!-- 商品图 -->
        <div style="width:220px;height:165px;background:#f0f7ff;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative;cursor:pointer" @click="openDetail(p)">
          <img v-if="p.image" :src="'http://127.0.0.1:8000'+p.image" style="width:100%;height:100%;object-fit:cover" />
          <el-icon v-else style="font-size:48px;color:#c3dff7"><Picture /></el-icon>
          <div v-if="p.special_price" style="position:absolute;top:8px;left:8px;background:#f56c6c;color:#fff;font-size:11px;padding:2px 8px;border-radius:10px;font-weight:bold">特价</div>
          <div v-else-if="p.stock <= 0" style="position:absolute;top:8px;left:8px;background:#909399;color:#fff;font-size:11px;padding:2px 8px;border-radius:10px">暂时缺货</div>
          <div v-else-if="p.stock < 10" style="position:absolute;top:8px;left:8px;background:#e6a23c;color:#fff;font-size:11px;padding:2px 8px;border-radius:10px">库存紧张</div>
        </div>

        <!-- 商品信息 -->
        <div style="padding:12px;cursor:pointer" @click="openDetail(p)">
          <div style="font-weight:bold;font-size:13px;margin-bottom:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#333" :title="p.name">{{ p.name }}</div>
          <div style="font-size:11px;color:#999;margin-bottom:2px">条码：{{ p.barcode || '-' }}</div>
          <div style="font-size:11px;color:#999;margin-bottom:2px">规格：{{ p.spec || '-' }}</div>
          <div style="font-size:11px;color:#999;margin-bottom:2px" v-if="p.middle_pack || p.piece">
            <span v-if="p.middle_pack">每包 {{ p.middle_pack }} 件</span>
            <span v-if="p.middle_pack && p.piece"> · </span>
            <span v-if="p.piece">每件 {{ p.piece }} 个</span>
          </div>
          <div style="margin-top:8px">
            <template v-if="p.special_price">
              <div style="font-size:11px;color:#aaa;text-decoration:line-through">${{ p.sell_price }}</div>
              <div style="font-size:16px;font-weight:bold;color:#f56c6c">${{ p.special_price }}</div>
            </template>
            <template v-else>
              <div style="font-size:16px;font-weight:bold;color:#409eff">${{ p.sell_price }}</div>
            </template>
          </div>
        </div>

        <!-- 加购区 -->
        <div style="padding:0 12px 12px;display:flex;gap:6px;align-items:center">
          <el-input-number
            v-model="qtyMap[p.id]"
            :min="p.middle_pack || 1"
            :step="p.middle_pack || 1"
            :max="p.stock || 9999"
            size="small" style="flex:1"
            controls-position="right"
          />
          <el-button type="primary" size="small" :disabled="p.stock <= 0" @click.stop="addToCart(p)">加入</el-button>
          <el-button
            v-if="p.middle_pack && p.middle_pack > 1"
            size="small" style="padding:0 6px;font-size:11px"
            @click.stop="addPack(p)"
          >+{{ p.middle_pack }}</el-button>
        </div>
      </div>
    </div>

    <div v-if="filteredProducts.length === 0" style="text-align:center;color:#aaa;padding:80px 0;font-size:15px">暂无商品</div>

    <!-- 商品详情弹窗 -->
    <el-dialog v-model="detailVisible" width="520px" :title="detailProduct.name">
      <div style="display:flex;gap:20px">
        <div style="width:200px;height:150px;background:#f0f7ff;border-radius:8px;overflow:hidden;flex-shrink:0;display:flex;align-items:center;justify-content:center">
          <img v-if="detailProduct.image" :src="'http://127.0.0.1:8000'+detailProduct.image" style="width:100%;height:100%;object-fit:cover" />
          <el-icon v-else style="font-size:48px;color:#c3dff7"><Picture /></el-icon>
        </div>
        <div style="flex:1;font-size:13px;line-height:2">
          <div><b>条码：</b>{{ detailProduct.barcode || '-' }}</div>
          <div><b>货号：</b>{{ detailProduct.item_no || '-' }}</div>
          <div><b>规格：</b>{{ detailProduct.spec || '-' }}</div>
          <div v-if="detailProduct.middle_pack"><b>每包数量：</b>{{ detailProduct.middle_pack }} 件</div>
          <div v-if="detailProduct.piece"><b>每件数量：</b>{{ detailProduct.piece }} 个</div>
          <div><b>库存：</b>{{ detailProduct.stock }}</div>
          <template v-if="detailProduct.special_price">
            <div><b>原价：</b><span style="text-decoration:line-through;color:#aaa">${{ detailProduct.sell_price }}</span></div>
            <div><b>特价：</b><span style="color:#f56c6c;font-weight:bold;font-size:16px">${{ detailProduct.special_price }}</span></div>
          </template>
          <template v-else>
            <div><b>售价：</b><span style="color:#409eff;font-weight:bold;font-size:16px">${{ detailProduct.sell_price }}</span></div>
          </template>
        </div>
      </div>
      <div style="margin-top:20px;display:flex;gap:10px;align-items:center">
        <el-input-number
          v-model="detailQty"
          :min="detailProduct.middle_pack || 1"
          :step="detailProduct.middle_pack || 1"
          :max="detailProduct.stock || 9999"
          size="large" style="flex:1"
        />
        <el-button type="primary" size="large" :disabled="detailProduct.stock <= 0" @click="addDetailToCart">加入购物车</el-button>
      </div>
    </el-dialog>

    <!-- 气泡点击修改购物车数量弹窗 -->
    <el-dialog v-model="qtyEditVisible" width="340px" :title="`修改购物车数量 - ${qtyEditProduct.name}`">
      <div style="font-size:13px;color:#999;margin-bottom:12px">
        当前库存：{{ qtyEditProduct.stock }} 件
        <span v-if="qtyEditProduct.middle_pack">· 每包 {{ qtyEditProduct.middle_pack }} 件</span>
      </div>
      <el-input-number
        v-model="qtyEditVal"
        :min="0"
        :step="qtyEditProduct.middle_pack || 1"
        :max="qtyEditProduct.stock || 9999"
        size="large" style="width:100%"
      />
      <div style="font-size:12px;color:#aaa;margin-top:8px">输入 0 则从购物车中删除</div>
      <template #footer>
        <el-button @click="qtyEditVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmQtyEdit">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import request from '../utils/request'
import { useCartStore } from '../stores/cart'

const props = defineProps({ searchKeyword: String })

const cart = useCartStore()
const products = ref([])
const categories = ref([])
const selectedCategory = ref(null)
const qtyMap = ref({})
const detailVisible = ref(false)
const detailProduct = ref({})
const detailQty = ref(1)
const discount = ref(1.0)
const qtyEditVisible = ref(false)
const qtyEditProduct = ref({})
const qtyEditVal = ref(0)

const filteredProducts = computed(() => {
  let list = products.value
  if (selectedCategory.value) list = list.filter(p => p.category_id === selectedCategory.value)
  if (props.searchKeyword) {
    const kw = props.searchKeyword.toLowerCase()
    list = list.filter(p =>
      (p.name || '').toLowerCase().includes(kw) ||
      (p.barcode || '').toLowerCase().includes(kw) ||
      (p.item_no || '').toLowerCase().includes(kw)
    )
  }
  return list
})

const cartPrice = (p) => p.special_price ? p.special_price : p.sell_price

const loadProducts = async () => {
  products.value = await request.get('/products/')
  products.value.forEach(p => { qtyMap.value[p.id] = p.middle_pack || 1 })
}

const loadCategories = async () => {
  categories.value = await request.get('/categories/')
}

const addToCart = (p) => {
  const qty = qtyMap.value[p.id]
  if (!Number.isInteger(qty) || qty <= 0) { ElMessage.warning('请输入正确数字'); return }
  const result = cart.addItem({ ...p, sell_price: cartPrice(p) }, qty, discount.value)
  if (!result.success) { ElMessage.warning(result.message); return }
  ElMessage.success('已加入购物车')
}

const addPack = (p) => {
  const result = cart.addItem({ ...p, sell_price: cartPrice(p) }, p.middle_pack, discount.value)
  if (!result.success) { ElMessage.warning(result.message); return }
  ElMessage.success(`已加入 ${p.middle_pack} 件`)
}

const openDetail = (p) => {
  detailProduct.value = p
  detailQty.value = p.middle_pack || 1
  detailVisible.value = true
}

const addDetailToCart = () => {
  const qty = detailQty.value
  if (!Number.isInteger(qty) || qty <= 0) { ElMessage.warning('请输入正确数字'); return }
  const result = cart.addItem({ ...detailProduct.value, sell_price: cartPrice(detailProduct.value) }, qty, discount.value)
  if (!result.success) { ElMessage.warning(result.message); return }
  ElMessage.success('已加入购物车')
  detailVisible.value = false
}

const openQtyEdit = (p) => {
  qtyEditProduct.value = p
  qtyEditVal.value = cart.getQty(p.id)
  qtyEditVisible.value = true
}

const confirmQtyEdit = () => {
  const val = qtyEditVal.value
  if (val !== 0 && (!Number.isInteger(val) || val < 0)) { ElMessage.warning('请输入正确数字'); return }
  const result = cart.updateQty(qtyEditProduct.value.id, val, qtyEditProduct.value.stock)
  if (!result.success) { ElMessage.warning(result.message); return }
  ElMessage.success(val === 0 ? '已从购物车删除' : '数量已更新')
  qtyEditVisible.value = false
}

onMounted(() => {
  const u = localStorage.getItem('client_user')
  if (u) discount.value = JSON.parse(u).discount ?? 1.0
  loadProducts()
  loadCategories()
})
</script>