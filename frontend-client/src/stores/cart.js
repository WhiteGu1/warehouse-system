import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref(JSON.parse(localStorage.getItem('cart') || '[]'))

  const save = () => {
    localStorage.setItem('cart', JSON.stringify(items.value))
  }

  const total = computed(() =>
    items.value.reduce((sum, i) => sum + i.quantity * i.unit_price, 0)
  )

  const count = computed(() =>
    items.value.reduce((sum, i) => sum + i.quantity, 0)
  )

  // 获取某商品在购物车中的数量
  const getQty = (product_id) => {
    const item = items.value.find(i => i.product_id === product_id)
    return item ? item.quantity : 0
  }

  // 返回 {success, message}
  const addItem = (product, quantity, discount = 1.0) => {
    // 数量校验：必须是正整数
    if (!Number.isInteger(quantity) || quantity <= 0) {
      return { success: false, message: '请输入正确数字' }
    }
    const existing = items.value.find(i => i.product_id === product.id)
    const newQty = (existing ? existing.quantity : 0) + quantity
    // 库存校验
    if (product.stock !== undefined && newQty > product.stock) {
      return { success: false, message: `库存不足，当前库存 ${product.stock} 件` }
    }
    const unit_price = +(parseFloat(product.sell_price || 0) * discount).toFixed(2)
    if (existing) {
      existing.quantity = newQty
    } else {
      items.value.push({
        product_id: product.id,
        product_name: product.name,
        product_barcode: product.barcode,
        product_spec: product.spec,
        product_image: product.image,
        middle_pack: product.middle_pack,
        piece: product.piece,
        stock: product.stock,
        unit_price,
        quantity
      })
    }
    save()
    return { success: true }
  }

  // 直接设置数量（购物车内修改），qty=0则删除，返回 {success, message}
  const updateQty = (product_id, quantity, stock) => {
    if (quantity === 0) {
      removeItem(product_id)
      return { success: true }
    }
    if (!Number.isInteger(quantity) || quantity < 0) {
      return { success: false, message: '请输入正确数字' }
    }
    if (stock !== undefined && quantity > stock) {
      return { success: false, message: `库存不足，当前库存 ${stock} 件` }
    }
    const item = items.value.find(i => i.product_id === product_id)
    if (item) {
      item.quantity = quantity
      save()
    }
    return { success: true }
  }

  const removeItem = (product_id) => {
    items.value = items.value.filter(i => i.product_id !== product_id)
    save()
  }

  // 提交订单前库存校验，返回缺货商品列表
  const validateStock = async (productList) => {
    const outOfStock = []
    for (const item of items.value) {
      const p = productList.find(p => p.id === item.product_id)
      if (p && item.quantity > p.stock) {
        outOfStock.push({ ...item, available: p.stock })
      }
    }
    return outOfStock
  }

  const clear = () => {
    items.value = []
    save()
  }

  return { items, total, count, getQty, addItem, updateQty, removeItem, validateStock, clear }
})