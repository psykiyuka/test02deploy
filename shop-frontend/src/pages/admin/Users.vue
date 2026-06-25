<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'
import { Users, Mail, MapPin, ShoppingBag, RotateCcw, X, Shield, Eye, EyeOff, CheckCircle, XCircle } from 'lucide-vue-next'
import Pagination from '@/components/Pagination.vue'

const users = ref<any[]>([])
const loading = ref(true)
const currentPage = ref(1)
const total = ref(0)
const pageSize = 20

const selectedUser = ref<any>(null)
const showDetail = ref(false)
const showResetPassword = ref(false)
const newPassword = ref('')
const confirmPassword = ref('')
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const resetting = ref(false)

async function fetchUsers() {
  loading.value = true
  try {
    const res = await api.get<any>(`/b-endpoint/users?page=${currentPage.value}&size=${pageSize}`)
    if (res.code === 0) {
      users.value = res.data.items
      total.value = res.data.total
    }
  } finally {
    loading.value = false
  }
}

async function viewUserDetail(userId: number) {
  const res = await api.get<any>(`/b-endpoint/users/${userId}`)
  if (res.code === 0) {
    selectedUser.value = res.data
    showDetail.value = true
  }
}

function onPageChange(page: number) {
  currentPage.value = page
  fetchUsers()
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

const roleLabel: Record<string, string> = { admin: '管理员', user: '普通用户', merchant: '商家' }
const roleClass: Record<string, string> = {
  admin: 'bg-gradient-to-r from-gold-400 to-gold-500 text-white',
  user: 'bg-gray-100 text-gray-600',
  merchant: 'bg-indigo-100 text-indigo-600',
}

async function resetUserPassword() {
  if (!newPassword.value || newPassword.value.length < 8) {
    alert('新密码至少8位')
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    alert('两次密码不一致')
    return
  }

  resetting.value = true
  try {
    const res = await api.put(`/b-endpoint/users/${selectedUser.value.id}/password`, {
      new_password: newPassword.value,
    })
    if (res.code === 0) {
      alert('密码重置成功')
      showResetPassword.value = false
      newPassword.value = ''
      confirmPassword.value = ''
    } else {
      alert(res.message || '重置失败')
    }
  } catch (error) {
    alert('重置失败')
  } finally {
    resetting.value = false
  }
}

function openResetPassword() {
  newPassword.value = ''
  confirmPassword.value = ''
  showResetPassword.value = true
}

const merchantStatusLabel: Record<string, string> = { pending: '待审核', approved: '已通过', rejected: '已拒绝' }
const merchantStatusClass: Record<string, string> = {
  pending: 'bg-amber-100 text-amber-600',
  approved: 'bg-emerald-100 text-emerald-600',
  rejected: 'bg-rose-100 text-rose-600',
}

async function approveMerchant(userId: number) {
  if (!confirm('确认审核通过该商家？')) return
  const res = await api.put(`/b-endpoint/users/${userId}/merchant/approve`)
  if (res.code === 0) {
    alert('商家已审核通过')
    fetchUsers()
  } else {
    alert(res.message || '操作失败')
  }
}

async function rejectMerchant(userId: number) {
  const reason = prompt('请输入拒绝原因（选填）：')
  if (reason === null) return
  if (!confirm(`确认拒绝该商家入驻？${reason ? '原因：' + reason : ''}`)) return
  const res = await api.put(`/b-endpoint/users/${userId}/merchant/reject`, { reason })
  if (res.code === 0) {
    alert('已拒绝该商家入驻')
    fetchUsers()
  } else {
    alert(res.message || '操作失败')
  }
}

onMounted(fetchUsers)
</script>

<template>
  <div>
    <div class="mb-8">
      <h1 class="font-display text-3xl text-charcoal mb-1">用户管理</h1>
      <p class="text-charcoal/40 text-sm">查看和管理平台注册用户</p>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-gold-50 overflow-hidden">
      <div v-if="loading" class="animate-pulse p-6 space-y-4">
        <div v-for="i in 5" :key="i" class="h-16 rounded-xl bg-gray-100" />
      </div>
      <div v-else-if="users.length === 0" class="flex flex-col items-center justify-center py-20">
        <div class="w-16 h-16 rounded-2xl bg-gold-50 flex items-center justify-center mb-4">
          <Users :size="28" class="text-gold-300" />
        </div>
        <p class="text-charcoal/30">暂无用户数据</p>
      </div>
      <template v-else>
        <table class="w-full">
          <thead>
            <tr class="border-b border-gold-50 bg-gradient-to-r from-gold-50/50 to-cream/50">
              <th class="text-left px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">用户 ID</th>
              <th class="text-left px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">昵称</th>
              <th class="text-left px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">邮箱</th>
              <th class="text-left px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">角色</th>
              <th class="text-left px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">注册时间</th>
              <th class="text-center px-6 py-4 text-xs font-semibold text-charcoal/40 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in users"
              :key="user.id"
              class="border-b border-gold-50/50 hover:bg-gold-50/20 transition-colors"
            >
              <td class="px-6 py-4">
                <span class="text-sm text-charcoal font-mono font-semibold">#{{ user.id }}</span>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-gradient-to-br from-gold-300 to-gold-500 flex items-center justify-center">
                    <span class="text-xs text-white font-bold">{{ (user.nickname || '?').charAt(0).toUpperCase() }}</span>
                  </div>
                  <span class="text-sm text-charcoal font-medium">{{ user.nickname || '-' }}</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="text-sm text-charcoal/50">{{ user.email }}</span>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                  <span class="text-xs px-2.5 py-1 rounded-full font-medium" :class="roleClass[user.role] || 'bg-gray-100 text-gray-600'">
                    {{ roleLabel[user.role] || user.role }}
                  </span>
                  <span v-if="user.role === 'merchant' && user.merchant_status" class="text-xs px-2 py-0.5 rounded-full font-medium" :class="merchantStatusClass[user.merchant_status] || 'bg-gray-100 text-gray-600'">
                    {{ merchantStatusLabel[user.merchant_status] || user.merchant_status }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="text-sm text-charcoal/30">{{ formatDate(user.created_at) }}</span>
              </td>
              <td class="px-6 py-4 text-center">
                <div class="flex items-center justify-center gap-1.5">
                  <button
                    @click="viewUserDetail(user.id)"
                    class="px-3 py-1.5 text-xs font-medium text-gold-500 hover:bg-gold-50 rounded-lg transition-colors cursor-pointer"
                  >
                    查看详情
                  </button>
                  <template v-if="user.role === 'merchant' && user.merchant_status === 'pending'">
                    <button
                      @click="approveMerchant(user.id)"
                      class="px-3 py-1.5 text-xs font-medium text-emerald-500 hover:bg-emerald-50 rounded-lg transition-colors cursor-pointer flex items-center gap-1"
                    >
                      <CheckCircle :size="13" /> 通过
                    </button>
                    <button
                      @click="rejectMerchant(user.id)"
                      class="px-3 py-1.5 text-xs font-medium text-rose-500 hover:bg-rose-50 rounded-lg transition-colors cursor-pointer flex items-center gap-1"
                    >
                      <XCircle :size="13" /> 拒绝
                    </button>
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="px-6 py-4 border-t border-gold-50">
          <Pagination
            :current="currentPage"
            :total="total"
            :page-size="pageSize"
            @change="onPageChange"
          />
        </div>
      </template>
    </div>

    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showDetail" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="showDetail = false">
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
            <div class="flex items-center justify-between px-6 py-4 border-b border-gold-50">
              <h3 class="font-display text-lg text-charcoal">用户详情</h3>
              <button @click="showDetail = false" class="p-2 text-charcoal/30 hover:text-charcoal hover:bg-gold-50 rounded-lg transition-colors cursor-pointer">
                <X :size="18" />
              </button>
            </div>
            <div v-if="selectedUser" class="p-6 space-y-5">
              <div class="flex items-center gap-4">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-gold-300 to-gold-500 flex items-center justify-center text-white text-xl font-bold">
                  {{ (selectedUser.nickname || '?').charAt(0).toUpperCase() }}
                </div>
                <div>
                  <p class="text-lg font-semibold text-charcoal">{{ selectedUser.nickname || '未设置昵称' }}</p>
                  <span class="text-xs px-2 py-0.5 rounded-full font-medium" :class="roleClass[selectedUser.role] || 'bg-gray-100 text-gray-600'">
                    {{ roleLabel[selectedUser.role] || selectedUser.role }}
                  </span>
                </div>
              </div>

              <div class="space-y-3 bg-gold-50/30 rounded-xl p-4">
                <div class="flex items-center gap-3 text-sm">
                  <Mail :size="16" class="text-charcoal/30" />
                  <span class="text-charcoal/40">邮箱：</span>
                  <span class="text-charcoal font-medium">{{ selectedUser.email }}</span>
                </div>
                <div class="flex items-center gap-3 text-sm">
                  <MapPin :size="16" class="text-charcoal/30" />
                  <span class="text-charcoal/40">地址：</span>
                  <span class="text-charcoal">{{ selectedUser.address || '未设置' }}</span>
                </div>
                <div class="flex items-center gap-3 text-sm">
                  <ShoppingBag :size="16" class="text-charcoal/30" />
                  <span class="text-charcoal/40">订单数：</span>
                  <span class="text-charcoal font-semibold">{{ selectedUser.order_count }}</span>
                </div>
                <div class="flex items-center gap-3 text-sm">
                  <RotateCcw :size="16" class="text-charcoal/30" />
                  <span class="text-charcoal/40">售后申请：</span>
                  <span class="text-charcoal font-semibold">{{ selectedUser.after_sale_count }}</span>
                </div>
              </div>

              <div class="text-xs text-charcoal/30">
                注册时间：{{ formatDate(selectedUser.created_at) }}
              </div>

              <button
                @click="openResetPassword"
                class="w-full py-3 bg-gradient-to-r from-gold-400 to-gold-500 text-white rounded-xl font-semibold hover:from-gold-500 hover:to-gold-600 transition-all shadow-lg shadow-gold-300/25 cursor-pointer flex items-center justify-center gap-2"
              >
                <Shield class="w-4 h-4" />
                重置密码
              </button>
            </div>
          </div>
        </div>
      </Transition>

      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showResetPassword" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="showResetPassword = false">
            <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
              <div class="flex items-center justify-between px-6 py-4 border-b border-gold-50">
                <h3 class="font-display text-lg text-charcoal">重置密码</h3>
                <button @click="showResetPassword = false" class="p-2 text-charcoal/30 hover:text-charcoal hover:bg-gold-50 rounded-lg transition-colors cursor-pointer">
                  <X :size="18" />
                </button>
              </div>
              <div class="p-6 space-y-4">
                <div>
                  <label class="block text-sm font-medium text-charcoal/60 mb-2">新密码</label>
                  <div class="relative">
                    <Shield class="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-gold-300" />
                    <input
                      v-model="newPassword"
                      :type="showNewPassword ? 'text' : 'password'"
                      placeholder="请输入新密码（至少8位）"
                      class="w-full pl-10 pr-12 py-3 bg-gold-50/30 border border-gold-100 rounded-xl text-charcoal placeholder-charcoal/30 focus:bg-white focus:border-gold-300 focus:ring-4 focus:ring-gold-50 transition-all text-sm"
                    />
                    <button @click="showNewPassword = !showNewPassword" class="absolute right-3 top-1/2 -translate-y-1/2 text-charcoal/30 hover:text-charcoal/60 cursor-pointer">
                      <Eye v-if="showNewPassword" :size="18" />
                      <EyeOff v-else :size="18" />
                    </button>
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium text-charcoal/60 mb-2">确认密码</label>
                  <div class="relative">
                    <Shield class="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-gold-300" />
                    <input
                      v-model="confirmPassword"
                      :type="showConfirmPassword ? 'text' : 'password'"
                      placeholder="请再次输入新密码"
                      class="w-full pl-10 pr-12 py-3 bg-gold-50/30 border border-gold-100 rounded-xl text-charcoal placeholder-charcoal/30 focus:bg-white focus:border-gold-300 focus:ring-4 focus:ring-gold-50 transition-all text-sm"
                    />
                    <button @click="showConfirmPassword = !showConfirmPassword" class="absolute right-3 top-1/2 -translate-y-1/2 text-charcoal/30 hover:text-charcoal/60 cursor-pointer">
                      <Eye v-if="showConfirmPassword" :size="18" />
                      <EyeOff v-else :size="18" />
                    </button>
                  </div>
                </div>
                <button
                  @click="resetUserPassword"
                  :disabled="resetting"
                  class="w-full py-3 bg-gradient-to-r from-gold-400 to-gold-500 text-white rounded-xl font-semibold hover:from-gold-500 hover:to-gold-600 transition-all shadow-lg shadow-gold-300/25 cursor-pointer disabled:opacity-60"
                >
                  {{ resetting ? '重置中...' : '确认重置' }}
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>
    </Teleport>
  </div>
</template>

<style scoped>
.modal-enter-active { transition: all 0.25s ease-out; }
.modal-leave-active { transition: all 0.15s ease-in; }
.modal-enter-from { opacity: 0; }
.modal-enter-from > div { transform: scale(0.95); opacity: 0; }
.modal-leave-to { opacity: 0; }
.modal-leave-to > div { transform: scale(0.95); opacity: 0; }
</style>