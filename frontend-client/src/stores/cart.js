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

  const getQty = (product_id) => {
    const item = items.value.find(i => i.product_id === product_id)
    return item ? item.quantity : 0
  }

  // 返回 {success, code, stock} — 组件负责翻译
  const addItem = (product, quantity, discount = 1.0) => {
    if (!Number.isInteger(quantity) || quantity <= 0) {
      return { success: false, code: 'invalid_qty' }
    }
    const existing = items.value.find(i => i.product_id === product.id)
    const newQty = (existing ? existing.quantity : 0) + quantity
    if (product.stock !== undefined && newQty > product.stock) {
      return { success: false, code: 'insufficient_stock', stock: product.stock }
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

  // 返回 {success, code, stock}
  const updateQty = (product_id, quantity, stock) => {
    if (quantity === 0) {
      removeItem(product_id)
      return { success: true }
    }
    if (!Number.isInteger(quantity) || quantity < 0) {
      return { success: false, code: 'invalid_qty' }
    }
    if (stock !== undefined && quantity > stock) {
      return { success: false, code: 'insufficient_stock', stock }
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