<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useDashboardStore } from '@/stores/dashboard'
import StatStrip from '@/components/StatStrip.vue'

const store = useDashboardStore()

const stats = computed(() => [
  { label: '输出总数', value: store.outputs.length },
  {
    label: 'Demo',
    value: store.outputs.filter((o) => o.kind === 'demo').length,
  },
  {
    label: 'Repo',
    value: store.outputs.filter((o) => o.kind === 'repo').length,
  },
  {
    label: 'Tweet / 其他',
    value: store.outputs.filter((o) => o.kind === 'tweet' || o.kind === 'link').length,
  },
])

const kindIcon: Record<string, string> = {
  demo: 'lucide:monitor-play',
  repo: 'lucide:github',
  tweet: 'lucide:twitter',
  link: 'lucide:link',
}
</script>

<template>
  <div class="space-y-5">
    <header>
      <h1 class="text-2xl font-semibold">输出追溯</h1>
      <p class="mt-1 text-sm text-[var(--muted)]">
        Live Demo / Repo / Tweet — 回链到来源笔记
      </p>
    </header>

    <StatStrip :items="stats" />

    <div class="grid gap-3">
      <article
        v-for="item in store.outputs"
        :key="item.id"
        class="panel flex flex-col gap-3 px-4 py-4 md:flex-row md:items-center md:justify-between"
      >
        <div class="min-w-0">
          <div class="flex items-center gap-2">
            <Icon :icon="kindIcon[item.kind] || kindIcon.link" class="text-blue-300" />
            <span class="rounded-md bg-white/5 px-2 py-0.5 text-xs uppercase tracking-wide text-[var(--muted)]">
              {{ item.kind }}
            </span>
            <h2 class="truncate text-base font-medium">{{ item.title }}</h2>
          </div>
          <a
            :href="item.url"
            target="_blank"
            class="mt-2 block truncate text-sm text-blue-300 hover:underline"
          >
            {{ item.url }}
          </a>
          <div class="mt-2 flex flex-wrap gap-3 text-xs text-[var(--muted)]">
            <span class="inline-flex items-center gap-1">
              <Icon icon="lucide:file-text" />
              {{ item.note_path }}
            </span>
            <span class="inline-flex items-center gap-1">
              <Icon icon="lucide:clock-3" />
              {{ item.mtime }}
            </span>
          </div>
        </div>
      </article>

      <div v-if="!store.outputs.length" class="panel px-4 py-10 text-center text-sm text-[var(--muted)]">
        暂无输出链接。在周记或笔记中放入 Demo / GitHub / Tweet 链接即可被解析。
      </div>
    </div>
  </div>
</template>
