<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold text-gray-800">邮箱换绑审核</h2>
      <div class="flex gap-2">
        <select
          v-model="filterStatus"
          @change="loadData"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        >
          <option value="">全部</option>
          <option value="pending">待审核</option>
          <option value="approved">已通过</option>
          <option value="rejected">已拒绝</option>
        </select>
        <button
          @click="loadData"
          class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 transition-colors"
        >
          刷新
        </button>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-md overflow-hidden">
      <div class="px-4 py-2 bg-gray-50 text-xs text-gray-400">调试: 共 {{ items.length }} 条记录</div>
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-600">
          <tr>
            <th class="px-4 py-3 text-left">ID</th>
            <th class="px-4 py-3 text-left">用户</th>
            <th class="px-4 py-3 text-left">原邮箱</th>
            <th class="px-4 py-3 text-left">新邮箱</th>
            <th class="px-4 py-3 text-left">状态</th>
            <th class="px-4 py-3 text-left">申请时间</th>
            <th class="px-4 py-3 text-left">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="items.length === 0">
            <td colspan="7" class="px-4 py-8 text-center text-gray-400">暂无申请记录</td>
          </tr>
          <tr
            v-for="item in items"
            :key="item.id"
            class="border-t hover:bg-gray-50"
          >
            <td class="px-4 py-3">{{ item.id }}</td>
            <td class="px-4 py-3">
              <div class="font-medium">{{ item.nickname || '未知' }}</div>
              <div class="text-xs text-gray-400">{{ item.shop_name || '' }}</div>
            </td>
            <td class="px-4 py-3">{{ item.old_email }}</td>
            <td class="px-4 py-3 font-medium text-indigo-700">{{ item.new_email }}</td>
            <td class="px-4 py-3">
              <span
                :class="{
                  'bg-yellow-100 text-yellow-700': item.status === 'pending',
                  'bg-green-100 text-green-700': item.status === 'approved',
                  'bg-red-100 text-red-700': item.status === 'rejected',
                }"
                class="px-2 py-1 rounded text-xs"
              >
                {{ statusLabel(item.status) }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-500">{{ formatTime(item.created_at) }}</td>
            <td class="px-4 py-3">
              <div class="flex gap-2" v-if="item.status === 'pending'">
                <button
                  @click="handleApprove(item)"
                  class="px-3 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700 transition-colors"
                >
                  通过
                </button>
                <button
                  @click="handleReject(item)"
                  class="px-3 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700 transition-colors"
                >
                  拒绝
                </button>
              </div>
              <span v-if="item.status === 'rejected'" class="text-xs text-red-500">{{ item.reject_reason || '无原因' }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 拒绝原因弹窗 -->
    <div
      v-if="rejectDialogVisible"
      class="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-xl p-6 w-96 shadow-xl">
        <h3 class="text-lg font-semibold mb-4">拒绝原因</h3>
        <textarea
          v-model="rejectReason"
          rows="3"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
          placeholder="请输入拒绝原因（可选）"
        ></textarea>
        <div class="flex justify-end gap-3 mt-4">
          <button
            @click="rejectDialogVisible = false"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm"
          >取消</button>
          <button
            @click="confirmReject"
            class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700"
          >确认拒绝</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'

const items = ref<any[]>([])
const filterStatus = ref('')
const rejectDialogVisible = ref(false)
const rejectReason = ref('')
const currentRequestId = ref<number | null>(null)

const statusLabel = (s: string) => {
  return { pending: '待审核', approved: '已通过', rejected: '已拒绝', cancelled: '已取消' }[s] || s
}

const formatTime = (t: string) => {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN')
}

const loadData = async () => {
  try {
    const res = await api.get<any>('/b-endpoint/users/email-changes', {
      params: { page: 1, size: 100, status: filterStatus.value || undefined },
    })
    console.log('[EmailChanges] API response:', res)
    console.log('[EmailChanges] res.data:', res.data)
    console.log('[EmailChanges] res.data.items:', res.data?.items)
    items.value = res.data?.items || []
    console.log('[EmailChanges] items.value:', items.value)
  } catch (err) {
    console.error('[EmailChanges] loadData error:', err)
    items.value = []
  }
}

const handleApprove = async (item: any) => {
  if (!confirm(`确认通过用户「${item.nickname || item.old_email}」的邮箱换绑申请？\n新邮箱：${item.new_email}`)) return
  try {
    await api.put(`/b-endpoint/users/email-changes/${item.id}/approve`)
    alert('已通过')
    loadData()
  } catch (err: any) {
    alert(err.response?.data?.message || '操作失败')
  }
}

const handleReject = (item: any) => {
  currentRequestId.value = item.id
  rejectReason.value = ''
  rejectDialogVisible.value = true
}

const confirmReject = async () => {
  if (!currentRequestId.value) return
  try {
    const url = `/b-endpoint/users/email-changes/${currentRequestId.value}/reject` +
      (rejectReason.value ? `?reason=${encodeURIComponent(rejectReason.value)}` : '')
    await api.put(url, undefined)
    rejectDialogVisible.value = false
    alert('已拒绝')
    loadData()
  } catch (err: any) {
    alert(err.response?.data?.message || '操作失败')
  }
}

onMounted(() => {
  loadData()
})
</script>
