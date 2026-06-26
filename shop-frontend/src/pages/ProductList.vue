<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Search, ChevronDown, ShoppingCart, SlidersHorizontal, X } from 'lucide-vue-next'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/utils/api'
import type { Product, Category } from '@/types'

const router = useRouter()
const route = useRoute()
const cart = useCartStore()
const auth = useAuthStore()

// 筛选状态
const searchQuery = ref('')
const sortBy = ref('default')
const selectedCategory = ref<number | null>(null)
const minPrice = ref('')
const maxPrice = ref('')
const onlyInStock = ref(false)
const currentPage = ref(1)
const pageSize = 12

// 数据状态
const products = ref<Product[]>([])
const totalProducts = ref(0)
const totalPages = ref(1)
const loading = ref(false)
const categories = ref<Category[]>([])
const expandedCategories = ref<number[]>([])
const mobileFilterOpen = ref(false)

// 当前选中分类的名称（遍历一级 / 二级分类树查找），用于"已选条件"标签展示
const selectedCategoryName = computed(() => {
  const id = selectedCategory.value
  if (id == null) return ''
  for (const cat of categories.value) {
    if (cat.id === id) return cat.name
    const child = cat.children?.find((c) => c.id === id)
    if (child) return child.name
  }
  return ''
})

// 防抖搜索
let searchTimer: ReturnType<typeof setTimeout> | null = null
const debouncedSearch = ref('')

watch(searchQuery, (val) => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    debouncedSearch.value = val
    currentPage.value = 1
    // 更新 URL，让浏览器历史记录可用
    const query: Record<string, string> = {}
    if (val) query.keyword = val
    if (selectedCategory.value) query.category_id = String(selectedCategory.value)
    router.push({ path: '/products', query }).catch(() => {})
  }, 400)
})

// 排序选项
const sortOptions = [
  { value: 'default', label: '综合排序' },
  { value: 'price-asc', label: '价格从低到高' },
  { value: 'price-desc', label: '价格从高到低' },
  { value: 'sales', label: '销量优先' },
  { value: 'newest', label: '最新上架' },
]

// 获取分类列表（将扁平列表转为树形结构）
async function fetchCategories() {
  try {
    const res = await api.get<Category[]>('/c-endpoint/categories')
    if (res.code === 0 && Array.isArray(res.data)) {
      const flatList = res.data
      // 构建树形结构：parent_id 为 null 的是顶级分类
      const tree: Category[] = []
      const map = new Map<number, Category>()
      flatList.forEach((cat) => {
        map.set(cat.id, { ...cat, children: [] })
      })
      flatList.forEach((cat) => {
        const node = map.get(cat.id)!
        if (cat.parent_id && map.has(cat.parent_id)) {
          map.get(cat.parent_id)!.children!.push(node)
        } else {
          tree.push(node)
        }
      })
      categories.value = tree
      // 默认展开所有顶级分类
      expandedCategories.value = tree.map((c) => c.id)
    }
  } catch {
    // 分类加载失败不影响商品展示
  }
}

function toggleCategory(categoryId: number) {
  const index = expandedCategories.value.indexOf(categoryId)
  if (index > -1) {
    expandedCategories.value.splice(index, 1)
  } else {
    expandedCategories.value.push(categoryId)
  }
}

// 获取商品列表
async function fetchProducts() {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: currentPage.value,
      size: pageSize,
      sort_by: sortBy.value,
    }
    if (debouncedSearch.value) params.keyword = debouncedSearch.value
    if (selectedCategory.value) params.category_id = selectedCategory.value
    if (minPrice.value) params.min_price = Number(minPrice.value)
    if (maxPrice.value) params.max_price = Number(maxPrice.value)
    if (onlyInStock.value) params.in_stock = true

    const res = await api.get<{ items: Product[]; total: number; page: number; size: number }>(
      '/c-endpoint/products',
      { params },
    )
    if (res.code === 0) {
      products.value = res.data.items || []
      totalProducts.value = res.data.total
      totalPages.value = Math.ceil(res.data.total / pageSize)
    }
  } catch {
    products.value = []
  } finally {
    loading.value = false
  }
}

// 应用价格筛选（手动触发，防止用户输入过程中频繁请求）
function applyPriceFilter() {
  currentPage.value = 1
  fetchProducts()
}

