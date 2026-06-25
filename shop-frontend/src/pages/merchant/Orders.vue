<template>
  <div class="bg-white rounded-xl shadow-md p-6">
    <div class="flex justify-between items-center mb-6">
      <h3 class="text-lg font-semibold text-gray-800">订单管理</h3>
    </div>

    <div v-if="loading" class="animate-pulse p-6 space-y-4">
      <div v-for="i in 5" :key="i" class="h-16 rounded-xl bg-gray-100" />
    </div>
    <div v-else-if="orders.length === 0" class="flex flex-col items-center justify-center py-20">
      <p class="text-charcoal/30">暂无订单数据</p>
    </div>
    <div v-else class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="border-b">
            <th class="text-left py-3 px-4 text-sm font-medium text-gray-600">订单号</th>
            <th class="text-left py-3 px-4 text-sm font-medium text-gray-600">买家</th>
            <th class="text-left py-3 px-4 text-sm font-medium text-gray-600">商品</th>
            <th class="text-right py-3 px-4 text-sm font-medium text-gray-600">金额</th>
            <th class="text-right py-3 px-4 text-sm font-medium text-gray-600">状态</th>
            <th class="text-right py-3 px-4 text-sm font-medium text-gray-600">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id" class="border-b hover:bg-gray-50">
            <td class="py-3 px-4 text-sm">{{ order.id }}</td>
            <td class="py-3 px-4">
              <div class="text-sm font-medium text-gray-800">{{ order.buyer_nickname || '未知用户' }}</div>
              <div class="text-xs text-gray-400 mt-0.5">{{ order.buyer_email || '-' }}</div>
            </td>
            <td class="py-3 px-4">
              <div v-for="item in order.items" :key="item.id" class="text-sm">
                {{ item.product_name }} x {{ item.quantity }}
              </div>
            </td>
            <td class="py-3 px-4 text-sm text-right">¥{{ order.total_amount }}</td>
            <td class="py-3 px-4 text-right">
              <span :class="getStatusClass(order)" class="px-2 py-1 rounded text-xs">
                {{ getStatusText(order) }}
              </span>
            </td>
            <td class="py-3 px-4 text-right">
              <button v-if="order.status === 'paid'" @click="showShipModal(order)" class="text-indigo-600 hover:text-indigo-800">
                发货
              </button>
              <button v-else-if="order.status === 'shipped'" @click="showLogisticsModal(order)" class="text-green-600 hover:text-green-800">
                更新物流
              </button>
              <span v-else class="text-gray-400">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showShipModalData" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">确认发货</h3>
        <form @submit.prevent="handleShip" class="space-y-4">
          <div>
            <label class="block text-sm text-gray-500 mb-1">运单号（可选，不填则使用系统自动生成的运单号）</label>
            <input v-model="shipForm.tracking_number" type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg" placeholder="留空则使用自动运单号" />
          </div>
          <div class="flex justify-end space-x-3">
            <button type="button" @click="showShipModalData = null" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">取消</button>
            <button type="submit" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">确认发货</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showLogisticsModalData" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">更新物流状态</h3>
        <form @submit.prevent="handleUpdateLogistics" class="space-y-4">
          <div>
            <label class="block text-sm text-gray-500 mb-1">物流状态</label>
            <select v-model="logisticsForm.status" class="w-full px-4 py-2 border border-gray-300 rounded-lg">
              <option value="in_transit">运输中</option>
              <option value="out_for_delivery">派送中</option>
              <option value="delivered">已送达</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-500 mb-1">运单号（可选，留空保留原运单号）</label>
            <input v-model="logisticsForm.tracking_number" type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg" placeholder="留空则保留原运单号" />
          </div>
          <div class="flex justify-end space-x-3">
            <button type="button" @click="showLogisticsModalData = null" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">取消</button>
            <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">确认更新</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { api } from '@/utils/api'

const orders = ref<any[]>([])
const loading = ref(true)
const showShipModalData = ref<any>(null)
const showLogisticsModalData = ref<any>(null)

const shipForm = reactive({
  tracking_number: '',
})

const logisticsForm = reactive({
  status: 'in_transit',
  tracking_number: '',
})

const getStatusClass = (order: any) => {
  // 根据订单状态 + 物流细分状态返回对应颜色
  if (order.status === 'pending') return 'bg-yellow-100 text-yellow-700'
  if (order.status === 'paid') return 'bg-blue-100 text-blue-700'
  if (order.status === 'cancelled') return 'bg-gray-100 text-gray-700'
  if (order.status === 'delivered') return 'bg-green-100 text-green-700'
  // shipped: 根据物流细分状态区分颜色
  const ls = order.logistics_status
  if (ls === 'picked_up') return 'bg-amber-100 text-amber-700'
  if (ls === 'in_transit') return 'bg-orange-100 text-orange-700'
  if (ls === 'out_for_delivery') return 'bg-cyan-100 text-cyan-700'
  return 'bg-orange-100 text-orange-700' // 默认运输中
}

const getStatusText = (order: any) => {
  if (order.status === 'pending') return '待付款'
  if (order.status === 'paid') return '待发货'
  if (order.status === 'cancelled') return '已取消'
  if (order.status === 'delivered') return '已送达'
  // shipped: 根据物流细分状态显示文本
  const ls = order.logistics_status
  if (ls === 'picked_up') return '已揽收'
  if (ls === 'in_transit') return '运输中'
  if (ls === 'out_for_delivery') return '派送中'
  return '运输中'
}

const loadOrders = async () => {
  loading.value = true
  try {
    const res = await api.get<any>('/m-endpoint/orders')
    orders.value = res.data.items || []
  } catch (error) {
    console.error('Failed to load orders:', error)
  } finally {
    loading.value = false
  }
}

const showShipModal = (order: any) => {
  showShipModalData.value = order
  shipForm.tracking_number = ''
}

const handleShip = async () => {
  try {
    await api.put(`/m-endpoint/orders/${showShipModalData.value.id}/logistics`, {
      status: 'in_transit',
      tracking_number: shipForm.tracking_number || null,
    })
    showShipModalData.value = null
    loadOrders()
  } catch (error) {
    alert('发货失败')
  }
}

const showLogisticsModal = (order: any) => {
  showLogisticsModalData.value = order
  logisticsForm.status = 'in_transit'
  logisticsForm.tracking_number = ''
}

const handleUpdateLogistics = async () => {
  try {
    await api.put(`/m-endpoint/orders/${showLogisticsModalData.value.id}/logistics`, {
      status: logisticsForm.status,
      tracking_number: logisticsForm.tracking_number || null,
    })
    showLogisticsModalData.value = null
    loadOrders()
  } catch (error) {
    alert('更新失败')
  }
}

onMounted(loadOrders)
</script>