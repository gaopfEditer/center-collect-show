<script setup lang="ts">
import { computed, ref } from 'vue'
import { Icon } from '@iconify/vue'
import { useDashboardStore } from '@/stores/dashboard'
import StatStrip from '@/components/StatStrip.vue'

const store = useDashboardStore()
const vaultInput = ref('')

const stats = computed(() => [
  {
    label: '执行率',
    value: `${store.stats?.execution_rate ?? 0}%`,
    hint: `${store.stats?.tasks_completed ?? 0}/${store.stats?.tasks_planned ?? 0} 完成`,
  },
  { label: '周记数', value: store.stats?.weekly_notes ?? 0 },
  { label: '灵感数', value: store.stats?.ideas_count ?? 0 },
  { label: '输出数', value: store.stats?.outputs_count ?? 0 },
])

const tagEntries = computed(() =>
  Object.entries(store.stats?.tag_distribution ?? {}).slice(0, 12),
)

async function saveVault() {
  if (!vaultInput.value.trim()) return
  await store.setVaultPath(vaultInput.value.trim())
}
</script>

<template>
  <div class="space-y-5">
    <header>
      <h1 class="text-2xl font-semibold">周复盘</h1>
      <p class="mt-1 text-sm text-[var(--muted)]">
        聚合 checklist 完成率、产出数量与 tag 分布
      </p>
    </header>

    <StatStrip :items="stats" />

    <section class="panel px-4 py-4">
      <h2 class="text-sm font-medium">Vault 路径</h2>
      <p class="mt-1 text-xs text-[var(--muted)]">
        当前：{{ store.config?.vault_resolved || store.summary?.vault_path || '未配置' }}
      </p>
      <div class="mt-3 flex flex-wrap gap-2">
        <input
          v-model="vaultInput"
          class="min-w-[280px] flex-1 rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm outline-none focus:border-blue-400/50"
          placeholder="~/Documents/Obsidian/MyVault"
        />
        <button
          class="rounded-lg bg-blue-600 px-3 py-2 text-sm hover:bg-blue-500"
          @click="saveVault"
        >
          保存并扫描
        </button>
      </div>
    </section>

    <section class="grid gap-4 lg:grid-cols-2">
      <div class="panel px-4 py-4">
        <h2 class="mb-3 text-sm font-medium">周记列表</h2>
        <div class="space-y-2">
          <article
            v-for="week in store.weekly"
            :key="week.id"
            class="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] px-3 py-3"
          >
            <div class="flex items-center justify-between gap-2">
              <div class="font-medium">{{ week.name }}</div>
              <div class="text-sm text-emerald-300">{{ week.execution_rate }}%</div>
            </div>
            <div class="mt-2 flex flex-wrap gap-3 text-xs text-[var(--muted)]">
              <span>完成 {{ week.completed }}/{{ week.planned }}</span>
              <span>输出 {{ week.outputs_count }}</span>
              <span class="inline-flex items-center gap-1">
                <Icon icon="lucide:file-text" />
                {{ week.path }}
              </span>
            </div>
            <div class="mt-2 h-1.5 overflow-hidden rounded-full bg-white/5">
              <div
                class="h-full rounded-full bg-emerald-400/80"
                :style="{ width: `${Math.min(week.execution_rate, 100)}%` }"
              />
            </div>
          </article>
          <div v-if="!store.weekly.length" class="py-8 text-center text-sm text-[var(--muted)]">
            未找到 `Weekly-*.md` 周记
          </div>
        </div>
      </div>

      <div class="panel px-4 py-4">
        <h2 class="mb-3 text-sm font-medium">Tag 分布（Top）</h2>
        <div class="space-y-2">
          <div
            v-for="[tag, count] in tagEntries"
            :key="tag"
            class="flex items-center justify-between rounded-lg bg-white/5 px-3 py-2 text-sm"
          >
            <span class="text-[var(--muted)]">#{{ tag }}</span>
            <span class="font-medium">{{ count }}</span>
          </div>
          <div v-if="!tagEntries.length" class="py-8 text-center text-sm text-[var(--muted)]">
            暂无 tag 统计
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
