<template>
  <div class="space-y-6">
    <!-- 页面标题 + 筛选 -->
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-semibold text-gray-800">AI 客服知识库</h3>
      <select v-model="filterProductId" class="text-sm border border-gray-300 rounded-lg px-3 py-1.5 bg-white">
        <option :value="null">全部文件</option>
        <option :value="0">商家级（兜底）</option>
        <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
      </select>
    </div>

    <!-- 上传区域：选择绑定范围 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex items-center gap-4 flex-wrap">
      <span class="text-sm text-gray-600">上传到第：</span>
      <select v-model="uploadProductId" class="text-sm border border-gray-300 rounded-lg px-3 py-1.5 bg-white">
        <option :value="0">商家级（所有商品兜底）</option>
        <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
      </select>
      <label class="flex items-center gap-2 text-sm text-white bg-indigo-600 px-4 py-2 rounded-lg cursor-pointer hover:bg-indigo-700 transition-colors">
        <input type="file" accept=".md,.txt,.markdown" class="hidden" @change="handleFileUpload" :disabled="uploading" />
        {{ uploading ? '上传中...' : '选择文件上传' }}
      </label>
    </div>

    <!-- 说明卡片 -->
    <div class="bg-indigo-50 border border-indigo-100 rounded-xl p-4 text-sm text-indigo-700">
      <p class="font-medium mb-1">📋 文件格式说明</p>
      <p>支持 <code class="bg-white px-1 rounded">.md</code> / <code class="bg-white px-1 rounded">.txt</code> 格式，内容格式为：</p>
      <pre class="mt-2 bg-white/60 rounded-lg p-3 text-xs text-gray-600 overflow-x-auto">**问题标题**
回答内容（可多行）

**另一个问题**
对应的回答内容</pre>
      <p class="mt-2">💡 推荐按商品分别上传 FAQ，买家在该商品页咨询时会优先匹配对应商品的知识库。</p>
    </div>

    <!-- 文件列表 -->
    <div v-if="loading" class="animate-pulse space-y-3">
      <div v-for="i in 3" :key="i" class="h-16 rounded-xl bg-gray-100" />
    </div>
    <div v-else-if="files.length === 0" class="flex flex-col items-center justify-center py-16 text-gray-400">
      <svg class="w-12 h-12 mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.879 7.519c1.171-1.242 3.055-1.242 4.242 0 1.172 1.243 1.172 3.259 0 4.502l-4.242 4.5a1.75 1.75 0 01-2.829 0L3.17 14.4a5.25 5.25 0 010-7.58 5.25 5.25 0 017.58 0z"/></svg>
      <p>暂无知识库文件</p>
      <p class="text-xs mt-1">点击右上角"上传 FAQ 文件"开始</p>
    </div>
    <div v-else class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-gray-50 text-left text-xs text-gray-500 uppercase">
            <th class="py-3 px-4 font-medium">文件名</th>
            <th class="py-3 px-4 font-medium">绑定范围</th>
            <th class="py-3 px-4 font-medium">FAQ 条目数</th>
            <th class="py-3 px-4 font-medium">上传时间</th>
            <th class="py-3 px-4 font-medium text-right">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="file in files" :key="file.id" class="border-t border-gray-50 hover:bg-gray-50/50 transition-colors">
            <td class="py-3 px-4">
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                <span class="text-gray-800 font-medium">{{ file.filename }}</span>
                <span class="text-xs text-gray-400">{{ file.file_type }}</span>
              </div>
            </td>
            <td class="py-3 px-4 text-gray-600">
              <span v-if="file.product_id" class="inline-block bg-indigo-100 text-indigo-700 text-xs px-2 py-0.5 rounded">
                商品 #{{ file.product_id }}
              </span>
              <span v-else class="inline-block bg-gray-100 text-gray-500 text-xs px-2 py-0.5 rounded">
                商家级
              </span>
            </td>
            <td class="py-3 px-4 text-gray-600">{{ file.chunk_count || 0 }} 条</td>
            <td class="py-3 px-4 text-gray-500 text-xs">{{ file.created_at }}</td>
            <td class="py-3 px-4 text-right">
              <button @click="deleteFile(file.id, file.filename)" class="text-red-500 hover:text-red-700 text-xs transition-colors">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { api } from '@/utils/api'

const files = ref<{ id: number; filename: string; file_type: string; product_id: number | null; chunk_count: number; created_at: string }[]>([])
const products = ref<{ id: number; name: string }[]>([])
const loading = ref(false)
const uploading = ref(false)
const filterProductId = ref<number | null>(null)
const uploadProductId = ref<number>(0)

// 加载商家的商品列表（用于下拉选择）
const loadProducts = async () => {
  try {
    const res = await api.get<any>('/m-endpoint/products')
    if (res.code === 0 && res.data) {
      products.value = (res.data.items || res.data || [])
    }
  } catch {
    products.value = []
  }
}

const loadFiles = async () => {
  loading.value = true
  try {
    const params = filterProductId.value !== null ? `?product_id=${filterProductId.value}` : ''
    const res = await api.get<any>(`/m-endpoint/ai-kb/files${params}`)
    if (res.code === 0 && res.data) {
      files.value = (res.data.items || []).map((f: any) => ({
        ...f,
        created_at: f.created_at ? new Date(f.created_at).toLocaleDateString('zh-CN') : '-',
      }))
    }
  } finally {
    loading.value = false
  }
}

// 筛选条件变化时重新加载
watch(filterProductId, () => loadFiles())

const handleFileUpload = async (e: Event) => {
  const input = e.target as HTMLInputElement
  if (!input.files?.length) return
  const file = input.files[0]

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    if (uploadProductId.value !== null && uploadProductId.value !== 0) {
      formData.append('product_id', String(uploadProductId.value))
    }
    // product_id=0 表示商家级，不传即可
    const res = await api.post('/m-endpoint/ai-kb/upload', formData)
    if (res.code === 0) {
      await loadFiles()
      alert(`上传成功！解析得到 ${(res.data as any)?.chunk_count || 0} 条 FAQ`)
    } else {
      alert(res.message || '上传失败')
    }
  } catch (err: any) {
    alert(err.response?.data?.message || '上传失败')
  } finally {
    uploading.value = false
    input.value = ''
  }
}

const deleteFile = async (id: number, filename: string) => {
  if (!confirm(`确定删除「${filename}」吗？删除后买家将无法基于该文件内容咨询 AI 客服。`)) return
  try {
    const res = await api.delete(`/m-endpoint/ai-kb/files/${id}`)
    if (res.code === 0) await loadFiles()
  } catch (err: any) {
    alert(err.response?.data?.message || '删除失败')
  }
}

onMounted(() => {
  loadProducts()
  loadFiles()
})
</script>
