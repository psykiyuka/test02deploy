<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '@/utils/api'
import type { Category } from '@/types'
import { useCategoryStore } from '@/stores/category'
import { Plus, Edit2, Trash2, FolderTree, ChevronRight, X } from 'lucide-vue-next'

const categoryStore = useCategoryStore()
const loading = ref(true)

const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showDeleteConfirm = ref(false)
const targetCategory = ref<Category | null>(null)

const form = ref({
  name: '',
  parent_id: null as number | null,
  sort_order: 0,
})

function resetForm() {
  form.value = { name: '', parent_id: null, sort_order: 0 }
}

function openAddDialog() {
  resetForm()
  showAddDialog.value = true
}

function openEditDialog(cat: Category) {
  targetCategory.value = cat
  form.value = {
    name: cat.name,
    parent_id: cat.parent_id,
    sort_order: cat.sort_order,
  }
  showEditDialog.value = true
}

function openDeleteConfirm(cat: Category) {
  targetCategory.value = cat
  showDeleteConfirm.value = true
}

function getIndentLevel(cat: Category): number {
  if (cat.parent_id === null) return 0
  const parent = categoryStore.categories.find(c => c.id === cat.parent_id)
  if (!parent) return 0
  return 1 + getIndentLevel(parent)
}

function getCategoryPath(cat: Category): string {
  if (cat.parent_id === null) return cat.name
  const parent = categoryStore.categories.find(c => c.id === cat.parent_id)
  if (!parent) return cat.name
  return getCategoryPath(parent) + ' / ' + cat.name
}

const parentOptions = computed(() =>
  categoryStore.categories.filter(c => c.id !== targetCategory.value?.id)
)

const sortedCategories = computed(() => {
  const cloned = [...categoryStore.categories]
  cloned.sort((a, b) => a.sort_order - b.sort_order)
  return cloned
})

async function createCategory() {
  const res = await api.post<Category>('/b-endpoint/categories', form.value)
  if (res.code === 0) {
    showAddDialog.value = false
    await categoryStore.fetchCategories()
  }
}

async function updateCategory() {
  if (!targetCategory.value) return
  const res = await api.put<Category>(`/b-endpoint/categories/${targetCategory.value.id}`, form.value)
  if (res.code === 0) {
    showEditDialog.value = false
    targetCategory.value = null
    await categoryStore.fetchCategories()
  }
}

async function deleteCategory() {
  if (!targetCategory.value) return
  const res = await api.delete<any>(`/b-endpoint/categories/${targetCategory.value.id}`)
  if (res.code === 0) {
    showDeleteConfirm.value = false
    targetCategory.value = null
    await categoryStore.fetchCategories()
  }
}

onMounted(async () => {
  await categoryStore.fetchCategories()
  loading.value = false
})
</script>

