<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'
import type { AfterSaleRequest } from '@/types'
import StatusBadge from '@/components/StatusBadge.vue'
import Pagination from '@/components/Pagination.vue'
import { ShieldCheck } from 'lucide-vue-next'

const afterSales = ref<AfterSaleRequest[]>([])
const loading = ref(false)
const currentStatus = ref<string>('')
const currentPage = ref(1)
const totalPages = ref(1)

const statusTabs = [
  { value: '', label: '全部' },
  { value: 'pending', label: '待处理' },
  { value: 'approved', label: '已通过' },
  { value: 'rejected', label: '已驳回' },
  { value: 'completed', label: '已完成' },
]

const typeLabels: Record<string, string> = {
  refund: '退款',
  return: '退货',
  exchange: '换货',
}

function getTypeLabel(type: string): string {
  return typeLabels[type] ?? type
}

async function fetchAfterSales() {
  loading.value = true
  const params = new URLSearchParams()
  if (currentStatus.value) params.append('status', currentStatus.value)
  params.append('page', String(currentPage.value))

  const res = await api.get<any>(`/b-endpoint/after-sales?${params.toString()}`)
  if (res.code === 0) {
    afterSales.value = res.data.items ?? res.data
    const total = res.data.total ?? 0
    const size = res.data.size ?? 20
    totalPages.value = Math.max(1, Math.ceil(total / size))
  }
  loading.value = false
}

function setStatus(status: string) {
  currentStatus.value = status
  currentPage.value = 1
  fetchAfterSales()
}

function goToPage(page: number) {
  currentPage.value = page
  fetchAfterSales()
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

onMounted(fetchAfterSales)
</script>

<template>
  <div>
    <div class="mb-8">
      <h1 class="font-display text-3xl text-charcoal mb-1">售后监管</h1>
      <p class="text-charcoal/40 text-sm">查看买家与卖家之间的售后纠纷，维护平台秩序</p>
    </div>

    <div class="flex flex-wrap gap-2 mb-6 overflow-x-auto pb-1 scrollbar-hide">
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
      <div v-else-if="afterSales.length === 0" class="flex flex-col items-center justify-center py-20">
        <div class="w-16 h-16 rounded-2xl bg-gold-50 flex items-center justify-center mb-4">
          <ShieldCheck :size="28" class="text-gold-300" />
        </div>
        <p class="text-charcoal/30">暂无售后纠纷</p>
      </div>
      <template v-else>
        <div class="overflow-x-auto">
          <table class="w-full min-w-[800px]">
            <thead>
              <tr class="border-b border-gold-50 bg-gradient-to-r from-gold-50/50 to-cream/50">
                <th class="text-left px-5 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">ID</th>
                <th class="text-left px-5 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">订单</th>
                <th class="text-left px-5 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">类型</th>
                <th class="text-left px-5 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">买家</th>
                <th class="text-left px-5 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">卖家</th>
                <th class="text-left px-5 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">原因</th>
                <th class="text-left px-5 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">状态</th>
                <th class="text-left px-5 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">时间</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in afterSales"
                :key="item.id"
                class="border-b border-gold-50/50 last:border-b-0 hover:bg-gold-50/20 transition-colors"
              >
                <td class="px-5 py-4">
                  <span class="text-sm text-charcoal font-mono font-semibold">#{{ item.id }}</span>
                </td>
                <td class="px-5 py-4">
                  <span class="text-sm text-charcoal font-mono">#{{ item.order_id }}</span>
                </td>
                <td class="px-5 py-4">
                  <span class="text-xs px-2.5 py-1 rounded-full bg-gold-50 text-gold-600 font-medium">
                    {{ getTypeLabel(item.type) }}
                  </span>
                </td>
                <td class="px-5 py-4">
                  <div class="flex items-center gap-2">
                    <div class="w-7 h-7 rounded-full bg-blue-50 flex items-center justify-center shrink-0">
                      <span class="text-xs font-bold text-blue-500">{{ (item.buyer_name || item.buyer_email || '?')[0] }}</span>
                    </div>
                    <div class="min-w-0">
                      <p class="text-sm text-charcoal truncate">{{ item.buyer_name || '未知买家' }}</p>
                      <p class="text-xs text-charcoal/30 truncate">{{ item.buyer_email || '' }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-5 py-4">
                  <div class="flex items-center gap-2">
                    <div class="w-7 h-7 rounded-full bg-orange-50 flex items-center justify-center shrink-0">
                      <span class="text-xs font-bold text-orange-500">{{ (item.seller_shop_name || item.seller_name || '?')[0] }}</span>
                    </div>
                    <div class="min-w-0">
                      <p class="text-sm text-charcoal truncate">{{ item.seller_shop_name || item.seller_name || '未知卖家' }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-5 py-4">
                  <span class="text-sm text-charcoal/50 truncate max-w-[150px] block">{{ item.reason }}</span>
                </td>
                <td class="px-5 py-4">
                  <StatusBadge :status="item.status" />
                </td>
                <td class="px-5 py-4">
                  <span class="text-sm text-charcoal/30">{{ formatDate(item.created_at) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="px-6 py-4 border-t border-gold-50">
          <Pagination
            :current-page="currentPage"
            :total-pages="totalPages"
            @page-change="goToPage"
          />
        </div>
      </template>
    </div>
  </div>
</template>
