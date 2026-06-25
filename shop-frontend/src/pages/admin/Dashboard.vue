<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/utils/api'
import { Package, ShoppingBag, FolderTree, RotateCcw, ArrowRight, TrendingUp, AlertCircle, Users, DollarSign, Mail } from 'lucide-vue-next'

const router = useRouter()

const loading = ref(true)
const stats = ref({
  totalOrders: 0,
  totalProducts: 0,
  pendingAfterSales: 0,
  totalCategories: 0,
  totalRevenue: 0,
  totalUsers: 0,
})
const recentOrders = ref<any[]>([])
const salesTrend = ref<{ label: string; total: number; height: number }[]>([])
const hoverIdx = ref(-1)

// SVG 图表计算
const CHART_H = 180
function getY(item: { total: number; height: number }): number {
  return item.total > 0 ? CHART_H - (item.height / 100) * CHART_H : CHART_H
}

const linePath = computed(() => {
  if (salesTrend.value.length === 0) return ''
  const points = salesTrend.value.map((item, i) => `${i * 80 + 40},${getY(item)}`)
  return `M ${points.join(' L ')}`
})

const areaPath = computed(() => {
  if (salesTrend.value.length === 0) return ''
  const topPoints = salesTrend.value.map((item, i) => `${i * 80 + 40},${getY(item)}`)
  const firstX = 40
  const lastX = (salesTrend.value.length - 1) * 80 + 40
  return `M ${firstX},${CHART_H} L ${topPoints.join(' L ')} L ${lastX},${CHART_H} Z`
})

const statCards = [
  { key: 'totalOrders', label: '订单总数', icon: ShoppingBag, gradient: 'from-blue-500 to-blue-600' },
  { key: 'totalRevenue', label: '总收入', icon: DollarSign, gradient: 'from-emerald-500 to-emerald-600', prefix: '¥' },
  { key: 'totalUsers', label: '用户总数', icon: Users, gradient: 'from-violet-500 to-violet-600' },
  { key: 'totalProducts', label: '在售商品', icon: Package, gradient: 'from-gold-400 to-gold-500' },
  { key: 'pendingAfterSales', label: '待处理售后', icon: AlertCircle, gradient: 'from-orange-400 to-orange-500' },
  { key: 'totalCategories', label: '商品分类', icon: FolderTree, gradient: 'from-cyan-500 to-cyan-600' },
]

const quickActions = [
  { label: '商品管理', path: '/admin/products', icon: Package, gradient: 'from-gold-400 to-gold-500' },
  { label: '分类管理', path: '/admin/categories', icon: FolderTree, gradient: 'from-emerald-500 to-emerald-600' },
  { label: '查看订单', path: '/admin/orders', icon: ShoppingBag, gradient: 'from-blue-500 to-blue-600' },
  { label: '用户管理', path: '/admin/users', icon: Users, gradient: 'from-violet-500 to-violet-600' },
  { label: '处理售后', path: '/admin/after-sales', icon: RotateCcw, gradient: 'from-orange-400 to-orange-500' },
  { label: '邮箱换绑审核', path: '/admin/email-changes', icon: Mail, gradient: 'from-sky-500 to-sky-600' },
]

async function fetchStats() {
  loading.value = true
  try {
    const res = await api.get<any>('/b-endpoint/dashboard/stats')
    if (res.code === 0) {
      const d = res.data
      stats.value = {
        totalOrders: d.total_orders,
        totalProducts: d.total_products,
        pendingAfterSales: d.pending_after_sales,
        totalCategories: d.total_categories,
        totalRevenue: d.total_revenue,
        totalUsers: d.total_users,
      }
      recentOrders.value = d.recent_orders || []
    }
  } finally {
    loading.value = false
  }
}

async function fetchSalesTrend() {
  try {
    const res = await api.get<any>('/b-endpoint/dashboard/sales-trend')
    console.log('[Dashboard] sales-trend response:', JSON.stringify(res))
    if (res.code === 0 && res.data?.trend) {
      const trend = res.data.trend as { label: string; total: number }[]
      const maxTotal = Math.max(...trend.map(t => t.total), 1)
      salesTrend.value = trend.map(t => ({
        label: t.label,
        total: t.total,
        height: t.total > 0 ? Math.max(15, (t.total / maxTotal) * 100) : 0,
      }))
      console.log('[Dashboard] salesTrend set:', salesTrend.value)
    } else {
      console.warn('[Dashboard] sales-trend returned non-zero code or no trend data:', res.code, res.data)
    }
  } catch (e) {
    console.error('[Dashboard] fetchSalesTrend error:', e)
  }
}

function navigateTo(path: string) {
  router.push(path)
}

function formatRevenue(val: number): string {
  if (val >= 10000) return (val / 10000).toFixed(1) + '万'
  return val.toFixed(2)
}

