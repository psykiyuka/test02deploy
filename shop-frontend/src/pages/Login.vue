<script setup lang="ts">
import { ref, computed } from 'vue';
import { Eye, EyeOff, ShoppingBag, X } from 'lucide-vue-next';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import { api } from '@/utils/api';

const authStore = useAuthStore();
const router = useRouter();

const isLogin = ref(true);
const showPassword = ref(false);
const rememberMe = ref(false);
const showError = ref(false);
const errorMessage = ref('');
const isLoading = ref(false);
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const nickname = ref('');
const securityQuestion = ref('我最喜欢的食物');
const securityAnswer = ref('');
const isFormValid = computed(() => {
  if (isLogin.value) {
    return email.value && password.value;
  }
  return email.value && password.value && confirmPassword.value && nickname.value && securityAnswer.value && password.value === confirmPassword.value;
});

async function handleSubmit() {
  if (!isFormValid.value) return;
  isLoading.value = true;
  showError.value = false;
  try {
    if (isLogin.value) {
      const res = await authStore.login(email.value, password.value);
      if (res.code === 0) {
        const role = res.data.user.role;
        if (role === 'admin') {
          router.push('/admin');
        } else if (role === 'merchant') {
          router.push('/merchant');
        } else {
          router.push('/');
        }
      } else {
        errorMessage.value = res.message || '邮箱或密码错误';
        showError.value = true;
      }
    } else {
      const res = await authStore.register(email.value, password.value, nickname.value, securityQuestion.value, securityAnswer.value);
      if (res.code === 0) {
        alert('注册成功，请登录');
        isLogin.value = true;
      } else {
        errorMessage.value = res.message || '注册失败';
        showError.value = true;
      }
    }
  } catch (err: any) {
    errorMessage.value = err.message || '网络错误';
    showError.value = true;
  } finally {
    isLoading.value = false;
  }
}

// ── 忘记密码（安全问题） ──
const showForgot = ref(false);
const forgotStep = ref(1); // 1=输入邮箱, 2=回答问题, 3=设新密码, 4=成功
const forgotEmail = ref('');
const forgotQuestion = ref('');
const forgotAnswer = ref('');
const forgotPassword = ref('');
const forgotConfirm = ref('');
const forgotError = ref('');
const forgotLoading = ref(false);

function openForgot() {
  showForgot.value = true;
  forgotStep.value = 1;
  forgotEmail.value = '';
  forgotQuestion.value = '';
  forgotAnswer.value = '';
  forgotPassword.value = '';
  forgotConfirm.value = '';
  forgotError.value = '';
}

function closeForgot() {
  showForgot.value = false;
}

async function fetchQuestion() {
  if (!forgotEmail.value || !forgotEmail.value.includes('@')) {
    forgotError.value = '请输入正确的邮箱';
    return;
  }
  forgotLoading.value = true;
  forgotError.value = '';
  try {
    const res = await api.post<any>('/c-endpoint/user/forgot-password/question', { email: forgotEmail.value });
    if (res.code === 0) {
      forgotQuestion.value = res.data.question;
      forgotStep.value = 2;
    } else {
      forgotError.value = res.message || '查询失败';
    }
  } catch (err: any) {
    forgotError.value = err.message || '网络错误';
  } finally {
    forgotLoading.value = false;
  }
}

async function verifyAnswer() {
  if (!forgotAnswer.value) {
    forgotError.value = '请输入安全问题答案';
    return;
  }
  forgotLoading.value = true;
  forgotError.value = '';
  try {
    const res = await api.post<any>('/c-endpoint/user/forgot-password/verify', {
      email: forgotEmail.value,
      answer: forgotAnswer.value,
    });
    if (res.code === 0) {
      forgotStep.value = 3;
    }
  } catch (err: any) {
    forgotError.value = err.message || '答案不正确';
  } finally {
    forgotLoading.value = false;
  }
}

