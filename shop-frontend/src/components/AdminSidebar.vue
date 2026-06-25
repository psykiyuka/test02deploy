<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { LayoutDashboard, Layers, Package, ShoppingBag, RotateCcw, LogOut, ArrowLeft, Sparkles, Users, Mail, MessageCircle } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import { api } from '@/utils/api'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const quickStats = ref({
  todayOrders: '--',
  pendingAfterSales: '--',
})

const navItems = [
  { name: 'admin',             label: '仪表盘',   icon: LayoutDashboard },
  { name: 'admin-categories',  label: '分类管理', icon: Layers },
  { name: 'admin-products',    label: '商品管理', icon: Package },
  { name: 'admin-orders',      label: '订单管理', icon: ShoppingBag },
  { name: 'admin-after-sales', label: '售后管理', icon: RotateCcw },
  { name: 'admin-users',       label: '用户管理', icon: Users },
  { name: 'admin-email-changes', label: '换绑审核', icon: Mail },
  { name: 'admin-ai-chat',   label: 'AI 客服',  icon: Sparkles },
  { name: 'admin-chat',     label: '客服消息', icon: MessageCircle },
]

// 安全匹配：精确匹配，或当前路由是某项的子路由（如 admin-products 匹配 admin-products/new）
function isActive(routeName: string): boolean {
  if (route.name === routeName) return true
  // 只对有子路由的父级做前缀匹配，这里所有项都是叶子节点，无需前缀匹配
  return false
}

function handleLogout() {
  auth.logout()
  router.push({ name: 'home' })
}

onMounted(async () => {
  try {
    const res = await api.get<any>('/b-endpoint/dashboard/stats')
    if (res.code === 0 && res.data) {
      quickStats.value.todayOrders = String(res.data.today_orders ?? 0)
      quickStats.value.pendingAfterSales = String(res.data.pending_after_sales ?? 0)
    }
  } catch {
    // 静默失败，保持 -- 占位
  }
})
</script>

<template>
  <aside class="sidebar">

    <!-- 品牌区 -->
    <div class="sidebar-brand">
      <router-link to="/admin" class="sidebar-logo">
        <div class="sidebar-logo-icon">
          <Sparkles class="sidebar-logo-svg" />
        </div>
        <div>
          <h1 class="sidebar-title">Shop Admin</h1>
          <p class="sidebar-subtitle">管理控制台</p>
        </div>
      </router-link>

      <!-- 管理员信息 -->
      <div class="admin-info">
        <div class="admin-avatar">
          <span class="admin-avatar-letter">{{ auth.user?.nickname?.charAt(0) ?? 'A' }}</span>
        </div>
        <div class="admin-meta">
          <p class="admin-name">{{ auth.user?.nickname ?? 'Admin' }}</p>
          <p class="admin-email">{{ auth.user?.email ?? '' }}</p>
        </div>
      </div>
    </div>

    <!-- 导航菜单 -->
    <nav class="sidebar-nav">
      <p class="nav-section-label">主菜单</p>
      <ul class="nav-list">
        <li v-for="item in navItems" :key="item.name">
          <router-link
            :to="{ name: item.name }"
            class="nav-item"
            :class="isActive(item.name) ? 'nav-item--active' : 'nav-item--default'"
          >
            <span v-if="isActive(item.name)" class="nav-active-bar" />
            <component :is="item.icon" class="nav-icon" />
            {{ item.label }}
          </router-link>
        </li>
      </ul>

      <!-- 分隔线 -->
      <div class="nav-divider" />

      <p class="nav-section-label">快捷数据</p>
      <div class="stat-card">
        <div class="stat-row">
          <span class="stat-label">今日订单</span>
          <span class="stat-value">{{ quickStats.todayOrders }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">待处理售后</span>
          <span class="stat-value">{{ quickStats.pendingAfterSales }}</span>
        </div>
      </div>
    </nav>

    <!-- 底部操作 -->
    <div class="sidebar-footer">
      <router-link to="/" class="nav-item nav-item--default">
        <ArrowLeft class="nav-icon" />
        返回商城
      </router-link>
      <button
        class="nav-item nav-item--default nav-item--logout"
        @click="handleLogout"
      >
        <LogOut class="nav-icon" />
        退出登录
      </button>
    </div>
  </aside>
</template>

<style scoped>
/* ── 侧边栏容器 ── */
.sidebar {
  width: 256px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  background: linear-gradient(180deg, #2C2018, #221A12, #1A130B);
  scrollbar-width: thin;
  scrollbar-color: rgba(255,255,255,0.1) transparent;
}
.sidebar::-webkit-scrollbar {
  width: 4px;
}
.sidebar::-webkit-scrollbar-track {
  background: transparent;
}
.sidebar::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
}

/* ── 品牌区 ── */
.sidebar-brand {
  padding: 1.5rem 1.25rem;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  transition: opacity 0.2s;
}
.sidebar-logo:hover { opacity: 0.85; }

.sidebar-logo-icon {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--gold-300, #d4a96a), var(--gold-500, #b5722a));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(181,114,42,0.3);
  flex-shrink: 0;
  transition: transform 0.25s, box-shadow 0.25s;
}
.sidebar-logo:hover .sidebar-logo-icon {
  transform: scale(1.05);
  box-shadow: 0 6px 18px rgba(181,114,42,0.4);
}
.sidebar-logo-svg {
  width: 18px;
  height: 18px;
  color: #fff;
  position: relative;
  z-index: 1;
}

.sidebar-title {
  font-family: var(--font-display, 'Noto Serif SC', serif);
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.06em;
  margin: 0;
  line-height: 1.2;
}
.sidebar-subtitle {
  font-size: 9px;
  color: rgba(196,144,64,0.5);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin: 2px 0 0;
}

/* 管理员信息 */
.admin-info {
  margin-top: 1.25rem;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.06);
  display: flex;
  align-items: center;
  gap: 10px;
}

