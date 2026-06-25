<script setup lang="ts">
import { ref } from 'vue'
import { ChevronRight, Upload, Check } from 'lucide-vue-next'
import { api } from '@/utils/api'
import { useRouter } from 'vue-router'

const router = useRouter()
const currentStep = ref(1)
const isSubmitting = ref(false)
const errorMessage = ref('')

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const nickname = ref('')
const securityQuestion = ref('我最喜欢的食物')
const securityAnswer = ref('')
const shopName = ref('')
const businessCategory = ref('')
const businessLicense = ref<File | null>(null)
const idCard = ref<File | null>(null)

const categories = [
  { id: 'electronics', name: '数码电子产品' },
  { id: 'clothing', name: '服装配饰' },
  { id: 'food', name: '食品零食' },
  { id: 'beauty', name: '美妆护肤' },
  { id: 'home', name: '家居用品' },
  { id: 'sports', name: '运动户外' },
  { id: 'gift', name: '礼品饰品' },
  { id: 'other', name: '其他' },
]

const steps = [
  { id: 1, title: '账号信息' },
  { id: 2, title: '店铺信息' },
  { id: 3, title: '资质上传' },
  { id: 4, title: '提交完成' },
]

function nextStep() {
  errorMessage.value = ''
  
  if (currentStep.value === 1) {
    if (!email.value.trim()) {
      errorMessage.value = '请输入邮箱地址'
      return
    }
    if (!email.value.includes('@')) {
      errorMessage.value = '邮箱格式不正确'
      return
    }
    if (!password.value) {
      errorMessage.value = '请输入密码'
      return
    }
    if (password.value.length < 8) {
      errorMessage.value = '密码长度不能少于8位'
      return
    }
    if (password.value !== confirmPassword.value) {
      errorMessage.value = '两次输入的密码不一致'
      return
    }
    if (!nickname.value.trim()) {
      errorMessage.value = '请输入昵称'
      return
    }
    if (!securityQuestion.value.trim()) {
      errorMessage.value = '请输入安全问题'
      return
    }
    if (!securityAnswer.value.trim()) {
      errorMessage.value = '请输入安全问题答案'
      return
    }
  }
  
  if (currentStep.value === 2) {
    if (!shopName.value.trim()) {
      errorMessage.value = '请输入店铺名称'
      return
    }
    if (!businessCategory.value) {
      errorMessage.value = '请选择经营类目'
      return
    }
  }
  
  if (currentStep.value === 3) {
    submitApplication()
    return
  }
  
  currentStep.value++
}

function prevStep() {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

async function submitApplication() {
  if (!businessLicense.value || !idCard.value) {
    errorMessage.value = '请上传营业执照和身份证照片'
    return
  }
  
  isSubmitting.value = true
  errorMessage.value = ''
  
  try {
    const formData = new FormData()
    formData.append('email', email.value)
    formData.append('password', password.value)
    formData.append('nickname', nickname.value)
    formData.append('security_question', securityQuestion.value)
    formData.append('security_answer', securityAnswer.value)
    formData.append('shop_name', shopName.value)
    formData.append('business_category', businessCategory.value)
    formData.append('business_license', businessLicense.value)
    formData.append('id_card', idCard.value)

    const res = await fetch('/api/shop/c-endpoint/user/register/merchant', {
      method: 'POST',
      body: formData
    })
    
    const data = await res.json()
    
    if (data.code === 0) {
      currentStep.value = 4
    } else {
      errorMessage.value = data.message || '提交失败'
    }
  } catch (err: any) {
    errorMessage.value = err.message || '网络错误'
  } finally {
    isSubmitting.value = false
  }
}

function handleFileUpload(fileType: 'license' | 'idcard', event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    if (file.size > 5 * 1024 * 1024) {
      errorMessage.value = '文件大小不能超过5MB'
      return
    }
    
    if (!file.type.startsWith('image/')) {
      errorMessage.value = '只支持图片格式'
      return
    }
    
    if (fileType === 'license') {
      businessLicense.value = file
    } else {
      idCard.value = file
    }
    
    errorMessage.value = ''
  }
}

