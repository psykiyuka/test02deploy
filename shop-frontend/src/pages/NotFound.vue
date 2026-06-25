<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Home, ArrowLeft } from 'lucide-vue-next'

const router = useRouter()
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center p-4">
    <div class="text-center">
      <div class="relative w-32 h-32 mx-auto mb-8">
        <div class="absolute inset-0 bg-indigo-100 rounded-full"></div>
        <div class="absolute inset-0 flex items-center justify-center">
          <span class="text-5xl font-bold text-indigo-600">404</span>
        </div>
      </div>

      <h1 class="text-2xl font-bold text-gray-900 mb-2">页面未找到</h1>
      <p class="text-gray-500 mb-8">抱歉，您访问的页面不存在或已被移除</p>

      <div class="flex items-center justify-center gap-4">
        <button
          @click="router.back()"
          class="flex items-center gap-2 px-6 py-3 border border-gray-200 rounded-xl text-gray-700 font-medium hover:bg-gray-50 transition-colors"
        >
          <ArrowLeft class="w-5 h-5" />
          返回上页
        </button>
        <button
          @click="router.push('/')"
          class="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors"
        >
          <Home class="w-5 h-5" />
          回到首页
        </button>
      </div>
    </div>
  </div>
</template>
