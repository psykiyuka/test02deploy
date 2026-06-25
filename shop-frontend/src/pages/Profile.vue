<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { User, Edit, Mail, MapPin, Shield, Settings, Save, X, Plus, Trash2, Camera, Eye, EyeOff } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/utils/api'
import MapPicker from '@/components/MapPicker.vue'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.user?.role === 'admin')

const editingNickname = ref(false)
const newNickname = ref('')
const nicknameSaving = ref(false)
const editingPassword = ref(false)
const showOldPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const passwordSaving = ref(false)

// 换绑邮箱相关
const newEmail = ref('')
const emailApplying = ref(false)
const emailApplyMsg = ref('')
const emailApplyOk = ref(false)

// 地址相关
interface Address {
  id: number
  name: string
  phone: string
  province: string
  city: string
  district: string
  detail: string
  is_default: boolean
}
const addresses = ref<Address[]>([])
const addressLoading = ref(false)
const showAddressForm = ref(false)
const editingAddressId = ref<number | null>(null)
const addressForm = ref({ name: '', phone: '', province: '', city: '', district: '', detail: '' })
const addressSaving = ref(false)

// 地图选址相关
const showMapPicker = ref(false)

/**
 * 地图选址回调：接收结构化地址数据，自动填充表单
 */
function onMapAddressSelected(addr: { province: string; city: string; district: string; detail: string; address: string }) {
  addressForm.value.province = addr.province
  addressForm.value.city = addr.city
  addressForm.value.district = addr.district
  addressForm.value.detail = addr.detail
  showMapPicker.value = false
}

// 头像上传相关
const avatarUploading = ref(false)
const avatarPreviewUrl = ref<string | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

function onAvatarFileSelected(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  // 文件大小校验：5MB
  if (file.size > 5 * 1024 * 1024) {
    alert('图片大小不能超过5MB')
    return
  }

  // 类型校验
  if (!file.type.startsWith('image/')) {
    alert('请选择图片文件')
    return
  }

  // 使用 FileReader 预览
  const reader = new FileReader()
  reader.onload = (e) => {
    avatarPreviewUrl.value = e.target?.result as string
  }
  reader.readAsDataURL(file)

  // 自动上传
  uploadAvatar(file)
}

async function uploadAvatar(file: File) {
  avatarUploading.value = true
  try {
    const formData = new FormData()
    formData.append('avatar', file)
    const token = localStorage.getItem('token')
    const BASE = import.meta.env.VITE_API_BASE || '/api/shop'
    const res = await fetch(`${BASE}/c-endpoint/user/avatar`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })
    const data = await res.json()
    if (data.code === 0) {
      await authStore.fetchProfile()
      avatarPreviewUrl.value = null
    } else {
      alert(data.message || '头像上传失败')
      avatarPreviewUrl.value = null
    }
  } catch (err: any) {
    alert(err.message || '头像上传失败')
    avatarPreviewUrl.value = null
  } finally {
    avatarUploading.value = false
  }
}

function triggerAvatarUpload() {
  fileInputRef.value?.click()
}

function getUserAvatar(): string | null {
  const user = authStore.user as any
  return user?.avatar_url || user?.avatar || null
}

function formatAddress(addr: Address) {
  return `${addr.province}${addr.city}${addr.district} ${addr.detail}`
}

onMounted(async () => {
  await authStore.fetchProfile()
  newNickname.value = authStore.user?.nickname || ''
  if (!isAdmin.value) {
    fetchAddresses()
  }
})

async function fetchAddresses() {
  addressLoading.value = true
  try {
    const res = await api.get<any>('/c-endpoint/addresses')
    if (res.code === 0) {
      const data = res.data as any
      addresses.value = Array.isArray(data) ? data : (data.items || data)
    }
  } catch (err) {
    console.error('获取地址失败:', err)
  } finally {
    addressLoading.value = false
  }
}

