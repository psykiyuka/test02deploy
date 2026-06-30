<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { RefreshCw, Upload, Plus, Clock, CheckCircle, XCircle, Truck } from 'lucide-vue-next'
import { api } from '@/utils/api'
import { formatTime } from '@/utils/formatTime'
import type { AfterSaleRequest } from '@/types'

const route = useRoute()
const router = useRouter()
const selectedType = ref('refund')
const reason = ref('')
const orderId = ref<number | null>(null)
const isSubmitting = ref(false)
const loading = ref(true)
const afterSaleRecords = ref<AfterSaleRequest[]>([])

// 订单选择弹窗
const showOrderPicker = ref(false)
const orderList = ref<any[]>([])
const orderLoading = ref(false)

// 退货物流弹窗
const showReturnLogistics = ref(false)
const returnLogisticsAfterSaleId = ref<number | null>(null)
const returnTrackingNumber = ref('')
const returnCarrier = ref('SF-Express')
const returnLogisticsSubmitting = ref(false)

const typeOptions = [
  { id: 'refund', label: '仅退款', description: '不需要退货，仅申请退款' },
  { id: 'return', label: '退货退款', description: '需要退货并申请退款' },
  { id: 'exchange', label: '换货', description: '更换同款或其他商品' },
]

async function fetchAfterSales() {
  loading.value = true
  try {
    const res = await api.get<any>('/c-endpoint/after-sales')
    if (res.code === 0) {
      const data = res.data as any
      afterSaleRecords.value = Array.isArray(data) ? data : (data.items || data)
    }
  } catch (err) {
    console.error('获取售后记录失败:', err)
  } finally {
    loading.value = false
  }
}

async function openOrderPicker() {
  showOrderPicker.value = true
  orderLoading.value = true
  try {
    const res = await api.get<any>('/c-endpoint/orders', { params: { status: 'paid' } })
    if (res.code === 0) {
      const data = res.data as any
      const paidOrders = Array.isArray(data) ? data : (data.items || data)
      // 同时获取 shipped 状态的订单
      const res2 = await api.get<any>('/c-endpoint/orders', { params: { status: 'shipped' } })
      let shippedOrders: any[] = []
      if (res2.code === 0) {
        const data2 = res2.data as any
        shippedOrders = Array.isArray(data2) ? data2 : (data2.items || data2)
      }
      // 同时获取 delivered 状态的订单
      const res3 = await api.get<any>('/c-endpoint/orders', { params: { status: 'delivered' } })
      let deliveredOrders: any[] = []
      if (res3.code === 0) {
        const data3 = res3.data as any
        deliveredOrders = Array.isArray(data3) ? data3 : (data3.items || data3)
      }
      orderList.value = [...paidOrders, ...shippedOrders, ...deliveredOrders]
    }
  } catch (err) {
    console.error('获取订单列表失败:', err)
  } finally {
    orderLoading.value = false
  }
}

function selectOrder(order: any) {
  orderId.value = order.id
  showOrderPicker.value = false
}

async function submitAfterSale() {
  if (!orderId.value) {
    alert('请选择或输入订单号')
    return
  }
  if (!reason.value.trim()) {
    alert('请填写申请原因')
    return
  }

  isSubmitting.value = true
  try {
    const res = await api.post('/c-endpoint/after-sales', {
      order_id: orderId.value,
      type: selectedType.value,
      reason: reason.value,
    })
    if (res.code === 0) {
      alert('售后申请提交成功')
      orderId.value = null
      reason.value = ''
      selectedType.value = 'refund'
      await fetchAfterSales()
    } else {
      alert(res.message || '提交失败')
    }
  } catch (err: any) {
    alert(err.message || '提交失败')
  } finally {
    isSubmitting.value = false
  }
}

async function cancelAfterSale(id: number) {
  if (!confirm('确定要取消该售后申请吗？')) return
  try {
    const res = await api.put(`/c-endpoint/after-sales/${id}/cancel`)
    if (res.code === 0) {
      await fetchAfterSales()
    } else {
      alert(res.message || '取消失败')
    }
  } catch (err: any) {
    alert(err.message || '取消失败')
  }
}

function openReturnLogistics(afterSaleId: number) {
  returnLogisticsAfterSaleId.value = afterSaleId
  returnTrackingNumber.value = ''
  returnCarrier.value = 'SF-Express'
  showReturnLogistics.value = true
}

async function submitReturnLogistics() {
  if (!returnTrackingNumber.value.trim()) {
    alert('请输入快递单号')
    return
  }
  returnLogisticsSubmitting.value = true
  try {
    const res = await api.put(`/c-endpoint/after-sales/${returnLogisticsAfterSaleId.value}/return-logistics`, {
      tracking_number: returnTrackingNumber.value.trim(),
      carrier: returnCarrier.value,
    })
    if (res.code === 0) {
      alert('退货物流信息已提交')
      showReturnLogistics.value = false
      await fetchAfterSales()
    } else {
      alert(res.message || '提交失败')
    }
  } catch (err: any) {
    alert(err.message || '提交失败')
  } finally {
    returnLogisticsSubmitting.value = false
  }
}

