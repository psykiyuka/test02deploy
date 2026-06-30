<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CreditCard, CheckCircle, Loader2, Banknote, Smartphone, Monitor } from 'lucide-vue-next'
import { api } from '@/utils/api'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const orderId = Number(route.params.id)
const orderInfo = ref<any>(null)
const loading = ref(true)
const paying = ref(false)
const activeMethod = ref<'qr' | 'page' | 'mock' | ''>('')
const qrCodeUrl = ref('')
const pollTimer = ref<ReturnType<typeof setInterval> | null>(null)
const polling = ref(false)
const countdown = ref(0)

// 支付结果状态
const payResult = ref<'success' | 'fail' | ''>('')

// 获取订单信息
async function fetchOrder() {
  loading.value = true
  try {
    const res = await api.get<any>(`/c-endpoint/orders/${orderId}`)
    if (res.code === 0) {
      orderInfo.value = res.data
      // 如果从支付宝回调回来，检测订单是否已支付
      if (route.query.from === 'alipay') {
        if (res.data.status === 'paid') {
          payResult.value = 'success'
        } else {
          // 回调回来但本地还没更新，主动查询支付宝
          const queryRes = await api.get<any>(`/c-endpoint/payment/alipay/query/${orderId}`)
          if (queryRes.code === 0 && queryRes.data?.status === 'paid') {
            payResult.value = 'success'
            // 重新获取订单信息以更新页面
            const freshRes = await api.get<any>(`/c-endpoint/orders/${orderId}`)
            if (freshRes.code === 0) orderInfo.value = freshRes.data
          } else {
            payResult.value = 'fail'
          }
        }
      } else if (res.data.status === 'paid') {
        payResult.value = 'success'
      } else if (res.data.status !== 'pending') {
        toast.show('warning', '当前订单状态不可支付')
        setTimeout(() => router.push('/orders'), 1500)
      }
    } else {
      toast.show('error', res.message || '获取订单信息失败')
      router.push('/orders')
    }
  } catch (err: any) {
    toast.show('error', err.message || '获取订单信息失败')
    router.push('/orders')
  } finally {
    loading.value = false
  }
}

// 支付宝扫码支付（当面付预下单）
async function startAlipayQrPay() {
  if (paying.value || polling.value) return
  paying.value = true
  activeMethod.value = 'qr'
  payResult.value = ''
  try {
    const res = await api.get<any>(`/c-endpoint/payment/alipay/qr-pay/${orderId}`)
    if (res.code === 0 && res.data?.qr_code) {
      qrCodeUrl.value = res.data.qr_code
      startPolling()
    } else {
      toast.show('error', res.message || '创建支付订单失败')
      activeMethod.value = ''
    }
  } catch (err: any) {
    toast.show('error', err.message || '创建支付订单失败')
    activeMethod.value = ''
  } finally {
    paying.value = false
  }
}

// 支付宝网页支付（电脑网站支付，新窗口跳转）
async function startAlipayPagePay() {
  if (paying.value || polling.value) return
  paying.value = true
  activeMethod.value = 'page'
  payResult.value = ''
  try {
    const res = await api.get<any>(`/c-endpoint/payment/alipay/page-pay/${orderId}`)
    if (res.code === 0 && res.data?.pay_url) {
      // 在新窗口打开支付宝支付页面，当前页面保持不变并启动轮询
      window.open(res.data.pay_url, '_blank')
      startPolling()
    } else {
      toast.show('error', res.message || '创建支付订单失败')
      activeMethod.value = ''
    }
  } catch (err: any) {
    toast.show('error', err.message || '创建支付订单失败')
    activeMethod.value = ''
  } finally {
    paying.value = false
  }
}

// 模拟支付
async function mockPay() {
  if (paying.value || polling.value) return
  paying.value = true
  activeMethod.value = 'mock'
  payResult.value = ''
  try {
    const res = await api.post<any>(`/c-endpoint/payment/mock-pay/${orderId}`)
    if (res.code === 0) {
      payResult.value = 'success'
    } else {
      payResult.value = 'fail'
      toast.show('error', res.message || '支付失败')
    }
  } catch (err: any) {
    payResult.value = 'fail'
    toast.show('error', err.message || '支付失败')
  } finally {
    paying.value = false
    activeMethod.value = ''
  }
}