.admin-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(212,169,106,0.8), rgba(181,114,42,0.8));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.admin-avatar-letter {
  font-size: 11px;
  color: #fff;
  font-weight: 700;
}

.admin-meta { min-width: 0; }
.admin-name {
  font-size: 0.75rem;
  font-weight: 500;
  color: rgba(255,255,255,0.75);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.admin-email {
  font-size: 10px;
  color: rgba(255,255,255,0.28);
  margin: 1px 0 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ── 导航菜单 ── */
.sidebar-nav {
  flex: 1;
  padding: 1.25rem 0.75rem;
}

.nav-section-label {
  padding: 0 0.75rem;
  margin-bottom: 0.75rem;
  font-size: 9px;
  font-weight: 600;
  color: rgba(255,255,255,0.2);
  text-transform: uppercase;
  letter-spacing: 0.15em;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 0.8125rem;
  font-weight: 500;
  text-decoration: none;
  border: 1px solid transparent;
  transition: all 0.2s ease;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  box-sizing: border-box;
}
.nav-icon {
  width: 17px;
  height: 17px;
  flex-shrink: 0;
}
.nav-item--default {
  color: rgba(255,255,255,0.38);
}
.nav-item--default:hover {
  color: rgba(255,255,255,0.78);
  background: rgba(255,255,255,0.05);
  border-color: rgba(255,255,255,0.05);
}
.nav-item--active {
  background: linear-gradient(135deg, rgba(181,114,42,0.18), rgba(181,114,42,0.06));
  color: var(--gold-300, #d4a96a);
  border-color: rgba(181,114,42,0.22);
  box-shadow: 0 2px 8px rgba(181,114,42,0.08);
}
.nav-item--logout:hover {
  color: #f87171 !important;
  background: rgba(239,68,68,0.08) !important;
}

/* 活跃指示条 */
.nav-active-bar {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  border-radius: 2px;
  background: var(--gold-400, #c49040);
}

/* 分隔线 */
.nav-divider {
  height: 1px;
  margin: 1.25rem 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
}

/* 快捷数据 */
.stat-card {
  padding: 12px;
  border-radius: 12px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.05);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
}
.stat-label { color: rgba(255,255,255,0.35); }
.stat-value { color: rgba(196,144,64,0.8); font-weight: 600; }

/* ── 底部操作 ── */
.sidebar-footer {
  padding: 1rem 0.75rem 1.5rem;
  border-top: 1px solid rgba(255,255,255,0.06);
  display: flex;
  flex-direction: column;
  gap: 2px;
}
</style>
