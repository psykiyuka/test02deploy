<script setup lang="ts">
import { onMounted, ref, provide } from 'vue'
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AIChatWidget from '@/components/AIChatWidget.vue'
import Toast from '@/components/Toast.vue'
import { TOAST_KEY, type ToastAPI } from '@/composables/useToast'

const auth = useAuthStore()
const toastRef = ref<InstanceType<typeof Toast> | null>(null)

provide<ToastAPI>(TOAST_KEY, {
  show: (type, message, duration) => toastRef.value?.show(type, message, duration),
})

onMounted(async () => {
  if (auth.token && !auth.user) {
    try {
      await auth.fetchProfile()
    } catch (e) {
      console.error('Failed to fetch profile:', e)
    }
  }
})
</script>

<template>
  <RouterView />
  <AIChatWidget />
  <Toast ref="toastRef" />
</template>