async function saveNickname() {
  const nickname = newNickname.value.trim()
  if (!nickname) return
  nicknameSaving.value = true
  try {
    const res = await api.put('/c-endpoint/user/profile', { nickname })
    if (res.code === 0) {
      await authStore.fetchProfile()
      editingNickname.value = false
    } else {
      alert(res.message || '修改昵称失败')
    }
  } catch (err: any) {
    alert(err.message || '修改昵称失败')
  } finally {
    nicknameSaving.value = false
  }
}

function cancelEditNickname() {
  newNickname.value = authStore.user?.nickname || ''
  editingNickname.value = false
}

async function savePassword() {
  if (!oldPassword.value || !newPassword.value || !confirmPassword.value) {
    alert('请填写完整密码信息')
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    alert('两次密码不一致')
    return
  }
  if (newPassword.value.length < 6) {
    alert('新密码至少6位')
    return
  }
  passwordSaving.value = true
  try {
    const res = await api.put('/c-endpoint/user/password', {
      old_password: oldPassword.value,
      new_password: newPassword.value,
    })
    if (res.code === 0) {
      alert('密码修改成功')
      editingPassword.value = false
      oldPassword.value = ''
      newPassword.value = ''
      confirmPassword.value = ''
    } else {
      alert(res.message || '修改密码失败')
    }
  } catch (err: any) {
    alert(err.message || '修改密码失败')
  } finally {
    passwordSaving.value = false
  }
}

async function applyEmailChange() {
  const email = newEmail.value.trim()
  if (!email || !email.includes('@')) {
    emailApplyMsg.value = '请输入有效的邮箱地址'
    emailApplyOk.value = false
    return
  }
  
  emailApplying.value = true
  emailApplyMsg.value = ''
  
  try {
    const res = await api.post('/c-endpoint/user/email-change/apply', { new_email: email })
    if (res.code === 0) {
      emailApplyMsg.value = '申请提交成功，请等待管理员审核'
      emailApplyOk.value = true
      newEmail.value = ''
    } else {
      emailApplyMsg.value = res.message || '提交失败'
      emailApplyOk.value = false
    }
  } catch (err: any) {
    emailApplyMsg.value = err.message || '提交失败'
    emailApplyOk.value = false
  } finally {
    emailApplying.value = false
  }
}

function openAddAddress() {
  editingAddressId.value = null
  addressForm.value = { name: '', phone: '', province: '', city: '', district: '', detail: '' }
  showAddressForm.value = true
}

function openEditAddress(addr: Address) {
  editingAddressId.value = addr.id
  addressForm.value = {
    name: addr.name,
    phone: addr.phone,
    province: addr.province || '',
    city: addr.city || '',
    district: addr.district || '',
    detail: addr.detail || '',
  }
  showAddressForm.value = true
}

async function saveAddress() {
  const { name, phone, province, city, district, detail } = addressForm.value
  if (!name.trim() || !phone.trim() || !province.trim() || !city.trim() || !detail.trim()) {
    alert('请填写完整地址信息')
    return
  }
  addressSaving.value = true
  try {
    const body = {
      name: name.trim(),
      phone: phone.trim(),
      province: province.trim(),
      city: city.trim(),
      district: district.trim(),
      detail: detail.trim(),
    }
    if (editingAddressId.value) {
      const res = await api.put(`/c-endpoint/addresses/${editingAddressId.value}`, body)
      if (res.code !== 0) {
        alert(res.message || '修改地址失败')
        return
      }
    } else {
      const res = await api.post('/c-endpoint/addresses', body)
      if (res.code !== 0) {
        alert(res.message || '添加地址失败')
        return
      }
    }
    showAddressForm.value = false
    await fetchAddresses()
  } catch (err: any) {
    alert(err.message || '保存地址失败')
  } finally {
    addressSaving.value = false
  }
}