function getStatusConfig(status: string) {
  const configs: Record<string, { label: string; class: string; icon: typeof Clock }> = {
    pending: { label: '申请中', class: 'bg-yellow-100 text-yellow-700', icon: Clock },
    approved: { label: '已同意', class: 'bg-green-100 text-green-700', icon: CheckCircle },
    returned: { label: '退货中', class: 'bg-amber-100 text-amber-700', icon: Truck },
    resend: { label: '换货发货中', class: 'bg-purple-100 text-purple-700', icon: Truck },
    rejected: { label: '已拒绝', class: 'bg-red-100 text-red-700', icon: XCircle },
    cancelled: { label: '已取消', class: 'bg-gray-100 text-gray-600', icon: XCircle },
    completed: { label: '已完成', class: 'bg-blue-100 text-blue-700', icon: CheckCircle },
  }
  return configs[status] || { label: status, class: 'bg-gray-100 text-gray-600', icon: Clock }
}

function getTypeLabel(type: string) {
  const labels: Record<string, string> = { refund: '仅退款', return: '退货退款', exchange: '换货' }
  return labels[type] || type
}

function getTypeClass(type: string) {
  const classes: Record<string, string> = {
    refund: 'bg-blue-100 text-blue-700',
    return: 'bg-purple-100 text-purple-700',
    exchange: 'bg-orange-100 text-orange-700',
  }
  return classes[type] || 'bg-gray-100 text-gray-700'
}