// 重置所有筛选
function resetFilters() {
  searchQuery.value = ''
  debouncedSearch.value = ''
  selectedCategory.value = null
  minPrice.value = ''
  maxPrice.value = ''
  onlyInStock.value = false
  sortBy.value = 'default'
  currentPage.value = 1
}

// 是否有活跃筛选
const hasActiveFilters = computed(() => {
  return debouncedSearch.value || selectedCategory.value || minPrice.value || maxPrice.value || onlyInStock.value
})

// 监听筛选条件变化
watch([debouncedSearch, sortBy, selectedCategory, onlyInStock, currentPage], () => {
  fetchProducts()
})

// 监听价格区间变化（手动触发）
watch([minPrice, maxPrice], () => {
  // 价格区间变化时不自动触发，等用户点"应用筛选"
})

function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
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
    // 忽略错误
  }
}

// 分页按钮生成
const pageNumbers = computed(() => {
  const pages: number[] = []
  const tp = totalPages.value
  const cp = currentPage.value

  if (tp <= 7) {
    for (let i = 1; i <= tp; i++) pages.push(i)
  } else {
    pages.push(1)
    if (cp > 3) pages.push(-1) // 省略号
    for (let i = Math.max(2, cp - 1); i <= Math.min(tp - 1, cp + 1); i++) {
      pages.push(i)
    }
    if (cp < tp - 2) pages.push(-1)
    pages.push(tp)
  }
  return pages
})

// 监听路由变化（浏览器前进/后退）
watch(() => route.query.keyword, (kw) => {
  const keyword = (kw as string) || ''
  searchQuery.value = keyword
  debouncedSearch.value = keyword
  currentPage.value = 1
})

watch(() => route.query.category_id, (catId) => {
  selectedCategory.value = catId ? Number(catId) : null
  currentPage.value = 1
})

