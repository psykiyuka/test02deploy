import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(email: string, password: string) {
    const res = await api.post<{ token: string; user: User }>('/c-endpoint/user/login', { email, password })
    if (res.code === 0) {
      token.value = res.data.token
      // 直接使用后端返回的用户数据
      user.value = {
        id: res.data.user.id,
        email: res.data.user.email,
        nickname: res.data.user.nickname,
        role: res.data.user.role as 'user' | 'admin' | 'merchant',
        address: null,
        shop_name: res.data.user.shop_name || ''
      }
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('role', res.data.user.role || 'user')
      if (res.data.user.merchant_status) {
        localStorage.setItem('merchant_status', res.data.user.merchant_status)
      }
    }
    return res
  }

  async function register(email: string, password: string, nickname: string, securityQuestion?: string, securityAnswer?: string) {
    const res = await api.post('/c-endpoint/user/register', { email, password, nickname, security_question: securityQuestion, security_answer: securityAnswer })
    return res
  }

  async function fetchProfile() {
    const res = await api.get<User & { avatar_url?: string }>('/c-endpoint/user/profile')
    if (res.code === 0) {
      user.value = {
        id: res.data.id,
        email: res.data.email,
        nickname: res.data.nickname,
        role: res.data.role as 'user' | 'admin' | 'merchant',
        address: null,
        shop_name: res.data.shop_name || '',
        avatar_url: res.data.avatar_url || null,
        merchant_status: res.data.merchant_status,
      }
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('user')
    localStorage.removeItem('merchant_status')
  }

  return { user, token, isLoggedIn, isAdmin, login, register, fetchProfile, logout }
})