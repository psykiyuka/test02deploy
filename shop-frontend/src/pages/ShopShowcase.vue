<script setup lang="ts">
/**
 * ShopShowcase.vue — 电商平台展示页
 * 包含：顶部导航栏、Hero Banner、商品网格、购物车侧边栏
 * 技术栈：Vue 3 (Composition API) + Tailwind CSS + Lucide Vue Next
 */
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import {
  ShoppingCart, Search, User, X, Plus, Minus, Trash2,
  ChevronRight, Star, Zap, Shield, Truck, Heart,
  ArrowRight, Sparkles, Tag, TrendingUp, Package,
} from 'lucide-vue-next'

// ─────────────────────────────────────────────
// 类型定义
// ─────────────────────────────────────────────
interface Product {
  id: number
  name: string
  price: number
  originalPrice: number
  rating: number
  sales: number
  badge?: string       // '热卖' | '折扣' | '新品' | '限时'
  badgeType?: string   // 'hot' | 'sale' | 'new' | 'limited'
  image: string
  category: string
  discount?: number    // 折扣百分比，如 20 = 八折
}

interface CartItem {
  product: Product
  quantity: number
}

// ─────────────────────────────────────────────
// 商品数据（模拟）
// ─────────────────────────────────────────────
const products = ref<Product[]>([
  {
    id: 1, name: '极光无线蓝牙耳机 Pro', price: 399, originalPrice: 699,
    rating: 4.9, sales: 3841, badge: '热卖', badgeType: 'hot',
    image: 'https://placehold.co/400x400/111827/ffffff?text=耳机',
    category: '数码', discount: 43,
  },
  {
    id: 2, name: '碳纤维机械键盘 RGB', price: 688, originalPrice: 988,
    rating: 4.8, sales: 2156, badge: '折扣', badgeType: 'sale',
    image: 'https://placehold.co/400x400/1e3a5f/ffffff?text=键盘',
    category: '数码', discount: 30,
  },
  {
    id: 3, name: '轻奢真皮简约钱包', price: 258, originalPrice: 458,
    rating: 4.7, sales: 5320, badge: '热卖', badgeType: 'hot',
    image: 'https://placehold.co/400x400/2d1b0e/ffffff?text=钱包',
    category: '配件',
  },
  {
    id: 4, name: '智能运动手表 Ultra', price: 1299, originalPrice: 1899,
    rating: 4.9, sales: 1289, badge: '限时', badgeType: 'limited',
    image: 'https://placehold.co/400x400/0a1628/ffffff?text=手表',
    category: '穿戴', discount: 32,
  },
  {
    id: 5, name: '全铝 USB-C 扩展坞', price: 319, originalPrice: 499,
    rating: 4.6, sales: 7843, badge: '折扣', badgeType: 'sale',
    image: 'https://placehold.co/400x400/1c2833/ffffff?text=扩展坞',
    category: '数码', discount: 36,
  },
  {
    id: 6, name: '小米 15 寸便携显示器', price: 799, originalPrice: 1199,
    rating: 4.8, sales: 4102, badge: '新品', badgeType: 'new',
    image: 'https://placehold.co/400x400/0d1f2d/ffffff?text=显示器',
    category: '数码',
  },
  {
    id: 7, name: '航空铝合金笔记本支架', price: 189, originalPrice: 299,
    rating: 4.7, sales: 9231, badge: '热卖', badgeType: 'hot',
    image: 'https://placehold.co/400x400/1a1a2e/ffffff?text=支架',
    category: '配件', discount: 37,
  },
  {
    id: 8, name: '马卡龙速干毛巾套装', price: 128, originalPrice: 198,
    rating: 4.5, sales: 12048, badge: '折扣', badgeType: 'sale',
    image: 'https://placehold.co/400x400/f97316/ffffff?text=毛巾',
    category: '生活', discount: 35,
  },
])

// ─────────────────────────────────────────────
// 购物车状态
// ─────────────────────────────────────────────
const cartOpen = ref(false)
const cartItems = ref<CartItem[]>([])

const cartTotal = computed(() =>
  cartItems.value.reduce((sum, i) => sum + i.product.price * i.quantity, 0)
)

const cartCount = computed(() =>
  cartItems.value.reduce((sum, i) => sum + i.quantity, 0)
)

