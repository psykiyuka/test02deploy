<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Package, Truck, CheckCircle, XCircle, Clock, ArrowRight, Trash2, Info } from 'lucide-vue-next'
import { api } from '@/utils/api'
import { useToast } from '@/composables/useToast'
import type { Order } from '@/types'

const router = useRouter()
const route = useRoute()
const toast = useToast()
const activeTab = ref('all')
const orders = ref<Order[]>([])
const loading = ref(true)

// 物流信息缓存：orderId -> logistics data
const logisticsMap = ref<Record<number, any>>({})
const logisticsLoading = ref<Record<number, boolean>>({})

// 售后信息缓存：orderId -> afterSale data
const afterSaleMap = ref<Record<number, any>>({})

const tabs = [
  { id: 'all', label: '全部' },
  { id: 'pending', label: '待付款' },
  { id: 'paid', label: '已付款' },
  { id: 'shipped', label: '已发货' },
  { id: 'delivered', label: '已完成' },
  { id: 'cancelled', label: '已取消' },
]

async function fetchOrders() {
  loading.value = true
  try {
    const status = activeTab.value === 'all' ? undefined : activeTab.value
    const res = await api.get<any>('/c-endpoint/orders', { params: status ? { status } : undefined })
    if (res.code === 0) {
      const data = res.data as any
      orders.value = Array.isArray(data) ? data : (data.items || data)
    }
  } catch (err) {
    console.error('获取订单列表失败:', err)
  } finally {
    loading.value = false
  }
}

function handleTabChange(tabId: string) {
  activeTab.value = tabId
  fetchOrders()
}

function getStatusBadge(status: string) {
  const statusConfig: Record<string, { label: string; class: string }> = {
    pending: { label: '待付款', class: 'bg-yellow-100 text-yellow-700' },
    paid: { label: '已付款', class: 'bg-blue-100 text-blue-700' },
    shipped: { label: '已发货', class: 'bg-indigo-100 text-indigo-700' },
    delivered: { label: '已完成', class: 'bg-green-100 text-green-700' },
    cancelled: { label: '已取消', class: 'bg-gray-100 text-gray-600' },
    rejected: { label: '已拒绝', class: 'bg-red-100 text-red-700' },
  }
  return statusConfig[status] || { label: status, class: 'bg-gray-100 text-gray-600' }
}

async function cancelOrder(orderId: number) {
  if (!confirm('确定要取消该订单吗？')) return
  try {
    const res = await api.put(`/c-endpoint/orders/${orderId}/cancel`)
    if (res.code === 0) {
      toast.show('success', '订单已取消')
      await fetchOrders()
    } else {
      toast.show('error', res.message || '取消订单失败')
    }
  } catch (err: any) {
    toast.show('error', err.message || '取消订单失败')
  }
}

function goToPayment(orderId: number) {
  router.push(`/payment/${orderId}`)
}

async function payOrder(orderId: number) {
  // 改为跳转支付页面
  goToPayment(orderId)
}

function viewLogistics(orderId: number) {
  router.push(`/orders/${orderId}/logistics`)
}

async function fetchLogistics(orderId: number) {
  logisticsLoading.value[orderId] = true
  try {
    const res = await api.get<any>('/c-endpoint/logistics', { params: { order_id: orderId } })
    if (res.code === 0) {
      const data = res.data
      // API 返回数组，取第一条记录
      const record = Array.isArray(data) ? data[0] : data
      if (record) {
        // timeline 可能是 JSON 字符串，需要解析
        if (typeof record.timeline === 'string') {
          try {
            record.timeline = JSON.parse(record.timeline)
          } catch {
            record.timeline = []
          }
        }
        logisticsMap.value[orderId] = record
      } else {
        logisticsMap.value[orderId] = null
      }
    }
  } catch (err) {
    console.error('获取物流信息失败:', err)
  } finally {
    logisticsLoading.value[orderId] = false
  }
}

async function fetchAfterSaleForOrder(orderId: number) {
  try {
    const res = await api.get<any>('/c-endpoint/after-sales', { params: { order_id: orderId } })
    if (res.code === 0) {
      const data = res.data as any
      const items = Array.isArray(data) ? data : (data.items || data || [])
      const match = items.find((a: any) => a.order_id === orderId)
      if (match) {
        afterSaleMap.value[orderId] = match
      }
    }
  } catch (err) {
    console.error('获取售后信息失败:', err)
  }
}

async function confirmReceive(orderId: number) {
  if (!confirm('确认已收到商品？')) return
  try {
    const res = await api.put(`/c-endpoint/orders/${orderId}/confirm`)
    if (res.code === 0) {
      toast.show('success', '确认收货成功')
      await fetchOrders()
    } else {
      toast.show('error', res.message || '确认收货失败')
    }
  } catch (err: any) {
    toast.show('error', err.message || '确认收货失败')
  }
}

