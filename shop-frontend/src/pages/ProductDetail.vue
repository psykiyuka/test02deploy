<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Heart, Minus, Plus, ShoppingCart, ArrowRight, Truck, Shield, RefreshCw, Eye } from 'lucide-vue-next'
import { api } from '@/utils/api'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { favoriteApi } from '@/utils/favoriteApi'
import type { Product } from '@/types'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

const isAdmin = computed(() => authStore.user?.role === 'admin' || localStorage.getItem('role') === 'admin')

const product = ref<Product | null>(null)
const loading = ref(true)
const selectedImage = ref(0)
const quantity = ref(1)
const isFavorite = ref(false)
const favoriteLoading = ref(false)
const addCartLoading = ref(false)
const buyNowLoading = ref(false)

async function fetchProduct() {
  loading.value = true
  try {
    const productId = route.params.id
    const res = await api.get<Product>(`/c-endpoint/products/${productId}`)
    // api.ts 直接返回 ApiResponse<T>，res.data 就是商品数据
    if (res.code === 0 && res.data) {
      product.value = res.data as Product
      // 注入 merchant_id / product_id 供 AI 客服浮窗使用
      ;(window as any).__currentMerchantId = (res.data as any).merchant_id
      ;(window as any).__currentProductId = (res.data as any).id
      // 检查是否已收藏（仅登录用户）
      const token = localStorage.getItem('token')
      const role = localStorage.getItem('role')
      if (token && role !== 'admin') {
        try {
          const favRes = await favoriteApi.check(Number(productId))
          if (favRes.code === 0 && favRes.data) {
            isFavorite.value = (favRes.data as any)?.is_favorited || (favRes.data as any)?.favorited || false
          }
        } catch {
          // 忽略收藏检查失败
        }
      }
    } else {
      console.error('获取商品详情失败:', res.message)
    }
  } catch (err: any) {
    console.error('获取商品详情失败:', err)
  } finally {
    loading.value = false
  }
}

function decreaseQuantity() {
  if (quantity.value > 1) {
    quantity.value--
  }
}

function increaseQuantity() {
  if (product.value && quantity.value < product.value.stock) {
    quantity.value++
  }
}

async function toggleFavorite() {
  if (!product.value) return
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
    return
  }
  favoriteLoading.value = true
  try {
    if (isFavorite.value) {
      await favoriteApi.remove(product.value.id)
      isFavorite.value = false
    } else {
      await favoriteApi.add(product.value.id)
      isFavorite.value = true
    }
  } catch (err) {
    console.error('收藏操作失败:', err)
  } finally {
    favoriteLoading.value = false
  }
}

async function addToCart() {
  if (!product.value) return
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
    return
  }
  addCartLoading.value = true
  try {
    await cartStore.addItem(product.value.id, quantity.value)
    alert('已加入购物车')
  } catch (err) {
    console.error('加入购物车失败:', err)
  } finally {
    addCartLoading.value = false
  }
}

async function buyNow() {
  if (!product.value) return
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
    return
  }
  buyNowLoading.value = true
  try {
    // 先加入购物车
    await cartStore.addItem(product.value.id, quantity.value)
    // 跳转购物车
    router.push('/cart')
  } catch (err) {
    console.error('购买操作失败:', err)
  } finally {
    buyNowLoading.value = false
  }
}

