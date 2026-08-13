<script setup lang="ts">
import { onMounted } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import { useDashboardStore } from '@/stores/dashboard'

const store = useDashboardStore()

onMounted(() => {
  void store.refreshAll()
})
</script>

<template>
  <div class="flex min-h-screen">
    <AppSidebar />
    <main class="min-w-0 flex-1 overflow-auto p-6 md:p-8">
      <RouterView />
    </main>
  </div>
</template>
