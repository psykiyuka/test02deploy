<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '@/utils/api'
import type { Product } from '@/types'
import { useCategoryStore } from '@/stores/category'
import StatusBadge from '@/components/StatusBadge.vue'
import { Edit2, Trash2, Package, Search, Eye, EyeOff, X, ExternalLink, CheckCircle2, XCircle, Clock } from 'lucide-vue-next'

const categoryStore = useCategoryStore()
const products = ref<Product[]>([])
const loading = ref(true)
const searchQuery = ref('')

const showEditDialog = ref(false)
const showDeleteConfirm = ref(false)
const targetProduct = ref<Product | null>(null)

const form = ref({
  name: '',
  description: '',
  price: 0,
  stock: 0,
  image_url: '',
  category_id: null as number | null,
})

// ── 图片上传相关 ──
const imgInputRef = ref<HTMLInputElement | null>(null)
const imgDragOver = ref(false)
const imgError = ref('')

const triggerImgInput = () => {
  imgInputRef.value?.click()
}

const processImageFile = (file: File) => {
  imgError.value = ''
  if (!file.type.startsWith('image/')) {
    imgError.value = '请选择图片文件'
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    imgError.value = '图片大小不能超过 5MB'
    return
  }
  const reader = new FileReader()
  reader.onload = (e) => {
    form.value.image_url = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

const onImgFileChange = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) processImageFile(file)
}

const onImgDrop = (e: DragEvent) => {
  imgDragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) processImageFile(file)
}

function openEditDialog(product: Product) {
  targetProduct.value = product
  form.value = {
    name: product.name,
    description: product.description,
    price: product.price,
    stock: product.stock,
    image_url: product.image_url,
    category_id: product.category_id,
  }
  showEditDialog.value = true
}

function openDeleteConfirm(product: Product) {
  targetProduct.value = product
  showDeleteConfirm.value = true
}

function getCategoryName(categoryId: number): string {
  const cat = categoryStore.categories.find(c => c.id === categoryId)
  return cat?.name ?? '未分类'
}

const filteredProducts = computed(() => {
  if (!searchQuery.value.trim()) return products.value
  const q = searchQuery.value.toLowerCase()
  return products.value.filter(
    p =>
      p.name.toLowerCase().includes(q) ||
      p.description.toLowerCase().includes(q)
  )
})

async function fetchProducts() {
  loading.value = true
  const res = await api.get<{ items: Product[]; total: number }>('/b-endpoint/products', {
    params: { page: 1, size: 100 },
  })
  if (res.code === 0) products.value = res.data.items ?? []
  loading.value = false
}

async function updateProduct() {
  if (!targetProduct.value) return
  const res = await api.put<Product>(`/b-endpoint/products/${targetProduct.value.id}`, form.value)
  if (res.code === 0) {
    showEditDialog.value = false
    targetProduct.value = null
    await fetchProducts()
  }
}

async function deleteProduct() {
  if (!targetProduct.value) return
  const res = await api.delete<any>(`/b-endpoint/products/${targetProduct.value.id}`)
  if (res.code === 0) {
    showDeleteConfirm.value = false
    targetProduct.value = null
    await fetchProducts()
  }
}

async function toggleStatus(product: Product) {
  const newStatus = product.status === 'on_sale' ? 'off_sale' : 'on_sale'
  const res = await api.put<Product>(`/b-endpoint/products/${product.id}/status`, { status: newStatus })
  if (res.code === 0) {
    product.status = newStatus
  }
}

async function approveProduct(product: Product) {
  const res = await api.put<any>(`/b-endpoint/products/${product.id}/approve`)
  if (res.code === 0) {
    product.approval_status = 'approved'
    product.status = 'on_sale'
  }
}

async function rejectProduct(product: Product) {
  const res = await api.put<any>(`/b-endpoint/products/${product.id}/reject`)
  if (res.code === 0) {
    product.approval_status = 'rejected'
    product.status = 'off_sale'
  }
}

