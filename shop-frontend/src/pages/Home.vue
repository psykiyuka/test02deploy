<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  ChevronLeft, 
  ChevronRight, 
  ShoppingCart, 
  Smartphone, 
  Plug, 
  Briefcase, 
  Sparkles 
} from 'lucide-vue-next'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/utils/api'
import type { Product } from '@/types'

const router = useRouter()
const cart = useCartStore()
const auth = useAuthStore()

const currentSlide = ref(0)
const products = ref<Product[]>([])
const loading = ref(true)

const categories = [
  { id: 1, name: '数码', icon: Smartphone },
  { id: 2, name: '电器', icon: Plug },
  { id: 3, name: '办公', icon: Briefcase },
]

const banners = [
  { id: 1, title: '秋季新品', subtitle: '', description: '全场低至5折起', image: '/src/assets/banner1.png' },
  { id: 2, title: '数码狂欢', subtitle: '科技盛宴', description: '新品首发特惠', image: '/src/assets/banner2.jpg' },
  { id: 3, title: '时尚穿搭', subtitle: '潮流前线', description: '打造你的专属风格', image: '/src/assets/banner3.png' },
]

async function fetchHotProducts() {
  loading.value = true
  try {
    const res = await api.get<any>('/c-endpoint/products/hot')
    if (res.code === 0) {
      products.value = Array.isArray(res.data) ? res.data : []
    }
  } catch (err) {
    console.error('获取热门商品失败:', err)
  } finally {
    loading.value = false
  }
}

function prevSlide() {
  currentSlide.value = currentSlide.value === 0 ? banners.length - 1 : currentSlide.value - 1
}

function nextSlide() {
  currentSlide.value = currentSlide.value === banners.length - 1 ? 0 : currentSlide.value + 1
}

function goToCategory(categoryId: number) {
  router.push({ name: 'products', query: { category: String(categoryId) } })
}

function goToProduct(productId: number) {
  router.push({ name: 'product-detail', params: { id: productId } })
}

async function addToCart(productId: number, event?: Event) {
  if (event) event.stopPropagation()
  if (!auth.isLoggedIn) {
    router.push({ name: 'login' })
    return
  }
  try {
    await cart.addItem(productId, 1)
  } catch {
    // 静态数据模式下忽略错误
  }
}

onMounted(() => {
  fetchHotProducts()
})
</script>

