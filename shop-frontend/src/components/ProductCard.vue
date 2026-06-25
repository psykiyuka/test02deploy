<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import { Package, ShoppingCart, Heart, Star } from 'lucide-vue-next'
import type { Product } from '../types'
import { favoriteApi } from '../utils/favoriteApi'

const props = defineProps<{
  product: Product
}>()

const router = useRouter()
const cart = useCartStore()
const isHovered = ref(false)
const isLiked = ref(false)
const isAdmin = ref(localStorage.getItem('role') === 'admin')
const isFavoriting = ref(false)

function goToDetail() {
  router.push({ name: 'product-detail', params: { id: props.product.id } })
}

function handleAddToCart(e: Event) {
  e.stopPropagation()
  cart.addItem(props.product.id, 1)
}

// 检查是否已收藏
onMounted(async () => {
  try {
    const res: any = await favoriteApi.check(props.product.id)
    if (res.code === 0) {
      isLiked.value = res.data.is_favorited
    }
  } catch {}
})

async function toggleLike(e: Event) {
  e.stopPropagation()
  if (isFavoriting.value) return
  isFavoriting.value = true
  try {
    if (isLiked.value) {
      const res: any = await favoriteApi.remove(props.product.id)
      if (res.code === 0) isLiked.value = false
    } else {
      const res: any = await favoriteApi.add(props.product.id)
      if (res.code === 0) isLiked.value = true
    }
  } catch (err: any) {
    alert(err.response?.data?.message || '操作失败，请先登录')
  } finally {
    isFavoriting.value = false
  }
}
</script>

<template>
  <div
    class="group relative bg-white rounded-2xl overflow-hidden cursor-pointer transition-all duration-500 hover:shadow-2xl hover:shadow-gold-100/40 hover:-translate-y-2"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
    @click="goToDetail"
  >
    <div class="aspect-[4/5] overflow-hidden bg-gradient-to-br from-gold-50 via-warm-white to-cream relative">
      <div class="absolute top-3 left-3 z-20 flex flex-col gap-2">
        <button
          class="w-9 h-9 rounded-full bg-white/90 backdrop-blur-md shadow-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transform translate-x-[-10px] group-hover:translate-x-0 transition-all duration-300 hover:bg-white hover:scale-105 cursor-pointer"
          :class="{ 'text-rose-500': isLiked, 'text-charcoal/40': !isLiked }"
          @click="toggleLike"
        >
          <Heart class="w-4 h-4" :fill="isLiked ? 'currentColor' : 'none'" />
        </button>
      </div>

      <div v-if="(product.discount ?? 0) > 0" class="absolute top-3 right-3 z-20">
        <div class="px-3 py-1.5 bg-gradient-to-r from-terracotta to-rose-500 rounded-full text-white text-xs font-bold shadow-lg shadow-terracotta/30 transform rotate-6 hover:rotate-0 transition-transform duration-300">
          -{{ product.discount }}%
        </div>
      </div>

      <img
        v-if="product.image_url"
        :src="product.image_url"
        :alt="product.name"
        class="w-full h-full object-cover transition-all duration-700 group-hover:scale-115"
        loading="lazy"
      />
      <div v-else class="w-full h-full flex items-center justify-center">
        <div class="text-center">
          <Package class="w-16 h-16 text-gold-200/50 mx-auto mb-3" />
          <span class="text-sm text-gold-300/60">暂无图片</span>
        </div>
      </div>

      <div
        v-if="product.stock <= 0"
        class="absolute inset-0 bg-charcoal/50 backdrop-blur-sm flex items-center justify-center"
      >
        <span class="px-8 py-3 bg-white/95 text-charcoal/70 rounded-full text-sm font-bold backdrop-blur-md shadow-xl">已售罄</span>
      </div>

      <div class="absolute inset-0 bg-gradient-to-t from-charcoal/30 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      <button
        v-if="product.stock > 0 && !isAdmin"
        class="absolute bottom-4 right-4 w-12 h-12 rounded-full bg-gradient-to-r from-gold-400 to-gold-500 backdrop-blur-md shadow-xl shadow-gold-500/30 flex items-center justify-center opacity-0 group-hover:opacity-100 translate-y-4 group-hover:translate-y-0 transition-all duration-300 hover:from-gold-500 hover:to-gold-600 hover:shadow-gold-500/50 hover:scale-110 text-white"
        @click="handleAddToCart"
      >
        <ShoppingCart class="w-5 h-5" />
      </button>

      <div class="absolute bottom-4 left-4 opacity-0 group-hover:opacity-100 transform translate-y-4 group-hover:translate-y-0 transition-all duration-300">
        <div class="flex items-center gap-1">
          <Star class="w-4 h-4 text-amber-400 fill-amber-400" />
          <span class="text-xs text-white/90 font-medium">4.8</span>
          <span class="text-xs text-white/60">|</span>
          <span class="text-xs text-white/80">{{ product.sales }}人购买</span>
        </div>
      </div>
    </div>

    <div class="p-5">
      <div class="flex items-center gap-2 mb-2">
        <span class="px-2.5 py-0.5 bg-gold-50 text-gold-600 text-xs font-medium rounded-full">
          精选
        </span>
        <span class="text-xs text-charcoal/40">{{ product.category_name }}</span>
      </div>

      <h3 class="font-semibold text-charcoal text-sm leading-snug mb-3 line-clamp-2 min-h-[40px]">
        {{ product.name }}
      </h3>

      <p class="text-xs text-charcoal/40 mb-4 line-clamp-1">
        {{ product.description }}
      </p>

      <div class="flex items-end justify-between">
        <div class="flex items-baseline gap-1">
          <span class="text-xs text-gold-500 font-semibold">¥</span>
          <span class="text-xl font-bold text-gold-500 tracking-tight">
            {{ (product.discount ?? 0) > 0 ? Math.floor(Number(product.price) * (1 - (product.discount ?? 0) / 100)) : Math.floor(Number(product.price)) }}
          </span>
          <span v-if="(product.discount ?? 0) > 0" class="text-xs text-charcoal/30 line-through">
            ¥{{ Math.floor(Number(product.price)) }}
          </span>
        </div>
        <span
          class="text-xs font-medium px-2 py-1 rounded-full"
          :class="product.stock > 10 ? 'bg-emerald-50 text-emerald-600' : product.stock > 0 ? 'bg-amber-50 text-amber-600' : 'bg-rose-50 text-rose-500'"
        >
          {{ product.stock > 10 ? '现货' : product.stock > 0 ? `${product.stock}件` : '缺货' }}
        </span>
      </div>
    </div>
  </div>
</template>