onMounted(() => {
  fetchProduct()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <div class="mx-4 md:mx-8 lg:mx-12 py-8">
      <!-- 加载中 -->
      <div v-if="loading" class="animate-pulse space-y-6">
        <div class="bg-white rounded-2xl shadow-sm p-6">
          <div class="grid lg:grid-cols-12 gap-8">
            <div class="lg:col-span-5">
              <div class="aspect-square bg-gray-200 rounded-xl"></div>
            </div>
            <div class="lg:col-span-7 space-y-4">
              <div class="h-8 bg-gray-200 rounded w-3/4"></div>
              <div class="h-4 bg-gray-200 rounded w-full"></div>
              <div class="h-12 bg-gray-200 rounded w-1/3"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 商品不存在 -->
      <div v-else-if="!product" class="text-center py-20">
        <div class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <ShoppingCart class="w-10 h-10 text-gray-400" />
        </div>
        <p class="text-gray-500 mb-4">商品不存在或已下架</p>
        <button @click="router.push('/products')" class="px-6 py-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors">
          返回商品列表
        </button>
      </div>

      <!-- 商品详情 -->
      <div v-else class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div class="grid lg:grid-cols-12 gap-8 p-6">
          <div class="lg:col-span-5">
            <div class="space-y-4">
              <div class="relative bg-gray-100 rounded-xl overflow-hidden aspect-square">
                <img 
                  :src="product.image_url" 
                  :alt="product.name"
                  class="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>

          <div class="lg:col-span-7">
            <nav class="flex items-center gap-2 text-sm text-gray-500 mb-4">
              <router-link to="/" class="hover:text-indigo-600 transition-colors">首页</router-link>
              <ArrowRight class="w-4 h-4" />
              <router-link to="/products" class="hover:text-indigo-600 transition-colors">商品列表</router-link>
              <ArrowRight class="w-4 h-4" />
              <span class="text-gray-700">{{ product.name }}</span>
            </nav>

            <div class="flex items-start justify-between mb-6">
              <div>
                <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-2">{{ product.name }}</h1>
                <p class="text-gray-600">{{ product.description }}</p>
              </div>
              <!-- 管理员隐藏收藏按钮 -->
              <button
                v-if="!isAdmin"
                @click="toggleFavorite"
                :disabled="favoriteLoading"
                :class="[
                  'p-3 rounded-full transition-all duration-300',
                  isFavorite ? 'bg-red-50 text-red-500' : 'bg-gray-100 text-gray-400 hover:bg-red-50 hover:text-red-500'
                ]"
              >
                <Heart :class="['w-6 h-6', isFavorite ? 'fill-current' : '']" />
              </button>
              <!-- 管理员预览标识 -->
              <span v-if="isAdmin" class="px-3 py-1.5 bg-gray-100 text-gray-500 text-xs rounded-full flex items-center gap-1">
                <Eye class="w-3 h-3" />
                预览模式
              </span>
            </div>

            <div class="bg-gray-50 rounded-xl p-4 mb-6">
              <div class="flex items-baseline gap-3">
                <span class="text-3xl md:text-4xl font-extrabold text-rose-600">¥{{ product.price }}</span>
                <span v-if="product.discount" class="text-lg text-gray-400 line-through">
                  ¥{{ Math.round(product.price / (1 - product.discount / 100)) }}
                </span>
                <span 
                  v-if="product.discount" 
                  class="px-2 py-1 bg-red-100 text-red-600 text-sm font-medium rounded-full"
                >
                  {{ product.discount }}% OFF
                </span>
              </div>
              <div class="mt-2 flex items-center gap-4 text-sm text-gray-500">
                <span>已售 {{ product.sales || 0 }} 件</span>
                <span>库存 {{ product.stock }} 件</span>
              </div>
            </div>

            <div class="mb-6">
              <h3 class="text-sm font-medium text-gray-700 mb-3">数量</h3>
              <div class="flex items-center gap-4">
                <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden">
                  <button 
                    @click="decreaseQuantity"
                    :disabled="quantity === 1"
                    :class="[
                      'w-10 h-10 flex items-center justify-center transition-colors',
                      quantity === 1 ? 'text-gray-300 cursor-not-allowed' : 'text-gray-600 hover:bg-gray-100'
                    ]"
                  >
                    <Minus class="w-4 h-4" />
                  </button>
                  <span class="w-12 h-10 flex items-center justify-center text-gray-900 font-medium">
                    {{ quantity }}
                  </span>
                  <button 
                    @click="increaseQuantity"
                    :disabled="quantity >= product.stock"
                    :class="[
                      'w-10 h-10 flex items-center justify-center transition-colors',
                      quantity >= product.stock ? 'text-gray-300 cursor-not-allowed' : 'text-gray-600 hover:bg-gray-100'
                    ]"
                  >
                    <Plus class="w-4 h-4" />
                  </button>
                </div>
                <span class="text-sm text-gray-500">库存 {{ product.stock }} 件</span>
              </div>
            </div>

            <div v-if="isAdmin" class="flex gap-4">
              <div class="flex-1 py-3 bg-gray-100 text-gray-400 rounded-xl font-medium text-center text-sm">
                预览模式 — 无法购买
              </div>
            </div>
            <div v-else class="flex gap-4">
              <button
                @click="addToCart"
                :disabled="addCartLoading || product.stock === 0"
                class="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-all duration-300 hover:shadow-lg hover:shadow-indigo-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ShoppingCart class="w-5 h-5" />
                {{ addCartLoading ? '加入中...' : '加入购物车' }}
              </button>
              <button
                @click="buyNow"
                :disabled="buyNowLoading || product.stock === 0"
                class="flex-1 px-6 py-3 bg-gray-900 text-white rounded-xl font-medium hover:bg-gray-800 transition-all duration-300 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ buyNowLoading ? '处理中...' : '立即购买' }}
              </button>
            </div>

            <div class="mt-8 pt-8 border-t border-gray-100">
              <div class="grid grid-cols-3 gap-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center">
                    <Truck class="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">顺丰包邮</p>
                    <p class="text-xs text-gray-500">24小时内发货</p>
                  </div>
                </div>
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-green-50 rounded-full flex items-center justify-center">
                    <Shield class="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">正品保障</p>
                    <p class="text-xs text-gray-500">官方授权</p>
                  </div>
                </div>
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-orange-50 rounded-full flex items-center justify-center">
                    <RefreshCw class="w-5 h-5 text-orange-600" />
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">7天无理由</p>
                    <p class="text-xs text-gray-500">退换货无忧</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="product" class="mt-8 bg-white rounded-2xl shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-6">商品详情</h2>
        <div class="prose prose-gray max-w-none">
          <p class="text-gray-600 whitespace-pre-wrap">{{ product.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