// 主动查询支付状态（先查本地，如果仍是 pending 再查支付宝端）
async function checkPayStatus(): Promise<'paid' | 'pending' | 'other'> {
  try {
    // 先查本地订单状态
    const orderRes = await api.get<any>(`/c-endpoint/orders/${orderId}`)
    if (orderRes.code === 0) {
      const localStatus = orderRes.data?.status
      if (localStatus === 'paid') return 'paid'
      if (localStatus !== 'pending') return 'other'

      // 本地仍是 pending，主动查询支付宝交易状态
      if (activeMethod.value === 'qr' || activeMethod.value === 'page') {
        const queryRes = await api.get<any>(`/c-endpoint/payment/alipay/query/${orderId}`)
        if (queryRes.code === 0 && queryRes.data?.status === 'paid') return 'paid'
      }
    }
    return 'pending'
  } catch {
    return 'pending'
  }
}

// 轮询支付状态
function startPolling() {
  polling.value = true
  countdown.value = 180 // 3分钟超时
  payResult.value = ''
  pollTimer.value = setInterval(async () => {
    countdown.value--
    const result = await checkPayStatus()
    if (result === 'paid') {
      stopPolling()
      payResult.value = 'success'
      activeMethod.value = ''
      return
    }
    if (result === 'other') {
      stopPolling()
      payResult.value = 'fail'
      activeMethod.value = ''
      return
    }
    if (countdown.value <= 0) {
      stopPolling()
      payResult.value = 'fail'
      toast.show('warning', '支付超时，如已付款请稍后查看订单状态')
      activeMethod.value = ''
    }
  }, 3000)
}

function stopPolling() {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
  polling.value = false
}

function goToOrders() {
  router.push('/orders')
}

