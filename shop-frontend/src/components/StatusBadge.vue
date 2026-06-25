<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: string
}>()

const statusMap: Record<string, { label: string; classes: string }> = {
  pending: { label: '待支付', classes: 'bg-amber-50 text-amber-700 border border-amber-200' },
  paid: { label: '已支付', classes: 'bg-emerald-50 text-emerald-700 border border-emerald-200' },
  cancelled: { label: '已取消', classes: 'bg-rose-50 text-rose-500 border border-rose-200' },
  approved: { label: '已通过', classes: 'bg-sky-50 text-sky-700 border border-sky-200' },
  rejected: { label: '已拒绝', classes: 'bg-rose-50 text-rose-500 border border-rose-200' },
  completed: { label: '已完成', classes: 'bg-emerald-50 text-emerald-700 border border-emerald-200' },
  returned: { label: '退货中', classes: 'bg-amber-50 text-amber-700 border border-amber-200' },
  picked_up: { label: '已揽收', classes: 'bg-sky-50 text-sky-700 border border-sky-200' },
  in_transit: { label: '运输中', classes: 'bg-blue-50 text-blue-700 border border-blue-200' },
  out_for_delivery: { label: '派送中', classes: 'bg-indigo-50 text-indigo-700 border border-indigo-200' },
  delivered: { label: '已签收', classes: 'bg-emerald-50 text-emerald-700 border border-emerald-200' },
}

const badge = computed(() => {
  return statusMap[props.status] || { label: props.status, classes: 'bg-gray-50 text-gray-600 border border-gray-200' }
})
</script>

<template>
  <span
    class="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold"
    :class="badge.classes"
  >
    {{ badge.label }}
  </span>
</template>