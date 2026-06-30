<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Copy, Check, Package, Truck, MapPin, Calendar } from 'lucide-vue-next'
import { api } from '@/utils/api'
import { formatTime } from '@/utils/formatTime'

const route = useRoute()

const copied = ref(false)
const loading = ref(true)
const logistics = ref<any>(null)

const STATUS_LABEL: Record<string, string> = {
  pending: '待发货',
  picked_up: '已揽收',
  in_transit: '运输中',
  out_for_delivery: '派送中',
  delivered: '已送达',
}

function copyTrackingNumber() {
  navigator.clipboard.writeText(logistics.value.tracking_number)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}

const loadLogistics = async () => {
  loading.value = true
  try {
    const orderId = route.params.id as string
    if (!orderId) {
      throw new Error('订单ID不存在')
    }
    const res = await api.get<any>('/c-endpoint/logistics', { params: { order_id: Number(orderId) } })
    if (res.code === 0) {
      const data = res.data
      const record = Array.isArray(data) ? data[0] : data
      if (record) {
        // timeline 可能是 JSON 字符串
        if (typeof record.timeline === 'string') {
          try {
            record.timeline = JSON.parse(record.timeline)
          } catch {
            record.timeline = []
          }
        }
        logistics.value = record
      } else {
        logistics.value = null
      }
    } else {
      logistics.value = null
    }
  } catch (error) {
    console.error('Failed to load logistics:', error)
    logistics.value = null
  } finally {
    loading.value = false
  }
}

onMounted(loadLogistics)
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <div v-if="loading" class="min-h-screen flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>
    <div v-else-if="!logistics" class="mx-4 md:mx-8 lg:mx-12 py-6">
      <div class="bg-white rounded-2xl shadow-sm p-6 text-center">
        <Package class="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <p class="text-gray-500 text-lg">暂无物流信息</p>
        <p class="text-gray-400 text-sm mt-2">商家尚未发货或物流信息尚未更新</p>
      </div>
    </div>
    <div v-else class="mx-4 md:mx-8 lg:mx-12 py-6">
      <div class="bg-white rounded-2xl shadow-sm p-6">
        <div class="flex items-center justify-between mb-6">
          <h1 class="text-xl font-bold text-gray-900">物流详情</h1>
          <span class="text-sm text-gray-500">订单号：#{{ logistics.order_id }}</span>
        </div>

        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 mb-8">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-sm">
                <Truck class="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p class="font-semibold text-gray-900">{{ logistics.carrier }}</p>
                <div class="flex items-center gap-2 mt-1">
                  <span class="text-sm text-gray-500">运单号：</span>
                  <span class="text-sm font-medium text-indigo-600">{{ logistics.tracking_number }}</span>
                  <button 
                    @click="copyTrackingNumber"
                    class="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                    title="复制运单号"
                  >
                    <Check v-if="copied" class="w-4 h-4 text-green-500" />
                    <Copy v-else class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
            <div 
              :class="[
                'px-4 py-2 rounded-full text-sm font-medium',
                logistics.status === 'delivered' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
              ]"
            >
              {{ STATUS_LABEL[logistics.status] || logistics.status }}
            </div>
          </div>

          <div class="mt-4 flex items-center gap-6">
            <div class="flex items-center gap-2 text-sm text-gray-500">
              <Calendar class="w-4 h-4" />
              <span>预计送达：{{ formatTime(logistics.estimated_delivery) || '暂无' }}</span>
            </div>
          </div>
        </div>

        <div class="relative">
          <div class="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200"></div>

          <div class="space-y-6">
            <div 
              v-for="(record, index) in logistics.timeline" 
              :key="index"
              :class="[
                'relative flex gap-4',
                index === 0 ? '' : ''
              ]"
            >
              <div 
                :class="[
                  'relative z-10 w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0',
                  index === 0 
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' 
                    : 'bg-white border-2 border-gray-200'
                ]"
              >
                <Package 
                  :class="[
                    'w-5 h-5',
                    index === 0 ? 'text-white' : 'text-gray-400'
                  ]" 
                />
              </div>

              <div 
                :class="[
                  'flex-1 pb-6',
                  index === 0 ? 'border-l-2 border-indigo-600 pl-6' : ''
                ]"
              >
                <div class="flex items-center gap-3 mb-1">
                  <span 
                    :class="[
                      'text-sm font-medium',
                      index === 0 ? 'text-indigo-600' : 'text-gray-900'
                    ]"
                  >
                    {{ STATUS_LABEL[record.status] || record.status }}
                  </span>
                  <span class="text-sm text-gray-400">{{ formatTime(record.time) }}</span>
                </div>
                <p 
                  :class="[
                    'text-sm',
                    index === 0 ? 'text-gray-900' : 'text-gray-500'
                  ]"
                >
                  {{ record.location || record.description || '' }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="logistics.order_address" class="mt-6 bg-white rounded-2xl shadow-sm p-6">
        <h3 class="font-semibold text-gray-900 mb-4">收货地址</h3>
        <div class="flex items-start gap-3">
          <div class="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
            <MapPin class="w-5 h-5 text-gray-400" />
          </div>
          <p class="text-sm text-gray-700">{{ logistics.order_address }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
