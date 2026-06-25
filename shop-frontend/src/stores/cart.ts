import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'
import type { CartItem } from '@/types'

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])

  const totalCount = computed(() => items.value.reduce((s, i) => s + i.quantity, 0))
  const totalPrice = computed(() => items.value.reduce((s, i) => s + i.price * i.quantity, 0))

  async function fetchCart() {
    const res = await api.get<CartItem[]>('/c-endpoint/cart')
    if (res.code === 0) items.value = res.data
  }

  async function addItem(productId: number, quantity: number) {
    await api.post('/c-endpoint/cart', { product_id: productId, quantity })
    await fetchCart()
  }

  async function updateQuantity(productId: number, quantity: number) {
    await api.put(`/c-endpoint/cart/${productId}`, { quantity })
    await fetchCart()
  }

  async function removeItem(productId: number) {
    await api.delete(`/c-endpoint/cart/${productId}`)
    await fetchCart()
  }

  function clearCart() {
    items.value = []
  }

  return { items, totalCount, totalPrice, fetchCart, addItem, updateQuantity, removeItem, clearCart }
})