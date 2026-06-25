import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/merchant-pending',
      name: 'merchant-pending',
      component: () => import('@/pages/MerchantPending.vue'),
    },
    {
      path: '/',
      component: () => import('@/layouts/DefaultLayout.vue'),
      children: [
        { path: '', name: 'home', component: () => import('@/pages/Home.vue') },
        { path: 'products', name: 'products', component: () => import('@/pages/ProductList.vue') },
        { path: 'products/:id', name: 'product-detail', component: () => import('@/pages/ProductDetail.vue') },
        { path: 'cart', name: 'cart', component: () => import('@/pages/Cart.vue') },
        { path: 'orders', name: 'orders', component: () => import('@/pages/Orders.vue') },
        { path: 'orders/:id/logistics', name: 'logistics', component: () => import('@/pages/Logistics.vue') },
        { path: 'after-sales', name: 'after-sales', component: () => import('@/pages/AfterSale.vue') },
        { path: 'login', name: 'login', component: () => import('@/pages/Login.vue') },
        { path: 'profile', name: 'profile', component: () => import('@/pages/Profile.vue') },
        { path: 'merchant-register', name: 'merchant-register', component: () => import('@/pages/MerchantRegister.vue') },
        { path: 'favorites', name: 'favorites', component: () => import('@/pages/Favorites.vue') },
      ],
    },
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      children: [
        { path: '', name: 'admin', component: () => import('@/pages/admin/Dashboard.vue') },
        { path: 'categories', name: 'admin-categories', component: () => import('@/pages/admin/Categories.vue') },
        { path: 'products', name: 'admin-products', component: () => import('@/pages/admin/Products.vue') },
        { path: 'orders', name: 'admin-orders', component: () => import('@/pages/admin/Orders.vue') },
        { path: 'after-sales', name: 'admin-after-sales', component: () => import('@/pages/admin/AfterSales.vue') },
        { path: 'users', name: 'admin-users', component: () => import('@/pages/admin/Users.vue') },
        { path: 'email-changes', name: 'admin-email-changes', component: () => import('@/pages/admin/EmailChanges.vue') },
        { path: 'ai-chat', name: 'admin-ai-chat', component: () => import('@/pages/admin/AIChatSettings.vue') },
        { path: 'chat', name: 'admin-chat', component: () => import('@/pages/admin/Chat.vue') },
      ],
    },
    {
      path: '/merchant',
      component: () => import('@/layouts/MerchantLayout.vue'),
      children: [
        { path: '', name: 'merchant', component: () => import('@/pages/merchant/Dashboard.vue') },
        { path: 'products', name: 'merchant-products', component: () => import('@/pages/merchant/Products.vue') },
        { path: 'orders', name: 'merchant-orders', component: () => import('@/pages/merchant/Orders.vue') },
        { path: 'after-sales', name: 'merchant-after-sales', component: () => import('@/pages/merchant/AfterSales.vue') },
        { path: 'profile', name: 'merchant-profile', component: () => import('@/pages/merchant/Profile.vue') },
        { path: 'ai-chat', name: 'merchant-ai-chat', component: () => import('@/pages/merchant/AIChatSettings.vue') },
        { path: 'chat', name: 'merchant-chat', component: () => import('@/pages/merchant/Chat.vue') },
      ],
    },
  ],
})



router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  if (to.path === '/merchant-register') {
    return next()
  }

  if (to.path.startsWith('/admin')) {
    if (!token || role !== 'admin') {
      return next('/login')
    }
  }

  if (to.path.startsWith('/merchant')) {
    if (!token || role !== 'merchant') {
      return next('/login')
    }
    const merchantStatus = localStorage.getItem('merchant_status')
    if (merchantStatus === 'pending') {
      alert('您的商家账号正在审核中，请等待管理员审核通过后再登录。')
      return next('/login')
    }
    if (merchantStatus === 'rejected') {
      alert('您的商家入驻申请未通过审核，如有疑问请联系客服。')
      return next('/login')
    }
  }

  const protectedRoutes = ['/cart', '/orders', '/profile', '/after-sales', '/favorites']
  if (protectedRoutes.some(r => to.path.startsWith(r))) {
    if (!token) {
      return next('/login')
    }
  }

  next()
})

export default router