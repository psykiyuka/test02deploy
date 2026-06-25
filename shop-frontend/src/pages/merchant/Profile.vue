<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <div class="bg-white rounded-xl shadow-md p-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-6">店铺设置</h3>

      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">昵称</label>
          <input
            v-model="form.nickname"
            type="text"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            placeholder="请输入昵称"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">店铺名称</label>
          <input
            v-model="form.shopName"
            type="text"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">店铺描述</label>
          <textarea
            v-model="form.shopDescription"
            rows="4"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            placeholder="请描述您的店铺"
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">店铺Logo</label>
          <div v-if="shopLogoPreview || form.shopLogo" class="relative inline-block mb-3">
            <img :src="shopLogoPreview || form.shopLogo" class="w-24 h-24 rounded-lg object-cover border" />
            <button
              type="button"
              @click="removeLogo"
              class="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs hover:bg-red-600 transition-colors shadow"
              title="删除Logo"
            >
              ×
            </button>
          </div>
          <input
            ref="shopLogoInput"
            type="file"
            accept="image/*"
            class="hidden"
            @change="handleLogoUpload"
          />
          <button
            type="button"
            @click="shopLogoInput?.click()"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors"
          >
            选择图片
          </button>
          <p v-if="shopLogoFile" class="text-xs text-gray-500 mt-1">{{ shopLogoFile.name }}</p>
          <p class="text-xs text-gray-400 mt-1">支持 JPG/PNG，大小不超过 5MB</p>
        </div>

        <div class="pt-4">
          <button
            type="submit"
            :disabled="isSubmitting"
            class="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all disabled:opacity-50"
          >
            {{ isSubmitting ? '保存中...' : '保存设置' }}
          </button>
        </div>
      </form>

      <div class="mt-8 pt-6 border-t">
        <h4 class="text-sm font-medium text-gray-700 mb-4">账号信息</h4>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-gray-500 mb-1">邮箱</label>
            <p class="text-gray-800">{{ profile.email }}</p>
          </div>
          <div>
            <label class="block text-sm text-gray-500 mb-1">昵称</label>
            <p class="text-gray-800">{{ profile.nickname }}</p>
          </div>
          <div>
            <label class="block text-sm text-gray-500 mb-1">角色</label>
            <span class="bg-indigo-100 text-indigo-700 px-2 py-1 rounded text-sm">商家</span>
          </div>
          <div>
            <label class="block text-sm text-gray-500 mb-1">状态</label>
            <span :class="profile.merchant_status === 'approved' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'" class="px-2 py-1 rounded text-sm">
              {{ profile.merchant_status === 'approved' ? '已审核通过' : '待审核' }}
            </span>
          </div>
        </div>

        <div class="mt-6 pt-4 border-t">
          <h5 class="text-sm font-medium text-gray-700 mb-3">换绑邮箱</h5>
          <p class="text-xs text-gray-400 mb-2">更换邮箱需要管理员审核通过后生效</p>
          <div class="flex items-center gap-3">
            <input
              v-model="newEmail"
              type="email"
              class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
              placeholder="请输入新邮箱"
            />
            <button
              type="button"
              @click="applyEmailChange"
              :disabled="emailApplying"
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 transition-colors disabled:opacity-50"
            >
              {{ emailApplying ? '提交中...' : '提交申请' }}
            </button>
          </div>
          <p v-if="emailApplyMsg" :class="emailApplyOk ? 'text-green-600' : 'text-red-500'" class="text-xs mt-1">{{ emailApplyMsg }}</p>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-md p-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-6">修改密码</h3>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">原密码</label>
          <div class="relative">
            <input
              v-model="passwordForm.oldPassword"
              :type="showOldPassword ? 'text' : 'password'"
              class="w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
              placeholder="请输入原密码"
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
              v-model="passwordForm.newPassword"
              :type="showNewPassword ? 'text' : 'password'"
              class="w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
              placeholder="请输入新密码（至少8位）"
            />
            <button type="button" @click="showNewPassword = !showNewPassword" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors p-0.5 rounded-md hover:bg-gray-100" tabindex="-1">
              <Eye v-if="showNewPassword" class="w-5 h-5" />
              <EyeOff v-else class="w-5 h-5" />
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">确认密码</label>
          <div class="relative">
            <input
              v-model="passwordForm.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              class="w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
              placeholder="请再次输入新密码"
            />
            <button type="button" @click="showConfirmPassword = !showConfirmPassword" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors p-0.5 rounded-md hover:bg-gray-100" tabindex="-1">
              <Eye v-if="showConfirmPassword" class="w-5 h-5" />
              <EyeOff v-else class="w-5 h-5" />
            </button>
          </div>
        </div>

        <div class="pt-4">
          <button
            @click="handlePasswordSubmit"
            :disabled="passwordSubmitting"
            class="w-full bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all disabled:opacity-50"
          >
            {{ passwordSubmitting ? '修改中...' : '修改密码' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { api } from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { Eye, EyeOff } from 'lucide-vue-next'

const authStore = useAuthStore()
const router = useRouter()

const isSubmitting = ref(false)
const passwordSubmitting = ref(false)

const showOldPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const newEmail = ref('')
const emailApplying = ref(false)
const emailApplyMsg = ref('')
const emailApplyOk = ref(false)

const shopLogoInput = ref<HTMLInputElement | null>(null)
const shopLogoFile = ref<File | null>(null)
const shopLogoPreview = ref<string>('')

const form = reactive({
  nickname: '',
  shopName: '',
  shopDescription: '',
  shopLogo: '',
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const profile = reactive({
  email: '',
  nickname: '',
  merchant_status: 'pending',
})

const applyEmailChange = async () => {
  if (!newEmail.value || !newEmail.value.includes('@')) {
    emailApplyMsg.value = '请输入有效的邮箱地址'
    emailApplyOk.value = false
    return
  }
  emailApplying.value = true
  emailApplyMsg.value = ''
  try {
    await api.post('/c-endpoint/user/email-change/apply', { new_email: newEmail.value })
    emailApplyMsg.value = '申请已提交，请等待管理员审核'
    emailApplyOk.value = true
    newEmail.value = ''
  } catch (err: any) {
    emailApplyMsg.value = err.response?.data?.message || '提交失败'
    emailApplyOk.value = false
  } finally {
    emailApplying.value = false
  }
}

const removeLogo = () => {
  shopLogoFile.value = null
  shopLogoPreview.value = ''
  form.shopLogo = ''
  if (shopLogoInput.value) shopLogoInput.value.value = ''
}

const handleLogoUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  if (file.size > 5 * 1024 * 1024) {
    alert('文件大小不能超过5MB')
    return
  }
  if (!file.type.startsWith('image/')) {
    alert('只支持图片格式')
    return
  }

  shopLogoFile.value = file
  const reader = new FileReader()
  reader.onload = (e) => {
    shopLogoPreview.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

const handleSubmit = async () => {
  isSubmitting.value = true
  try {
    const promises: Promise<any>[] = []

    // 昵称有变化则更新
    if (form.nickname !== profile.nickname) {
      promises.push(
        api.put('/c-endpoint/user/profile', { nickname: form.nickname })
      )
    }

    // 店铺信息
    let shopLogoData: string | null = form.shopLogo

    if (shopLogoFile.value) {
      shopLogoData = await fileToBase64(shopLogoFile.value)
    } else if (!form.shopLogo) {
      shopLogoData = null
    }

    promises.push(
      api.put('/c-endpoint/user/shop', {
        shop_name: form.shopName,
        shop_description: form.shopDescription,
        shop_logo: shopLogoData,
      })
    )

    await Promise.all(promises)
    // 同步更新本地 profile
    profile.nickname = form.nickname
    alert('保存成功')
  } catch (error) {
    alert('保存失败')
  } finally {
    isSubmitting.value = false
  }
}

const handlePasswordSubmit = async () => {
  if (!passwordForm.oldPassword) {
    alert('请输入原密码')
    return
  }
  if (!passwordForm.newPassword || passwordForm.newPassword.length < 8) {
    alert('新密码至少8位')
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    alert('两次密码不一致')
    return
  }

  passwordSubmitting.value = true
  try {
    const res = await api.put('/c-endpoint/user/password', {
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword,
    })
    if (res.code === 0) {
      alert('密码修改成功，请重新登录')
      authStore.logout()
      router.push('/login')
    } else {
      alert(res.message || '修改失败')
    }
  } catch (error) {
    alert('修改失败')
  } finally {
    passwordSubmitting.value = false
  }
}

onMounted(async () => {
  try {
    const res = await api.get<any>('/c-endpoint/user/profile')
    const data = res.data
    if (data) {
      profile.email = data.email || ''
      profile.nickname = data.nickname || ''
      profile.merchant_status = data.merchant_status || 'pending'
      form.nickname = data.nickname || ''
      form.shopName = data.shop_name || ''
      form.shopDescription = data.shop_description || ''
      form.shopLogo = data.shop_logo || ''
    }
  } catch (error) {
    console.error('Failed to load profile:', error)
  }
})
</script>