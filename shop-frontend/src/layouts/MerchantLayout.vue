<template>
  <div class="min-h-screen bg-slate-50">
    <div class="flex">
      <!-- 深色侧边栏 -->
      <aside class="w-64 bg-slate-900 text-slate-300 sticky top-0 h-screen overflow-y-auto flex flex-col">
        <div class="p-5 border-b border-slate-700/50">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-amber-400 to-amber-500 flex items-center justify-center shadow-lg shadow-amber-500/20">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
              </svg>
            </div>
            <div>
              <h1 class="text-sm font-bold text-white">商家后台</h1>
              <p class="text-[10px] text-slate-500 uppercase tracking-wider">Merchant Console</p>
            </div>
          </div>
        </div>
        <nav class="flex-1 p-4 space-y-1">
          <router-link to="/merchant" class="nav-item" :class="{ 'nav-item--active': $route.path === '/merchant' }">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
            仪表盘
          </router-link>
          <router-link to="/merchant/products" class="nav-item" :class="{ 'nav-item--active': $route.path.startsWith('/merchant/products') }">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
            商品管理
          </router-link>
          <router-link to="/merchant/orders" class="nav-item" :class="{ 'nav-item--active': $route.path.startsWith('/merchant/orders') }">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>
            订单管理
          </router-link>
          <router-link to="/merchant/after-sales" class="nav-item" :class="{ 'nav-item--active': $route.path.startsWith('/merchant/after-sales') }">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>
            售后服务
          </router-link>
          <router-link to="/merchant/profile" class="nav-item" :class="{ 'nav-item--active': $route.path === '/merchant/profile' }">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
            店铺设置
          </router-link>
          <router-link to="/merchant/ai-chat" class="nav-item" :class="{ 'nav-item--active': $route.path.startsWith('/merchant/ai-chat') }">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.813 15.5c.37.299.92.5 1.5.5s1.13-.201 1.5-.5M9 7a3 3 0 116 0 3 3 0 01-6 0zm-3.465 5.827a6 6 0 0111.544 0M12 17v2m-7.5-7.5h.01M16.5 9.5h.01M12 12.75a.75.75 0 100-1.5.75.75 0 000 1.5z"/></svg>
            AI 客服
          </router-link>
          <router-link to="/merchant/chat" class="nav-item" :class="{ 'nav-item--active': $route.path.startsWith('/merchant/chat') }">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
            客服消息
          </router-link>
        </nav>
        <div class="p-4 border-t border-slate-700/50">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-xs text-slate-400 font-medium">商</div>
            <div class="flex-1 min-w-0">
              <p class="text-xs text-slate-400 truncate">商家用户</p>
            </div>
            <button @click="handleLogout" class="text-slate-500 hover:text-rose-400 transition-colors cursor-pointer" title="退出登录">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
            </button>
          </div>
        </div>
      </aside>

      <!-- 内容区 -->
      <main class="flex-1 p-6 md:p-8">
        <div class="flex justify-between items-center mb-6">
          <div>
            <h2 class="text-xl font-bold text-slate-800">{{ title }}</h2>
            <p class="text-sm text-slate-400 mt-0.5">欢迎回来，查看您的店铺运营数据</p>
          </div>
        </div>
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => {
  const path = route.path
  const titles: Record<string, string> = {
    '/merchant': '仪表盘',
    '/merchant/products': '商品管理',
    '/merchant/orders': '订单管理',
    '/merchant/after-sales': '售后管理',
    '/merchant/profile': '店铺设置',
    '/merchant/ai-chat': 'AI 客服',
    '/merchant/chat': '客服消息',
  }
  // 精确匹配，若无则尝试前缀匹配
  if (titles[path]) return titles[path]
  // 兜底：取路径第一段
  const base = '/' + path.split('/').filter(Boolean).slice(0, 2).join('/')
  return titles[base] || '商家管理后台'
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  localStorage.removeItem('merchant_status')
  window.location.href = '/login'
}
</script>

<style scoped>
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(203, 213, 225, 0.6);
  text-decoration: none;
  transition: all 0.2s;
}
.nav-item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(203, 213, 225, 0.9);
}
.nav-item--active {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}
</style>
