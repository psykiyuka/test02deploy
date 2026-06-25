import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/utils/api'
import type { Category } from '@/types'

export const useCategoryStore = defineStore('category', () => {
  const categories = ref<Category[]>([])

  async function fetchCategories() {
    const res = await api.get<Category[]>('/c-endpoint/categories')
    if (res.code === 0) categories.value = res.data
  }

  return { categories, fetchCategories }
})