<template>
  <div class="min-h-screen bg-[#F9FAFB]">
    <section class="relative overflow-hidden rounded-2xl mx-4 md:mx-8 lg:mx-12 mt-6">
      <div class="relative h-64 md:h-80 lg:h-96">
        <div 
          v-for="(banner, index) in banners" 
          :key="banner.id"
          :class="[
            'absolute inset-0 transition-all duration-500 ease-in-out',
            index === currentSlide ? 'opacity-100 scale-100' : 'opacity-0 scale-105'
          ]"
        >
          <img :src="banner.image" :alt="banner.title" class="absolute inset-0 w-full h-full object-cover" />
          <div class="absolute inset-0 bg-black/30"></div>
          <div class="relative h-full flex items-center px-8 md:px-16">
            <div class="text-white max-w-lg">
              <p class="text-lg md:text-xl font-medium mb-2">{{ banner.subtitle }}</p>
              <h1 class="text-3xl md:text-5xl font-bold mb-4">{{ banner.title }}</h1>
              <p class="text-lg md:text-xl opacity-90 mb-6">{{ banner.description }}</p>
              <router-link to="/products" class="inline-block px-8 py-3 bg-white text-gray-900 font-semibold rounded-full hover:bg-gray-100 transition-all duration-300 hover:scale-105 shadow-lg">
                立即选购
              </router-link>
            </div>
          </div>
        </div>
        
        <button 
          @click="prevSlide"
          class="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-white hover:bg-white/30 transition-all duration-300"
        >
          <ChevronLeft class="w-6 h-6" />
        </button>
        <button 
          @click="nextSlide"
          class="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-white hover:bg-white/30 transition-all duration-300"
        >
          <ChevronRight class="w-6 h-6" />
        </button>
        
        <div class="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2">
          <button 
            v-for="(_, index) in banners" 
            :key="index"
            @click="currentSlide = index"
            :class="[
              'w-2 h-2 rounded-full transition-all duration-300',
              index === currentSlide ? 'bg-white w-6' : 'bg-white/50'
            ]"
          ></button>
        </div>
      </div>
    </section>

    <section class="mx-4 md:mx-8 lg:mx-12 mt-12">
      <div class="flex justify-center">
        <div class="flex gap-6 md:gap-10">
          <div 
            v-for="category in categories" 
            :key="category.id"
            class="flex flex-col items-center cursor-pointer group"
            @click="goToCategory(category.id)"
          >
            <div class="w-16 h-16 md:w-20 md:h-20 rounded-full bg-gray-100 flex items-center justify-center group-hover:-translate-y-1 group-hover:shadow-lg group-hover:shadow-indigo-200 transition-all duration-300">
              <component :is="category.icon" class="w-7 h-7 md:w-8 md:h-8 text-gray-600 group-hover:text-indigo-600 transition-colors duration-300" />
            </div>
            <span class="mt-3 text-sm md:text-base font-medium text-gray-700">{{ category.name }}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="mx-4 md:mx-8 lg:mx-12 mt-12">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-2">
          <Sparkles class="w-5 h-5 text-indigo-600" />
          <h2 class="text-xl md:text-2xl font-bold text-gray-900">热门推荐</h2>
        </div>
        <router-link to="/products" class="text-indigo-600 hover:text-indigo-700 font-medium text-sm hover:underline transition-colors duration-300">
          查看更多 →
        </router-link>
      </div>
      
      <div v-if="loading" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
        <div v-for="i in 4" :key="i" class="bg-white rounded-xl overflow-hidden shadow-sm">
          <div class="w-full aspect-square bg-gray-100 animate-pulse"></div>
          <div class="p-3 md:p-4 space-y-2">
            <div class="h-4 bg-gray-100 rounded animate-pulse"></div>
            <div class="h-3 bg-gray-100 rounded animate-pulse w-2/3"></div>
            <div class="h-5 bg-gray-100 rounded animate-pulse w-1/3"></div>
          </div>
        </div>
      </div>

      <div v-else-if="products.length === 0" class="py-16 text-center">
        <p class="text-gray-500">暂无热门商品</p>
      </div>

      <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
        <div 
          v-for="product in products" 
          :key="product.id"
          class="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 group cursor-pointer"
          @click="goToProduct(product.id)"
        >
          <div class="relative overflow-hidden">
            <img 
              :src="product.image_url" 
              :alt="product.name"
              class="w-full aspect-square object-cover group-hover:scale-105 transition-transform duration-500"
            />
            <div 
              v-if="product.discount" 
              class="absolute top-3 left-3 px-2 py-1 bg-red-500 text-white text-xs font-medium rounded-full"
            >
              {{ product.discount }}% OFF
            </div>
            <button 
              @click="addToCart(product.id, $event)"
              class="absolute right-3 bottom-3 w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-lg opacity-0 group-hover:opacity-100 transform translate-y-2 group-hover:translate-y-0 transition-all duration-300 hover:bg-indigo-600 hover:text-white"
            >
              <ShoppingCart class="w-5 h-5" />
            </button>
          </div>
          
          <div class="p-3 md:p-4">
            <h3 class="text-sm md:text-base font-medium text-gray-900 truncate mb-1">{{ product.name }}</h3>
            <p class="text-xs text-gray-500 mb-2 line-clamp-1">{{ product.description }}</p>
            <div class="flex items-baseline gap-2">
              <span class="text-lg md:text-xl font-bold text-rose-600">¥{{ product.price }}</span>
              <span 
                v-if="product.discount" 
                class="text-xs text-gray-400 line-through"
              >
                ¥{{ Math.round(product.price / (1 - product.discount / 100)) }}
              </span>
            </div>
            <p class="text-xs text-gray-400 mt-2">已售 {{ product.sales }} 件</p>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>