function applyRefund(orderId: number) {
  router.push('/after-sales?order_id=' + orderId)
}

function applyAfterSale(orderId: number) {
  router.push('/after-sales?order_id=' + orderId)
}

function viewAfterSale(afterSaleId: number) {
  router.push('/after-sales?id=' + afterSaleId)
}

async function deleteOrder(orderId: number) {
  if (!confirm('确定要删除该订单吗？删除后不可恢复。')) return
  try {
    const res = await api.delete(`/c-endpoint/orders/${orderId}`)
    if (res.code === 0) {
      toast.show('success', '订单已删除')
      await fetchOrders()
    } else {
      toast.show('error', res.message || '删除订单失败')
    }
  } catch (err: any) {
    toast.show('error', err.message || '删除订单失败')
  }
}

function canDeleteOrder(status: string): boolean {
  return ['cancelled', 'delivered', 'rejected'].includes(status)
}

function toggleLogistics(orderId: number) {
  if (logisticsMap.value[orderId]) {
    delete logisticsMap.value[orderId]
  } else {
    fetchLogistics(orderId)
  }
}

onMounted(() => {
  fetchOrders()
})

// 每次路由变化时刷新订单列表（如从支付页返回时）
watch(() => route.path, (newPath) => {
  if (newPath === '/orders') {
    fetchOrders()
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <div class="mx-4 md:mx-8 lg:mx-12 py-6">
      <div class="flex items-center gap-3 mb-6">
        <Package class="w-6 h-6 text-indigo-600" />
        <h1 class="text-2xl font-bold text-gray-900">我的订单</h1>
      </div>

      <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div class="flex border-b border-gray-100 overflow-x-auto">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="handleTabChange(tab.id)"
            :class="[
              'px-4 md:px-6 py-4 text-sm font-medium whitespace-nowrap transition-all duration-300 relative',
              activeTab === tab.id 
                ? 'text-indigo-600' 
                : 'text-gray-500 hover:text-gray-700'
            ]"
          >
            {{ tab.label }}
            <div 
              v-if="activeTab === tab.id"
              class="absolute bottom-0 left-1/2 -translate-x-1/2 w-12 h-0.5 bg-indigo-600 rounded-full"
            ></div>
          </button>
        </div>

        <div v-if="loading" class="p-6 space-y-4">
          <div v-for="i in 3" :key="i" class="h-40 bg-gray-100 rounded-xl animate-pulse"></div>
        </div>

        <div v-else-if="orders.length === 0" class="py-16 text-center">
          <div class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Package class="w-10 h-10 text-gray-400" />
          </div>
          <p class="text-gray-500">暂无订单</p>
        </div>

        <div v-else class="divide-y divide-gray-100">
          <div 
            v-for="order in orders" 
            :key="order.id"
            class="p-6 hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-500">订单号：</span>
                <span class="text-sm font-medium text-gray-900">#{{ order.id }}</span>
              </div>
              <span class="text-sm text-gray-400">{{ order.created_at }}</span>
            </div>

            <div 
              v-for="(item, index) in order.items" 
              :key="index"
              class="flex items-center gap-4 py-3 border-b border-gray-100 last:border-0"
            >
              <div class="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center">
                <Package class="w-8 h-8 text-gray-400" />
              </div>
              <div class="flex-1">
                <h3 class="font-medium text-gray-900">{{ item.product_name }}</h3>
                <div class="flex items-center gap-4 mt-1">
                  <span class="text-sm text-rose-600 font-medium">¥{{ item.price }}</span>
                  <span class="text-sm text-gray-400">x{{ item.quantity }}</span>
                </div>
              </div>
            </div>

            <div class="flex items-center justify-between mt-4">
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-500">收货地址：</span>
                <span class="text-sm text-gray-700 truncate max-w-xs md:max-w-md">{{ order.address }}</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-sm text-gray-500">共 {{ order.items.length }} 件商品，合计</span>
                <span class="text-lg font-bold text-rose-600">¥{{ order.total_amount }}</span>
              </div>
            </div>

            <!-- 物流信息展示（已发货/已完成的订单） -->
            <div v-if="order.status === 'shipped' || order.status === 'delivered'" class="mt-3">
              <button
                @click="toggleLogistics(order.id)"
                class="flex items-center gap-1.5 text-sm text-indigo-600 hover:text-indigo-700 font-medium transition-colors"
              >
                <Truck class="w-4 h-4" />
                {{ logisticsMap[order.id] ? '收起物流' : '查看物流' }}
              </button>
              <div v-if="logisticsLoading[order.id]" class="mt-2 text-sm text-gray-400">加载物流信息中...</div>
              <div v-else-if="logisticsMap[order.id]" class="mt-3 p-4 bg-gray-50 rounded-xl">
                <div class="flex items-center gap-3 mb-3">
                  <Truck class="w-5 h-5 text-indigo-500" />
                  <div>
                    <p class="text-sm font-medium text-gray-800">
                      {{ logisticsMap[order.id].carrier || '物流公司' }}
                      <span v-if="logisticsMap[order.id].tracking_number" class="text-gray-500 ml-2">
                        运单号：{{ logisticsMap[order.id].tracking_number }}
                      </span>
                    </p>
                    <p class="text-xs text-gray-500 mt-0.5">
                      预计送达：{{ logisticsMap[order.id].estimated_delivery || '暂无' }}
                    </p>
                  </div>
                </div>
                <div v-if="logisticsMap[order.id].timeline && logisticsMap[order.id].timeline.length > 0" class="space-y-2 ml-1">
                  <div 
                    v-for="(step, idx) in logisticsMap[order.id].timeline" 
                    :key="idx"
                    class="flex gap-3 text-sm"
                  >
                    <div class="flex flex-col items-center">
                      <div :class="idx === 0 ? 'w-2.5 h-2.5 rounded-full bg-indigo-500' : 'w-2 h-2 rounded-full bg-gray-300 mt-0.5'"></div>
                      <div v-if="idx < logisticsMap[order.id].timeline.length - 1" class="w-px h-6 bg-gray-200"></div>
                    </div>
                    <div>
                      <p :class="idx === 0 ? 'text-gray-800 font-medium' : 'text-gray-500'">{{ step.location || step.status }}</p>
                      <p class="text-xs text-gray-400">{{ step.time }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 售后信息入口（已申请售后的订单） -->
            <div v-if="afterSaleMap[order.id]" class="mt-3">
              <button
                @click="viewAfterSale(afterSaleMap[order.id].id)"
                class="flex items-center gap-1.5 text-sm text-amber-600 hover:text-amber-700 font-medium transition-colors"
              >
                <Info class="w-4 h-4" />
                查看售后（{{ afterSaleMap[order.id].status === 'pending' ? '待处理' : afterSaleMap[order.id].status === 'approved' ? '已同意' : afterSaleMap[order.id].status === 'rejected' ? '已拒绝' : afterSaleMap[order.id].status === 'completed' ? '已完成' : afterSaleMap[order.id].status }}）
              </button>
            </div>

            <div class="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
              <span 
                :class="[
                  'px-3 py-1 rounded-full text-sm font-medium',
                  getStatusBadge(order.status).class
                ]"
              >
                {{ getStatusBadge(order.status).label }}
              </span>

              <div class="flex gap-2">
                <template v-if="order.status === 'pending'">
                  <button 
                    @click="cancelOrder(order.id)"
                    class="px-4 py-2 text-gray-600 hover:text-red-500 text-sm font-medium"
                  >
                    取消订单
                  </button>
                  <button 
                    @click="payOrder(order.id)"
                    class="px-6 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors flex items-center gap-2"
                  >
                    立即支付
                    <ArrowRight class="w-4 h-4" />
                  </button>
                </template>
                <template v-else-if="order.status === 'paid'">
                  <button
                    @click="applyRefund(order.id)"
                    class="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors"
                  >
                    申请退款
                  </button>
                </template>
                <template v-else-if="order.status === 'shipped'">
                  <button
                    @click="confirmReceive(order.id)"
                    class="px-6 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors flex items-center gap-2"
                  >
                    <CheckCircle class="w-4 h-4" />
                    确认收货
                  </button>
                  <button
                    @click="applyRefund(order.id)"
                    class="px-4 py-2 text-indigo-600 text-sm font-medium flex items-center gap-1"
                  >
                    申请售后
                  </button>
                  <button 
                    @click="viewLogistics(order.id)"
                    class="px-4 py-2 text-gray-500 text-sm font-medium flex items-center gap-1"
                  >
                    查看物流
                    <ArrowRight class="w-4 h-4" />
                  </button>
                </template>
                <template v-else-if="order.status === 'delivered'">
                  <button
                    @click="applyAfterSale(order.id)"
                    class="px-6 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
                  >
                    申请售后
                  </button>
                </template>
                <template v-else-if="order.status === 'cancelled'">
                  <button
                    disabled
                    title="暂不支持重新购买"
                    class="px-6 py-2 bg-gray-100 text-gray-400 rounded-lg text-sm font-medium cursor-not-allowed"
                  >
                    重新购买
                  </button>
                </template>

                <!-- 删除订单按钮：仅已取消/已完成/已拒绝的订单显示 -->
                <button
                  v-if="canDeleteOrder(order.status)"
                  @click="deleteOrder(order.id)"
                  class="px-4 py-2 text-red-500 hover:text-red-600 text-sm font-medium flex items-center gap-1"
                  title="删除订单"
                >
                  <Trash2 class="w-4 h-4" />
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
