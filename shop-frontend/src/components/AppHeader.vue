<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Search, ShoppingCart, User, LogOut, Menu, X, ChevronDown, Sparkles, ArrowRight } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const cart = useCartStore()

const searchKeyword = ref('')
const showUserMenu = ref(false)
const showMobileMenu = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)
const isScrolled = ref(false)
const headerRef = ref<HTMLElement | null>(null)

function handleSearch() {
  const keyword = searchKeyword.value.trim()
  if (keyword) {
    router.push({ name: 'products', query: { keyword } })
  } else {
    router.push({ name: 'products' })
  }
  showMobileMenu.value = false
}

function handleLogout() {
  auth.logout()
  showUserMenu.value = false
  router.push({ name: 'home' })
}

function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value
}

function closeUserMenu() {
  showUserMenu.value = false
}

function handleClickOutside(event: MouseEvent) {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target as Node)) {
    closeUserMenu()
  }
}

function handleToggleUserMenu() {
  showUserMenu.value = !showUserMenu.value
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  const handleScroll = () => { isScrolled.value = window.scrollY > 20 }
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <!-- 顶部金色装饰线 -->
  <div class="top-deco-bar" />

  <header ref="headerRef" class="site-header" :class="{ 'scrolled': isScrolled }">
    <div class="header-inner">

      <!-- 品牌 Logo -->
      <router-link to="/" class="brand-logo">
        <div class="brand-icon">
          <Sparkles class="brand-icon-svg" />
        </div>
        <div class="brand-text">
          <span class="brand-name">ELEGANCE</span>
          <span class="brand-sub">精致生活</span>
        </div>
      </router-link>

      <!-- 桌面导航 -->
      <nav class="desktop-nav">
        <router-link
          to="/"
          class="nav-link"
          :class="{ 'nav-link--active': route.path === '/' }"
        >
          首页
          <span v-if="route.path === '/'" class="nav-active-dot" />
        </router-link>
        <router-link
          to="/products"
          class="nav-link"
          :class="{ 'nav-link--active': route.path.startsWith('/products') }"
        >
          全部商品
          <span v-if="route.path.startsWith('/products')" class="nav-active-dot" />
        </router-link>
      </nav>

      <!-- 搜索框 -->
      <div class="search-wrapper">
        <div class="elegant-input-wrapper">
          <Search class="elegant-input-icon" />
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索心仪好物..."
            class="elegant-input elegant-input-right-icon"
            @keydown.enter="handleSearch"
          />
          <button class="elegant-input-icon elegant-input-icon-right" @click="handleSearch">
            <ArrowRight :size="14" />
          </button>
        </div>
      </div>

      <!-- 右侧操作区 -->
      <div class="header-actions">
        <!-- 购物车 -->
        <router-link v-if="!auth.isAdmin" to="/cart" class="action-btn cart-btn">
          <ShoppingCart class="action-icon" />
          <span v-if="cart.totalCount > 0" class="cart-badge">
            {{ cart.totalCount > 99 ? '99+' : cart.totalCount }}
          </span>
        </router-link>

        <!-- 用户菜单（已登录） -->
        <template v-if="auth.isLoggedIn">
          <div ref="userMenuRef" class="user-menu-wrap">
            <button class="user-trigger" @click="handleToggleUserMenu">
              <div class="user-avatar">
                <User class="user-avatar-icon" />
              </div>
              <span class="user-name">{{ auth.user?.nickname }}</span>
              <ChevronDown
                class="chevron-icon"
                :style="showUserMenu ? 'transform:rotate(180deg)' : ''"
              />
            </button>

            <Transition name="dropdown">
              <div v-if="showUserMenu" class="dropdown-menu">
                <!-- 用户信息头 -->
                <div class="dropdown-user-head">
                  <p class="dropdown-username">{{ auth.user?.nickname }}</p>
                  <p class="dropdown-email">{{ auth.user?.email }}</p>
                </div>
                <router-link v-if="!auth.isAdmin && auth.user?.role !== 'merchant'" to="/orders"     class="dropdown-item" @click="closeUserMenu">我的订单</router-link>
                <router-link v-if="!auth.isAdmin" to="/favorites" class="dropdown-item" @click="closeUserMenu">我的收藏</router-link>
                <router-link v-if="auth.user?.role === 'merchant'" to="/merchant/orders" class="dropdown-item" @click="closeUserMenu">物流管理</router-link>
                <router-link to="/profile"    class="dropdown-item" @click="closeUserMenu">个人中心</router-link>
                <router-link v-if="!auth.isAdmin" to="/after-sales" class="dropdown-item" @click="closeUserMenu">售后服务</router-link>
                <router-link v-if="auth.isAdmin" to="/admin" class="dropdown-item dropdown-item--gold" @click="closeUserMenu">管理后台</router-link>
                <div class="dropdown-divider" />
                <button class="dropdown-item dropdown-item--danger" @click="handleLogout">
                  <LogOut class="dropdown-item-icon" />退出登录
                </button>
              </div>
            </Transition>
          </div>
        </template>

        <!-- 登录按钮（未登录） -->
        <template v-else>
          <router-link to="/login" class="login-btn">登录 / 注册</router-link>
        </template>

        <!-- 移动端菜单按钮 -->
        <button class="mobile-menu-btn" @click="showMobileMenu = !showMobileMenu">
          <X v-if="showMobileMenu" class="action-icon" />
          <Menu v-else class="action-icon" />
        </button>
      </div>
    </div>

    <!-- 移动端下拉菜单 -->
    <Transition name="mobile-menu">
      <div v-if="showMobileMenu" class="mobile-nav">
        <div class="elegant-input-wrapper">
          <Search class="elegant-input-icon" />
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索心仪好物..."
            class="elegant-input"
            @keydown.enter="handleSearch"
          />
        </div>
        <div class="mobile-links">
          <router-link to="/"         class="mobile-link" @click="showMobileMenu = false">🏠 首页</router-link>
          <router-link to="/products" class="mobile-link" @click="showMobileMenu = false">🛍️ 全部商品</router-link>
          <router-link v-if="!auth.isAdmin" to="/cart"     class="mobile-link" @click="showMobileMenu = false">🛒 购物车</router-link>
          <router-link v-if="auth.isLoggedIn && !auth.isAdmin && auth.user?.role !== 'merchant'" to="/orders" class="mobile-link" @click="showMobileMenu = false">📦 我的订单</router-link>
          <router-link v-if="auth.isLoggedIn && !auth.isAdmin" to="/favorites" class="mobile-link" @click="showMobileMenu = false">❤️ 我的收藏</router-link>
        </div>
      </div>
    </Transition>
  </header>
</template>

<style scoped>
/* ── 顶部装饰线 ── */
.top-deco-bar {
  height: 3px;
  width: 100%;
  background: linear-gradient(90deg, var(--gold-300, #d4a96a), var(--gold-500, #b5722a), var(--gold-300, #d4a96a));
}

/* ── Header 主体 ── */
.site-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(212, 169, 106, 0.1);
  box-shadow: 0 1px 3px rgba(181, 114, 42, 0.04);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.site-header.scrolled {
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 4px 24px rgba(181, 114, 42, 0.1), 0 1px 3px rgba(0, 0, 0, 0.04);
  border-bottom-color: rgba(212, 169, 106, 0.16);
}

.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 68px;
  gap: 1rem;
}

/* ── 品牌 Logo ── */
.brand-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  flex-shrink: 0;
  transition: opacity 0.2s;
}
.brand-logo:hover { opacity: 0.85; }

.brand-icon {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--gold-300, #d4a96a), var(--gold-500, #b5722a));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(181, 114, 42, 0.35);
  transition: transform 0.25s, box-shadow 0.25s;
}
.brand-logo:hover .brand-icon {
  transform: scale(1.06);
  box-shadow: 0 6px 18px rgba(181, 114, 42, 0.45);
}
.brand-icon-svg {
  width: 20px;
  height: 20px;
  color: #fff;
}

.brand-text { line-height: 1; }
.brand-name {
  display: block;
  font-family: var(--font-display, 'Noto Serif SC', serif);
  font-size: 1.1rem;
  font-weight: 700;
  background: linear-gradient(120deg, var(--gold-600, #8b5a1a), var(--gold-400, #c49040));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.06em;
}
.brand-sub {
  display: block;
  font-size: 9px;
  color: rgba(181, 114, 42, 0.6);
  letter-spacing: 0.22em;
  text-transform: uppercase;
  margin-top: -1px;
}

/* ── 桌面导航 ── */
.desktop-nav {
  display: none;
  align-items: center;
  gap: 2px;
  margin-left: 1.5rem;
}
@media (min-width: 768px) {
  .desktop-nav { display: flex; }
}

.nav-link {
  position: relative;
  padding: 6px 16px;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  color: rgba(51, 43, 36, 0.55);
  transition: color 0.2s, background 0.2s, transform 0.2s;
}
.nav-link:hover {
  color: rgba(51, 43, 36, 0.9);
  background: rgba(212, 169, 106, 0.1);
  transform: scale(1.04);
}
.nav-link--active {
  color: var(--gold-600, #8b5a1a);
  background: linear-gradient(135deg, rgba(212, 169, 106, 0.15), rgba(253, 249, 244, 0.8));
}

.nav-active-dot {
  position: absolute;
  bottom: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 16px;
  height: 2.5px;
  border-radius: 2px;
  background: var(--gold-400, #c49040);
}

/* ── 搜索框 ── */
.search-wrapper {
  display: none;
  flex: 1;
  max-width: 380px;
  margin: 0 1rem;
}
@media (min-width: 768px) {
  .search-wrapper { display: flex; }
}

.search-box {
  position: relative;
  width: 100%;
}
.search-icon {
  position: absolute;
  left: 13px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: rgba(196, 144, 64, 0.7);
  pointer-events: none;
}
.search-input {
  width: 100%;
  padding: 9px 40px 9px 38px;
  border-radius: 18px;
  background: rgba(253, 247, 237, 0.7);
  border: 1.5px solid rgba(212, 169, 106, 0.25);
  outline: none;
  font-size: 0.875rem;
  color: var(--charcoal, #332b24);
  transition: all 0.2s;
  box-sizing: border-box;
}
.search-input::placeholder { color: rgba(51, 43, 36, 0.3); }
.search-input:focus {
  border-color: rgba(212, 169, 106, 0.55);
  background: #fff;
  box-shadow: 0 0 0 4px rgba(212, 169, 106, 0.1);
}
.search-enter-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 26px;
  height: 26px;
  border-radius: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(51, 43, 36, 0.3);
  font-size: 13px;
  transition: background 0.15s;
}
.search-enter-btn:hover { background: rgba(212, 169, 106, 0.15); }

/* ── 右侧操作区 ── */
.header-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

/* 购物车按钮 */
.action-btn {
  position: relative;
  padding: 8px 10px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  text-decoration: none;
  transition: background 0.18s;
}
.action-btn:hover { background: rgba(212, 169, 106, 0.1); }

.action-icon {
  width: 20px;
  height: 20px;
  color: rgba(51, 43, 36, 0.5);
  transition: color 0.18s;
}
.action-btn:hover .action-icon { color: rgba(51, 43, 36, 0.8); }

.cart-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  background: linear-gradient(135deg, var(--gold-400, #c49040), var(--gold-500, #b5722a));
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  border-radius: 999px;
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 3px;
  box-shadow: 0 2px 6px rgba(181, 114, 42, 0.4);
}

/* 用户菜单 */
.user-menu-wrap {
  position: relative;
}
.user-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  border-radius: 12px;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: background 0.18s;
}
.user-trigger:hover { background: rgba(212, 169, 106, 0.1); }

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--gold-200, #e8c98a), var(--gold-400, #c49040));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(196, 144, 64, 0.3);
}
.user-avatar-icon {
  width: 16px;
  height: 16px;
  color: #fff;
}
.user-name {
  display: none;
  font-size: 0.75rem;
  font-weight: 500;
  color: rgba(51, 43, 36, 0.6);
  max-width: 72px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
@media (min-width: 640px) {
  .user-name { display: block; }
}
.chevron-icon {
  width: 13px;
  height: 13px;
  color: rgba(51, 43, 36, 0.3);
  transition: transform 0.2s;
  display: none;
}
@media (min-width: 640px) {
  .chevron-icon { display: block; }
}

/* 下拉菜单 */
.dropdown-menu {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  width: 220px;
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(14px);
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(181, 114, 42, 0.16), 0 2px 8px rgba(0,0,0,0.06);
  border: 1px solid rgba(212, 169, 106, 0.2);
  padding: 6px 0;
  z-index: 60;
  overflow: hidden;
}
.dropdown-user-head {
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(212, 169, 106, 0.1), rgba(253, 249, 244, 0.8));
  border-bottom: 1px solid rgba(212, 169, 106, 0.15);
  margin-bottom: 4px;
}
.dropdown-username {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--charcoal, #332b24);
  margin: 0;
}
.dropdown-email {
  font-size: 0.75rem;
  color: rgba(51, 43, 36, 0.4);
  margin: 2px 0 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  font-size: 0.875rem;
  color: rgba(51, 43, 36, 0.65);
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
  background: transparent;
  border: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  box-sizing: border-box;
}
.dropdown-item:hover {
  background: rgba(212, 169, 106, 0.1);
  color: var(--charcoal, #332b24);
}
.dropdown-item--gold { color: var(--gold-600, #8b5a1a); font-weight: 500; }
.dropdown-item--danger { color: #e05050; }
.dropdown-item--danger:hover { background: rgba(224, 80, 80, 0.06); }

.dropdown-item-icon {
  width: 15px;
  height: 15px;
}
.dropdown-divider {
  border-top: 1px solid rgba(212, 169, 106, 0.12);
  margin: 4px 0;
}

/* 登录按钮 */
.login-btn {
  margin-left: 4px;
  padding: 7px 18px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--gold-400, #c49040), var(--gold-500, #b5722a));
  color: #fff;
  font-size: 0.875rem;
  font-weight: 600;
  text-decoration: none;
  box-shadow: 0 3px 10px rgba(181, 114, 42, 0.28);
  transition: all 0.22s;
}
.login-btn:hover {
  background: linear-gradient(135deg, var(--gold-500, #b5722a), var(--gold-600, #8b5a1a));
  box-shadow: 0 5px 14px rgba(181, 114, 42, 0.38);
  transform: translateY(-1px);
}

/* 移动端菜单按钮 */
.mobile-menu-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 10px;
  border-radius: 12px;
  background: transparent;
  border: none;
  cursor: pointer;
  margin-left: 4px;
  transition: background 0.18s;
}
.mobile-menu-btn:hover { background: rgba(212, 169, 106, 0.1); }
@media (min-width: 768px) {
  .mobile-menu-btn { display: none; }
}

/* ── 移动端下拉菜单 ── */
.mobile-nav {
  border-top: 1px solid rgba(212, 169, 106, 0.15);
  padding: 14px 1.5rem 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.mobile-search-wrap {
  position: relative;
}
.mobile-links {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.mobile-link {
  display: block;
  padding: 9px 12px;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(51, 43, 36, 0.65);
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}
.mobile-link:hover {
  background: rgba(212, 169, 106, 0.1);
  color: var(--charcoal, #332b24);
}

/* ── 下拉动画 ── */
.dropdown-enter-active  { transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1); }
.dropdown-leave-active  { transition: all 0.15s ease-in; }
.dropdown-enter-from    { opacity: 0; transform: translateY(-10px) scale(0.95); }
.dropdown-leave-to      { opacity: 0; transform: translateY(-6px) scale(0.97); }

/* ── 移动菜单动画 ── */
.mobile-menu-enter-active { transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1); }
.mobile-menu-leave-active { transition: all 0.18s ease-in; }
.mobile-menu-enter-from   { opacity: 0; transform: translateY(-8px); }
.mobile-menu-leave-to     { opacity: 0; transform: translateY(-5px); }
</style>
