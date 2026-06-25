<script setup lang="ts">
import { RouterView } from 'vue-router'
import AdminSidebar from '@/components/AdminSidebar.vue'
</script>

<template>
  <div class="flex min-h-screen bg-soft-black">
    <AdminSidebar />
    <main class="flex-1 p-6 md:p-8 bg-slate-50 rounded-l-3xl overflow-y-auto">
      <RouterView />
    </main>
  </div>
</template>