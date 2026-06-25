<template>
  <div>
    <div class="mb-8">
      <h1 class="font-display text-3xl text-gray-800 mb-2">售后管理</h1>
      <p class="text-gray-500">处理买家的售后申请</p>
    </div>

    <div class="bg-white rounded-xl shadow-md overflow-hidden">
      <div v-if="loading" class="animate-pulse p-6 space-y-4">
        <div v-for="i in 5" :key="i" class="h-16 rounded-xl bg-gray-100" />
      </div>
      <template v-else>
      <table v-if="requests.length > 0" class="w-full">
        <thead>
          <tr class="bg-gray-50">
            <th class="text-left px-6 py-4 text-sm font-semibold text-gray-600">售后ID</th>
            <th class="text-left px-6 py-4 text-sm font-semibold text-gray-600">订单号</th>
            <th class="text-left px-6 py-4 text-sm font-semibold text-gray-600">买家</th>
            <th class="text-left px-6 py-4 text-sm font-semibold text-gray-600">类型</th>
            <th class="text-left px-6 py-4 text-sm font-semibold text-gray-600">状态</th>
            <th class="text-left px-6 py-4 text-sm font-semibold text-gray-600">原因</th>
            <th class="text-center px-6 py-4 text-sm font-semibold text-gray-600">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="req in requests" :key="req.id" class="border-b border-gray-100 hover:bg-gray-50">
            <td class="px-6 py-4">
              <span class="text-sm font-mono text-gray-800">#{{ req.id }}</span>
            </td>
            <td class="px-6 py-4">
              <span class="text-sm text-gray-600">#{{ req.order_id }}</span>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-full bg-blue-50 flex items-center justify-center shrink-0">
                  <span class="text-xs font-bold text-blue-500">{{ (req.buyer_name || req.buyer_email || '?')[0] }}</span>
                </div>
                <div class="min-w-0">
                  <p class="text-sm text-gray-800 truncate">{{ req.buyer_name || '未知买家' }}</p>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <span :class="typeClass[req.type]" class="px-2.5 py-0.5 rounded-full text-xs font-medium">
                {{ typeLabel[req.type] }}
              </span>
            </td>
            <td class="px-6 py-4">
              <span :class="statusClass[req.status]" class="px-2.5 py-0.5 rounded-full text-xs font-medium">
                {{ statusLabel[req.status] }}
              </span>
            </td>
            <td class="px-6 py-4">
              <p class="text-sm text-gray-600 max-w-xs truncate">{{ req.reason }}</p>
            </td>
            <td class="px-6 py-4 text-center">
              <div class="flex items-center justify-center gap-2">
                <button
                  v-if="req.status === 'pending'"
                  @click="handleApprove(req.id)"
                  class="px-3 py-1.5 bg-green-100 text-green-700 rounded-lg text-xs font-medium hover:bg-green-200 transition-colors cursor-pointer"
                >
                  同意
                </button>
                <button
                  v-if="req.status === 'pending'"
                  @click="handleReject(req.id)"
                  class="px-3 py-1.5 bg-red-100 text-red-700 rounded-lg text-xs font-medium hover:bg-red-200 transition-colors cursor-pointer"
                >
                  拒绝
                </button>
                <!-- refund + approved: 直接完成 -->
                <button
                  v-if="req.status === 'approved' && req.type === 'refund'"
                  @click="handleComplete(req.id)"
                  class="px-3 py-1.5 bg-blue-100 text-blue-700 rounded-lg text-xs font-medium hover:bg-blue-200 transition-colors cursor-pointer"
                >
                  完成退款
                </button>
                <!-- return/exchange + approved: 等待退货 -->
                <span v-if="req.status === 'approved' && (req.type === 'return' || req.type === 'exchange')" class="text-xs text-amber-600 font-medium">
                  等待买家退货
                </span>
                <!-- returned: 确认收货 -->
                <button
                  v-if="req.status === 'returned'"
                  @click="handleConfirmReceived(req.id)"
                  class="px-3 py-1.5 bg-blue-100 text-blue-700 rounded-lg text-xs font-medium hover:bg-blue-200 transition-colors cursor-pointer"
                >
                  确认收货
                </button>
                <!-- resend: 填写换货物流 -->
                <button
                  v-if="req.status === 'resend'"
                  @click="openResendModal(req.id)"
                  class="px-3 py-1.5 bg-purple-100 text-purple-700 rounded-lg text-xs font-medium hover:bg-purple-200 transition-colors cursor-pointer"
                >
                  填写换货物流
                </button>
                <span v-if="req.status === 'completed'" class="text-xs text-green-600 font-medium">已完成</span>
                <span v-if="req.status === 'rejected'" class="text-xs text-red-600 font-medium">已拒绝</span>
              </div>
              <!-- 退货/换货物流信息 -->
              <div v-if="req.return_tracking_number" class="mt-1 text-xs text-gray-500">
                退货：{{ req.return_carrier }} {{ req.return_tracking_number }}
              </div>
              <div v-if="req.resend_tracking_number" class="mt-1 text-xs text-purple-500">
                换货发货：{{ req.resend_carrier }} {{ req.resend_tracking_number }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 换货物流弹窗 -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showResendModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="showResendModal = false">
            <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <h3 class="text-lg font-semibold text-gray-900">填写换货物流</h3>
                <button @click="showResendModal = false" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors text-xl">
                  &times;
                </button>
              </div>
              <div class="p-6 space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">快递公司</label>
                  <select v-model="resendCarrier" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500">
                    <option value="SF-Express">顺丰速运</option>
                    <option value="JD-Express">京东物流</option>
                    <option value="ZTO-Express">中通快递</option>
                    <option value="YTO-Express">圆通快递</option>
                    <option value="EMS">邮政EMS</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">快递单号</label>
                  <input
                    v-model="resendTrackingNumber"
                    type="text"
                    placeholder="请输入换货快递单号"
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <button
                  @click="submitResend"
                  :disabled="resendSubmitting"
                  class="w-full py-3 bg-purple-600 text-white rounded-xl font-medium hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ resendSubmitting ? '提交中...' : '确认发货' }}
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <div v-if="requests.length === 0" class="flex flex-col items-center justify-center py-20">
        <div class="w-16 h-16 rounded-xl bg-gray-100 flex items-center justify-center mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
          </svg>
        </div>
        <p class="text-gray-500">暂无售后申请</p>
      </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'

const requests = ref<any[]>([])
const loading = ref(true)

// 换货发货弹窗
const showResendModal = ref(false)
const resendAfterSaleId = ref<number | null>(null)
const resendTrackingNumber = ref('')
const resendCarrier = ref('SF-Express')
const resendSubmitting = ref(false)

const typeLabel: Record<string, string> = {
  refund: '退款',
  return: '退货',
  exchange: '换货',
}

const typeClass: Record<string, string> = {
  refund: 'bg-blue-100 text-blue-700',
  return: 'bg-orange-100 text-orange-700',
  exchange: 'bg-purple-100 text-purple-700',
}

const statusLabel: Record<string, string> = {
  pending: '待处理',
  approved: '已同意',
  returned: '退货中',
  resend: '换货发货中',
  rejected: '已拒绝',
  completed: '已完成',
  cancelled: '已取消',
}

const statusClass: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-700',
  approved: 'bg-green-100 text-green-700',
  returned: 'bg-amber-100 text-amber-700',
  resend: 'bg-purple-100 text-purple-700',
  rejected: 'bg-red-100 text-red-700',
  completed: 'bg-blue-100 text-blue-700',
  cancelled: 'bg-gray-100 text-gray-500',
}