function addToCart(product: Product) {
  const existing = cartItems.value.find(i => i.product.id === product.id)
  if (existing) {
    existing.quantity++
  } else {
    cartItems.value.push({ product, quantity: 1 })
  }
  // 加入时短暂弹出购物车提示
  cartBounce.value = true
  setTimeout(() => { cartBounce.value = false }, 400)
}

function removeFromCart(id: number) {
  cartItems.value = cartItems.value.filter(i => i.product.id !== id)
}

function changeQty(id: number, delta: number) {
  const item = cartItems.value.find(i => i.product.id === id)
  if (!item) return
  item.quantity += delta
  if (item.quantity <= 0) removeFromCart(id)
}

// ─────────────────────────────────────────────
// 搜索状态
// ─────────────────────────────────────────────
const searchQuery = ref('')
const searchFocused = ref(false)

// ─────────────────────────────────────────────
// Hero 轮播
// ─────────────────────────────────────────────
const heroSlides = [
  {
    title: '不止于快\n更在于精',
    subtitle: '甄选全球顶级数码好物，每一件都是生活的升华',
    tag: '限时特惠 · 全场8折起',
    cta: '立即抢购',
    accent: '#F97316',
    bg: 'from-[#0a0f1e] via-[#111827] to-[#1a2540]',
    img: 'https://placehold.co/800x500/0a0f1e/F97316?text=Premium+Tech',
    stats: [{ v: '500+', l: '精选好物' }, { v: '98%', l: '好评率' }, { v: '50W+', l: '用户信赖' }],
  },
  {
    title: '科技赋能\n智慧生活',
    subtitle: '探索前沿科技产品，让每天都充满惊喜与效率',
    tag: '新品首发 · 到手即用',
    cta: '探索新品',
    accent: '#8B5CF6',
    bg: 'from-[#0d0d2b] via-[#1a1040] to-[#0f172a]',
    img: 'https://placehold.co/800x500/0d0d2b/8B5CF6?text=Smart+Life',
    stats: [{ v: '30+', l: '顶级品牌' }, { v: '7×24', l: '客服支持' }, { v: '极速', l: '发货配送' }],
  },
]
const currentSlide = ref(0)
const slideTimer = ref<ReturnType<typeof setInterval> | null>(null)

function startSlideTimer() {
  slideTimer.value = setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % heroSlides.length
  }, 4000)
}

// ─────────────────────────────────────────────
// 收藏状态
// ─────────────────────────────────────────────
const liked = reactive(new Set<number>())
function toggleLike(id: number) {
  if (liked.has(id)) liked.delete(id)
  else liked.add(id)
}

// ─────────────────────────────────────────────
// Badge 色彩映射
// ─────────────────────────────────────────────
const badgeStyles: Record<string, string> = {
  hot:     'bg-orange-500 text-white',
  sale:    'bg-rose-500 text-white',
  new:     'bg-emerald-500 text-white',
  limited: 'bg-purple-500 text-white',
}

// ─────────────────────────────────────────────
// 购物车弹跳动画
// ─────────────────────────────────────────────
const cartBounce = ref(false)

// ─────────────────────────────────────────────
// 分类过滤
// ─────────────────────────────────────────────
const activeCategory = ref('全部')
const categories = ['全部', '数码', '穿戴', '配件', '生活']

const filteredProducts = computed(() => {
  let list = products.value
  if (activeCategory.value !== '全部') {
    list = list.filter(p => p.category === activeCategory.value)
  }
  if (searchQuery.value.trim()) {
    list = list.filter(p =>
      p.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }
  return list
})

// ─────────────────────────────────────────────
// 滚动 Header 效果
// ─────────────────────────────────────────────
const scrolled = ref(false)
function onScroll() { scrolled.value = window.scrollY > 30 }

onMounted(() => {
  window.addEventListener('scroll', onScroll)
  startSlideTimer()
})
onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  if (slideTimer.value) clearInterval(slideTimer.value)
})
</script>

