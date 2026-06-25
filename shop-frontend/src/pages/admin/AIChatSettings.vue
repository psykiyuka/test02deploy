<template>
  <div class="space-y-6">
    <h3 class="text-lg font-semibold text-gray-800">系统级 AI 客服知识库</h3>
    <p class="text-sm text-gray-500">上传的 FAQ 将作为所有商家的兜底知识库，当商家自身 FAQ 无法回答时，会引用此处内容。</p>

    <!-- 上传区域 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex items-center gap-4 flex-wrap">
      <span class="text-sm text-gray-600">绑定商品（可选）：</span>
      <select v-model="uploadProductId" class="text-sm border border-gray-300 rounded-lg px-3 py-1.5 bg-white">
        <option :value="null">不绑定（全平台通用）</option>
        <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
      </select>
      <label class="flex items-center gap-2 text-sm text-white bg-indigo-600 px-4 py-2 rounded-lg cursor-pointer hover:bg-indigo-700 transition-colors">
        <input type="file" accept=".md,.txt,.markdown" class="hidden" @change="handleFileUpload" :disabled="uploading" />
        {{ uploading ? '上传中...' : '选择文件上传' }}
      </label>
    </div>

    <!-- 说明 -->
    <div class="bg-indigo-50 border border-indigo-100 rounded-xl p-4 text-sm text-indigo-700">
      <p class="font-medium mb-1">📋 文件格式说明</p>
      <p>支持 <code class="bg-white px-1 rounded">.md</code> / <code class="bg-white px-1 rounded">.txt</code> 格式，内容格式为：</p>
      <pre class="mt-2 bg-white/60 rounded-lg p-3 text-xs text-gray-600 overflow-x-auto">**问题标题**
回答内容（可多行）

**另一个问题**
对应的回答内容</pre>
    </div>

    <!-- 文件列表 -->
    <div v-if="loading" class="animate-pulse space-y-3">
      <div v-for="i in 3" :key="i" class="h-16 rounded-xl bg-gray-100" />
    </div>
    <div v-else-if="files.length === 0" class="flex flex-col items-center justify-center py-16 text-gray-400">
      <p>暂无系统级知识库文件</p>
      <p class="text-xs mt-1">点击上方"选择文件上传"开始</p>
    </div>
    <div v-else class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-gray-50 text-left text-xs text-gray-500 uppercase">
            <th class="py-3 px-4 font-medium">文件名</th>
            <th class="py-3 px-4 font-medium">绑定商品</th>
            <th class="py-3 px-4 font-medium">FAQ 条目数</th>
            <th class="py-3 px-4 font-medium">上传时间</th>
            <th class="py-3 px-4 font-medium text-right">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="file in files" :key="file.id" class="border-t border-gray-50 hover:bg-gray-50/50 transition-colors">
            <td class="py-3 px-4">
              <span class="text-gray-800 font-medium">{{ file.filename }}</span>
            </td>
            <td class="py-3 px-4 text-gray-600">
              <span v-if="file.product_id" class="inline-block bg-indigo-100 text-indigo-700 text-xs px-2 py-0.5 rounded">
                商品 #{{ file.product_id }}
              </span>
              <span v-else class="text-gray-400">全平台</span>
            </td>
            <td class="py-3 px-4 text-gray-600">{{ file.chunk_count || 0 }} 条</td>
            <td class="py-3 px-4 text-gray-500 text-xs">{{ file.created_at }}</td>
            <td class="py-3 px-4 text-right">
              <button @click="deleteFile(file.id, file.filename)" class="text-red-500 hover:text-red-700 text-xs">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'

const files = ref<any[]>([])
const products = ref<{ id: number; name: string }[]>([])
const loading = ref(false)
const uploading = ref(false)
const uploadProductId = ref<number | null>(null)

const loadProducts = async () => {
  try {
    const res = await api.get<any>('/b-endpoint/products')
    if (res.code === 0 && res.data) {
      products.value = (res.data.items || res.data || [])
    }
  } catch {}
}

const loadFiles = async () => {
  loading.value = true
  try {
    const res = await api.get<any>('/admin-endpoint/ai-kb/files')
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

const handleFileUpload = async (e: Event) => {
  const input = e.target as HTMLInputElement
  if (!input.files?.length) return
  const file = input.files[0]

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    if (uploadProductId.value !== null) {
      formData.append('product_id', String(uploadProductId.value))
    }
    const res = await api.post('/admin-endpoint/ai-kb/upload', formData)
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
    ;(input as HTMLInputElement).value = ''
  }
}

const deleteFile = async (id: number, filename: string) => {
  if (!confirm(`确定删除系统级文件「${filename}」吗？所有商家都将无法引用该内容。`)) return
  try {
    const res = await api.delete(`/admin-endpoint/ai-kb/files/${id}`)
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
