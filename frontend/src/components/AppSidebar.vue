<script setup lang="ts">
import { Icon } from '@iconify/vue'
import { useRoute, useRouter } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboard'

const route = useRoute()
const router = useRouter()
const store = useDashboardStore()

const nav = [
  { to: '/inbox', label: '灵感 Inbox', icon: 'lucide:lightbulb' },
  { to: '/kanban', label: '任务看板', icon: 'lucide:columns-3' },
  { to: '/outputs', label: '输出追溯', icon: 'lucide:link-2' },
  { to: '/weekly', label: '周复盘', icon: 'lucide:calendar-range' },
]
</script>

<template>
  <aside class="flex w-60 shrink-0 flex-col border-r border-[var(--border)] bg-[color-mix(in_oklab,var(--panel)_88%,black)] px-3 py-4">
    <div class="mb-6 px-2">
      <div class="text-xs tracking-[0.18em] text-[var(--muted)] uppercase">Control Panel</div>
      <div class="mt-1 text-lg font-semibold">工程师效能台</div>
      <div class="mt-2 flex items-center gap-2 text-xs text-[var(--muted)]">
        <span
          class="inline-block h-2 w-2 rounded-full"
          :class="store.bridgeReady ? 'bg-emerald-400' : 'bg-amber-400'"
        />
        {{ store.bridgeReady ? 'pywebview 已连接' : '浏览器 Mock' }}
      </div>
    </div>

    <nav class="flex flex-1 flex-col gap-1">
      <button
        v-for="item in nav"
        :key="item.to"
        class="flex items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm transition"
        :class="
          route.path === item.to
            ? 'bg-blue-500/15 text-blue-200'
            : 'text-[var(--muted)] hover:bg-white/5 hover:text-[var(--text)]'
        "
        @click="router.push(item.to)"
      >
        <Icon :icon="item.icon" class="text-base" />
        {{ item.label }}
      </button>
    </nav>

    <button
      class="mt-4 flex items-center justify-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--panel-2)] px-3 py-2 text-sm hover:border-blue-400/40"
      :disabled="store.loading"
      @click="store.refreshAll()"
    >
      <Icon icon="lucide:refresh-cw" :class="{ 'animate-spin': store.loading }" />
      刷新数据
    </button>
  </aside>
</template>