async function resetPassword() {
  if (!forgotPassword.value || forgotPassword.value.length < 8) {
    forgotError.value = '密码长度不能少于8位';
    return;
  }
  if (!/[A-Za-z]/.test(forgotPassword.value) || !/\d/.test(forgotPassword.value)) {
    forgotError.value = '密码必须包含字母和数字';
    return;
  }
  if (forgotPassword.value !== forgotConfirm.value) {
    forgotError.value = '两次密码不一致';
    return;
  }
  forgotLoading.value = true;
  forgotError.value = '';
  try {
    const res = await api.post<any>('/c-endpoint/user/forgot-password/reset', {
      email: forgotEmail.value,
      answer: forgotAnswer.value,
      new_password: forgotPassword.value,
    });
    if (res.code === 0) {
      forgotStep.value = 4;
    } else {
      forgotError.value = res.message || '重置失败';
    }
  } catch (err: any) {
    forgotError.value = err.message || '网络错误';
  } finally {
    forgotLoading.value = false;
  }
}

function forgotDone() {
  closeForgot();
  email.value = forgotEmail.value;
  password.value = '';
}
</script>

<template>
  <div class="min-h-screen flex">
    <!-- 左侧品牌区 -->
    <div class="hidden lg:flex lg:w-1/2 relative">
      <div class="absolute inset-0 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500"></div>
      <div class="absolute inset-0 bg-black/20"></div>
      <div class="relative z-10 flex flex-col justify-center px-16 text-white">
        <div class="flex items-center gap-3 mb-8">
          <div class="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
            <ShoppingBag class="w-6 h-6" />
          </div>
          <span class="text-2xl font-bold">优选商城</span>
        </div>
        <h1 class="text-4xl font-bold mb-4">发现品质生活</h1>
        <p class="text-lg opacity-90 mb-8">精选全球好物，为您的生活添彩</p>
        <div class="space-y-4">
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center text-lg">✓</div>
            <span>100%正品保障</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center text-lg">✓</div>
            <span>7天无理由退换</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center text-lg">✓</div>
            <span>顺丰包邮到家</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧表单区 -->
    <div class="flex-1 flex items-center justify-center p-4 md:p-8">
      <div class="w-full max-w-md">
        <div class="text-center mb-8">
          <div class="inline-flex items-center gap-3 mb-4">
            <div class="w-12 h-12 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center">
              <ShoppingBag class="w-6 h-6 text-white" />
            </div>
            <span class="text-2xl font-bold text-gray-900">优选商城</span>
          </div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2">
            {{ isLogin ? '欢迎回来' : '创建账户' }}
          </h2>
          <p class="text-gray-500">
            {{ isLogin ? '请登录您的账户' : '开启您的购物之旅' }}
          </p>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-5">
          <div v-if="showError" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{{ errorMessage }}</span>
          </div>

          <!-- 注册：昵称 -->
          <div v-if="!isLogin" class="space-y-5">
            <div>
              <input
                v-model="nickname"
                type="text"
                placeholder="昵称"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
              />
            </div>
            <!-- 安全问题 -->
            <div>
              <input
                v-model="securityQuestion"
                type="text"
                placeholder="安全问题（用于找回密码）"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
              />
            </div>
            <!-- 安全答案 -->
            <div>
              <input
                v-model="securityAnswer"
                type="text"
                placeholder="安全问题答案"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
              />
            </div>
          </div>

          <!-- 邮箱 -->
          <div>
            <input
              v-model="email"
              type="email"
              placeholder="电子邮箱"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
            />
          </div>

          <!-- 密码 -->
          <div class="relative">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="密码"
              class="w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <Eye v-if="showPassword" class="w-5 h-5" />
              <EyeOff v-else class="w-5 h-5" />
            </button>
          </div>

          <!-- 注册：确认密码 -->
          <div v-if="!isLogin" class="relative">
            <input
              v-model="confirmPassword"
              :type="showPassword ? 'text' : 'password'"
              placeholder="确认密码"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
            />
          </div>

          <!-- 登录：记住我 & 忘记密码 -->
          <div v-if="isLogin" class="flex items-center justify-between">
            <label class="flex items-center gap-2 cursor-pointer select-none group">
              <div class="relative w-4 h-4 flex-shrink-0">
                <input
                  v-model="rememberMe"
                  type="checkbox"
                  class="peer sr-only"
                />
                <div class="w-4 h-4 rounded border-2 border-gray-300 bg-white transition-colors group-hover:border-indigo-400 peer-checked:border-indigo-600 peer-checked:bg-indigo-600 flex items-center justify-center">
                  <svg v-if="rememberMe" class="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              <span class="text-sm text-gray-600 group-hover:text-gray-800 transition-colors">记住我</span>
            </label>
            <a href="#" @click.prevent="openForgot" class="text-sm text-indigo-600 hover:text-indigo-700 hover:underline">
              忘记密码？
            </a>
          </div>

          <!-- 提交按钮 -->
          <button
            type="submit"
            :disabled="!isFormValid || isLoading"
            :class="[
              'w-full py-3 rounded-xl font-semibold transition-all duration-300 relative overflow-hidden',
              (isFormValid && !isLoading)
                ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:shadow-lg hover:shadow-indigo-200 hover:scale-[1.02]'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            ]"
          >
            <span class="relative z-10 flex items-center justify-center gap-2">
              <svg v-if="isLoading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isLoading ? (isLogin ? '登录中...' : '注册中...') : (isLogin ? '登录' : '注册') }}
            </span>
          </button>
        </form>

        <!-- 切换登录/注册 -->
        <div class="mt-8 text-center">
          <span class="text-gray-600">
            {{ isLogin ? '还没有账户？' : '已有账户？' }}
          </span>
          <button
            @click="isLogin = !isLogin"
            class="ml-2 text-indigo-600 font-medium hover:text-indigo-700 hover:underline transition-colors"
          >
            {{ isLogin ? '立即注册' : '立即登录' }}
          </button>
        </div>

        <!-- 商家入驻入口 -->
        <div v-if="!isLogin" class="mt-6 text-center">
          <div class="relative my-4">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-200"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-4 bg-white text-gray-400">或</span>
            </div>
          </div>
          <p class="text-sm text-gray-500 mb-2">想要开设自己的店铺？</p>
          <router-link
            to="/merchant-register"
            class="inline-flex items-center gap-1.5 text-sm font-medium text-indigo-600 hover:text-indigo-700 hover:underline transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
            </svg>
            申请商家入驻
          </router-link>
        </div>
      </div>
    </div>

    <!-- 忘记密码弹窗 -->
    <Teleport to="body">
      <div v-if="showForgot" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="closeForgot"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">

          <!-- 关闭按钮 -->
          <button
            @click="closeForgot"
            class="absolute top-4 right-4 p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors z-10"
          >
            <X :size="18" />
          </button>

          <!-- 步骤 1: 输入邮箱 -->
          <div v-if="forgotStep === 1" class="p-8">
            <div class="text-center mb-6">
              <div class="w-14 h-14 bg-indigo-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg class="w-7 h-7 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.51-1.795 2.106-3 3.772-3 2.21 0 4 1.79 4 4 0 1.681-.753 3.182-1.937 4.2a1.48 1.48 0 01-2.126 0L8.228 9z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.51-1.795 2.106-3 3.772-3 2.21 0 4 1.79 4 4 0 .568-.118 1.109-.332 1.6" />
                </svg>
              </div>
              <h3 class="text-xl font-bold text-gray-900">忘记密码</h3>
              <p class="text-sm text-gray-500 mt-1">输入注册邮箱，回答问题验证身份</p>
            </div>

            <div v-if="forgotError" class="bg-red-50 border border-red-200 text-red-600 px-4 py-2.5 rounded-xl text-sm mb-4">
              {{ forgotError }}
            </div>

            <div class="mb-4">
              <input
                v-model="forgotEmail"
                type="email"
                placeholder="注册邮箱"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
              />
            </div>

            <button
              @click="fetchQuestion"
              :disabled="forgotLoading || !forgotEmail"
              :class="[
                'w-full py-3 rounded-xl font-semibold transition-all',
                forgotEmail && !forgotLoading
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:shadow-lg hover:shadow-indigo-200'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              ]"
            >
              {{ forgotLoading ? '查询中...' : '下一步' }}
            </button>
          </div>

          <!-- 步骤 2: 回答安全问题 -->
          <div v-else-if="forgotStep === 2" class="p-8">
            <div class="text-center mb-6">
              <div class="w-14 h-14 bg-amber-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg class="w-7 h-7 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.51-1.795 2.106-3 3.772-3 2.21 0 4 1.79 4 4 0 1.681-.753 3.182-1.937 4.2a1.48 1.48 0 01-2.126 0L8.228 9z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.51-1.795 2.106-3 3.772-3 2.21 0 4 1.79 4 4 0 .568-.118 1.109-.332 1.6" />
                </svg>
              </div>
              <h3 class="text-xl font-bold text-gray-900">验证身份</h3>
              <p class="text-sm text-gray-500 mt-1">{{ forgotQuestion }}</p>
            </div>

            <div v-if="forgotError" class="bg-red-50 border border-red-200 text-red-600 px-4 py-2.5 rounded-xl text-sm mb-4">
              {{ forgotError }}
            </div>

            <div class="mb-4">
              <input
                v-model="forgotAnswer"
                type="text"
                placeholder="请输入答案"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
              />
            </div>

            <button
              @click="verifyAnswer"
              :disabled="forgotLoading || !forgotAnswer"
              :class="[
                'w-full py-3 rounded-xl font-semibold transition-all',
                forgotAnswer && !forgotLoading
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:shadow-lg hover:shadow-indigo-200'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              ]"
            >
              {{ forgotLoading ? '验证中...' : '验证' }}
            </button>
          </div>

          <!-- 步骤 3: 设置新密码 -->
          <div v-else-if="forgotStep === 3" class="p-8">
            <div class="text-center mb-6">
              <div class="w-14 h-14 bg-emerald-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg class="w-7 h-7 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1112 21z" />
                </svg>
              </div>
              <h3 class="text-xl font-bold text-gray-900">设置新密码</h3>
              <p class="text-sm text-gray-500 mt-1">请输入新密码</p>
            </div>

            <div v-if="forgotError" class="bg-red-50 border border-red-200 text-red-600 px-4 py-2.5 rounded-xl text-sm mb-4">
              {{ forgotError }}
            </div>

            <div class="space-y-4">
              <div class="relative">
                <input
                  v-model="forgotPassword"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="新密码"
                  class="w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <Eye v-if="showPassword" class="w-5 h-5" />
                  <EyeOff v-else class="w-5 h-5" />
                </button>
              </div>

              <div>
                <input
                  v-model="forgotConfirm"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="确认新密码"
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
                />
              </div>

              <button
                @click="resetPassword"
                :disabled="forgotLoading"
                :class="[
                  'w-full py-3 rounded-xl font-semibold transition-all',
                  !forgotLoading
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:shadow-lg hover:shadow-indigo-200'
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                ]"
              >
                {{ forgotLoading ? '重置中...' : '确认重置' }}
              </button>
            </div>
          </div>

          <!-- 步骤 4: 成功 -->
          <div v-else-if="forgotStep === 4" class="p-8 text-center">
            <div class="w-16 h-16 bg-emerald-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-2">密码重置成功</h3>
            <p class="text-sm text-gray-500 mb-6">请使用新密码登录</p>
            <button
              @click="forgotDone"
              class="w-full py-3 rounded-xl font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:shadow-lg hover:shadow-indigo-200 transition-all"
            >
              去登录
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
