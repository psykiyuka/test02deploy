<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Heart, ShoppingCart, Trash2, ArrowLeft } from 'lucide-vue-next'
import { favoriteApi, type FavoriteItem } from '@/utils/favoriteApi'
import { useCartStore } from '@/stores/cart'

const router = useRouter()
const cartStore = useCartStore()
const items = ref<FavoriteItem[]>([])
const loading = ref(true)
const removing = ref<number | null>(null)

onMounted(async () => {
  try {
    const res: any = await favoriteApi.list(1, 100)
    if (res.code === 0) {
      items.value = res.data.items
    }
  } finally {
    loading.value = false
  }
})

async function removeFavorite(productId: number) {
  if (removing.value !== null) return
  removing.value = productId
  try {
    const res: any = await favoriteApi.remove(productId)
    if (res.code === 0) {
      items.value = items.value.filter(i => i.id !== productId)
    }
  } catch {
    alert('操作失败')
  } finally {
    removing.value = null
  }
}

function goToDetail(id: number) {
  router.push({ name: 'product-detail', params: { id } })
}

function addToCart(product: FavoriteItem) {
  cartStore.addItem(product.id, 1)
  alert('已加入购物车')
}
</script>

<template>
  <div>
    <div class="flex items-center gap-4 mb-8">
      <button
        @click="router.back()"
        class="p-2 rounded-xl hover:bg-gold-50 text-charcoal/40 hover:text-gold-500 transition-colors cursor-pointer"
      >
        <ArrowLeft class="w-5 h-5" />
      </button>
      <h1 class="font-display text-2xl text-charcoal">我的收藏</h1>
      <span class="text-sm text-charcoal/40">共 {{ items.length }} 件商品</span>
    </div>

    <div v-if="loading" class="space-y-4">
      <div v-for="i in 3" :key="i" class="skeleton h-28 rounded-2xl" />
    </div>

    <div v-else-if="items.length === 0" class="text-center py-24">
      <div class="w-20 h-20 mx-auto mb-6 rounded-full bg-rose-50 flex items-center justify-center">
        <Heart class="w-10 h-10 text-rose-300" />
      </div>
      <p class="text-charcoal/40 text-lg mb-4">收藏夹还是空的</p>
        <button
        @click="router.push('/products')"
        class="px-6 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-200 cursor-pointer"
      >
        去逛逛
      </button>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="item in items"
        :key="item.favorite_id"
        class="bg-white rounded-2xl p-4 flex items-center gap-4 hover:shadow-lg hover:shadow-gold-50 transition-all cursor-pointer group"
        @click="goToDetail(item.id)"
      >
        <div class="w-20 h-20 shrink-0 rounded-xl overflow-hidden bg-gradient-to-br from-gold-50 to-cream">
          <img
            v-if="item.image_url"
            :src="item.image_url"
            :alt="item.name"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center">
            <ShoppingCart class="w-8 h-8 text-gold-200/50" />
          </div>
        </div>

        <div class="flex-1 min-w-0">
          <h3 class="font-semibold text-charcoal text-sm line-clamp-1 mb-1">{{ item.name }}</h3>
          <p class="text-xs text-charcoal/40 mb-2">{{ item.category_name }}</p>
          <div class="flex items-center gap-3">
            <span class="text-lg font-bold text-gold-500">¥{{ Number(item.price).toFixed(2) }}</span>
            <span
              class="text-xs px-2 py-0.5 rounded-full font-medium"
              :class="item.stock > 0 ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-500'"
            >
              {{ item.stock > 0 ? '有货' : '缺货' }}
            </span>
          </div>
        </div>

        <div class="flex items-center gap-2 shrink-0" @click.stop>
          <button
            v-if="item.stock > 0"
            @click="addToCart(item)"
            class="px-4 py-2 bg-gradient-to-r from-gold-400 to-gold-500 text-white rounded-lg text-xs font-semibold hover:from-gold-500 hover:to-gold-600 transition-all cursor-pointer flex items-center gap-1"
          >
            <ShoppingCart class="w-3.5 h-3.5" />
            加入购物车
          </button>
          <button
            @click="removeFavorite(item.id)"
            :disabled="removing === item.id"
            class="p-2 rounded-lg text-charcoal/30 hover:text-rose-500 hover:bg-rose-50 transition-colors cursor-pointer disabled:opacity-50"
            :title="'取消收藏'"
          >
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
