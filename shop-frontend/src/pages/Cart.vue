<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Minus, Plus, Trash2, ShoppingCart, ArrowRight, MapPin, Eye, Store } from 'lucide-vue-next'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/utils/api'
import { useToast } from '@/composables/useToast'
import type { CartItem } from '@/types'

const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()
const toast = useToast()
const selectedItems = ref<number[]>([])
const checkoutLoading = ref(false)
const isAdmin = computed(() => authStore.user?.role === 'admin' || localStorage.getItem('role') === 'admin')

// 地址选择
interface Address {
  id: number
  name: string
  phone: string
  province: string
  city: string
  district: string
  detail: string
  is_default: boolean
}
const showAddressPicker = ref(false)
const addresses = ref<Address[]>([])
const selectedAddressId = ref<number | null>(null)
const addressLoading = ref(false)

function formatAddress(addr: Address) {
  return `${addr.province}${addr.city}${addr.district} ${addr.detail}`
}

// 按商家分组购物车商品
const groupedItems = computed(() => {
  const groups: { merchant_id: number; shop_name: string; items: CartItem[] }[] = []
  for (const item of cartStore.items) {
    const mid = item.merchant_id || 0
    let group = groups.find(g => g.merchant_id === mid)
    if (!group) {
      group = { merchant_id: mid, shop_name: item.shop_name || '平台自营', items: [] }
      groups.push(group)
    }
    group.items.push(item)
  }
  return groups
})

const totalAmount = computed(() => {
  return cartStore.items
    .filter(item => selectedItems.value.includes(item.product_id))
    .reduce((sum, item) => sum + item.price * item.quantity, 0)
})

const selectedCount = computed(() => {
  return cartStore.items
    .filter(item => selectedItems.value.includes(item.product_id))
    .reduce((sum, item) => sum + item.quantity, 0)
})

// 选中的商品涉及多少个商家（= 将生成多少个订单）
const selectedMerchantCount = computed(() => {
  const mids = new Set<number>()
  cartStore.items
    .filter(item => selectedItems.value.includes(item.product_id))
    .forEach(item => mids.add(item.merchant_id || 0))
  return mids.size
})

function toggleSelect(productId: number) {
  const index = selectedItems.value.indexOf(productId)
  if (index > -1) {
    selectedItems.value.splice(index, 1)
  } else {
    selectedItems.value.push(productId)
  }
}

function selectAll() {
  if (selectedItems.value.length === cartStore.items.length && cartStore.items.length > 0) {
    selectedItems.value = []
  } else {
    selectedItems.value = cartStore.items.map(item => item.product_id)
  }
}

// 按商家分组全选/取消
function toggleGroupSelect(group: { merchant_id: number; items: CartItem[] }) {
  const groupProductIds = group.items.map(i => i.product_id)
  const allSelected = groupProductIds.every(id => selectedItems.value.includes(id))
  if (allSelected) {
    // 取消该组全选
    selectedItems.value = selectedItems.value.filter(id => !groupProductIds.includes(id))
  } else {
    // 选中该组全部
    for (const id of groupProductIds) {
      if (!selectedItems.value.includes(id)) {
        selectedItems.value.push(id)
      }
    }
  }
}

function isGroupAllSelected(group: { items: CartItem[] }) {
  return group.items.every(i => selectedItems.value.includes(i.product_id))
}

async function decreaseQuantity(item: any) {
  if (item.quantity > 1) {
    await cartStore.updateQuantity(item.product_id, item.quantity - 1)
  }
}

async function increaseQuantity(item: any) {
  if (item.quantity < item.stock) {
    await cartStore.updateQuantity(item.product_id, item.quantity + 1)
  }
}

async function removeItem(productId: number) {
  await cartStore.removeItem(productId)
  const index = selectedItems.value.indexOf(productId)
  if (index > -1) {
    selectedItems.value.splice(index, 1)
  }
}