onMounted(() => {
  // 从 URL 读取搜索关键词和分类筛选
  const kw = (route.query.keyword as string) || ''
  if (kw) {
    searchQuery.value = kw
    debouncedSearch.value = kw
  }
  const catId = Number(route.query.category_id)
  if (catId) {
    selectedCategory.value = catId
  }
  fetchCategories()
  fetchProducts()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <div class="mx-4 md:mx-8 lg:mx-12 py-6">
      <div class="flex gap-4 md:gap-8">
        <!-- 左侧边栏 - 桌面端 -->
        <aside class="hidden lg:block w-64 flex-shrink-0">
          <div class="bg-white rounded-xl shadow-sm p-5 sticky top-4">
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-semibold text-gray-900">商品分类</h3>
              <button
                v-if="selectedCategory"
                @click="selectedCategory = null; currentPage = 1"
                class="text-xs text-indigo-600 hover:text-indigo-700"
              >
                清除
              </button>
            </div>

            <!-- 分类树 -->
            <ul class="space-y-1">
              <li
                v-for="category in categories"
                :key="category.id"
              >
                <button
                  @click="toggleCategory(category.id)"
                  class="w-full flex items-center gap-2 py-2 text-left hover:bg-gray-50 rounded-lg px-2 transition-colors"
                >
                  <ChevronDown
                    :class="[
                      'w-4 h-4 text-gray-400 transition-transform duration-200',
                      expandedCategories.includes(category.id) ? 'rotate-90' : '',
                    ]"
                  />
                  <span class="text-sm text-gray-700">{{ category.name }}</span>
                </button>
                <ul
                  v-if="expandedCategories.includes(category.id) && category.children?.length"
                  class="ml-6 mt-1 space-y-1"
                >
                  <li v-for="child in category.children" :key="child.id">
                    <button
                      @click="selectedCategory = selectedCategory === child.id ? null : child.id; currentPage = 1"
                      :class="[
                        'w-full text-left py-1.5 px-2 rounded-lg text-sm transition-colors',
                        selectedCategory === child.id
                          ? 'bg-indigo-50 text-indigo-600 font-medium'
                          : 'text-gray-600 hover:bg-gray-50',
                      ]"
                    >
                      <span class="ml-2">{{ child.name }}</span>
                    </button>
                  </li>
                </ul>
              </li>
            </ul>

            <!-- 价格区间 -->
            <div class="mt-6 pt-6 border-t border-gray-100">
              <h3 class="font-semibold text-gray-900 mb-4">价格区间</h3>
              <div class="grid grid-cols-2 gap-2">
                <input
                  v-model="minPrice"
                  type="number"
                  placeholder="最低价"
                  min="0"
                  class="w-full px-2 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
                <input
                  v-model="maxPrice"
                  type="number"
                  placeholder="最高价"
                  min="0"
                  class="w-full px-2 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <button
                @click="applyPriceFilter(); currentPage = 1"
                class="w-full mt-3 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
              >
                应用筛选
              </button>
            </div>

            <!-- 仅看有货 -->
            <div class="mt-6 pt-6 border-t border-gray-100">
              <label class="flex items-center gap-3 cursor-pointer">
                <div
                  :class="[
                    'w-5 h-5 rounded border-2 flex items-center justify-center transition-colors',
                    onlyInStock ? 'bg-indigo-600 border-indigo-600' : 'border-gray-300',
                  ]"
                >
                  <svg v-if="onlyInStock" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span class="text-sm text-gray-700">仅看有货</span>
                <input
                  v-model="onlyInStock"
                  type="checkbox"
                  class="sr-only"
                  @change="currentPage = 1"
                />
              </label>
            </div>

            <!-- 重置 -->
            <button
              v-if="hasActiveFilters"
              @click="resetFilters"
              class="w-full mt-6 py-2.5 border border-gray-200 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
            >
              <X class="w-4 h-4" />
              重置筛选
            </button>
          </div>
        </aside>

        <!-- 主内容区 -->
        <main class="flex-1 min-w-0">
          <!-- 顶部工具栏 -->
          <div class="bg-white rounded-xl shadow-sm p-4 md:p-6 mb-6">
            <div class="flex flex-col md:flex-row md:items-center gap-4">
              <!-- 搜索栏 -->
              <div class="relative flex-1">
                <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="搜索商品..."
                  class="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                />
              </div>

              <!-- 移动端筛选按钮 -->
              <button
                @click="mobileFilterOpen = !mobileFilterOpen"
                class="lg:hidden flex items-center gap-2 px-4 py-3 border border-gray-200 rounded-xl text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <SlidersHorizontal class="w-5 h-5" />
                <span>筛选</span>
              </button>

              <!-- 排序 -->
              <div class="relative">
                <select
                  v-model="sortBy"
                  class="appearance-none pl-4 pr-10 py-3 border border-gray-200 rounded-xl bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent cursor-pointer"
                >
                  <option v-for="option in sortOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
                <ChevronDown class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
              </div>
            </div>

            <!-- 活跃筛选标签 -->
            <div v-if="hasActiveFilters" class="flex flex-wrap gap-2 mt-4">
              <span
                v-if="debouncedSearch"
                class="inline-flex items-center gap-1 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs"
              >
                搜索: {{ debouncedSearch }}
                <button @click="searchQuery = ''; debouncedSearch = ''" class="hover:text-indigo-900">
                  <X class="w-3 h-3" />
                </button>
              </span>
              <span
                v-if="selectedCategory"
                class="inline-flex items-center gap-1 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs"
              >
                {{ selectedCategoryName }}
                <button @click="selectedCategory = null; currentPage = 1" class="hover:text-indigo-900">
                  <X class="w-3 h-3" />
                </button>
              </span>
              <span
                v-if="minPrice || maxPrice"
                class="inline-flex items-center gap-1 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs"
              >
                价格: {{ minPrice || '0' }} - {{ maxPrice || '∞' }}
                <button @click="minPrice = ''; maxPrice = ''; currentPage = 1" class="hover:text-indigo-900">
                  <X class="w-3 h-3" />
                </button>
              </span>
              <span
                v-if="onlyInStock"
                class="inline-flex items-center gap-1 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs"
              >
                仅看有货
                <button @click="onlyInStock = false; currentPage = 1" class="hover:text-indigo-900">
                  <X class="w-3 h-3" />
                </button>
              </span>
            </div>
          </div>

          <!-- 移动端筛选面板 -->
          <div
            v-if="mobileFilterOpen"
            class="lg:hidden bg-white rounded-xl shadow-sm p-5 mb-6 space-y-4"
          >
            <div class="flex items-center justify-between">
              <h3 class="font-semibold text-gray-900">筛选条件</h3>
              <button @click="mobileFilterOpen = false" class="text-gray-400 hover:text-gray-600">
                <X class="w-5 h-5" />
              </button>
            </div>

            <!-- 分类 -->
            <div>
              <label class="text-sm font-medium text-gray-700 mb-2 block">分类</label>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="cat in categories"
                  :key="cat.id"
                  @click="selectedCategory = selectedCategory === cat.id ? null : cat.id; currentPage = 1"
                  :class="[
                    'px-3 py-1.5 rounded-lg text-sm transition-colors',
                    selectedCategory === cat.id
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
                  ]"
                >
                  {{ cat.name }}
                </button>
              </div>
            </div>

            <!-- 价格 -->
            <div>
              <label class="text-sm font-medium text-gray-700 mb-2 block">价格区间</label>
              <div class="flex items-center gap-2">
                <input v-model="minPrice" type="number" placeholder="最低" min="0" class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
                <span class="text-gray-400">-</span>
                <input v-model="maxPrice" type="number" placeholder="最高" min="0" class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
              </div>
            </div>

            <div class="flex gap-3">
              <button
                @click="applyPriceFilter(); currentPage = 1; mobileFilterOpen = false"
                class="flex-1 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium"
              >
                应用筛选
              </button>
              <button
                @click="resetFilters; mobileFilterOpen = false"
                class="flex-1 py-2.5 border border-gray-200 text-gray-600 rounded-lg text-sm font-medium"
              >
                重置
              </button>
            </div>
          </div>

          <!-- 结果统计 -->
          <div class="flex items-center justify-between mb-4">
            <p class="text-sm text-gray-500">
              共 <span class="font-medium text-gray-700">{{ totalProducts }}</span> 件商品
            </p>
          </div>

          <!-- 加载状态 -->
          <div v-if="loading" class="flex items-center justify-center py-20">
            <div class="animate-spin rounded-full h-10 w-10 border-4 border-gray-200 border-t-indigo-600"></div>
          </div>

          <!-- 商品列表 -->
          <div v-else-if="products.length > 0" class="grid grid-cols-2 md:grid-cols-3 gap-4 md:gap-6">
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
                <div
                  v-if="product.stock === 0"
                  class="absolute inset-0 bg-black/40 flex items-center justify-center"
                >
                  <span class="text-white font-semibold text-sm bg-black/60 px-3 py-1 rounded-full">暂无库存</span>
                </div>
                <button
                  v-if="product.stock > 0"
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
                <div class="flex items-center justify-between mt-2">
                  <p class="text-xs text-gray-400">库存 {{ product.stock }} 件</p>
                  <p v-if="product.sales" class="text-xs text-gray-400">已售 {{ product.sales }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
            <Search class="w-16 h-16 mb-4 opacity-30" />
            <p class="text-lg font-medium text-gray-500">暂无符合条件的商品</p>
            <p class="text-sm mt-1">试试调整筛选条件或搜索关键词</p>
            <button
              @click="resetFilters"
              class="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
            >
              清除筛选
            </button>
          </div>

          <!-- 分页 -->
          <div v-if="totalPages > 1" class="mt-8 flex items-center justify-center">
            <div class="flex items-center gap-2">
              <button
                @click="goToPage(currentPage - 1)"
                :disabled="currentPage === 1"
                :class="[
                  'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                  currentPage === 1
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50',
                ]"
              >
                上一页
              </button>

              <template v-for="p in pageNumbers" :key="p">
                <span v-if="p === -1" class="px-2 text-gray-400">...</span>
                <button
                  v-else
                  @click="goToPage(p)"
                  :class="[
                    'w-9 h-9 rounded-lg text-sm font-medium transition-all',
                    currentPage === p
                      ? 'bg-indigo-600 text-white shadow-md'
                      : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50',
                  ]"
                >
                  {{ p }}
                </button>
              </template>

              <button
                @click="goToPage(currentPage + 1)"
                :disabled="currentPage === totalPages"
                :class="[
                  'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                  currentPage === totalPages
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50',
                ]"
              >
                下一页
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>