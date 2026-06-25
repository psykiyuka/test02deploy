<script setup lang="ts">
import { Eye, EyeOff } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  modelValue: string | number
  type?: string
  label?: string
  disabled?: boolean
  error?: boolean
}>(), {
  type: 'text',
  label: '',
  disabled: false,
  error: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const showPassword = ref(false)
</script>

<template>
  <div class="relative">
    <!-- 输入框 -->
    <input
      :type="type === 'password' ? (showPassword ? 'text' : 'password') : type"
      :value="String(modelValue ?? '')"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      :disabled="disabled"
      placeholder=" "
      class="peer w-full px-4 pt-5 pb-2 border rounded-xl focus:outline-none focus:ring-2 transition-all text-sm text-gray-900
             placeholder-transparent
             disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
      :class="[
        error
          ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
          : 'border-gray-200 focus:ring-indigo-500 focus:border-transparent hover:border-gray-300'
      ]"
    />

    <!-- 浮动标签：利用 peer:placeholder-shown 纯 CSS 控制 -->
    <label
      class="absolute left-4 text-gray-400 transition-all duration-200 pointer-events-none
             peer-placeholder-shown:top-1/2 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:text-sm
             peer-focus:top-1.5 peer-focus:text-xs peer-focus:text-indigo-600 peer-focus:font-medium
             peer-not-placeholder-shown:top-1.5 peer-not-placeholder-shown:text-xs peer-not-placeholder-shown:text-indigo-600 peer-not-placeholder-shown:font-medium"
    >
      {{ label }}
    </label>

    <!-- 密码显示/隐藏按钮 -->
    <button
      v-if="type === 'password'"
      type="button"
      @click="showPassword = !showPassword"
      class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors p-0.5"
      tabindex="-1"
    >
      <Eye v-if="showPassword" class="w-5 h-5" />
      <EyeOff v-else class="w-5 h-5" />
    </button>
  </div>
</template>