async function deleteSelected() {
  for (const productId of selectedItems.value) {
    await cartStore.removeItem(productId)
  }
  selectedItems.value = []
}

async function openAddressPicker() {
  if (selectedCount.value === 0) return
  showAddressPicker.value = true
  addressLoading.value = true
  try {
    const res = await api.get<any>('/c-endpoint/addresses')
    if (res.code === 0) {
      const data = res.data as any
      addresses.value = Array.isArray(data) ? data : (data.items || data)
      // 默认选中默认地址
      const defaultAddr = addresses.value.find(a => a.is_default)
      if (defaultAddr) {
        selectedAddressId.value = defaultAddr.id
      } else if (addresses.value.length > 0) {
        selectedAddressId.value = addresses.value[0].id
      }
    }
  } catch (err) {
    console.error('获取地址失败:', err)
  } finally {
    addressLoading.value = false
  }
}

async function confirmCheckout() {
  if (!selectedAddressId.value) {
    toast.show('warning', '请选择收货地址')
    return
  }
  const selectedAddr = addresses.value.find(a => a.id === selectedAddressId.value)
  if (!selectedAddr) return

  checkoutLoading.value = true
  try {
    const addressStr = `${selectedAddr.name} ${selectedAddr.phone} ${formatAddress(selectedAddr)}`
    const res = await api.post('/c-endpoint/orders', { address: addressStr })
    if (res.code === 0) {
      showAddressPicker.value = false
      selectedItems.value = []
      const orders = res.data?.orders || []
      if (orders.length === 1) {
        // 单订单：直接跳转支付页面
        router.push(`/payment/${orders[0].id}`)
      } else {
        // 多订单：跳转订单列表，逐一支付
        router.push('/orders')
        toast.show('info', `下单成功！已拆分为 ${orders.length} 个订单，请逐一支付`)
      }
    } else {
      toast.show('error', res.message || '下单失败')
    }
  } catch (err: any) {
    toast.show('error', err.message || '下单失败')
  } finally {
    checkoutLoading.value = false
  }
}