onMounted(() => {
  // 从路由参数获取 order_id
  const queryOrderId = route.query.order_id
  if (queryOrderId) {
    orderId.value = Number(queryOrderId)
  }
  fetchAfterSales()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <div class="mx-4 md:mx-8 lg:mx-12 py-6">
      <div class="flex items-center gap-3 mb-6">
        <RefreshCw class="w-6 h-6 text-indigo-600" />
        <h1 class="text-2xl font-bold text-gray-900">售后服务</h1>
      </div>

      <div class="grid lg:grid-cols-2 gap-6">
        <div class="bg-white rounded-2xl shadow-sm p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-6">申请售后</h2>

          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-3">售后类型</label>
            <div class="grid grid-cols-3 gap-3">
              <button
                v-for="option in typeOptions"
                :key="option.id"
                @click="selectedType = option.id"
                :class="[
                  'p-4 rounded-xl border-2 text-left transition-all duration-300',
                  selectedType === option.id
                    ? 'border-indigo-600 bg-indigo-50'
                    : 'border-gray-200 hover:border-gray-300'
                ]"
              >
                <div
                  :class="[
                    'w-6 h-6 rounded-full flex items-center justify-center mb-2',
                    selectedType === option.id ? 'bg-indigo-600' : 'bg-gray-200'
                  ]"
                >
                  <svg v-if="selectedType === option.id" class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <p :class="['font-medium text-sm', selectedType === option.id ? 'text-indigo-600' : 'text-gray-900']">
                  {{ option.label }}
                </p>
                <p class="text-xs text-gray-500 mt-1">{{ option.description }}</p>
              </button>
            </div>
          </div>

          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-3">订单号</label>
            <div class="flex gap-2">
              <input
                v-model.number="orderId"
                type="number"
                placeholder="请输入需要售后的订单号"
                class="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              />
              <button
                @click="openOrderPicker"
                class="px-4 py-3 border border-indigo-200 text-indigo-600 rounded-xl text-sm font-medium hover:bg-indigo-50 transition-colors flex items-center gap-1"
              >
                <Plus class="w-4 h-4" />
                从订单选择
              </button>
            </div>
            <p v-if="orderId" class="mt-2 text-sm text-indigo-600">已选择订单 #{{ orderId }}</p>
          </div>

          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-3">申请原因</label>
            <textarea
              v-model="reason"
              rows="4"
              placeholder="请描述您的问题..."
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
            ></textarea>
          </div>

          <button
            @click="submitAfterSale"
            :disabled="isSubmitting"
            class="w-full py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Upload class="w-5 h-5" />
            {{ isSubmitting ? '提交中...' : '提交申请' }}
          </button>
        </div>

        <div class="bg-white rounded-2xl shadow-sm p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-6">历史售后记录</h2>

          <div v-if="loading" class="py-12 text-center">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
              <RefreshCw class="w-8 h-8 text-gray-400" />
            </div>
            <p class="text-gray-500">加载中...</p>
          </div>

          <div v-else-if="afterSaleRecords.length === 0" class="py-12 text-center">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <RefreshCw class="w-8 h-8 text-gray-400" />
            </div>
            <p class="text-gray-500">暂无售后记录</p>
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="record in afterSaleRecords"
              :key="record.id"
              class="border border-gray-100 rounded-xl p-4 hover:border-gray-200 transition-colors"
            >
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-3">
                  <span class="text-sm text-gray-500">订单号：#{{ record.order_id }}</span>
                  <span
                    :class="[
                      'px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1',
                      getStatusConfig(record.status).class
                    ]"
                  >
                    <component :is="getStatusConfig(record.status).icon" class="w-3 h-3" />
                    {{ getStatusConfig(record.status).label }}
                  </span>
                </div>
                <span class="text-xs text-gray-400">{{ formatTime(record.created_at) }}</span>
              </div>

              <div class="flex items-center gap-3">
                <span
                  :class="[
                    'px-2 py-1 rounded-lg text-xs font-medium',
                    getTypeClass(record.type)
                  ]"
                >
                  {{ getTypeLabel(record.type) }}
                </span>
                <span class="text-sm text-gray-600">{{ record.reason }}</span>
              </div>

              <div v-if="record.status === 'pending'" class="mt-3 pt-3 border-t border-gray-50">
                <button
                  @click="cancelAfterSale(record.id)"
                  class="text-sm text-gray-500 hover:text-red-500 transition-colors"
                >
                  取消申请
                </button>
              </div>

              <!-- 退货物流：approved + return/exchange → 填写退货物流 -->
              <div v-if="record.status === 'approved' && (record.type === 'return' || record.type === 'exchange')" class="mt-3 pt-3 border-t border-gray-50">
                <button
                  @click="openReturnLogistics(record.id)"
                  class="flex items-center gap-1.5 text-sm text-amber-600 hover:text-amber-700 font-medium transition-colors"
                >
                  <Truck class="w-4 h-4" />
                  填写退货物流
                </button>
                <p class="text-xs text-gray-400 mt-1">商家已同意，请填写退货快递信息</p>
              </div>

              <!-- 退货物流信息展示 -->
              <div v-if="record.return_tracking_number" class="mt-3 pt-3 border-t border-gray-50">
                <div class="flex items-center gap-2">
                  <Truck class="w-4 h-4 text-amber-500" />
                  <span class="text-sm text-gray-700">退货快递：{{ record.return_carrier || 'SF-Express' }}</span>
                  <span class="text-sm text-gray-500">{{ record.return_tracking_number }}</span>
                </div>
              </div>

              <!-- 换货发货物流信息展示 -->
              <div v-if="record.resend_tracking_number" class="mt-3 pt-3 border-t border-gray-50">
                <div class="flex items-center gap-2">
                  <Truck class="w-4 h-4 text-purple-500" />
                  <span class="text-sm text-gray-700">换货发货：{{ record.resend_carrier || 'SF-Express' }}</span>
                  <span class="text-sm text-gray-500">{{ record.resend_tracking_number }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 订单选择弹窗 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showOrderPicker" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="showOrderPicker = false">
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <h3 class="text-lg font-semibold text-gray-900">选择订单</h3>
              <button @click="showOrderPicker = false" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors text-xl">
                &times;
              </button>
            </div>
            <div class="p-6 max-h-96 overflow-y-auto">
              <div v-if="orderLoading" class="py-8 text-center text-gray-400">加载中...</div>
              <div v-else-if="orderList.length === 0" class="py-8 text-center text-gray-400">
                没有可申请售后的订单（仅已付款/已发货/已完成的订单可申请售后）
              </div>
              <div v-else class="space-y-3">
                <div
                  v-for="order in orderList"
                  :key="order.id"
                  @click="selectOrder(order)"
                  class="p-4 rounded-xl border border-gray-200 cursor-pointer hover:border-indigo-400 hover:bg-indigo-50 transition-all"
                >
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium text-gray-900">订单 #{{ order.id }}</span>
                    <span class="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">
                      {{ order.status === 'paid' ? '已付款' : order.status === 'shipped' ? '已发货' : '已完成' }}
                    </span>
                  </div>
                  <div class="text-sm text-gray-500">
                    <span>{{ order.items?.map((i: any) => i.product_name).join('、') || '商品' }}</span>
                    <span class="ml-2 text-rose-600 font-medium">¥{{ order.total_amount }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 退货物流弹窗 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showReturnLogistics" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="showReturnLogistics = false">
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <h3 class="text-lg font-semibold text-gray-900">填写退货物流</h3>
              <button @click="showReturnLogistics = false" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors text-xl">
                &times;
              </button>
            </div>
            <div class="p-6 space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">快递公司</label>
                <select v-model="returnCarrier" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500">
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
                  v-model="returnTrackingNumber"
                  type="text"
                  placeholder="请输入退货快递单号"
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <button
                @click="submitReturnLogistics"
                :disabled="returnLogisticsSubmitting"
                class="w-full py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ returnLogisticsSubmitting ? '提交中...' : '提交退货物流' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.modal-enter-active { transition: all 0.25s ease-out; }
.modal-leave-active { transition: all 0.15s ease-in; }
.modal-enter-from { opacity: 0; }
.modal-enter-from > div { transform: scale(0.95); opacity: 0; }
.modal-leave-to { opacity: 0; }
.modal-leave-to > div { transform: scale(0.95); opacity: 0; }
</style>