function triggerFileInput(inputId: string) {
  const input = document.getElementById(inputId) as HTMLInputElement
  input?.click()
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="mx-4 md:mx-8 lg:mx-auto max-w-3xl">
      <div class="bg-white rounded-2xl shadow-sm p-6 md:p-8">
        <div class="text-center mb-8">
          <h1 class="text-2xl font-bold text-gray-900 mb-2">卖家入驻</h1>
          <p class="text-gray-500">成为我们的卖家，开启您的电商之旅</p>
        </div>
        
        <div v-if="errorMessage" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl mb-6">
          {{ errorMessage }}
        </div>

        <div class="relative mb-8">
          <div class="absolute top-5 left-0 right-0 h-1 bg-gray-200 rounded-full"></div>
          <div 
            class="absolute top-5 left-0 h-1 bg-indigo-600 rounded-full transition-all duration-500"
            :style="{ width: `${((currentStep - 1) / (steps.length - 1)) * 100}%` }"
          ></div>
          
          <div class="relative flex justify-between">
            <div 
              v-for="step in steps" 
              :key="step.id"
              class="flex flex-col items-center"
            >
              <div 
                :class="[
                  'w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300',
                  currentStep >= step.id 
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' 
                    : 'bg-gray-200 text-gray-500'
                ]"
              >
                <Check v-if="currentStep > step.id" class="w-5 h-5" />
                <span v-else class="font-semibold">{{ step.id }}</span>
              </div>
              <span 
                :class="[
                  'mt-2 text-sm font-medium',
                  currentStep >= step.id ? 'text-gray-900' : 'text-gray-400'
                ]"
              >
                {{ step.title }}
              </span>
            </div>
          </div>
        </div>

        <div v-if="currentStep === 1" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">邮箱地址</label>
            <input 
              v-model="email"
              type="email"
              placeholder="请输入邮箱地址"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">密码</label>
            <input 
              v-model="password"
              type="password"
              placeholder="请输入密码（至少8位）"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">确认密码</label>
            <input 
              v-model="confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">昵称</label>
            <input 
              v-model="nickname"
              type="text"
              placeholder="请输入昵称"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">安全问题（用于找回密码）</label>
            <input 
              v-model="securityQuestion"
              type="text"
              placeholder="请输入安全问题"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">安全问题答案</label>
            <input 
              v-model="securityAnswer"
              type="text"
              placeholder="请输入安全问题答案"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>
        </div>

        <div v-if="currentStep === 2" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">店铺名称</label>
            <input 
              v-model="shopName"
              type="text"
              placeholder="请输入店铺名称"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">经营类目</label>
            <select 
              v-model="businessCategory"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all appearance-none bg-white cursor-pointer"
            >
              <option value="">请选择经营类目</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
          </div>
        </div>

        <div v-if="currentStep === 3" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">营业执照</label>
            <div 
              @click="triggerFileInput('license-input')"
              :class="[
                'border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer',
                businessLicense ? 'border-green-400 bg-green-50' : 'border-gray-300 hover:border-indigo-400'
              ]"
            >
              <Check v-if="businessLicense" class="w-12 h-12 text-green-500 mx-auto mb-4" />
              <Upload v-else class="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p :class="businessLicense ? 'text-green-600' : 'text-gray-500'" class="mb-2">
                {{ businessLicense ? '已上传: ' + businessLicense.name : '点击或拖拽上传营业执照' }}
              </p>
              <p class="text-sm text-gray-400">支持 JPG/PNG 格式，不超过 5MB</p>
              <input 
                id="license-input"
                type="file"
                accept="image/jpeg,image/png"
                class="hidden"
                @change="handleFileUpload('license', $event)"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">个人身份证照片</label>
            <div 
              @click="triggerFileInput('idcard-input')"
              :class="[
                'border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer',
                idCard ? 'border-green-400 bg-green-50' : 'border-gray-300 hover:border-indigo-400'
              ]"
            >
              <Check v-if="idCard" class="w-12 h-12 text-green-500 mx-auto mb-4" />
              <Upload v-else class="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p :class="idCard ? 'text-green-600' : 'text-gray-500'" class="mb-2">
                {{ idCard ? '已上传: ' + idCard.name : '点击或拖拽上传身份证正反面照片' }}
              </p>
              <p class="text-sm text-gray-400">支持 JPG/PNG 格式，不超过 5MB</p>
              <input 
                id="idcard-input"
                type="file"
                accept="image/jpeg,image/png"
                class="hidden"
                @change="handleFileUpload('idcard', $event)"
              />
            </div>
          </div>
        </div>

        <div v-if="currentStep === 4" class="text-center py-12">
          <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Check class="w-10 h-10 text-green-600" />
          </div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2">提交成功</h2>
          <p class="text-gray-500 mb-6">您的开店申请已提交，平台正在审核中</p>
          <p class="text-sm text-gray-400">审核结果将通过短信通知您，请保持手机畅通</p>
        </div>

        <div v-if="currentStep < 4" class="flex gap-4 mt-8">
          <button 
            v-if="currentStep > 1"
            @click="prevStep"
            class="flex-1 py-3 border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors"
          >
            上一步
          </button>
          <button 
            @click="nextStep"
            :disabled="isSubmitting"
            class="flex-1 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="isSubmitting" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isSubmitting ? '提交中...' : (currentStep === 3 ? '提交申请' : '下一步') }}
            <ChevronRight v-if="!isSubmitting" class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>