function openPreview(productId: number) {
  window.open(`/products/${productId}`, '_blank')
}

onMounted(async () => {
  await Promise.all([fetchProducts(), categoryStore.fetchCategories()])
})
</script>

<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="font-display text-3xl text-charcoal mb-1">商品管理</h1>
        <p class="text-charcoal/40 text-sm">管理您的商品目录</p>
      </div>
      <div class="flex items-center gap-2 px-4 py-2 rounded-xl bg-gold-50 text-gold-600 text-sm font-medium">
        <Package :size="16" />
        共 {{ products.length }} 件商品
      </div>
    </div>

    <div class="mb-6">
      <div class="relative max-w-md">
        <Search :size="18" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-gold-300" />
        <input
          v-model="searchQuery"
          type="text"
          class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gold-100 bg-white focus:border-gold-300 focus:ring-4 focus:ring-gold-50 outline-none transition-all text-sm text-charcoal placeholder:text-charcoal/30"
          placeholder="搜索商品名称或描述..."
        />
      </div>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-gold-50 overflow-hidden">
      <div v-if="loading" class="animate-pulse p-6 space-y-4">
        <div v-for="i in 5" :key="i" class="h-16 rounded-xl bg-gray-100" />
      </div>
      <div v-else-if="filteredProducts.length === 0" class="flex flex-col items-center justify-center py-20">
        <div class="w-16 h-16 rounded-2xl bg-gold-50 flex items-center justify-center mb-4">
          <Package :size="28" class="text-gold-300" />
        </div>
        <p class="text-charcoal/30">{{ searchQuery ? '未找到匹配的商品' : '暂无商品' }}</p>
      </div>
      <table v-else class="w-full">
        <thead>
          <tr class="border-b border-gold-50 bg-gradient-to-r from-gold-50/50 to-cream/50">
            <th class="text-left px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">商品信息</th>
            <th class="text-left px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">分类</th>
            <th class="text-left px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">价格</th>
            <th class="text-left px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">库存</th>
            <th class="text-left px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">上架状态</th>
            <th class="text-left px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">审核</th>
            <th class="text-right px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="product in filteredProducts"
            :key="product.id"
            class="border-b border-gold-50/50 last:border-b-0 hover:bg-gold-50/20 transition-colors"
          >
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg overflow-hidden bg-gradient-to-br from-gold-50 to-cream flex items-center justify-center shrink-0">
                  <img
                    v-if="product.image_url"
                    :src="product.image_url"
                    :alt="product.name"
                    class="w-full h-full object-cover"
                  />
                  <Package v-else :size="18" class="text-gold-200/60" />
                </div>
                <div>
                  <p class="text-sm font-semibold text-charcoal">{{ product.name }}</p>
                  <p class="text-xs text-charcoal/30 truncate max-w-[200px]">{{ product.description }}</p>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <span class="text-sm text-charcoal/50">{{ getCategoryName(product.category_id) }}</span>
            </td>
            <td class="px-6 py-4">
              <span class="text-sm font-bold text-gold-500">¥{{ product.price }}</span>
            </td>
            <td class="px-6 py-4">
              <span
                class="text-sm font-semibold"
                :class="product.stock > 0 ? 'text-charcoal' : 'text-rose-500'"
              >
                {{ product.stock }}
              </span>
            </td>
            <td class="px-6 py-4">
              <StatusBadge :status="product.status" />
            </td>
            <td class="px-6 py-4">
              <span
                class="inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium"
                :class="{
                  'bg-amber-50 text-amber-600': (product as any).approval_status === 'pending',
                  'bg-emerald-50 text-emerald-600': (product as any).approval_status === 'approved',
                  'bg-rose-50 text-rose-600': (product as any).approval_status === 'rejected',
                }"
              >
                <Clock v-if="(product as any).approval_status === 'pending'" :size="12" />
                <CheckCircle2 v-else-if="(product as any).approval_status === 'approved'" :size="12" />
                <XCircle v-else :size="12" />
                {{ (product as any).approval_status === 'pending' ? '待审核' : (product as any).approval_status === 'approved' ? '已通过' : '已拒绝' }}
              </span>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center justify-end gap-0.5">
                <!-- 审核按钮：仅待审核状态显示 -->
                <button
                  v-if="(product as any).approval_status === 'pending'"
                  @click="approveProduct(product)"
                  class="p-2 rounded-lg text-charcoal/30 hover:text-emerald-500 hover:bg-emerald-50 transition-colors cursor-pointer"
                  title="审核通过"
                >
                  <CheckCircle2 :size="16" />
                </button>
                <button
                  v-if="(product as any).approval_status === 'pending'"
                  @click="rejectProduct(product)"
                  class="p-2 rounded-lg text-charcoal/30 hover:text-rose-500 hover:bg-rose-50 transition-colors cursor-pointer"
                  title="审核拒绝"
                >
                  <XCircle :size="16" />
                </button>
                <button
                  @click="toggleStatus(product)"
                  :title="product.status === 'on_sale' ? '下架' : '上架'"
                  class="p-2 rounded-lg transition-colors cursor-pointer"
                  :class="product.status === 'on_sale'
                    ? 'text-charcoal/30 hover:text-orange-500 hover:bg-orange-50'
                    : 'text-charcoal/30 hover:text-emerald-500 hover:bg-emerald-50'"
                >
                  <EyeOff v-if="product.status === 'on_sale'" :size="16" />
                  <Eye v-else :size="16" />
                </button>
                <button
                  @click="openEditDialog(product)"
                  class="p-2 rounded-lg text-charcoal/30 hover:text-blue-500 hover:bg-blue-50 transition-colors cursor-pointer"
                  title="编辑"
                >
                  <Edit2 :size="16" />
                </button>
                <button
                  @click="openPreview(product.id)"
                  class="p-2 rounded-lg text-charcoal/30 hover:text-violet-500 hover:bg-violet-50 transition-colors cursor-pointer"
                  title="预览"
                >
                  <ExternalLink :size="16" />
                </button>
                <button
                  @click="openDeleteConfirm(product)"
                  class="p-2 rounded-lg text-charcoal/30 hover:text-rose-500 hover:bg-rose-50 transition-colors cursor-pointer"
                  title="删除"
                >
                  <Trash2 :size="16" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <Teleport to="body">
      <div v-if="showEditDialog" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/30 backdrop-blur-sm" @click="showEditDialog = false" />
        <div class="relative bg-white rounded-2xl shadow-2xl p-8 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto animate-scale-in">
          <button
            class="absolute top-4 right-4 p-2 rounded-lg text-charcoal/30 hover:text-charcoal hover:bg-gold-50 transition-colors cursor-pointer"
            @click="showEditDialog = false"
          >
            <X :size="18" />
          </button>
          <h2 class="font-display text-xl text-charcoal mb-6">编辑商品</h2>
          <form @submit.prevent="updateProduct()" class="space-y-5">
            <div>
              <label class="elegant-input-label">商品名称</label>
              <input
                v-model="form.name"
                required
                class="elegant-input elegant-input-without-icon"
                placeholder="请输入商品名称"
              />
            </div>
            <div>
              <label class="elegant-input-label">商品描述</label>
              <textarea
                v-model="form.description"
                rows="3"
                class="elegant-input elegant-input-without-icon elegant-textarea"
                placeholder="请输入商品描述"
              />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="elegant-input-label">价格 (¥)</label>
                <input
                  v-model.number="form.price"
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  class="elegant-input elegant-input-without-icon"
                  placeholder="0.00"
                />
              </div>
              <div>
                <label class="elegant-input-label">库存数量</label>
                <input
                  v-model.number="form.stock"
                  type="number"
                  min="0"
                  required
                  class="elegant-input elegant-input-without-icon"
                  placeholder="0"
                />
              </div>
            </div>
            <div>
              <label class="elegant-input-label">所属分类</label>
              <select
                v-model="form.category_id"
                required
                class="elegant-input elegant-input-without-icon elegant-select"
              >
                <option :value="null" disabled>请选择分类</option>
                <option v-for="cat in categoryStore.categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="elegant-input-label">商品图片</label>
              <!-- 拖拽 / 点击上传区域 -->
              <div
                class="relative border-2 border-dashed rounded-xl transition-all cursor-pointer"
                :class="imgDragOver ? 'border-gold-400 bg-gold-50' : 'border-gold-100 hover:border-gold-300 hover:bg-gold-50/30'"
                @dragover.prevent="imgDragOver = true"
                @dragleave.prevent="imgDragOver = false"
                @drop.prevent="onImgDrop"
                @click="triggerImgInput"
              >
                <!-- 已选图片预览 -->
                <div v-if="form.image_url" class="flex flex-col items-center py-3">
                  <img :src="form.image_url" alt="预览" class="max-h-40 rounded-lg object-contain mb-2" />
                  <span class="text-xs text-charcoal/30">点击或拖拽可重新选择</span>
                </div>
                <!-- 未选图时的提示 -->
                <div v-else class="flex flex-col items-center py-8 text-charcoal/30">
                  <svg class="w-10 h-10 mb-2 text-gold-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <p class="text-sm font-medium">点击选择图片 或 拖拽到此处</p>
                  <p class="text-xs mt-1">支持 JPG / PNG / WebP，建议尺寸 800×800</p>
                </div>
                <!-- 隐藏的文件输入 -->
                <input
                  ref="imgInputRef"
                  type="file"
                  accept="image/*"
                  class="hidden"
                  @change="onImgFileChange"
                />
              </div>
              <p v-if="imgError" class="text-xs text-rose-500 mt-1">{{ imgError }}</p>
            </div>
            <div class="flex gap-3 pt-2">
              <button
                type="button"
                @click="showEditDialog = false"
                class="flex-1 px-4 py-2.5 rounded-xl border border-gold-100 text-charcoal/60 hover:bg-gold-50 hover:text-charcoal transition-all cursor-pointer font-medium text-sm"
              >
                取消
              </button>
              <button
                type="submit"
                class="flex-1 px-4 py-2.5 rounded-xl bg-gradient-to-r from-gold-400 to-gold-500 text-white hover:from-gold-500 hover:to-gold-600 transition-all font-semibold text-sm shadow-lg shadow-gold-300/25 cursor-pointer"
              >
                保存修改
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/30 backdrop-blur-sm" @click="showDeleteConfirm = false" />
        <div class="relative bg-white rounded-2xl shadow-2xl p-8 w-full max-w-sm mx-4 animate-scale-in">
          <div class="text-center">
            <div class="w-14 h-14 rounded-2xl bg-rose-50 flex items-center justify-center mx-auto mb-4">
              <Trash2 :size="24" class="text-rose-500" />
            </div>
            <h3 class="font-display text-xl text-charcoal mb-2">确认删除</h3>
            <p class="text-sm text-charcoal/40 mb-6">
              确定要删除商品「{{ targetProduct?.name }}」吗？<br/>删除后不可恢复。
            </p>
            <div class="flex gap-3">
              <button
                @click="showDeleteConfirm = false"
                class="flex-1 px-4 py-2.5 rounded-xl border border-gold-100 text-charcoal/60 hover:bg-gold-50 transition-all cursor-pointer font-medium text-sm"
              >
                取消
              </button>
              <button
                @click="deleteProduct"
                class="flex-1 px-4 py-2.5 rounded-xl bg-gradient-to-r from-rose-500 to-rose-600 text-white hover:from-rose-600 hover:to-rose-700 transition-all font-semibold text-sm shadow-lg shadow-rose-300/25 cursor-pointer"
              >
                确认删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>