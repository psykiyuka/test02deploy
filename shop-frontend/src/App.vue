<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AIChatWidget from '@/components/AIChatWidget.vue'

const auth = useAuthStore()

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
</template>
