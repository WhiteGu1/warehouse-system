<template>
  <div>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;flex-wrap:wrap">
      <el-button :icon="ArrowLeft" size="small" @click="$router.push('/')">{{ t.continueShopping }}</el-button>
      <h2 style="margin:0;color:#333;font-size:clamp(16px,4vw,22px)">{{ t.cart }}</h2>
      <el-tag type="info">{{ cart.items.length }} {{ t.kinds }}</el-tag>
    </div>

    <div v-if="cart.items.length === 0" style="text-align:center;padding:60px 0;color:#aaa">
      <el-icon style="font-size:64px;color:#c3dff7"><ShoppingCart /></el-icon>
      <div style="margin-top:16px;font-size:15px">{{ t.emptyCart }}</div>
      <el-button type="primary" style="margin-top:16px" @click="$router.push('/')">{{ t.goShopping }}</el-button>
    </div>

    <div v-else class="cart-layout">
      <!-- 购物车列表 -->
      <div style="flex:1;min-width:0">
        <el-card v-for="item in cart.items" :key="item.product_id" style="margin-bottom:10px">
          <div class="cart-item">
            <div style="width:70px;height:52px;background:#f0f7ff;border-radius:6px;overflow:hidden;flex-shrink:0;display:flex;align-items:center;justify-content:center">
              <img v-if="item.product_image" :src="'http://127.0.0.1:8000'+item.product_image" style="width:100%;height:100%;object-fit:cover" />
              <el-icon v-else style="color:#c3dff7;font-size:20px"><Picture /></el-icon>
            </div>
            <div style="flex:1;min-width:0">
              <div style="font-weight:bold;font-size:13px;color:#333;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ item.product_name }}</div>
              <div style="font-size:11px;color:#999;margin-top:2px">
                {{ item.product_barcode || '' }}
                <span v-if="item.product_spec"> · {{ item.product_spec }}</span>
              </div>
              <div style="font-size:11px;color:#409eff;font-weight:bold">${{ item.unit_price }}</div>
            </div>
            <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;flex-shrink:0">
              <el-input-number
                v-model="item.quantity"
                :min="1"
                :max="item.stock || 9999"
                :step="item.middle_pack || 1"
                size="small"
                controls-position="right"
                style="width:100px"
                @change="val => onQtyChange(item, val)"
              />
              <div style="font-size:14px;font-weight:bold;color:#f56c6c">${{ (item.quantity * item.unit_price).toFixed(2) }}</div>
            </div>
            <el-button type="danger" circle size="small" :icon="Delete" @click="confirmRemove(item)" />
          </div>
        </el-card>
      </div>

      <!-- 结算栏 -->
      <div class="cart-summary">
        <el-card>
          <div style="font-size:15px;font-weight:bold;margin-bottom:16px;color:#333">{{ t.orderSummary }}</div>
          <div style="font-size:13px;color:#666;margin-bottom:8px;display:flex;justify-content:space-between">
            <span>{{ t.totalQty }}</span><span>{{ cart.count }} {{ t.pieces }}</span>
          </div>
          <div v-if="discount < 1" style="font-size:13px;color:#666;margin-bottom:8px;display:flex;justify-content:space-between">
            <span>{{ t.originalTotal }}</span>
            <span style="text-decoration:line-through;color:#aaa">${{ originalTotal }}</span>
          </div>
          <div v-if="discount < 1" style="font-size:13px;color:#e6a23c;margin-bottom:8px;display:flex;justify-content:space-between">
            <span>{{ t.discount }}</span><span>-{{ ((1 - discount) * 100).toFixed(0) }}%</span>
          </div>
          <el-divider style="margin:12px 0" />
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
            <span style="font-size:15px;font-weight:bold">{{ t.total }}</span>
            <span style="font-size:22px;font-weight:bold;color:#409eff">${{ cart.total.toFixed(2) }}</span>
          </div>
          <el-input v-model="remark" :placeholder="t.remark" type="textarea" :rows="2" style="margin-bottom:12px" />
          <el-button type="primary" size="large" style="width:100%" :loading="submitting" @click="submitOrder">
            {{ t.submitOrder }}
          </el-button>
          <el-button style="width:100%;margin-top:8px" @click="confirmClear">{{ t.clearCart }}</el-button>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Delete, ShoppingCart, Picture } from '@element-plus/icons-vue'
import { useCartStore } from '../stores/cart'
import request from '../utils/request'
import { useLang } from '../composables/useLang'

const router = useRouter()
const cart = useCartStore()
const { t } = useLang()
const remark = ref('')
const submitting = ref(false)
const discount = ref(1.0)

const originalTotal = computed(() => {
  return cart.items.reduce((sum, i) => {
    const orig = discount.value > 0 ? i.unit_price / discount.value : i.unit_price
    return sum + orig * i.quantity
  }, 0).toFixed(2)
})

const onQtyChange = (item, val) => {
  if (!Number.isInteger(val) || val <= 0) { ElMessage.warning(t.value.correctNumber); item.quantity = item.middle_pack || 1; return }
  if (item.stock !== undefined && val > item.stock) { ElMessage.warning(`${t.value.stockInsufficient} ${item.stock}`); item.quantity = item.stock; return }
  cart.updateQty(item.product_id, val, item.stock)
}

const confirmRemove = async (item) => {
  await ElMessageBox.confirm(`${t.value.confirmDelete} "${item.product_name}"？`, t.value.confirm, { type: 'warning' })
  cart.removeItem(item.product_id)
}

const confirmClear = async () => {
  await ElMessageBox.confirm(t.value.confirmClear, t.value.confirm, { type: 'warning' })
  cart.clear()
}

const submitOrder = async () => {
  if (cart.items.length === 0) { ElMessage.warning(t.value.emptyCart); return }
  const latestProducts = await request.get('/products/')
  const outOfStock = await cart.validateStock(latestProducts)
  if (outOfStock.length > 0) {
    const names = outOfStock.map(i => `${i.product_name}（${t.value.stockInsufficient} ${i.available}）`).join('、')
    ElMessage.error(names)
    outOfStock.forEach(i => cart.removeItem(i.product_id))
    return
  }
  await ElMessageBox.confirm(`${t.value.confirmOrder} $${cart.total.toFixed(2)}`, t.value.confirm, { type: 'info' })
  submitting.value = true
  try {
    const user = JSON.parse(localStorage.getItem('client_user') || '{}')
    const items = cart.items.map(i => ({ product_id: i.product_id, quantity: i.quantity, unit_price: i.unit_price }))
    await request.post('/orders/', { supermarket_id: user.id, items, remark: remark.value, discount: discount.value, total_amount_override: parseFloat(cart.total.toFixed(2)) })
    ElMessage.success(t.value.orderSuccess)
    cart.clear()
    router.push('/orders')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || t.value.orderSuccess)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  const u = localStorage.getItem('client_user')
  if (u) discount.value = JSON.parse(u).discount ?? 1.0
})
</script>

<style scoped>
.cart-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}
.cart-summary {
  width: 280px;
  flex-shrink: 0;
}
.cart-item {
  display: flex;
  gap: 12px;
  align-items: center;
}
@media (max-width: 768px) {
  .cart-layout {
    flex-direction: column;
  }
  .cart-summary {
    width: 100%;
  }
}
</style>