<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="font-display text-3xl text-charcoal mb-1">分类管理</h1>
        <p class="text-charcoal/40 text-sm">管理商品分类层级结构</p>
      </div>
      <button
        @click="openAddDialog"
        class="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-gold-400 to-gold-500 text-white hover:from-gold-500 hover:to-gold-600 transition-all font-semibold text-sm shadow-lg shadow-gold-300/25 cursor-pointer"
      >
        <Plus :size="18" />
        新建分类
      </button>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-gold-50 overflow-hidden">
      <div v-if="loading" class="animate-pulse p-6 space-y-3">
        <div v-for="i in 5" :key="i" class="h-12 rounded-xl bg-gray-100" />
      </div>
      <div v-else-if="sortedCategories.length === 0" class="flex flex-col items-center justify-center py-20">
        <div class="w-16 h-16 rounded-2xl bg-gold-50 flex items-center justify-center mb-4">
          <FolderTree :size="28" class="text-gold-300" />
        </div>
        <p class="text-charcoal/30">暂无分类，点击上方按钮新建</p>
      </div>
      <div v-else>
        <div
          v-for="cat in sortedCategories"
          :key="cat.id"
          class="flex items-center justify-between px-6 py-4 border-b border-gold-50 last:border-b-0 hover:bg-gold-50/20 transition-colors"
          :style="{ paddingLeft: `${24 + getIndentLevel(cat) * 28}px` }"
        >
          <div class="flex items-center gap-3">
            <div v-if="getIndentLevel(cat) > 0" class="flex items-center text-gold-200">
              <ChevronRight :size="14" />
            </div>
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-gold-50 to-cream flex items-center justify-center">
                <FolderTree :size="16" class="text-gold-400" />
              </div>
              <span class="text-charcoal font-semibold text-sm">{{ cat.name }}</span>
              <span class="text-xs text-charcoal/25 bg-gold-50/50 px-2.5 py-0.5 rounded-full font-medium">排序: {{ cat.sort_order }}</span>
            </div>
          </div>
          <div class="flex items-center gap-0.5">
            <button
              @click="openEditDialog(cat)"
              class="p-2 rounded-lg text-charcoal/20 hover:text-blue-500 hover:bg-blue-50 transition-colors cursor-pointer"
            >
              <Edit2 :size="16" />
            </button>
            <button
              @click="openDeleteConfirm(cat)"
              class="p-2 rounded-lg text-charcoal/20 hover:text-rose-500 hover:bg-rose-50 transition-colors cursor-pointer"
            >
              <Trash2 :size="16" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showAddDialog || showEditDialog" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/30 backdrop-blur-sm" @click="showAddDialog = false; showEditDialog = false" />
        <div class="relative bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md mx-4 animate-scale-in">
          <button
            class="absolute top-4 right-4 p-2 rounded-lg text-charcoal/30 hover:text-charcoal hover:bg-gold-50 transition-colors cursor-pointer"
            @click="showAddDialog = false; showEditDialog = false"
          >
            <X :size="18" />
          </button>
          <h2 class="font-display text-xl text-charcoal mb-6">{{ showAddDialog ? '新建分类' : '编辑分类' }}</h2>
          <form @submit.prevent="showAddDialog ? createCategory() : updateCategory()" class="space-y-5">
            <div>
              <label class="elegant-input-label">分类名称</label>
              <input
                v-model="form.name"
                required
                class="elegant-input elegant-input-without-icon"
                placeholder="请输入分类名称"
              />
            </div>
            <div>
              <label class="elegant-input-label">父分类</label>
              <select
                v-model="form.parent_id"
                class="elegant-input elegant-input-without-icon elegant-select"
              >
                <option :value="null">无 (顶级分类)</option>
                <option v-for="cat in (showAddDialog ? categoryStore.categories : parentOptions)" :key="cat.id" :value="cat.id">
                  {{ getCategoryPath(cat) }}
                </option>
              </select>
            </div>
            <div>
              <label class="elegant-input-label">排序权重</label>
              <input
                v-model.number="form.sort_order"
                type="number"
                required
                class="elegant-input elegant-input-without-icon"
                placeholder="数字越小越靠前"
              />
            </div>
            <div class="flex gap-3 pt-2">
              <button
                type="button"
                @click="showAddDialog = false; showEditDialog = false"
                class="flex-1 px-4 py-2.5 rounded-xl border border-gold-100 text-charcoal/60 hover:bg-gold-50 hover:text-charcoal transition-all cursor-pointer font-medium text-sm"
              >
                取消
              </button>
              <button
                type="submit"
                class="flex-1 px-4 py-2.5 rounded-xl bg-gradient-to-r from-gold-400 to-gold-500 text-white hover:from-gold-500 hover:to-gold-600 transition-all font-semibold text-sm shadow-lg shadow-gold-300/25 cursor-pointer"
              >
                {{ showAddDialog ? '确认创建' : '保存修改' }}
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
              确定要删除分类「{{ targetCategory?.name }}」吗？<br/>删除后不可恢复。
            </p>
            <div class="flex gap-3">
              <button
                @click="showDeleteConfirm = false"
                class="flex-1 px-4 py-2.5 rounded-xl border border-gold-100 text-charcoal/60 hover:bg-gold-50 transition-all cursor-pointer font-medium text-sm"
              >
                取消
              </button>
              <button
                @click="deleteCategory"
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