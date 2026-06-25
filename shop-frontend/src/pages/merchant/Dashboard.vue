<template>
  <!-- 指标卡片 4列 -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
    <!-- 今日订单 -->
    <div class="bg-white rounded-2xl p-5 shadow-sm border border-slate-100 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 group relative overflow-hidden">
      <div class="flex items-center justify-between mb-3">
        <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>
        </div>
      </div>
      <p class="text-3xl font-bold text-slate-800 tracking-tight">{{ stats.todayOrders }}</p>
      <p class="text-sm text-slate-500 mt-1">今日订单</p>
    </div>

    <!-- 总商品数 -->
    <div class="bg-white rounded-2xl p-5 shadow-sm border border-slate-100 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 group relative overflow-hidden">
      <div class="flex items-center justify-between mb-3">
        <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-500/20">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
        </div>
      </div>
      <p class="text-3xl font-bold text-slate-800 tracking-tight">{{ stats.productCount }}</p>
      <p class="text-sm text-slate-500 mt-1">在售商品</p>
    </div>

    <!-- 待发货 -->
    <div class="bg-white rounded-2xl p-5 shadow-sm border border-slate-100 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 group relative overflow-hidden">
      <div class="flex items-center justify-between mb-3">
        <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center shadow-lg shadow-amber-500/20">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"/></svg>
        </div>
      </div>
      <p class="text-3xl font-bold text-slate-800 tracking-tight">{{ stats.pendingOrders }}</p>
      <p class="text-sm text-slate-500 mt-1">待发货</p>
      <span v-if="stats.pendingOrders > 0" class="inline-flex items-center gap-0.5 mt-2 text-xs font-medium text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full">
        需处理 <span class="text-rose-400">尽快发货</span>
      </span>
    </div>

    <!-- 本月销售额 -->
    <div class="bg-white rounded-2xl p-5 shadow-sm border border-slate-100 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 group relative overflow-hidden">
      <div class="flex items-center justify-between mb-3">
        <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-violet-500 to-violet-600 flex items-center justify-center shadow-lg shadow-violet-500/20">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        </div>
      </div>
      <p class="text-3xl font-bold text-slate-800 tracking-tight">¥{{ Number(stats.monthSales).toFixed(2) }}</p>
      <p class="text-sm text-slate-500 mt-1">本月销售额</p>
    </div>
  </div>

  <!-- 柱状图 + 店铺信息 -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
    <div class="lg:col-span-2 bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
      <h3 class="font-semibold text-lg text-slate-800 mb-6">销售额走势</h3>
      <div v-if="salesTrend.length > 0" class="relative h-48">
        <!-- SVG 面积图 -->
        <svg :viewBox="`0 0 ${salesTrend.length * 80} 192`" preserveAspectRatio="none" class="w-full h-full" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#818CF8" stop-opacity="0.35"/>
              <stop offset="100%" stop-color="#A78BFA" stop-opacity="0.05"/>
            </linearGradient>
          </defs>
          <!-- 网格线 -->
          <line v-for="(y, i) in [0, 48, 96, 144]" :key="'g'+i" x1="0" :y1="y" :x2="salesTrend.length * 80" :y2="y" :stroke="i === 3 ? '#E2E8F0' : '#F1F5F9'" stroke-width="1"/>
          <!-- 基线 -->
          <line x1="0" y1="180" :x2="salesTrend.length * 80" y2="180" stroke="#CBD5E1" stroke-width="1.5" stroke-linecap="round"/>

          <!-- 面积填充 -->
          <path
            :d="areaPath"
            fill="url(#areaGrad)"
          />
          <!-- 趋势线 -->
          <path
            :d="linePath"
            fill="none"
            stroke="#818CF8"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
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
      <h3 class="font-semibold text-lg text-slate-800 mb-4">店铺信息</h3>
      <div class="space-y-4">
        <div>
          <label class="block text-xs text-slate-400 mb-1 uppercase tracking-wider">店铺名称</label>
          <p class="text-slate-800 font-semibold">{{ shopInfo.shopName }}</p>
        </div>
        <div>
          <label class="block text-xs text-slate-400 mb-1 uppercase tracking-wider">商家状态</label>
          <span :class="shopInfo.status === 'approved' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'" class="px-2.5 py-1 rounded-full text-xs font-medium">
            {{ shopInfo.status === 'approved' ? '已审核通过' : '待审核' }}
          </span>
        </div>
        <div>
          <label class="block text-xs text-slate-400 mb-1 uppercase tracking-wider">入驻时间</label>
          <p class="text-slate-800">{{ shopInfo.createTime }}</p>
        </div>
      </div>
    </div>
  </div>

  <!-- 最近订单表格 -->
  <div class="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
    <h3 class="font-semibold text-lg text-slate-800 mb-5">最近订单</h3>
    <div v-if="recentOrders.length === 0" class="py-8 text-center text-slate-400 text-sm">暂无订单数据</div>
    <table v-else class="w-full text-sm">
      <thead>
        <tr class="bg-slate-50 text-slate-500 uppercase text-xs">
          <th class="text-left py-3 px-4 font-medium rounded-l-lg">订单号</th>
          <th class="text-left py-3 px-4 font-medium">商品</th>
          <th class="text-right py-3 px-4 font-medium">金额</th>
          <th class="text-right py-3 px-4 font-medium rounded-r-lg">状态</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="order in recentOrders" :key="order.id" class="border-b border-slate-50 last:border-b-0 hover:bg-slate-50/50 transition-colors">
          <td class="py-3 px-4 text-slate-500 font-mono text-xs">{{ order.id }}</td>
          <td class="py-3 px-4 text-slate-700">{{ order.productName }}</td>
          <td class="py-3 px-4 text-slate-700 font-semibold text-right">¥{{ Number(order.amount).toFixed(2) }}</td>
          <td class="py-3 px-4 text-right">
            <span :class="getStatusClass(order.status)" class="inline-flex px-2.5 py-1 rounded-full text-xs font-medium">
              {{ getStatusText(order.status) }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '@/utils/api'

const stats = ref({
  todayOrders: 0,
  productCount: 0,
  pendingOrders: 0,
  monthSales: 0,
})

const salesTrend = ref<{ label: string; total: number; height: number }[]>([])
const hoverIdx = ref(-1)

// SVG 图表计算
const CHART_H = 180  // 可用高度（192 - 底部留白）
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

const recentOrders = ref<{ id: string | number; productName: string; amount: number; status: string }[]>([])

const shopInfo = ref({
  shopName: '我的店铺',
  status: 'pending',
  createTime: '-',
})

const getStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    pending: 'bg-amber-50 text-amber-700 border border-amber-200',
    paid: 'bg-blue-50 text-blue-700 border border-blue-200',
    shipped: 'bg-orange-50 text-orange-700 border border-orange-200',
    delivered: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
    cancelled: 'bg-slate-50 text-slate-500 border border-slate-200',
  }
  return classes[status] || 'bg-slate-50 text-slate-500'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待付款',
    paid: '待发货',
    shipped: '运输中',
    delivered: '已完成',
    cancelled: '已取消',
  }
  return texts[status] || status
}

