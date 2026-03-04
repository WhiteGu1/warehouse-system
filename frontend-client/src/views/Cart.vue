<template>
  <div>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
      <el-button :icon="ArrowLeft" @click="$router.push('/')">继续购物</el-button>
      <h2 style="margin:0;color:#333">购物车</h2>
      <el-tag type="info">{{ cart.items.length }} 种商品</el-tag>
    </div>

    <div v-if="cart.items.length === 0" style="text-align:center;padding:80px 0;color:#aaa">
      <el-icon style="font-size:64px;color:#c3dff7"><ShoppingCart /></el-icon>
      <div style="margin-top:16px;font-size:15px">购物车是空的</div>
      <el-button type="primary" style="margin-top:16px" @click="$router.push('/')">去选购</el-button>
    </div>

    <div v-else style="display:flex;gap:20px;align-items:flex-start">
      <!-- 购物车列表 -->
      <div style="flex:1">
        <el-card v-for="item in cart.items" :key="item.product_id" style="margin-bottom:12px">
          <div style="display:flex;gap:16px;align-items:center">
            <div style="width:80px;height:60px;background:#f0f7ff;border-radius:6px;overflow:hidden;flex-shrink:0;display:flex;align-items:center;justify-content:center">
              <img v-if="item.product_image" :src="'http://127.0.0.1:8000'+item.product_image" style="width:100%;height:100%;object-fit:cover" />
              <el-icon v-else style="color:#c3dff7;font-size:24px"><Picture /></el-icon>
            </div>
            <div style="flex:1">
              <div style="font-weight:bold;font-size:14px;color:#333">{{ item.product_name }}</div>
              <div style="font-size:12px;color:#999;margin-top:2px">
                {{ item.product_barcode || '' }}
                <span v-if="item.product_spec"> · {{ item.product_spec }}</span>
              </div>
              <div style="font-size:12px;color:#999" v-if="item.middle_pack">每包 {{ item.middle_pack }} 件</div>
            </div>
            <div style="text-align:center">
              <div style="font-size:13px;color:#aaa;margin-bottom:4px">单价</div>
              <div style="font-size:15px;font-weight:bold;color:#409eff">${{ item.unit_price }}</div>
            </div>
            <div style="text-align:center">
              <div style="font-size:13px;color:#aaa;margin-bottom:4px">数量</div>
              <el-input-number
                v-model="item.quantity"
                :min="1"
                :max="item.stock || 9999"
                :step="item.middle_pack || 1"
                size="small"
                controls-position="right"
                style="width:110px"
                @change="val => onQtyChange(item, val)"
              />
            </div>
            <div style="text-align:center;min-width:80px">
              <div style="font-size:13px;color:#aaa;margin-bottom:4px">小计</div>
              <div style="font-size:15px;font-weight:bold;color:#f56c6c">
                ${{ (item.quantity * item.unit_price).toFixed(2) }}
              </div>
            </div>
            <el-button type="danger" circle size="small" :icon="Delete" @click="confirmRemove(item)" />
          </div>
        </el-card>
      </div>

      <!-- 结算栏 -->
      <div style="width:280px;flex-shrink:0">
        <el-card>
          <div style="font-size:15px;font-weight:bold;margin-bottom:16px;color:#333">订单摘要</div>
          <div style="font-size:13px;color:#666;margin-bottom:8px;display:flex;justify-content:space-between">
            <span>商品种类</span><span>{{ cart.items.length }} 种</span>
          </div>
          <div style="font-size:13px;color:#666;margin-bottom:8px;display:flex;justify-content:space-between">
            <span>商品总量</span><span>{{ cart.count }} 件</span>
          </div>
          <div v-if="discount < 1" style="font-size:13px;color:#666;margin-bottom:8px;display:flex;justify-content:space-between">
            <span>原价合计</span>
            <span style="text-decoration:line-through;color:#aaa">${{ originalTotal }}</span>
          </div>
          <div v-if="discount < 1" style="font-size:13px;color:#e6a23c;margin-bottom:8px;display:flex;justify-content:space-between">
            <span>折扣</span><span>-{{ ((1 - discount) * 100).toFixed(0) }}%</span>
          </div>
          <el-divider style="margin:12px 0" />
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
            <span style="font-size:15px;font-weight:bold">合计</span>
            <span style="font-size:22px;font-weight:bold;color:#409eff">${{ cart.total.toFixed(2) }}</span>
          </div>
          <el-input v-model="remark" placeholder="备注（选填）" type="textarea" :rows="2" style="margin-bottom:12px" />
          <el-button type="primary" size="large" style="width:100%" :loading="submitting" @click="submitOrder">
            提交订单
          </el-button>
          <el-button style="width:100%;margin-top:8px" @click="confirmClear">清空购物车</el-button>
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

const router = useRouter()
const cart = useCartStore()
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
  if (!Number.isInteger(val) || val <= 0) {
    ElMessage.warning('请输入正确数字')
    item.quantity = item.middle_pack || 1
    return
  }
  if (item.stock !== undefined && val > item.stock) {
    ElMessage.warning(`库存不足，当前库存 ${item.stock} 件`)
    item.quantity = item.stock
    return
  }
  cart.updateQty(item.product_id, val, item.stock)
}

const confirmRemove = async (item) => {
  await ElMessageBox.confirm(`确定从购物车删除"${item.product_name}"？`, '提示', { type: 'warning' })
  cart.removeItem(item.product_id)
}

const confirmClear = async () => {
  await ElMessageBox.confirm('确定清空购物车？', '提示', { type: 'warning' })
  cart.clear()
}

const submitOrder = async () => {
  if (cart.items.length === 0) { ElMessage.warning('购物车是空的'); return }

  // 提交前实时校验库存
  const latestProducts = await request.get('/products/')
  const outOfStock = await cart.validateStock(latestProducts)
  if (outOfStock.length > 0) {
    const names = outOfStock.map(i => `${i.product_name}（库存剩余 ${i.available} 件）`).join('、')
    ElMessage.error(`以下商品库存不足：${names}，已从购物车移除`)
    outOfStock.forEach(i => cart.removeItem(i.product_id))
    return
  }

  await ElMessageBox.confirm(`确认提交订单？合计 $${cart.total.toFixed(2)}`, '提示', { type: 'info' })
  submitting.value = true
  try {
    const user = JSON.parse(localStorage.getItem('client_user') || '{}')
    const items = cart.items.map(i => ({
      product_id: i.product_id,
      quantity: i.quantity,
      unit_price: i.unit_price
    }))
    await request.post('/orders/', {
      supermarket_id: user.id,
      items,
      remark: remark.value,
      discount: discount.value,
      total_amount_override: parseFloat(cart.total.toFixed(2))
    })
    ElMessage.success('订单提交成功！')
    cart.clear()
    router.push('/orders')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  const u = localStorage.getItem('client_user')
  if (u) discount.value = JSON.parse(u).discount ?? 1.0
})
</script>