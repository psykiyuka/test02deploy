<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'
import type { Order } from '@/types'
import StatusBadge from '@/components/StatusBadge.vue'
import Pagination from '@/components/Pagination.vue'
import { ShoppingBag, ChevronDown, ChevronUp } from 'lucide-vue-next'

const orders = ref<Order[]>([])
const loading = ref(true)
const currentStatus = ref<string>('')
const currentPage = ref(1)
const totalCount = ref(0)
const expandedRows = ref<Set<number>>(new Set())

const statusTabs = [
  { value: '', label: '全部' },
  { value: 'pending', label: '待支付' },
  { value: 'paid', label: '已支付' },
  { value: 'cancelled', label: '已取消' },
]

function toggleExpand(orderId: number) {
  const newSet = new Set(expandedRows.value)
  if (newSet.has(orderId)) {
    newSet.delete(orderId)
  } else {
    newSet.add(orderId)
  }
  expandedRows.value = newSet
}

async function fetchOrders() {
  loading.value = true
  const params = new URLSearchParams()
  if (currentStatus.value) params.append('status', currentStatus.value)
  params.append('page', String(currentPage.value))
  params.append('size', '20')

  const res = await api.get<any>(`/b-endpoint/orders?${params.toString()}`)
  if (res.code === 0) {
    orders.value = (res.data.items ?? []).map((o: any) => ({
      cancelled_at: null,
      shipped_at: null,
      delivered_at: null,
      ...o,
    }))
    totalCount.value = res.data.total ?? 0
  }
  loading.value = false
}

function setStatus(status: string) {
  currentStatus.value = status
  currentPage.value = 1
  fetchOrders()
}

function goToPage(page: number) {
  currentPage.value = page
  fetchOrders()
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(fetchOrders)
</script>

<template>
  <div>
    <div class="mb-8">
      <h1 class="font-display text-3xl text-charcoal mb-1">订单管理</h1>
      <p class="text-charcoal/40 text-sm">查看和管理所有订单</p>
    </div>

    <div class="flex gap-2 mb-6 overflow-x-auto pb-1 scrollbar-hide">
      <button
        v-for="tab in statusTabs"
        :key="tab.value"
        @click="setStatus(tab.value)"
        class="px-5 py-2.5 rounded-full text-sm font-semibold transition-all cursor-pointer shrink-0"
        :class="currentStatus === tab.value
          ? 'bg-gradient-to-r from-gold-400 to-gold-500 text-white shadow-lg shadow-gold-300/25'
          : 'bg-white text-charcoal/40 hover:text-charcoal hover:shadow-sm border border-gold-50'"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-gold-50 overflow-hidden">
      <div v-if="loading" class="animate-pulse p-6 space-y-4">
        <div v-for="i in 5" :key="i" class="h-16 rounded-xl bg-gray-100" />
      </div>
      <div v-else-if="orders.length === 0" class="flex flex-col items-center justify-center py-20">
        <div class="w-16 h-16 rounded-2xl bg-gold-50 flex items-center justify-center mb-4">
          <ShoppingBag :size="28" class="text-gold-300" />
        </div>
        <p class="text-charcoal/30">暂无订单数据</p>
      </div>
      <template v-else>
        <table class="w-full">
          <thead>
            <tr class="border-b border-gold-50 bg-gradient-to-r from-gold-50/50 to-cream/50">
              <th class="text-left px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">订单 ID</th>
              <th class="text-left px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">金额</th>
              <th class="text-left px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">状态</th>
              <th class="text-left px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">收货地址</th>
              <th class="text-left px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">创建时间</th>
              <th class="text-center px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">详情</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="order in orders" :key="order.id">
              <tr class="border-b border-gold-50/50 hover:bg-gold-50/20 transition-colors">
                <td class="px-6 py-4">
                  <span class="text-sm text-charcoal font-mono font-semibold">#{{ order.id }}</span>
                </td>
                <td class="px-6 py-4">
                  <span class="text-sm font-bold text-gold-500">¥{{ order.total_amount }}</span>
                </td>
                <td class="px-6 py-4">
                  <StatusBadge :status="order.status" />
                </td>
                <td class="px-6 py-4">
                  <span class="text-sm text-charcoal/50 truncate max-w-[180px] block">{{ order.address || '-' }}</span>
                </td>
                <td class="px-6 py-4">
                  <span class="text-sm text-charcoal/30">{{ formatDate(order.created_at) }}</span>
                </td>
                <td class="px-6 py-4 text-center">
                  <button
                    @click="toggleExpand(order.id)"
                    class="p-1.5 rounded-lg text-charcoal/25 hover:text-gold-500 hover:bg-gold-50 transition-colors cursor-pointer"
                  >
                    <ChevronDown v-if="!expandedRows.has(order.id)" :size="18" />
                    <ChevronUp v-else :size="18" />
                  </button>
                </td>
              </tr>
              <tr v-if="expandedRows.has(order.id)">
                <td colspan="6" class="px-6 py-4 bg-gradient-to-r from-gold-50/30 to-cream/30">
                  <div class="rounded-xl bg-white p-5 border border-gold-50 shadow-sm">
                    <h4 class="text-sm font-semibold text-charcoal mb-3">订单明细</h4>
                    <div v-if="order.items && order.items.length > 0" class="space-y-2">
                      <div
                        v-for="(item, idx) in order.items"
                        :key="idx"
                        class="flex items-center justify-between py-2 border-b border-gold-50 last:border-b-0"
                      >
                        <div class="flex items-center gap-3">
                          <span class="text-sm text-charcoal">{{ item.product_name }}</span>
                          <span class="text-xs text-charcoal/30">×{{ item.quantity }}</span>
                        </div>
                        <span class="text-sm text-charcoal font-semibold">¥{{ item.price * item.quantity }}</span>
                      </div>
                    </div>
                    <div v-else class="text-sm text-charcoal/30 py-2">
                      暂无明细数据
                    </div>
                    <div class="flex justify-between items-center mt-3 pt-3 border-t border-gold-50">
                      <span class="text-sm text-charcoal/40">
                        {{ order.paid_at ? '支付时间: ' + formatDate(order.paid_at) : '尚未支付' }}
                      </span>
                      <span class="text-sm font-bold text-charcoal">合计: ¥{{ order.total_amount }}</span>
                    </div>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
        <div class="px-6 py-4 border-t border-gold-50">
          <Pagination
            :current="currentPage"
            :total="totalCount"
            :page-size="20"
            @change="goToPage"
          />
        </div>
      </template>
    </div>
  </div>
</template>