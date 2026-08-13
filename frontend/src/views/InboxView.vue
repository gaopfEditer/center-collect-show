<script setup lang="ts">
import { computed, ref } from 'vue'
import { Icon } from '@iconify/vue'
import { useDashboardStore } from '@/stores/dashboard'
import StatStrip from '@/components/StatStrip.vue'
import type { Idea } from '@/types'

const store = useDashboardStore()
const filter = ref('')
const toast = ref('')

const filtered = computed(() => {
  const q = filter.value.trim().toLowerCase()
  if (!q) return store.ideas
  return store.ideas.filter(
    (idea) =>
      idea.title.toLowerCase().includes(q) ||
      idea.tags.some((t) => t.toLowerCase().includes(q)) ||
      idea.path.toLowerCase().includes(q),
  )
})

const stats = computed(() => [
  { label: '灵感数', value: store.stats?.ideas_count ?? 0 },
  { label: '扫描文件', value: store.stats?.files_scanned ?? 0 },
  { label: '输出数', value: store.stats?.outputs_count ?? 0 },
  {
    label: 'Vault',
    value: store.config?.vault_ready ? '已就绪' : '未配置',
    hint: store.config?.vault_resolved || store.summary?.vault_path || '设置 config.json',
  },
])

async function promote(idea: Idea) {
  const res = await store.promoteIdea(idea)
  toast.value = res?.created === false ? res.message || '已存在任务' : '已转为任务 → 看板'
  window.setTimeout(() => {
    toast.value = ''
  }, 2200)
}
</script>

<template>
  <div class="space-y-5">
    <header class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 class="text-2xl font-semibold">灵感 Inbox</h1>
        <p class="mt-1 text-sm text-[var(--muted)]">
          从 Obsidian 提取 `#inbox/demand|traffic|tech|resources`
        </p>
      </div>
      <input
        v-model="filter"
        class="w-64 rounded-lg border border-[var(--border)] bg-[var(--panel)] px-3 py-2 text-sm outline-none focus:border-blue-400/50"
        placeholder="筛选标题 / tag / 路径"
      />
    </header>

    <StatStrip :items="stats" />

    <div
      v-if="store.error"
      class="panel border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-100"
    >
      {{ store.error }}
    </div>

    <div class="grid gap-3">
      <article
        v-for="idea in filtered"
        :key="idea.id"
        class="panel flex flex-col gap-3 px-4 py-4 md:flex-row md:items-start md:justify-between"
      >
        <div class="min-w-0 flex-1">
          <div class="flex flex-wrap items-center gap-2">
            <h2 class="truncate text-base font-medium">{{ idea.title }}</h2>
            <span
              v-for="tag in idea.tags"
              :key="tag"
              class="rounded-md bg-blue-500/15 px-2 py-0.5 text-xs text-blue-200"
            >
              #{{ tag }}
            </span>
          </div>
          <p class="mt-2 text-sm leading-relaxed text-[var(--muted)]">{{ idea.preview || '（无预览）' }}</p>
          <div class="mt-2 flex flex-wrap gap-3 text-xs text-[var(--muted)]">
            <span class="inline-flex items-center gap-1">
              <Icon icon="lucide:file-text" />
              {{ idea.path }}
            </span>
            <span class="inline-flex items-center gap-1">
              <Icon icon="lucide:clock-3" />
              {{ idea.mtime }}
            </span>
          </div>
        </div>
        <button
          class="inline-flex shrink-0 items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium hover:bg-blue-500"
          @click="promote(idea)"
        >
          <Icon icon="lucide:arrow-right-to-line" />
          转为任务
        </button>
      </article>

      <div v-if="!filtered.length" class="panel px-4 py-10 text-center text-sm text-[var(--muted)]">
        暂无灵感。配置 Vault 后刷新，或检查笔记是否带有 inbox tags。
      </div>
    </div>

    <div
      v-if="toast"
      class="fixed bottom-6 right-6 rounded-lg border border-emerald-400/30 bg-emerald-500/15 px-4 py-2 text-sm text-emerald-100"
    >
      {{ toast }}
    </div>
  </div>
</template>
