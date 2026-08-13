<script setup lang="ts">
defineProps<{
  items: Array<{ label: string; value: string | number; hint?: string }>
}>()
</script>

<template>
  <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
    <div v-for="item in items" :key="item.label" class="panel px-4 py-3">
      <div class="text-xs text-[var(--muted)]">{{ item.label }}</div>
      <div class="mt-1 text-2xl font-semibold tracking-tight">{{ item.value }}</div>
      <div v-if="item.hint" class="mt-1 text-xs text-[var(--muted)]">{{ item.hint }}</div>
    </div>
  </div>
</template>