async function deleteAddress(id: number) {
  if (!confirm('确定要删除该地址吗？')) return
  try {
    const res = await api.delete(`/c-endpoint/addresses/${id}`)
    if (res.code === 0) {
      await fetchAddresses()
    } else {
      alert(res.message || '删除地址失败')
    }
  } catch (err: any) {
    alert(err.message || '删除地址失败')
  }
}

async function setDefaultAddress(id: number) {
  try {
    const res = await api.put(`/c-endpoint/addresses/${id}/default`)
    if (res.code === 0) {
      await fetchAddresses()
    } else {
      alert(res.message || '设置默认地址失败')
    }
  } catch (err: any) {
    alert(err.message || '设置默认地址失败')
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <div class="mx-4 md:mx-8 lg:mx-12 py-6">
      <div class="grid lg:grid-cols-3 gap-6">
        <div class="lg:col-span-1">
          <div class="bg-white rounded-2xl shadow-sm p-6 text-center">
            <div class="relative inline-block mb-4">
              <div class="w-24 h-24 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center overflow-hidden">
                <img
                  v-if="avatarPreviewUrl || getUserAvatar()"
                  :src="avatarPreviewUrl || getUserAvatar()!"
                  alt="头像"
                  class="w-full h-full object-cover"
                />
                <User v-else class="w-12 h-12 text-white" />
              </div>
              <button
                @click="triggerAvatarUpload"
                :disabled="avatarUploading"
                class="absolute bottom-0 right-0 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
                title="上传头像"
              >
                <Camera v-if="!avatarUploading" class="w-4 h-4 text-gray-600" />
                <svg v-else class="w-4 h-4 text-gray-600 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
              </button>
              <input
                ref="fileInputRef"
                type="file"
                accept="image/*"
                class="hidden"
                @change="onAvatarFileSelected"
              />
            </div>

            <div v-if="!editingNickname">
              <h2 class="text-xl font-bold text-gray-900">{{ authStore.user?.nickname || '未设置' }}</h2>
              <button
                @click="editingNickname = true"
                class="mt-2 text-sm text-indigo-600 hover:text-indigo-700 flex items-center justify-center gap-1 mx-auto"
              >
                <Edit class="w-4 h-4" />
                编辑昵称
              </button>
            </div>
            <div v-else class="mt-2">
              <div class="flex items-center gap-2">
                <input
                  v-model="newNickname"
                  type="text"
                  class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-center focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  @keyup.enter="saveNickname"
                />
                <button @click="saveNickname" :disabled="nicknameSaving" class="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors disabled:opacity-50">
                  <Save class="w-5 h-5" />
                </button>
                <button @click="cancelEditNickname" class="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors">
                  <X class="w-5 h-5" />
                </button>
              </div>
            </div>

            <div class="mt-4 flex items-center justify-center gap-2 text-gray-500">
              <Mail class="w-4 h-4" />
              <span class="text-sm">{{ authStore.user?.email }}</span>
            </div>

            <div class="mt-2 flex items-center justify-center gap-2 text-gray-500">
              <span
                :class="[
                  'px-2 py-1 rounded-full text-xs font-medium',
                  authStore.user?.role === 'admin' ? 'bg-gray-100 text-gray-700' :
                  authStore.user?.role === 'merchant' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'
                ]"
              >
                {{ authStore.user?.role === 'admin' ? '管理员' : authStore.user?.role === 'merchant' ? '卖家' : '普通用户' }}
              </span>
            </div>
          </div>
        </div>

        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-2xl shadow-sm p-6">
            <div class="flex items-center gap-3 mb-6">
              <Settings class="w-5 h-5 text-indigo-600" />
              <h2 class="text-lg font-semibold text-gray-900">基本资料</h2>
            </div>

            <div class="space-y-4">
              <div class="flex items-center justify-between py-3 border-b border-gray-100">
                <span class="text-gray-500">昵称</span>
                <div class="flex items-center gap-2">
                  <span class="font-medium text-gray-900">{{ authStore.user?.nickname || '未设置' }}</span>
                  <button
                    @click="editingNickname = true"
                    class="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                  >
                    <Edit class="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div class="flex items-center justify-between py-3 border-b border-gray-100">
                <span class="text-gray-500">邮箱</span>
                <div class="flex items-center gap-2">
                  <span class="font-medium text-gray-900">{{ authStore.user?.email }}</span>
                  <button
                    @click="editingNickname = !editingNickname"
                    class="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                  >
                    <Edit class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            <div class="mt-6 pt-4 border-t">
              <h5 class="text-sm font-medium text-gray-700 mb-3">换绑邮箱</h5>
              <p class="text-xs text-gray-400 mb-2">更换邮箱需要管理员审核通过后生效</p>
              <div class="flex items-center gap-3">
                <input
                  v-model="newEmail"
                  type="email"
                  class="flex-1 px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
                  placeholder="请输入新邮箱"
                />
                <button
                  type="button"
                  @click="applyEmailChange"
                  :disabled="emailApplying"
                  class="px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
                >
                  {{ emailApplying ? '提交中...' : '提交申请' }}
                </button>
              </div>
              <p v-if="emailApplyMsg" :class="emailApplyOk ? 'text-green-600' : 'text-red-500'" class="text-xs mt-2">{{ emailApplyMsg }}</p>
            </div>
          </div>

          <div class="bg-white rounded-2xl shadow-sm p-6">
            <div class="flex items-center gap-3 mb-6">
              <Shield class="w-5 h-5 text-indigo-600" />
              <h2 class="text-lg font-semibold text-gray-900">安全设置</h2>
            </div>

            <div v-if="!editingPassword">
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-medium text-gray-900">修改密码</p>
                  <p class="text-sm text-gray-500 mt-1">定期更换密码，保障账户安全</p>
                </div>
                <button
                  @click="editingPassword = true"
                  class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
                >
                  修改密码
                </button>
              </div>
            </div>

            <div v-else class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">原密码</label>
                <div class="relative">
                  <input
                    v-model="oldPassword"
                    :type="showOldPassword ? 'text' : 'password'"
                    placeholder="请输入原密码"
                    class="w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
                  />
                  <button type="button" @click="showOldPassword = !showOldPassword" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors p-0.5 rounded-md hover:bg-gray-100" tabindex="-1">
                    <Eye v-if="showOldPassword" class="w-5 h-5" />
                    <EyeOff v-else class="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">新密码</label>
                <div class="relative">
                  <input
                    v-model="newPassword"
                    :type="showNewPassword ? 'text' : 'password'"
                    placeholder="请输入新密码"
                    class="w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
                  />
                  <button type="button" @click="showNewPassword = !showNewPassword" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors p-0.5 rounded-md hover:bg-gray-100" tabindex="-1">
                    <Eye v-if="showNewPassword" class="w-5 h-5" />
                    <EyeOff v-else class="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">确认新密码</label>
                <div class="relative">
                  <input
                    v-model="confirmPassword"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    placeholder="请再次输入新密码"
                    class="w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
                  />
                  <button type="button" @click="showConfirmPassword = !showConfirmPassword" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors p-0.5 rounded-md hover:bg-gray-100" tabindex="-1">
                    <Eye v-if="showConfirmPassword" class="w-5 h-5" />
                    <EyeOff v-else class="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div class="flex gap-3">
                <button
                  @click="editingPassword = false; oldPassword = ''; newPassword = ''; confirmPassword = ''"
                  class="flex-1 py-3 border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors"
                >
                  取消
                </button>
                <button
                  @click="savePassword"
                  :disabled="passwordSaving"
                  class="flex-1 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
                >
                  {{ passwordSaving ? '保存中...' : '保存修改' }}
                </button>
              </div>
            </div>
          </div>

          <!-- 地址簿：管理员隐藏 -->
          <div v-if="!isAdmin" class="bg-white rounded-2xl shadow-sm p-6">
            <div class="flex items-center justify-between mb-6">
              <div class="flex items-center gap-3">
                <MapPin class="w-5 h-5 text-indigo-600" />
                <h2 class="text-lg font-semibold text-gray-900">收货地址</h2>
              </div>
              <button
                @click="openAddAddress"
                class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors flex items-center gap-1"
              >
                <Plus class="w-4 h-4" />
                添加地址
              </button>
            </div>

            <div v-if="addressLoading" class="py-8 text-center text-gray-400">加载中...</div>

            <div v-else-if="addresses.length === 0" class="py-8 text-center text-gray-400">
              暂无收货地址，请添加
            </div>

            <div v-else class="space-y-4">
              <div
                v-for="addr in addresses"
                :key="addr.id"
                class="flex items-start gap-4 p-4 bg-gray-50 rounded-xl"
              >
                <div
                  :class="[
                    'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0',
                    addr.is_default ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'
                  ]"
                >
                  <MapPin class="w-5 h-5" />
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2">
                    <span class="font-medium text-gray-900">{{ addr.name }}</span>
                    <span class="text-sm text-gray-500">{{ addr.phone }}</span>
                    <span
                      v-if="addr.is_default"
                      class="px-2 py-0.5 bg-indigo-100 text-indigo-700 text-xs rounded-full"
                    >
                      默认
                    </span>
                  </div>
                  <p class="text-sm text-gray-600 mt-1">{{ formatAddress(addr) }}</p>
                </div>
                <div class="flex gap-2">
                  <button
                    v-if="!addr.is_default"
                    @click="setDefaultAddress(addr.id)"
                    class="px-3 py-1.5 text-sm text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                  >
                    设为默认
                  </button>
                  <button
                    @click="openEditAddress(addr)"
                    class="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    编辑
                  </button>
                  <button
                    @click="deleteAddress(addr.id)"
                    class="px-3 py-1.5 text-sm text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    删除
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 地址表单弹窗 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showAddressForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="showAddressForm = false">
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <h3 class="text-lg font-semibold text-gray-900">{{ editingAddressId ? '编辑地址' : '添加地址' }}</h3>
              <button @click="showAddressForm = false" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                <X class="w-5 h-5" />
              </button>
            </div>
            <div class="p-6 space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">收货人</label>
                <input v-model="addressForm.name" type="text" placeholder="请输入收货人姓名"
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">联系电话</label>
                <input v-model="addressForm.phone" type="text" placeholder="请输入联系电话"
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <!-- 地图选址按钮 -->
              <div>
                <button
                  type="button"
                  @click="showMapPicker = true"
                  class="w-full py-3 border-2 border-dashed border-indigo-300 rounded-xl text-indigo-600 font-medium hover:bg-indigo-50 hover:border-indigo-400 transition-all flex items-center justify-center gap-2"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  高德地图选址
                </button>
              </div>
              <div class="grid grid-cols-3 gap-3">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">省份</label>
                  <input v-model="addressForm.province" type="text" placeholder="省份"
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">城市</label>
                  <input v-model="addressForm.city" type="text" placeholder="城市"
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">区/县</label>
                  <input v-model="addressForm.district" type="text" placeholder="区/县"
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">详细地址</label>
                <textarea v-model="addressForm.detail" rows="2" placeholder="街道、门牌号等"
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"></textarea>
              </div>
              <div class="flex gap-3">
                <button @click="showAddressForm = false"
                  class="flex-1 py-3 border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors">
                  取消
                </button>
                <button @click="saveAddress" :disabled="addressSaving"
                  class="flex-1 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50">
                  {{ addressSaving ? '保存中...' : '保存' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 高德地图选址弹窗 -->
    <MapPicker
      :show="showMapPicker"
      @close="showMapPicker = false"
      @select="onMapAddressSelected"
    />
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