onMounted(() => {
  if (!orderId) {
    router.push('/orders')
    return
  }
  fetchOrder()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-lg w-full max-w-md overflow-hidden">
      <!-- 头部 -->
      <div class="bg-indigo-600 px-6 py-5">
        <div class="flex items-center gap-3">
          <CreditCard class="w-6 h-6 text-white" />
          <h1 class="text-xl font-bold text-white">订单支付</h1>
        </div>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="flex flex-col items-center py-16">
        <Loader2 class="w-10 h-10 text-indigo-600 animate-spin" />
        <p class="text-gray-500 mt-4">加载订单信息...</p>
      </div>

      <!-- 支付成功结果 -->
      <div v-else-if="payResult === 'success'" class="p-8 text-center">
        <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle class="w-10 h-10 text-green-600" />
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">支付成功！</h2>
        <p class="text-gray-500 mb-6">订单 #{{ orderId }} 已完成支付</p>
        <button
          @click="goToOrders"
          class="w-full py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors"
        >
          查看订单列表
        </button>
      </div>

      <!-- 支付失败结果 -->
      <div v-else-if="payResult === 'fail'" class="p-8 text-center">
        <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <CreditCard class="w-10 h-10 text-red-600" />
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">支付未完成</h2>
        <p class="text-gray-500 mb-4">订单 #{{ orderId }} 尚未支付成功</p>
        <div class="space-y-3">
          <button
            @click="payResult = ''; activeMethod = ''; qrCodeUrl = ''"
            class="w-full py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors"
          >
            重新选择支付方式
          </button>
          <button
            @click="goToOrders"
            class="w-full py-3 border border-gray-200 text-gray-600 rounded-xl font-medium hover:bg-gray-50 transition-colors"
          >
            返回订单列表
          </button>
        </div>
      </div>

      <!-- 订单信息 + 支付方式选择 -->
      <div v-else-if="orderInfo" class="p-6">
        <div class="bg-gray-50 rounded-xl p-4 mb-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-500">订单编号</span>
            <span class="text-sm font-medium text-gray-900">#{{ orderInfo.id }}</span>
          </div>
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-500">商品数量</span>
            <span class="text-sm font-medium text-gray-900">{{ orderInfo.items?.length || 0 }} 件</span>
          </div>
          <div class="flex items-center justify-between pt-2 border-t border-gray-200">
            <span class="text-sm text-gray-500">应付金额</span>
            <span class="text-2xl font-bold text-rose-600">¥{{ orderInfo.total_amount }}</span>
          </div>
        </div>

        <!-- 支付方式选择 -->
        <div class="space-y-3 mb-6">
          <h3 class="text-sm font-semibold text-gray-700 mb-3">选择支付方式</h3>

          <!-- 支付宝扫码支付 -->
          <button
            @click="startAlipayQrPay()"
            :disabled="paying || polling"
            :class="[
              'w-full flex items-center gap-4 p-4 rounded-xl border-2 transition-all',
              activeMethod === 'qr'
                ? 'border-indigo-600 bg-indigo-50'
                : 'border-gray-200 hover:border-gray-300',
            ]"
          >
            <Smartphone class="w-6 h-6 text-blue-500" />
            <p class="font-medium text-gray-900">支付宝扫码支付</p>
            <Loader2 v-if="paying && activeMethod === 'qr'" class="w-5 h-5 text-indigo-600 animate-spin ml-auto" />
          </button>

          <!-- 支付宝网页支付 -->
          <button
            @click="startAlipayPagePay()"
            :disabled="paying || polling"
            :class="[
              'w-full flex items-center gap-4 p-4 rounded-xl border-2 transition-all',
              activeMethod === 'page'
                ? 'border-indigo-600 bg-indigo-50'
                : 'border-gray-200 hover:border-gray-300',
            ]"
          >
            <Monitor class="w-6 h-6 text-blue-500" />
            <p class="font-medium text-gray-900">支付宝网页支付</p>
            <Loader2 v-if="paying && activeMethod === 'page'" class="w-5 h-5 text-indigo-600 animate-spin ml-auto" />
          </button>

          <!-- 模拟支付 -->
          <button
            @click="mockPay()"
            :disabled="paying || polling"
            :class="[
              'w-full flex items-center gap-4 p-4 rounded-xl border-2 transition-all',
              activeMethod === 'mock'
                ? 'border-green-600 bg-green-50'
                : 'border-gray-200 hover:border-gray-300',
            ]"
          >
            <Banknote class="w-6 h-6 text-green-500" />
            <p class="font-medium text-gray-900">模拟支付（测试）</p>
            <Loader2 v-if="paying && activeMethod === 'mock'" class="w-5 h-5 text-indigo-600 animate-spin ml-auto" />
          </button>
        </div>

        <!-- 支付宝当面付二维码 -->
        <div v-if="qrCodeUrl && activeMethod === 'qr'" class="text-center mb-6">
          <div class="bg-gray-50 rounded-xl p-4">
            <p class="text-sm text-gray-600 mb-3">请使用支付宝扫描以下二维码</p>
            <div class="bg-white inline-block p-3 rounded-lg shadow-sm">
              <img
                :src="`https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(qrCodeUrl)}`"
                alt="支付宝扫码支付"
                class="w-[180px] h-[180px]"
              />
            </div>
            <div v-if="polling" class="mt-3 flex items-center justify-center gap-2 text-sm text-indigo-600">
              <Loader2 class="w-4 h-4 animate-spin" />
              等待支付中... ({{ countdown }}秒)
            </div>
          </div>
        </div>

        <!-- 网页支付等待提示 -->
        <div v-if="activeMethod === 'page' && polling" class="text-center mb-6">
          <div class="bg-gray-50 rounded-xl p-4">
            <p class="text-sm text-gray-600 mb-3">支付宝支付页面已在新窗口打开</p>
            <p class="text-xs text-gray-400 mb-3">请在新窗口完成支付，本页面会自动检测支付结果</p>
            <div class="flex items-center justify-center gap-2 text-sm text-indigo-600">
              <Loader2 class="w-4 h-4 animate-spin" />
              等待支付中... ({{ countdown }}秒)
            </div>
          </div>
        </div>

        <!-- 返回订单列表 -->
        <button
          @click="goToOrders"
          class="w-full mt-4 py-3 border border-gray-200 text-gray-600 rounded-xl font-medium hover:bg-gray-50 transition-colors"
        >
          返回订单列表
        </button>
      </div>
    </div>
  </div>
</template>
