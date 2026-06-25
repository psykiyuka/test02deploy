<template>
  <div class="bg-white rounded-xl shadow-md p-6">
    <div class="flex justify-between items-center mb-6">
      <h3 class="text-lg font-semibold text-gray-800">商品管理</h3>
      <button @click="showAddModal = true" class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
        上架商品
      </button>
    </div>

    <div v-if="loading" class="animate-pulse p-6 space-y-4">
      <div v-for="i in 5" :key="i" class="h-16 rounded-xl bg-gray-100" />
    </div>
    <div v-else-if="products.length === 0" class="flex flex-col items-center justify-center py-20">
      <p class="text-charcoal/30">暂无商品数据</p>
    </div>
    <div v-else class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="border-b">
            <th class="text-left py-3 px-4 text-sm font-medium text-gray-600">商品名称</th>
            <th class="text-left py-3 px-4 text-sm font-medium text-gray-600">价格</th>
            <th class="text-left py-3 px-4 text-sm font-medium text-gray-600">库存</th>
            <th class="text-left py-3 px-4 text-sm font-medium text-gray-600">审核状态</th>
            <th class="text-left py-3 px-4 text-sm font-medium text-gray-600">上架状态</th>
            <th class="text-left py-3 px-4 text-sm font-medium text-gray-600">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.id" class="border-b hover:bg-gray-50">
            <td class="py-3 px-4">
              <div class="flex items-center">
                <img :src="product.image_url" alt="" class="w-10 h-10 rounded object-cover mr-3" />
                <span class="text-sm">{{ product.name }}</span>
              </div>
            </td>
            <td class="py-3 px-4 text-sm">¥{{ product.price }}</td>
            <td class="py-3 px-4 text-sm">{{ product.stock }}</td>
            <td class="py-3 px-4">
              <span :class="getApprovalClass((product as any).approval_status)" class="px-2 py-1 rounded text-xs">
                {{ getApprovalText((product as any).approval_status) }}
              </span>
            </td>
            <td class="py-3 px-4">
              <span :class="getSaleClass(product.status)" class="px-2 py-1 rounded text-xs">
                {{ getSaleText(product.status) }}
              </span>
            </td>
            <td class="py-3 px-4">
              <button
                v-if="(product as any).approval_status === 'approved'"
                @click="toggleStatus(product)"
                class="text-sm mr-2 transition-colors"
                :class="product.status === 'on_sale' ? 'text-orange-600 hover:text-orange-800' : 'text-green-600 hover:text-green-800'"
              >
                {{ product.status === 'on_sale' ? '下架' : '上架' }}
              </button>
              <span v-else class="text-sm text-gray-300 mr-2" title="审核通过后可操作上下架">—</span>
              <button @click="editProduct(product)" class="text-indigo-600 hover:text-indigo-800 mr-2">编辑</button>
              <button @click="deleteProduct(product.id)" class="text-red-600 hover:text-red-800">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">{{ editingProduct ? '编辑商品' : '上架商品' }}</h3>
        <form @submit.prevent="submitProduct" class="space-y-4">
          <div>
            <label class="block text-sm text-gray-500 mb-1">商品名称</label>
            <input v-model="form.name" type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg" required />
          </div>
          <div>
            <label class="block text-sm text-gray-500 mb-1">商品描述</label>
            <textarea v-model="form.description" class="w-full px-4 py-2 border border-gray-300 rounded-lg" rows="3"></textarea>
          </div>
          <div>
            <label class="block text-sm text-gray-500 mb-1">商品分类</label>
            <select v-model="form.category_id" class="w-full px-4 py-2 border border-gray-300 rounded-lg" required>
              <option :value="0" disabled>请选择分类</option>
              <optgroup v-for="cat in categories" :key="cat.id" :label="cat.name">
                <option v-for="child in cat.children" :key="child.id" :value="child.id">{{ child.name }}</option>
              </optgroup>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-500 mb-1">价格</label>
            <input v-model.number="form.price" type="number" step="0.01" class="w-full px-4 py-2 border border-gray-300 rounded-lg" required />
          </div>
          <div>
            <label class="block text-sm text-gray-500 mb-1">库存</label>
            <input v-model.number="form.stock" type="number" class="w-full px-4 py-2 border border-gray-300 rounded-lg" required />
          </div>
          <div>
            <label class="block text-sm text-gray-500 mb-1">商品图片</label>
            <!-- 拖拽 / 点击上传区域 -->
            <div
              class="relative border-2 border-dashed rounded-xl transition-colors cursor-pointer"
              :class="imgDragOver ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400 hover:bg-gray-50'"
              @dragover.prevent="imgDragOver = true"
              @dragleave.prevent="imgDragOver = false"
              @drop.prevent="onImgDrop"
              @click="triggerImgInput"
            >
              <!-- 已选图片预览 -->
              <div v-if="form.image_url" class="flex flex-col items-center py-3">
                <img :src="form.image_url" alt="预览" class="max-h-40 rounded-lg object-contain mb-2" />
                <span class="text-xs text-gray-400">点击或拖拽可重新选择</span>
              </div>
              <!-- 未选图时的提示 -->
              <div v-else class="flex flex-col items-center py-8 text-gray-400">
                <svg class="w-10 h-10 mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
            <!-- 图片加载错误提示 -->
            <p v-if="imgError" class="text-xs text-red-500 mt-1">{{ imgError }}</p>
          </div>
          <div class="flex justify-end space-x-3">
            <button type="button" @click="closeModal" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">取消</button>
            <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">提交</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { api } from '@/utils/api'