const statusLabel: Record<string, string> = { pending: '待支付', paid: '已支付', cancelled: '已取消' }
const statusClass: Record<string, string> = {
  pending: 'bg-amber-50 text-amber-700 border border-amber-200',
  paid: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
  cancelled: 'bg-gray-50 text-gray-500 border border-gray-200',
}

onMounted(() => {
  fetchStats()
  fetchSalesTrend()
})
</script>

<template>
  <div>
    <div class="mb-8">
      <h1 class="font-display text-3xl text-charcoal mb-1">管理后台</h1>
      <p class="text-charcoal/40 text-sm">欢迎回来，这是您的运营数据概览</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
      <div
        v-for="card in statCards.slice(0, 4)"
        :key="card.key"
        class="bg-white rounded-2xl p-5 shadow-sm border border-slate-100 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 group relative overflow-hidden"
      >
        <div v-if="loading" class="animate-pulse space-y-3">
          <div class="h-11 w-11 rounded-xl bg-gray-200" />
          <div class="h-7 w-16 rounded bg-gray-200" />
          <div class="h-4 w-20 rounded bg-gray-100" />
        </div>
        <div v-else>
          <div class="flex items-center justify-between mb-3">
            <div :class="[card.gradient, 'w-11 h-11 rounded-xl flex items-center justify-center shadow-lg bg-gradient-to-br']">
              <component :is="card.icon" :size="20" class="text-white" />
            </div>
            <TrendingUp class="w-4 h-4 text-slate-200 group-hover:text-emerald-400 transition-colors" />
          </div>
          <p class="text-3xl font-bold text-slate-800 tracking-tight">
            <template v-if="card.key === 'totalRevenue'">
              ¥{{ formatRevenue((stats as any)[card.key]) }}
            </template>
            <template v-else>
              {{ (stats as any)[card.key] }}
            </template>
          </p>
          <p class="text-sm text-slate-500 mt-1">{{ card.label }}</p>
          <span class="inline-flex items-center gap-0.5 mt-2 text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
            <TrendingUp class="w-3 h-3" /> +12.5% <span class="text-emerald-400">自上周</span>
          </span>
        </div>
        <!-- 背景装饰图标 -->
        <component :is="card.icon" class="absolute -bottom-3 -right-3 w-20 h-20 opacity-[0.04]" />
      </div>
    </div>

    <!-- 销售额走势 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-8">
      <div class="lg:col-span-2 bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <h3 class="font-display text-lg text-slate-800 mb-6">销售额走势</h3>
        <div v-if="salesTrend.length > 0" class="relative h-48">
          <!-- SVG 面积图 -->
          <svg :viewBox="`0 0 ${salesTrend.length * 80} 192`" preserveAspectRatio="none" class="w-full h-full" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="adminAreaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#818CF8" stop-opacity="0.35"/>
                <stop offset="100%" stop-color="#A78BFA" stop-opacity="0.05"/>
              </linearGradient>
            </defs>
            <!-- 网格线 -->
            <line v-for="(y, i) in [0, 48, 96, 144]" :key="'g'+i" x1="0" :y1="y" :x2="salesTrend.length * 80" :y2="y" :stroke="i === 3 ? '#E2E8F0' : '#F1F5F9'" stroke-width="1"/>
            <!-- 基线 -->
            <line x1="0" y1="180" :x2="salesTrend.length * 80" y2="180" stroke="#CBD5E1" stroke-width="1.5" stroke-linecap="round"/>

            <!-- 面积填充 -->
            <path :d="areaPath" fill="url(#adminAreaGrad)"/>
            <!-- 趋势线 -->
            <path :d="linePath" fill="none" stroke="#818CF8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <!-- 数据点 -->
            <g v-for="(item, idx) in salesTrend" :key="'p'+idx">
              <circle
                :cx="idx * 80 + 40"
                :cy="getY(item)"
                r="4"
                :fill="item.total > 0 ? '#818CF8' : '#CBD5E1'"
                stroke="white"
                stroke-width="2"
                class="cursor-pointer transition-all hover:r-6"
                @mouseenter="hoverIdx = idx"
                @mouseleave="hoverIdx = -1"
              />
            </g>
          </svg>

          <!-- X轴标签 -->
          <div class="absolute bottom-0 left-0 right-0 flex justify-around px-4 pb-1">
            <span v-for="(item, idx) in salesTrend" :key="'l'+idx" class="text-xs text-slate-400 w-[60px] text-center">{{ item.label }}</span>
          </div>

          <!-- 悬浮提示 -->
          <div
            v-if="hoverIdx >= 0 && salesTrend[hoverIdx]"
            class="absolute -top-12 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-xs px-3 py-1.5 rounded-lg shadow-lg pointer-events-none z-10 whitespace-nowrap"
            :style="{ left: (hoverIdx / salesTrend.length * 100 + (100/salesTrend.length/2)) + '%' }"
          >
            {{ salesTrend[hoverIdx].total > 0 ? `¥${salesTrend[hoverIdx].total.toFixed(2)}` : '无' }}
            <div class="absolute bottom-[-4px] left-1/2 -translate-x-1/2 w-2 h-2 rotate-45 bg-slate-800"></div>
          </div>
        </div>
        <div v-else class="flex items-center justify-center h-48 text-slate-400 text-sm">暂无销售数据</div>
      </div>
      <div class="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <h3 class="font-display text-lg text-slate-800 mb-5">快捷操作</h3>
        <div class="space-y-2.5">
          <button
            v-for="action in quickActions.slice(0, 5)"
            :key="action.path"
            @click="navigateTo(action.path)"
            class="w-full flex items-center justify-between px-4 py-3 rounded-xl bg-slate-50 hover:bg-slate-100 transition-all group cursor-pointer"
          >
            <div class="flex items-center gap-3">
              <div :class="[action.gradient, 'w-9 h-9 rounded-lg flex items-center justify-center bg-gradient-to-br shadow-md']">
                <component :is="action.icon" :size="16" class="text-white" />
              </div>
              <span class="text-sm font-semibold text-slate-700">{{ action.label }}</span>
            </div>
            <ArrowRight :size="14" class="text-slate-300 group-hover:text-slate-500 group-hover:translate-x-1 transition-all" />
          </button>
        </div>
      </div>
    </div>

    <!-- 剩余两个小卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-5 mb-8">
      <div
        v-for="card in statCards.slice(4)"
        :key="card.key"
        class="bg-white rounded-2xl p-5 shadow-sm border border-slate-100 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 group"
      >
        <div v-if="loading" class="animate-pulse space-y-3">
          <div class="h-11 w-11 rounded-xl bg-gray-200" />
          <div class="h-7 w-16 rounded bg-gray-200" />
        </div>
        <div v-else>
          <div class="flex items-center justify-between mb-3">
            <div :class="[card.gradient, 'w-11 h-11 rounded-xl flex items-center justify-center shadow-lg bg-gradient-to-br']">
              <component :is="card.icon" :size="20" class="text-white" />
            </div>
          </div>
          <p class="text-3xl font-bold text-slate-800 tracking-tight">{{ (stats as any)[card.key] }}</p>
          <p class="text-sm text-slate-500 mt-1">{{ card.label }}</p>
        </div>
      </div>
    </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
      <div class="flex items-center justify-between mb-5">
        <h2 class="font-display text-xl text-slate-800">最近订单</h2>
        <button
          @click="navigateTo('/admin/orders')"
          class="flex items-center gap-1.5 text-sm text-indigo-500 hover:text-indigo-600 font-medium transition-colors cursor-pointer"
        >
          查看全部 <ArrowRight :size="14" />
        </button>
      </div>
      <div v-if="loading" class="animate-pulse space-y-3">
        <div v-for="i in 3" :key="i" class="h-12 rounded-xl bg-slate-100" />
      </div>
      <div v-else-if="recentOrders.length === 0" class="text-center py-12">
        <ShoppingBag class="w-10 h-10 text-slate-200 mx-auto mb-3" />
        <p class="text-slate-400">暂无订单数据</p>
      </div>
      <div v-else>
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-slate-50 text-slate-500 uppercase text-xs">
              <th class="text-left py-3 px-4 font-medium rounded-l-lg">订单号</th>
              <th class="text-left py-3 px-4 font-medium">用户</th>
              <th class="text-left py-3 px-4 font-medium">金额</th>
              <th class="text-left py-3 px-4 font-medium">状态</th>
              <th class="text-right py-3 px-4 font-medium rounded-r-lg">日期</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="order in recentOrders"
              :key="order.id"
              class="border-b border-slate-50 last:border-b-0 hover:bg-slate-50/50 transition-colors"
            >
              <td class="py-3 px-4 text-slate-500 font-mono">#{{ order.id }}</td>
              <td class="py-3 px-4 text-slate-400 text-xs">{{ order.email }}</td>
              <td class="py-3 px-4 text-slate-700 font-semibold">¥{{ order.total_amount }}</td>
              <td class="py-3 px-4">
                <span
                  class="inline-flex text-xs px-2.5 py-1 rounded-full font-medium"
                  :class="statusClass[order.status] || 'bg-gray-50 text-gray-500'"
                >
                  {{ statusLabel[order.status] || order.status }}
                </span>
              </td>
              <td class="py-3 px-4 text-right text-slate-400 text-xs">{{ new Date(order.created_at).toLocaleDateString('zh-CN') }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>