onMounted(() => {
  cartStore.fetchCart()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 pb-24">
    <div class="mx-4 md:mx-8 lg:mx-12 py-6">
      <div class="flex items-center gap-3 mb-6">
        <ShoppingCart class="w-6 h-6 text-indigo-600" />
        <h1 class="text-2xl font-bold text-gray-900">购物车</h1>
        <span class="text-gray-500">({{ cartStore.items.length }} 件商品)</span>
        <!-- 管理员预览提示 -->
        <span v-if="isAdmin" class="ml-auto px-3 py-1 bg-gray-100 text-gray-500 text-xs rounded-full flex items-center gap-1">
          <Eye class="w-3 h-3" />
          预览模式
        </span>
      </div>

      <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div class="flex items-center gap-4 px-6 py-4 border-b border-gray-100">
          <button
            @click="selectAll"
            :class="[
              'flex items-center gap-2 text-sm text-gray-700',
              selectedItems.length === cartStore.items.length && cartStore.items.length > 0 ? 'text-indigo-600 font-medium' : ''
            ]"
          >
            <div
              :class="[
                'w-5 h-5 rounded border-2 flex items-center justify-center transition-colors',
                selectedItems.length === cartStore.items.length && cartStore.items.length > 0
                  ? 'bg-indigo-600 border-indigo-600'
                  : 'border-gray-300'
              ]"
            >
              <svg v-if="selectedItems.length === cartStore.items.length && cartStore.items.length > 0" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            全选
          </button>
        </div>

        <div v-if="cartStore.items.length === 0" class="py-16 text-center">
          <div class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <ShoppingCart class="w-10 h-10 text-gray-400" />
          </div>
          <p class="text-gray-500">购物车是空的</p>
          <button
            @click="router.push('/products')"
            class="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            去逛逛
          </button>
        </div>

        <div v-else class="divide-y divide-gray-100">
          <!-- 按商家分组展示 -->
          <div v-for="group in groupedItems" :key="group.merchant_id" class="border-b border-gray-100 last:border-b-0">
            <!-- 商家标题栏 -->
            <div class="flex items-center gap-3 px-6 py-3 bg-gray-50">
              <button @click="toggleGroupSelect(group)" class="flex-shrink-0">
                <div
                  :class="[
                    'w-5 h-5 rounded border-2 flex items-center justify-center transition-colors',
                    isGroupAllSelected(group)
                      ? 'bg-indigo-600 border-indigo-600'
                      : 'border-gray-300'
                  ]"
                >
                  <svg v-if="isGroupAllSelected(group)" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </button>
              <Store class="w-4 h-4 text-indigo-600" />
              <span class="font-medium text-gray-800 text-sm">{{ group.shop_name }}</span>
            </div>

            <!-- 该商家的商品列表 -->
            <div
              v-for="item in group.items"
              :key="item.product_id"
              class="flex items-center gap-4 px-6 py-4 hover:bg-gray-50 transition-colors"
            >
              <button
                @click="toggleSelect(item.product_id)"
                class="flex-shrink-0"
              >
                <div
                  :class="[
                    'w-5 h-5 rounded border-2 flex items-center justify-center transition-colors',
                    selectedItems.includes(item.product_id)
                      ? 'bg-indigo-600 border-indigo-600'
                      : 'border-gray-300'
                  ]"
                >
                  <svg v-if="selectedItems.includes(item.product_id)" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </button>

              <router-link :to="`/products/${item.product_id}`" class="flex-shrink-0">
                <img
                  v-if="item.image_url"
                  :src="item.image_url"
                  :alt="item.product_name"
                  class="w-20 h-20 object-cover rounded-lg"
                />
                <div v-else class="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center">
                  <ShoppingCart class="w-8 h-8 text-gray-300" />
                </div>
              </router-link>

              <div class="flex-1 min-w-0">
                <router-link :to="`/products/${item.product_id}`">
                  <h3 class="font-medium text-gray-900 truncate">{{ item.product_name }}</h3>
                </router-link>
                <p class="text-sm text-gray-500 mt-1">库存 {{ item.stock }} 件</p>
              </div>

              <div class="text-right">
                <div class="text-lg font-bold text-rose-600">¥{{ item.price }}</div>

                <div class="flex items-center justify-end gap-2 mt-2">
                  <button
                    @click="decreaseQuantity(item)"
                    :disabled="item.quantity === 1"
                    :class="[
                      'w-8 h-8 rounded-lg flex items-center justify-center transition-colors',
                      item.quantity === 1
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    ]"
                  >
                    <Minus class="w-4 h-4" />
                  </button>
                  <span class="w-8 text-center font-medium">{{ item.quantity }}</span>
                  <button
                    @click="increaseQuantity(item)"
                    :disabled="item.quantity >= item.stock"
                    :class="[
                      'w-8 h-8 rounded-lg flex items-center justify-center transition-colors',
                      item.quantity >= item.stock
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    ]"
                  >
                    <Plus class="w-4 h-4" />
                  </button>
                </div>
              </div>

              <button
                @click="removeItem(item.product_id)"
                class="ml-4 p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
              >
                <Trash2 class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="cartStore.items.length > 0"
      class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 md:px-8 lg:px-12 py-4"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <button
            @click="selectAll"
            :class="[
              'flex items-center gap-2 text-sm',
              selectedItems.length === cartStore.items.length && cartStore.items.length > 0 ? 'text-indigo-600' : 'text-gray-600'
            ]"
          >
            <div
              :class="[
                'w-5 h-5 rounded border-2 flex items-center justify-center',
                selectedItems.length === cartStore.items.length && cartStore.items.length > 0
                  ? 'bg-indigo-600 border-indigo-600'
                  : 'border-gray-300'
              ]"
            >
              <svg v-if="selectedItems.length === cartStore.items.length && cartStore.items.length > 0" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <span>已选 {{ selectedCount }} 件</span>
          </button>
          <span class="text-gray-400">|</span>
          <button
            v-if="selectedItems.length > 0"
            @click="deleteSelected"
            class="text-sm text-gray-600 hover:text-red-500"
          >
            删除选中
          </button>
        </div>

        <div class="flex items-center gap-6">
          <div class="text-right">
            <p class="text-sm text-gray-500">合计</p>
            <div class="flex items-baseline gap-1">
              <span class="text-sm text-gray-500">¥</span>
              <span class="text-2xl font-bold text-rose-600">{{ totalAmount }}</span>
            </div>
            <p v-if="selectedMerchantCount > 1" class="text-xs text-indigo-500 mt-1">将拆分为 {{ selectedMerchantCount }} 个订单</p>
          </div>
          <!-- 管理员预览模式：隐藏结算按钮 -->
          <template v-if="isAdmin">
            <span class="px-6 py-3 bg-gray-200 text-gray-400 rounded-xl font-semibold text-sm">预览模式</span>
          </template>
          <template v-else>
            <button
              @click="openAddressPicker"
              :disabled="selectedCount === 0 || checkoutLoading"
              :class="[
                'px-8 py-3 rounded-xl font-semibold transition-all duration-300 flex items-center gap-2',
                selectedCount === 0
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700 hover:shadow-lg hover:shadow-indigo-200'
              ]"
            >
              {{ checkoutLoading ? '结算中...' : '去结算' }}
              <ArrowRight v-if="!checkoutLoading" class="w-5 h-5" />
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- 地址选择弹窗 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showAddressPicker" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="showAddressPicker = false">
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <h3 class="text-lg font-semibold text-gray-900">选择收货地址</h3>
              <button @click="showAddressPicker = false" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                &times;
              </button>
            </div>

            <div class="p-6 max-h-96 overflow-y-auto">
              <div v-if="addressLoading" class="py-8 text-center text-gray-400">加载中...</div>

              <div v-else-if="addresses.length === 0" class="py-8 text-center">
                <p class="text-gray-500 mb-4">暂无收货地址</p>
                <button @click="showAddressPicker = false; router.push('/profile')" class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">
                  去添加地址
                </button>
              </div>

              <div v-else class="space-y-3">
                <div
                  v-for="addr in addresses"
                  :key="addr.id"
                  @click="selectedAddressId = addr.id"
                  :class="[
                    'p-4 rounded-xl border-2 cursor-pointer transition-all',
                    selectedAddressId === addr.id
                      ? 'border-indigo-600 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300'
                  ]"
                >
                  <div class="flex items-center gap-2">
                    <MapPin class="w-4 h-4 text-indigo-600" />
                    <span class="font-medium text-gray-900">{{ addr.name }}</span>
                    <span class="text-sm text-gray-500">{{ addr.phone }}</span>
                    <span v-if="addr.is_default" class="px-2 py-0.5 bg-indigo-100 text-indigo-700 text-xs rounded-full">默认</span>
                  </div>
                  <p class="text-sm text-gray-600 mt-1 ml-6">{{ formatAddress(addr) }}</p>
                </div>
              </div>
            </div>

            <div v-if="addresses.length > 0" class="px-6 py-4 border-t border-gray-100">
              <button
                @click="confirmCheckout"
                :disabled="!selectedAddressId || checkoutLoading"
                class="w-full py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
              >
                {{ checkoutLoading ? '下单中...' : '确认下单' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.modal-enter-active { transition: all 0.25s ease-out; }
.modal-leave-active { transition: all 0.15s ease-in; }
.modal-enter-from { opacity: 0; }
.modal-enter-from > div { transform: scale(0.95); opacity: 0; }
.modal-leave-to { opacity: 0; }
.modal-leave-to > div { transform: scale(0.95); opacity: 0; }
</style>
