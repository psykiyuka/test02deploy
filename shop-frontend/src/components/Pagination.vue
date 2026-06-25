<script setup lang="ts">
import { computed } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

const props = defineProps<{
  current?: number
  currentPage?: number
  total?: number
  totalPages?: number
  pageSize?: number
}>()

const emit = defineEmits<{
  change: [page: number]
  pageChange: [page: number]
}>()

const currentPageNum = computed(() => props.current ?? props.currentPage ?? 1)
const totalPagesNum = computed(() => {
  if (props.totalPages) return props.totalPages
  return Math.ceil((props.total ?? 0) / (props.pageSize ?? 10))
})

const visible = computed(() => totalPagesNum.value > 1)

const pages = computed(() => {
  const result: (number | '...')[] = []
  const tp = totalPagesNum.value
  const cur = currentPageNum.value

  if (tp <= 7) {
    for (let i = 1; i <= tp; i++) result.push(i)
    return result
  }

  result.push(1)
  if (cur > 3) result.push('...')

  const start = Math.max(2, cur - 1)
  const end = Math.min(tp - 1, cur + 1)

  for (let i = start; i <= end; i++) {
    if (!result.includes(i)) result.push(i)
  }

  if (cur < tp - 2) result.push('...')
  if (!result.includes(tp)) result.push(tp)

  return result
})

function goTo(page: number) {
  if (page < 1 || page > totalPagesNum.value || page === currentPageNum.value) return
  emit('change', page)
  emit('pageChange', page)
}
</script>

<template>
  <div v-if="visible" class="flex items-center justify-center gap-1">
    <button
      class="w-10 h-10 flex items-center justify-center rounded-xl transition-all disabled:opacity-30 disabled:cursor-not-allowed text-charcoal/50 hover:text-charcoal hover:bg-gold-50 cursor-pointer"
      :disabled="currentPageNum <= 1"
      @click="goTo(currentPageNum - 1)"
    >
      <ChevronLeft class="w-4 h-4" />
    </button>

    <template v-for="page in pages" :key="page">
      <span
        v-if="page === '...'"
        class="w-10 h-10 flex items-center justify-center text-sm text-charcoal/25"
      >...</span>
      <button
        v-else
        class="w-10 h-10 rounded-xl text-sm font-medium transition-all cursor-pointer"
        :class="page === currentPageNum
          ? 'bg-gradient-to-r from-gold-400 to-gold-500 text-white shadow-lg shadow-gold-300/20'
          : 'text-charcoal/50 hover:text-charcoal hover:bg-gold-50'"
        @click="goTo(page)"
      >
        {{ page }}
      </button>
    </template>

    <button
      class="w-10 h-10 flex items-center justify-center rounded-xl transition-all disabled:opacity-30 disabled:cursor-not-allowed text-charcoal/50 hover:text-charcoal hover:bg-gold-50 cursor-pointer"
      :disabled="currentPageNum >= totalPagesNum"
      @click="goTo(currentPageNum + 1)"
    >
      <ChevronRight class="w-4 h-4" />
    </button>
  </div>
</template>