onMounted(async () => {
  // 独立请求，避免一个失败导致全部数据不显示
  // 1. 店铺信息
  try {
    const profileRes = await api.get<any>('/c-endpoint/user/profile')
    if (profileRes.code === 0 && profileRes.data) {
      const p = profileRes.data
      shopInfo.value = {
        shopName: p.shop_name || '我的店铺',
        status: p.merchant_status || 'pending',
        createTime: p.created_at ? new Date(p.created_at).toLocaleDateString('zh-CN') : '-',
      }
    }
  } catch { /* ignore */ }

  // 2. 订单数据
  try {
    const ordersRes = await api.get<any>('/m-endpoint/orders', { params: { size: 100 } })
    if (ordersRes.code === 0 && ordersRes.data) {
      const allOrders = ordersRes.data.items || []

      // 今日订单数
      const today = new Date().toISOString().slice(0, 10)
      stats.value.todayOrders = allOrders.filter((o: any) => o.created_at && o.created_at.startsWith(today)).length

      // 待发货数
      stats.value.pendingOrders = allOrders.filter((o: any) => o.status === 'paid').length

      // 本月销售额
      const currentMonth = new Date().toISOString().slice(0, 7)
      const monthOrders = allOrders.filter((o: any) => o.created_at && o.created_at.startsWith(currentMonth))
      stats.value.monthSales = monthOrders.reduce((sum: number, o: any) => sum + (o.total_amount || 0), 0)

      // 最近5条订单
      recentOrders.value = allOrders.slice(0, 5).map((o: any) => ({
        id: o.id,
        productName: o.items?.[0]?.product_name || '-',
        amount: o.total_amount,
        status: o.status,
      }))

      // 销售走势（最近7天）
      const last7Days: { label: string; total: number; height: number }[] = []
      const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      const maxDayTotal = Math.max(
        ...Array.from({ length: 7 }, (_, i) => {
          const d = new Date()
          d.setDate(d.getDate() - i)
          const dateStr = d.toISOString().slice(0, 10)
          return allOrders
            .filter((o: any) => o.created_at && o.created_at.startsWith(dateStr))
            .reduce((s: number, o: any) => s + (o.total_amount || 0), 0)
        }),
        1,
      )
      for (let i = 6; i >= 0; i--) {
        const d = new Date()
        d.setDate(d.getDate() - i)
        const dateStr = d.toISOString().slice(0, 10)
        const dayTotal = allOrders
          .filter((o: any) => o.created_at && o.created_at.startsWith(dateStr))
          .reduce((s: number, o: any) => s + (o.total_amount || 0), 0)
        last7Days.push({
          label: dayNames[d.getDay()],
          total: dayTotal,
          height: dayTotal > 0 ? Math.max(15, (dayTotal / maxDayTotal) * 100) : 0,
        })
      }
      salesTrend.value = last7Days
    }
  } catch { /* ignore */ }

  // 3. 商品数据
  try {
    const productsRes = await api.get<any>('/m-endpoint/products', { params: { size: 100 } })
    if (productsRes.code === 0 && productsRes.data) {
      const allProducts = productsRes.data.items || []
      stats.value.productCount = allProducts.filter((p: any) => p.status === 'on_sale').length
    }
  } catch { /* ignore */ }
})
</script>
