<template>
  <div>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
      <h2 style="margin:0;color:#333">我的收藏</h2>
      <el-tag type="info">{{ favProducts.length }} 件商品</el-tag>
      <el-button size="small" type="danger" plain v-if="favProducts.length > 0" @click="clearAll">清空收藏</el-button>
    </div>

    <div v-if="favProducts.length === 0" style="text-align:center;padding:80px 0;color:#aaa">
      <el-icon style="font-size:64px;color:#c3dff7"><Star /></el-icon>
      <div style="margin-top:16px;font-size:15px">暂无收藏商品</div>
      <el-button type="primary" style="margin-top:16px" @click="$router.push('/')">去逛逛</el-button>
    </div>

    <div style="display:flex;flex-wrap:wrap;gap:16px">
      <div
        v-for="p in favProducts" :key="p.id"
        style="width:220px;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(64,158,255,0.08);transition:box-shadow 0.2s;position:relative"
        @mouseenter="e => e.currentTarget.style.boxShadow='0 8px 24px rgba(64,158,255,0.18)'"
        @mouseleave="e => e.currentTarget.style.boxShadow='0 2px 12px rgba(64,158,255,0.08)'"
      >
        <!-- 取消收藏 -->
        <div
          style="position:absolute;top:8px;right:8px;z-index:10;background:rgba(255,255,255,0.9);border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,0.15)"
          @click.stop="removeFav(p.id)"
        >
          <el-icon style="color:#f56c6c"><Star /></el-icon>
        </div>

        <!-- 商品图 -->
        <div style="width:220px;height:165px;background:#f0f7ff;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative;cursor:pointer" @click="$router.push('/')">
          <img v-if="p.image" :src="'http://127.0.0.1:8000'+p.image" style="width:100%;height:100%;object-fit:cover" />
          <el-icon v-else style="font-size:48px;color:#c3dff7"><Picture /></el-icon>
          <div v-if="p.special_price" style="position:absolute;top:8px;left:8px;background:#f56c6c;color:#fff;font-size:11px;padding:2px 8px;border-radius:10px;font-weight:bold">特价</div>
          <div v-else-if="p.stock <= 0" style="position:absolute;top:8px;left:8px;background:#909399;color:#fff;font-size:11px;padding:2px 8px;border-radius:10px">暂时缺货</div>
        </div>

        <!-- 商品信息 -->
        <div style="padding:12px">
          <div style="font-weight:bold;font-size:13px;margin-bottom:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#333" :title="p.name">{{ p.name }}</div>
          <div style="font-size:11px;color:#999;margin-bottom:2px">规格：{{ p.spec || '-' }}</div>
          <div style="font-size:11px;color:#999;margin-bottom:8px">库存：{{ p.stock }}</div>
          <template v-if="p.special_price">
            <div style="font-size:11px;color:#aaa;text-decoration:line-through">${{ p.sell_price }}</div>
            <div style="font-size:16px;font-weight:bold;color:#f56c6c">${{ p.special_price }}</div>
          </template>
          <template v-else>
            <div style="font-size:16px;font-weight:bold;color:#409eff">${{ p.sell_price }}</div>
          </template>
        </div>

        <!-- 加购 -->
        <div style="padding:0 12px 12px;display:flex;gap:6px">
          <el-input-number
            v-model="qtyMap[p.id]"
            :min="p.middle_pack || 1"
            :step="p.middle_pack || 1"
            :max="p.stock || 9999"
            size="small" style="flex:1"
            controls-position="right"
          />
          <el-button type="primary" size="small" :disabled="p.stock <= 0" @click="addToCart(p)">加入</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Star, Picture } from '@element-plus/icons-vue'
import { useCartStore } from '../stores/cart'
import request from '../utils/request'

const cart = useCartStore()
const allProducts = ref([])
const qtyMap = ref({})
const favorites = ref(JSON.parse(localStorage.getItem('favorites') || '[]'))
const discount = ref(1.0)

const favProducts = computed(() =>
  allProducts.value.filter(p => favorites.value.includes(p.id))
)

const removeFav = (id) => {
  favorites.value = favorites.value.filter(f => f !== id)
  localStorage.setItem('favorites', JSON.stringify(favorites.value))
}

const clearAll = async () => {
  await ElMessageBox.confirm('确定清空所有收藏？', '提示', { type: 'warning' })
  favorites.value = []
  localStorage.setItem('favorites', JSON.stringify([]))
}

const cartPrice = (p) => p.special_price ? p.special_price : p.sell_price

const addToCart = (p) => {
  const qty = qtyMap.value[p.id]
  if (!Number.isInteger(qty) || qty <= 0) { ElMessage.warning('请输入正确数字'); return }
  const result = cart.addItem({ ...p, sell_price: cartPrice(p) }, qty, discount.value)
  if (!result.success) { ElMessage.warning(result.message); return }
  ElMessage.success('已加入购物车')
}

onMounted(async () => {
  const u = localStorage.getItem('client_user')
  if (u) discount.value = JSON.parse(u).discount ?? 1.0
  allProducts.value = await request.get('/products/')
  allProducts.value.forEach(p => { qtyMap.value[p.id] = p.middle_pack || 1 })
})
</script>