async function fetchRequests() {
  loading.value = true
  try {
    const res = await api.get<any>('/m-endpoint/after-sales')
    if (res.code === 0) {
      const data = res.data
      if (Array.isArray(data)) {
        requests.value = data
      } else if (data?.items) {
        requests.value = data.items
      } else if (data?.data?.items) {
        requests.value = data.data.items
      } else if (data?.data && Array.isArray(data.data)) {
        requests.value = data.data
      } else {
        requests.value = []
      }
    }
  } catch (error) {
    console.error('Failed to fetch after-sales:', error)
  } finally {
    loading.value = false
  }
}

async function handleApprove(id: number) {
  try {
    const res = await api.put(`/m-endpoint/after-sales/${id}/approve`)
    if (res.code === 0) {
      fetchRequests()
    }
  } catch (error) {
    console.error('Failed to approve:', error)
  }
}

async function handleReject(id: number) {
  try {
    const res = await api.put(`/m-endpoint/after-sales/${id}/reject`)
    if (res.code === 0) {
      fetchRequests()
    }
  } catch (error) {
    console.error('Failed to reject:', error)
  }
}

async function handleComplete(id: number) {
  if (!confirm('确认完成该售后退款？')) return
  try {
    const res = await api.put(`/m-endpoint/after-sales/${id}/complete`)
    if (res.code === 0) {
      fetchRequests()
    }
  } catch (error) {
    console.error('Failed to complete:', error)
  }
}

async function handleConfirmReceived(id: number) {
  if (!confirm('确认已收到退货商品？')) return
  try {
    const res = await api.put(`/m-endpoint/after-sales/${id}/confirm-received`)
    if (res.code === 0) {
      fetchRequests()
    }
  } catch (error) {
    console.error('Failed to confirm received:', error)
  }
}

function openResendModal(id: number) {
  resendAfterSaleId.value = id
  resendTrackingNumber.value = ''
  resendCarrier.value = 'SF-Express'
  showResendModal.value = true
}

async function submitResend() {
  if (!resendTrackingNumber.value.trim()) {
    alert('请输入换货快递单号')
    return
  }
  resendSubmitting.value = true
  try {
    const res = await api.put(`/m-endpoint/after-sales/${resendAfterSaleId.value}/resend`, {
      tracking_number: resendTrackingNumber.value.trim(),
      carrier: resendCarrier.value,
    })
    if (res.code === 0) {
      alert('换货已发出')
      showResendModal.value = false
      fetchRequests()
    } else {
      alert(res.message || '提交失败')
    }
  } catch (err: any) {
    alert(err.message || '提交失败')
  } finally {
    resendSubmitting.value = false
  }
}

onMounted(fetchRequests)
</script>