<template>
  <!-- ░░░ 最外层容器 ░░░ -->
  <div class="min-h-screen bg-[#f8f9fb] font-sans select-none">

    <!-- ══════════════════════════════════════════
         顶部导航栏 Header
    ══════════════════════════════════════════ -->
    <header
      :class="[
        'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
        scrolled
          ? 'bg-[#111827]/95 backdrop-blur-xl shadow-2xl shadow-black/30'
          : 'bg-[#111827]',
      ]"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center gap-4 h-16 lg:h-18">

          <!-- Logo -->
          <div class="flex items-center gap-2.5 shrink-0 cursor-pointer group">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-orange-500 to-amber-400 flex items-center justify-center shadow-lg shadow-orange-500/25 group-hover:scale-105 transition-transform duration-200">
              <Zap class="w-4 h-4 text-white" fill="currentColor" />
            </div>
            <span class="hidden sm:block text-white font-bold text-lg tracking-tight">
              Lux<span class="text-orange-400">Shop</span>
            </span>
          </div>

          <!-- 搜索框 -->
          <div class="flex-1 max-w-xl mx-auto">
            <div
              :class="[
                'relative flex items-center rounded-xl transition-all duration-300',
                searchFocused
                  ? 'ring-2 ring-orange-500/60 shadow-lg shadow-orange-500/10'
                  : 'ring-1 ring-white/10',
              ]"
            >
              <Search
                class="absolute left-3 w-4 h-4 transition-colors duration-200"
                :class="searchFocused ? 'text-orange-400' : 'text-gray-400'"
              />
              <input
                v-model="searchQuery"
                @focus="searchFocused = true"
                @blur="searchFocused = false"
                type="text"
                placeholder="搜索商品、品牌、分类…"
                class="w-full bg-white/8 text-white placeholder-gray-500 pl-10 pr-4 py-2.5 rounded-xl text-sm outline-none bg-[#1f2937] focus:bg-[#252f3e] transition-colors duration-200"
              />
              <!-- 搜索快捷键提示 -->
              <span
                v-if="!searchFocused && !searchQuery"
                class="hidden lg:flex absolute right-3 items-center gap-1 text-gray-600 text-xs pointer-events-none"
              >
                <kbd class="px-1.5 py-0.5 rounded-md bg-white/5 border border-white/10 font-mono text-[10px]">⌘</kbd>
                <kbd class="px-1.5 py-0.5 rounded-md bg-white/5 border border-white/10 font-mono text-[10px]">K</kbd>
              </span>
            </div>
          </div>

          <!-- 右侧操作区 -->
          <div class="flex items-center gap-2 shrink-0">
            <!-- 购物车 -->
            <button
              @click="cartOpen = true"
              :class="['relative p-2.5 rounded-xl text-gray-300 hover:text-white hover:bg-white/10 transition-all duration-200 cursor-pointer', cartBounce && 'animate-bounce']"
            >
              <ShoppingCart class="w-5 h-5" />
              <span
                v-if="cartCount > 0"
                class="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] bg-orange-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center px-1 shadow-lg shadow-orange-500/40 animate-scale-in"
              >
                {{ cartCount > 99 ? '99+' : cartCount }}
              </span>
            </button>

            <!-- 用户头像 -->
            <button class="hidden sm:flex items-center gap-2 p-1.5 rounded-xl hover:bg-white/10 transition-colors duration-200 cursor-pointer group">
              <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-orange-400 to-rose-500 flex items-center justify-center shadow-md">
                <User class="w-4 h-4 text-white" />
              </div>
            </button>
          </div>

        </div>

        <!-- 分类导航 Tab -->
        <div class="flex items-center gap-1 pb-3 overflow-x-auto scrollbar-hide">
          <button
            v-for="cat in categories"
            :key="cat"
            @click="activeCategory = cat"
            :class="[
              'shrink-0 px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200 cursor-pointer',
              activeCategory === cat
                ? 'bg-orange-500 text-white shadow-md shadow-orange-500/30'
                : 'text-gray-400 hover:text-white hover:bg-white/10',
            ]"
          >
            {{ cat }}
          </button>
        </div>
      </div>
    </header>

    <!-- Header 占位 -->
    <div class="h-[100px] lg:h-[108px]"></div>


    <!-- ══════════════════════════════════════════
         Hero Banner 区
    ══════════════════════════════════════════ -->
    <section class="relative overflow-hidden">
      <!-- 轮播容器 -->
      <div class="relative">
        <div
          v-for="(slide, idx) in heroSlides"
          :key="idx"
          :class="[
            'transition-all duration-700',
            idx === currentSlide ? 'block' : 'hidden',
          ]"
        >
          <div :class="`bg-gradient-to-br ${slide.bg} min-h-[480px] lg:min-h-[560px] flex items-center relative overflow-hidden`">

            <!-- 背景装饰 -->
            <div class="absolute inset-0 overflow-hidden pointer-events-none">
              <div class="absolute -top-32 -right-32 w-[600px] h-[600px] rounded-full opacity-8"
                   :style="`background: radial-gradient(circle, ${slide.accent}22, transparent 70%)`"></div>
              <div class="absolute -bottom-20 -left-20 w-80 h-80 rounded-full opacity-10"
                   :style="`background: radial-gradient(circle, ${slide.accent}33, transparent 70%)`"></div>
              <!-- 网格装饰 -->
              <div class="absolute inset-0 opacity-3"
                   style="background-image: linear-gradient(rgba(255,255,255,.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.03) 1px, transparent 1px); background-size: 40px 40px;"></div>
            </div>

            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full py-16 lg:py-20">
              <div class="grid lg:grid-cols-2 gap-12 items-center">

                <!-- 左：文案区 -->
                <div class="space-y-6 animate-fade-in-up">
                  <!-- 标签 -->
                  <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold"
                       :style="`border-color: ${slide.accent}55; color: ${slide.accent}; background: ${slide.accent}15`">
                    <Sparkles class="w-3 h-3" />
                    {{ slide.tag }}
                  </div>

                  <!-- 主标题 -->
                  <h1 class="text-4xl sm:text-5xl lg:text-6xl font-black text-white leading-tight tracking-tight whitespace-pre-line">
                    {{ slide.title }}
                  </h1>

                  <!-- 副标题 -->
                  <p class="text-gray-400 text-base lg:text-lg max-w-md leading-relaxed">
                    {{ slide.subtitle }}
                  </p>

                  <!-- 统计数字 -->
                  <div class="flex items-center gap-8">
                    <div v-for="stat in slide.stats" :key="stat.l" class="text-center">
                      <div class="text-xl font-black text-white">{{ stat.v }}</div>
                      <div class="text-xs text-gray-500 mt-0.5">{{ stat.l }}</div>
                    </div>
                  </div>

                  <!-- CTA 按钮 -->
                  <div class="flex items-center gap-3 pt-2">
                    <button
                      class="group flex items-center gap-2.5 px-7 py-3.5 rounded-2xl font-bold text-white text-base shadow-xl transition-all duration-300 hover:scale-105 hover:shadow-2xl active:scale-95 cursor-pointer"
                      :style="`background: linear-gradient(135deg, ${slide.accent}, ${slide.accent}cc); box-shadow: 0 8px 32px ${slide.accent}44`"
                    >
                      {{ slide.cta }}
                      <ArrowRight class="w-4 h-4 group-hover:translate-x-1 transition-transform duration-200" />
                    </button>
                    <button class="px-5 py-3.5 rounded-2xl font-semibold text-gray-300 hover:text-white border border-white/10 hover:border-white/20 hover:bg-white/5 transition-all duration-200 cursor-pointer text-sm">
                      了解更多
                    </button>
                  </div>
                </div>

                <!-- 右：图片区 -->
                <div class="flex justify-center animate-gentle-float">
                  <div class="relative">
                    <div class="absolute inset-0 rounded-3xl blur-3xl opacity-20 scale-90"
                         :style="`background: radial-gradient(circle, ${slide.accent}, transparent 70%)`"></div>
                    <img
                      :src="slide.img"
                      alt="Hero Product"
                      class="relative w-full max-w-md rounded-3xl shadow-2xl object-cover border border-white/10"
                      style="aspect-ratio: 16/10"
                    />
                    <!-- 浮动徽章 -->
                    <div class="absolute -bottom-4 -left-4 bg-[#111827] border border-white/10 rounded-2xl p-3 shadow-xl flex items-center gap-2.5 backdrop-blur-sm animate-slide-in-right">
                      <div class="w-9 h-9 rounded-xl flex items-center justify-center" :style="`background: ${slide.accent}25`">
                        <TrendingUp class="w-4.5 h-4.5" :style="`color: ${slide.accent}`" />
                      </div>
                      <div>
                        <div class="text-white text-xs font-bold">本周热销</div>
                        <div class="text-gray-400 text-[11px]">超3000+件已售</div>
                      </div>
                    </div>
                    <div class="absolute -top-4 -right-4 bg-[#111827] border border-white/10 rounded-2xl px-3 py-2 shadow-xl flex items-center gap-1.5 backdrop-blur-sm">
                      <Star class="w-3.5 h-3.5 text-amber-400" fill="currentColor" />
                      <span class="text-white text-xs font-bold">4.9</span>
                    </div>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>

        <!-- 轮播指示器 -->
        <div class="absolute bottom-5 left-1/2 -translate-x-1/2 flex gap-2">
          <button
            v-for="(_, idx) in heroSlides"
            :key="idx"
            @click="currentSlide = idx"
            :class="[
              'rounded-full transition-all duration-300 cursor-pointer',
              idx === currentSlide
                ? 'w-6 h-2 bg-orange-400'
                : 'w-2 h-2 bg-white/30 hover:bg-white/50',
            ]"
          />
        </div>
      </div>
    </section>


    <!-- ══════════════════════════════════════════
         特色服务栏
    ══════════════════════════════════════════ -->
    <section class="bg-[#111827] border-t border-white/5">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
        <div class="grid grid-cols-3 gap-4 lg:gap-8">
          <div v-for="item in [
            { icon: Truck,   label: '极速配送', desc: '次日达', color: 'text-orange-400' },
            { icon: Shield,  label: '品质保障', desc: '假一赔三', color: 'text-emerald-400' },
            { icon: Package, label: '极简退换', desc: '7日无理由', color: 'text-violet-400' },
          ]" :key="item.label"
            class="flex items-center justify-center lg:justify-start gap-3 py-2"
          >
            <component :is="item.icon" :class="['w-5 h-5 shrink-0', item.color]" />
            <div class="hidden sm:block">
              <p class="text-white text-sm font-semibold">{{ item.label }}</p>
              <p class="text-gray-500 text-xs">{{ item.desc }}</p>
            </div>
            <span class="sm:hidden text-gray-300 text-xs font-medium">{{ item.label }}</span>
          </div>
        </div>
      </div>
    </section>


    <!-- ══════════════════════════════════════════
         商品网格 Product Grid
    ══════════════════════════════════════════ -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">

      <!-- 区块标题 -->
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-3">
          <div class="w-1 h-8 bg-gradient-to-b from-orange-500 to-amber-400 rounded-full"></div>
          <div>
            <h2 class="text-xl lg:text-2xl font-black text-gray-900 tracking-tight">
              {{ activeCategory === '全部' ? '精选好物' : activeCategory + '精选' }}
            </h2>
            <p class="text-gray-400 text-sm mt-0.5">{{ filteredProducts.length }} 件商品</p>
          </div>
        </div>
        <button class="hidden sm:flex items-center gap-1.5 text-sm text-orange-500 font-semibold hover:text-orange-600 transition-colors cursor-pointer group">
          查看全部
          <ChevronRight class="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
        </button>
      </div>

      <!-- 商品网格 -->
      <div
        v-if="filteredProducts.length > 0"
        class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-5"
      >
        <div
          v-for="product in filteredProducts"
          :key="product.id"
          class="group relative bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer border border-gray-100/80"
        >

          <!-- 商品图片 -->
          <div class="relative overflow-hidden aspect-square bg-gray-50">
            <img
              :src="product.image"
              :alt="product.name"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            />
            <!-- 渐变遮罩 -->
            <div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

            <!-- Badge -->
            <span
              v-if="product.badge"
              :class="['absolute top-2.5 left-2.5 px-2 py-0.5 rounded-full text-[11px] font-bold tracking-wide shadow-md', badgeStyles[product.badgeType || 'hot']]"
            >
              {{ product.badge }}
            </span>

            <!-- 折扣标签 -->
            <span
              v-if="product.discount"
              class="absolute top-2.5 right-2.5 w-9 h-9 rounded-full bg-orange-500 text-white text-[10px] font-black flex items-center justify-center shadow-lg shadow-orange-500/30 leading-tight text-center"
            >
              -{{ product.discount }}%
            </span>

            <!-- 收藏按钮 -->
            <button
              @click.stop="toggleLike(product.id)"
              :class="[
                'absolute bottom-2.5 right-2.5 w-8 h-8 rounded-full flex items-center justify-center shadow-lg transition-all duration-200 cursor-pointer',
                liked.has(product.id)
                  ? 'bg-rose-500 text-white scale-110'
                  : 'bg-white/90 text-gray-400 opacity-0 group-hover:opacity-100 hover:text-rose-400 backdrop-blur-sm',
              ]"
            >
              <Heart class="w-3.5 h-3.5" :fill="liked.has(product.id) ? 'currentColor' : 'none'" />
            </button>
          </div>

          <!-- 商品信息 -->
          <div class="p-3.5 lg:p-4">

            <!-- 评分与销量 -->
            <div class="flex items-center gap-1.5 mb-2">
              <div class="flex items-center gap-0.5">
                <Star class="w-3 h-3 text-amber-400" fill="currentColor" />
                <span class="text-amber-600 text-[11px] font-semibold">{{ product.rating }}</span>
              </div>
              <span class="text-gray-300 text-[11px]">·</span>
              <span class="text-gray-400 text-[11px]">{{ product.sales.toLocaleString() }} 已售</span>
            </div>

            <!-- 商品名称 -->
            <h3 class="text-gray-900 font-semibold text-sm leading-snug line-clamp-2 mb-3 group-hover:text-gray-700 transition-colors">
              {{ product.name }}
            </h3>

            <!-- 价格区 + 加购按钮 -->
            <div class="flex items-center justify-between gap-2">
              <div>
                <span class="text-orange-500 font-black text-lg leading-none">¥{{ product.price }}</span>
                <span class="text-gray-300 text-xs line-through ml-1.5">¥{{ product.originalPrice }}</span>
              </div>
              <button
                @click.stop="addToCart(product)"
                class="flex items-center gap-1 bg-[#111827] hover:bg-orange-500 text-white text-xs font-semibold px-3 py-1.5 rounded-xl transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer shadow-sm hover:shadow-orange-500/30 hover:shadow-md shrink-0"
              >
                <Plus class="w-3 h-3" />
                加购
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="flex flex-col items-center justify-center py-24 text-center">
        <div class="w-20 h-20 rounded-2xl bg-gray-100 flex items-center justify-center mb-4">
          <Search class="w-9 h-9 text-gray-300" />
        </div>
        <p class="text-gray-900 font-semibold text-lg">没有找到相关商品</p>
        <p class="text-gray-400 text-sm mt-1">换个关键词试试吧</p>
        <button @click="searchQuery = ''; activeCategory = '全部'" class="mt-4 px-5 py-2 bg-orange-500 text-white rounded-xl text-sm font-semibold hover:bg-orange-600 transition-colors cursor-pointer">
          重置搜索
        </button>
      </div>

    </main>


    <!-- ══════════════════════════════════════════
         购物车侧边栏 Drawer
    ══════════════════════════════════════════ -->
    <!-- 遮罩层 -->
    <Transition name="fade-overlay">
      <div
        v-if="cartOpen"
        @click="cartOpen = false"
        class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
      ></div>
    </Transition>

    <!-- 侧边栏本体 -->
    <Transition name="slide-cart">
      <div
        v-if="cartOpen"
        class="fixed top-0 right-0 h-full w-full sm:w-[420px] bg-white z-50 flex flex-col shadow-2xl"
      >

        <!-- 购物车 Header -->
        <div class="flex items-center justify-between px-6 py-5 border-b border-gray-100">
          <div class="flex items-center gap-2.5">
            <ShoppingCart class="w-5 h-5 text-gray-800" />
            <h2 class="text-lg font-black text-gray-900">购物车</h2>
            <span
              v-if="cartCount > 0"
              class="px-2 py-0.5 rounded-full bg-orange-100 text-orange-600 text-xs font-bold"
            >
              {{ cartCount }}
            </span>
          </div>
          <button
            @click="cartOpen = false"
            class="w-8 h-8 rounded-xl bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors cursor-pointer"
          >
            <X class="w-4 h-4 text-gray-600" />
          </button>
        </div>

        <!-- 购物车商品列表 -->
        <div class="flex-1 overflow-y-auto">

          <!-- 空购物车 -->
          <div v-if="cartItems.length === 0" class="flex flex-col items-center justify-center h-full text-center px-6">
            <div class="w-24 h-24 rounded-3xl bg-gray-50 flex items-center justify-center mb-5 mx-auto">
              <ShoppingCart class="w-10 h-10 text-gray-200" />
            </div>
            <p class="text-gray-800 font-bold text-lg">购物车还是空的</p>
            <p class="text-gray-400 text-sm mt-1.5 mb-6">快去挑选心仪的商品吧</p>
            <button
              @click="cartOpen = false"
              class="px-6 py-2.5 bg-[#111827] text-white rounded-xl font-semibold text-sm hover:bg-gray-700 transition-colors cursor-pointer"
            >
              去逛逛
            </button>
          </div>

          <!-- 商品列表 -->
          <div v-else class="px-6 py-4 space-y-4">
            <TransitionGroup name="cart-item">
              <div
                v-for="item in cartItems"
                :key="item.product.id"
                class="flex items-start gap-4 p-3.5 rounded-2xl bg-gray-50 hover:bg-gray-100/70 transition-colors group"
              >
                <!-- 商品图 -->
                <div class="w-16 h-16 rounded-xl overflow-hidden shrink-0 bg-white shadow-sm">
                  <img :src="item.product.image" :alt="item.product.name" class="w-full h-full object-cover" />
                </div>

                <!-- 信息 -->
                <div class="flex-1 min-w-0">
                  <p class="text-gray-800 text-sm font-semibold line-clamp-2 leading-snug">{{ item.product.name }}</p>
                  <p class="text-orange-500 font-black text-base mt-1">¥{{ item.product.price }}</p>

                  <!-- 数量控制 -->
                  <div class="flex items-center gap-2 mt-2.5">
                    <button
                      @click="changeQty(item.product.id, -1)"
                      class="w-7 h-7 rounded-lg bg-white border border-gray-200 flex items-center justify-center hover:border-gray-300 hover:bg-gray-50 transition-all cursor-pointer active:scale-90 shadow-sm"
                    >
                      <Minus class="w-3 h-3 text-gray-600" />
                    </button>
                    <span class="w-6 text-center text-sm font-bold text-gray-900">{{ item.quantity }}</span>
                    <button
                      @click="changeQty(item.product.id, 1)"
                      class="w-7 h-7 rounded-lg bg-[#111827] flex items-center justify-center hover:bg-gray-700 transition-all cursor-pointer active:scale-90 shadow-sm"
                    >
                      <Plus class="w-3 h-3 text-white" />
                    </button>
                  </div>
                </div>

                <!-- 删除 -->
                <button
                  @click="removeFromCart(item.product.id)"
                  class="shrink-0 w-7 h-7 rounded-lg flex items-center justify-center text-gray-300 hover:text-rose-400 hover:bg-rose-50 transition-all cursor-pointer opacity-0 group-hover:opacity-100"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </div>
            </TransitionGroup>
          </div>
        </div>

        <!-- 购物车底部结算区 -->
        <div v-if="cartItems.length > 0" class="px-6 py-5 border-t border-gray-100 bg-white space-y-4">
          <!-- 优惠提示 -->
          <div class="flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-orange-50 border border-orange-100">
            <Tag class="w-3.5 h-3.5 text-orange-500 shrink-0" />
            <p class="text-orange-600 text-xs">满 299 减 30 · 满 599 减 80</p>
          </div>

          <!-- 总价 -->
          <div class="flex items-center justify-between">
            <span class="text-gray-500 text-sm">合计（{{ cartCount }} 件）</span>
            <div class="text-right">
              <span class="text-gray-400 text-xs mr-1">¥</span>
              <span class="text-gray-900 font-black text-2xl">{{ cartTotal.toLocaleString() }}</span>
            </div>
          </div>

          <!-- 结算按钮 -->
          <button
            class="w-full flex items-center justify-center gap-2.5 py-4 rounded-2xl bg-gradient-to-r from-[#111827] to-gray-800 hover:from-orange-500 hover:to-orange-600 text-white font-bold text-base shadow-xl transition-all duration-300 hover:shadow-orange-500/30 hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
          >
            去结算
            <ArrowRight class="w-4 h-4" />
          </button>
        </div>

      </div>
    </Transition>

  </div>
</template>

<style scoped>
/* 购物车侧边栏进出动画 */
.slide-cart-enter-active,
.slide-cart-leave-active {
  transition: transform 0.35s cubic-bezier(0.32, 0.72, 0, 1),
              opacity 0.35s ease;
}
.slide-cart-enter-from,
.slide-cart-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* 遮罩层进出动画 */
.fade-overlay-enter-active,
.fade-overlay-leave-active {
  transition: opacity 0.3s ease;
}
.fade-overlay-enter-from,
.fade-overlay-leave-to {
  opacity: 0;
}

/* 购物车条目动画 */
.cart-item-enter-active,
.cart-item-leave-active {
  transition: all 0.3s ease;
}
.cart-item-enter-from {
  opacity: 0;
  transform: translateX(20px);
}
.cart-item-leave-to {
  opacity: 0;
  transform: translateX(-20px);
  max-height: 0;
}
</style>
