<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Clock, AlertCircle, ArrowRight, CheckCircle } from 'lucide-vue-next'
import { api } from '@/utils/api'

const router = useRouter()
const status = ref<'pending' | 'approved' | 'rejected'>('pending')
const rejectReason = ref('')
const loading = ref(true)
let pollTimer: ReturnType<typeof setInterval> | null = null

async function checkMerchantStatus() {
  try {
    const res = await api.get<any>('/c-endpoint/user/profile')
    if (res.code === 0) {
      const merchantStatus = res.data.merchant_status
      localStorage.setItem('merchant_status', merchantStatus || '')
      
      if (merchantStatus === 'approved') {
        status.value = 'approved'
        // 审核通过，用当前账号重新登录获取新token（确保token里role=merchant）
        localStorage.setItem('role', 'merchant')
        localStorage.setItem('merchant_status', 'approved')
        stopPolling()
        // 重新登录以获取包含 merchant role 的 token
        try {
          const { useAuthStore } = await import('@/stores/auth')
          const auth = useAuthStore()
          const email = auth.user?.email
          if (email) {
            // 需要用户重新输入密码，或者用现有方式刷新token
            // 这里直接跳转到登录页让用户重新登录
            localStorage.removeItem('token')
            alert('您的商家入驻申请已通过，请重新登录。')
            router.push('/login')
            return
          }
        } catch {
          // 忽略错误，继续走原有逻辑
        }
        setTimeout(() => {
          router.push('/merchant')
        }, 2000)
      } else if (merchantStatus === 'rejected') {
        status.value = 'rejected'
        rejectReason.value = res.data.reject_reason || ''
        stopPolling()
      } else {
        status.value = 'pending'
      }
    }
  } catch (err) {
    console.error('检查审核状态失败:', err)
  } finally {
    loading.value = false
  }
}

function startPolling() {
  // 每10秒轮询一次审核状态
  pollTimer = setInterval(checkMerchantStatus, 10000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

onMounted(() => {
  // 先从 localStorage 读取初始状态
  const savedStatus = localStorage.getItem('merchant_status')
  if (savedStatus === 'approved') {
    router.push('/merchant')
    return
  }
  if (savedStatus === 'rejected') {
    status.value = 'rejected'
    loading.value = false
  } else {
    checkMerchantStatus()
  }
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- 加载中 -->
      <div v-if="loading" class="bg-white rounded-2xl shadow-sm p-8 text-center">
        <div class="relative w-24 h-24 mx-auto mb-6">
          <div class="absolute inset-0 bg-gray-100 rounded-full animate-pulse"></div>
          <div class="absolute inset-0 flex items-center justify-center">
            <Clock class="w-12 h-12 text-gray-400" />
          </div>
        </div>
        <h1 class="text-xl font-bold text-gray-900 mb-2">加载中...</h1>
      </div>

      <!-- 审核通过 -->
      <div v-else-if="status === 'approved'" class="bg-white rounded-2xl shadow-sm p-8 text-center">
        <div class="relative w-24 h-24 mx-auto mb-6">
          <div class="absolute inset-0 bg-green-100 rounded-full"></div>
          <div class="absolute inset-0 flex items-center justify-center">
            <CheckCircle class="w-12 h-12 text-green-500" />
          </div>
        </div>
        
        <h1 class="text-2xl font-bold text-gray-900 mb-2">审核通过！</h1>
        <p class="text-gray-500 mb-6">
          恭喜，您的商家入驻申请已通过审核，正在跳转到商家后台...
        </p>
        
        <div class="flex items-center justify-center gap-2 text-indigo-600">
          <div class="w-4 h-4 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          <span class="text-sm">正在跳转...</span>
        </div>
      </div>

      <!-- 审核中 -->
      <div v-else-if="status === 'pending'" class="bg-white rounded-2xl shadow-sm p-8 text-center">
        <div class="relative w-24 h-24 mx-auto mb-6">
          <div class="absolute inset-0 bg-indigo-100 rounded-full animate-pulse"></div>
          <div class="absolute inset-0 flex items-center justify-center">
            <Clock class="w-12 h-12 text-indigo-600 animate-spin" style="animation-duration: 3s;" />
          </div>
        </div>
        
        <h1 class="text-2xl font-bold text-gray-900 mb-2">审核中</h1>
        <p class="text-gray-500 mb-6">
          您的开店申请已提交，平台正在快马加鞭审核中...
        </p>
        
        <div class="bg-blue-50 rounded-xl p-4 mb-6">
          <p class="text-blue-600 text-sm">
            预计审核时间：1-3个工作日
          </p>
        </div>
        
        <div class="space-y-3 text-sm text-gray-500">
          <p>审核进度：</p>
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 bg-green-500 rounded-full"></span>
            <span>申请已提交</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 bg-indigo-500 rounded-full animate-pulse"></span>
            <span>人工审核中</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 bg-gray-300 rounded-full"></span>
            <span>等待结果通知</span>
          </div>
        </div>

        <div class="mt-6 flex items-center justify-center gap-2 text-gray-400">
          <div class="w-3 h-3 border-2 border-gray-300 border-t-transparent rounded-full animate-spin"></div>
          <span class="text-xs">自动检测审核结果中...</span>
        </div>

        <button 
          @click="router.push('/')"
          class="mt-6 px-6 py-2 text-gray-500 hover:text-gray-700 text-sm font-medium"
        >
          返回首页
        </button>
      </div>

      <!-- 审核未通过 -->
      <div v-else class="bg-white rounded-2xl shadow-sm p-8 text-center">
        <div class="relative w-24 h-24 mx-auto mb-6">
          <div class="absolute inset-0 bg-red-100 rounded-full"></div>
          <div class="absolute inset-0 flex items-center justify-center">
            <AlertCircle class="w-12 h-12 text-red-500" />
          </div>
        </div>
        
        <h1 class="text-2xl font-bold text-gray-900 mb-2">审核未通过</h1>
        <p class="text-gray-500 mb-6">
          很遗憾，您的申请未通过审核
        </p>
        
        <div class="bg-red-50 rounded-xl p-4 mb-6 text-left">
          <p class="text-sm font-medium text-red-700 mb-2">拒绝原因：</p>
          <p class="text-sm text-red-600">{{ rejectReason || '请根据平台要求重新提交审核资料' }}</p>
        </div>
        
        <button 
          @click="router.push('/merchant-register')"
          class="w-full py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
        >
          重新修改资料
          <ArrowRight class="w-5 h-5" />
        </button>

        <button 
          @click="router.push('/')"
          class="mt-4 px-6 py-2 text-gray-500 hover:text-gray-700 text-sm font-medium"
        >
          返回首页
        </button>
      </div>
    </div>
  </div>
</template>