import type { Product } from '@/types'

const products = ref<Product[]>([])
const loading = ref(true)
const showAddModal = ref(false)
const editingProduct = ref<any>(null)
const categories = ref<any[]>([])

const form = reactive({
  name: '',
  description: '',
  price: 0,
  stock: 0,
  image_url: '',
  category_id: 0,
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
    form.image_url = e.target?.result as string
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

const getApprovalClass = (status: string) => {
  const classes: Record<string, string> = {
    pending: 'bg-amber-100 text-amber-700',
    approved: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700',
  }
  return classes[status] || 'bg-gray-100 text-gray-700'
}

const getApprovalText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
  }
  return texts[status] || status
}

const getSaleClass = (status: string) => {
  const classes: Record<string, string> = {
    on_sale: 'bg-green-100 text-green-700',
    off_sale: 'bg-gray-100 text-gray-600',
  }
  return classes[status] || 'bg-gray-100 text-gray-600'
}

const getSaleText = (status: string) => {
  const texts: Record<string, string> = {
    on_sale: '在售',
    off_sale: '已下架',
  }
  return texts[status] || status
}

const toggleStatus = async (product: any) => {
  const newStatus = product.status === 'on_sale' ? 'off_sale' : 'on_sale'
  try {
    const res = await api.put(`/m-endpoint/products/${product.id}/status`, { status: newStatus })
    if (res.code === 0) {
      product.status = newStatus
    }
  } catch (error) {
    alert('操作失败')
  }
}

const loadProducts = async () => {
  loading.value = true
  try {
    const res = await api.get<any>('/m-endpoint/products')
    products.value = res.data.items || []
  } catch (error) {
    console.error('Failed to load products:', error)
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const res = await api.get<any>('/c-endpoint/categories')
    if (res.code === 0 && res.data) {
      // 后端返回扁平数组，前端构建树形结构
      const flat: any[] = res.data
      const roots = flat.filter((c: any) => !c.parent_id)
      categories.value = roots.map((r: any) => ({
        ...r,
        children: flat.filter((c: any) => c.parent_id === r.id),
      }))
    }
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const editProduct = (product: any) => {
  editingProduct.value = product
  form.name = product.name
  form.description = product.description || ''
  form.price = product.price
  form.stock = product.stock
  form.image_url = product.image_url || ''
  form.category_id = product.category_id || 0
  showAddModal.value = true
}

const deleteProduct = async (id: number) => {
  if (!confirm('确定要删除这个商品吗？')) return
  try {
    await api.delete(`/m-endpoint/products/${id}`)
    loadProducts()
  } catch (error) {
    alert('删除失败')
  }
}

const submitProduct = async () => {
  try {
    if (editingProduct.value) {
      await api.put(`/m-endpoint/products/${editingProduct.value.id}`, form)
    } else {
      await api.post('/m-endpoint/products', form)
    }
    closeModal()
    loadProducts()
  } catch (error) {
    alert('提交失败')
  }
}

const closeModal = () => {
  showAddModal.value = false
  editingProduct.value = null
  form.name = ''
  form.description = ''
  form.price = 0
  form.stock = 0
  form.image_url = ''
  form.category_id = 0
  imgError.value = ''
  if (imgInputRef.value) imgInputRef.value.value = ''
}

onMounted(() => {
  loadProducts()
  loadCategories()
})
</script>