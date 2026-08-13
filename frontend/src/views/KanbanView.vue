<script setup lang="ts">
import { Icon } from '@iconify/vue'
import { useDashboardStore } from '@/stores/dashboard'
import type { TaskStatus } from '@/types'

const store = useDashboardStore()

const columns: Array<{ key: TaskStatus; title: string; hint: string }> = [
  { key: 'todo', title: 'Todo', hint: '待执行' },
  { key: 'doing', title: 'In Progress', hint: '进行中' },
  { key: 'done', title: 'Done / Deployed', hint: '已完成' },
]

async function onDrop(status: TaskStatus, event: DragEvent) {
  const taskId = event.dataTransfer?.getData('text/task-id')
  if (!taskId) return
  await store.moveTask(taskId, status)
}

function onDragStart(taskId: string, event: DragEvent) {
  event.dataTransfer?.setData('text/task-id', taskId)
  event.dataTransfer!.effectAllowed = 'move'
}
</script>

<template>
  <div class="space-y-5">
    <header>
      <h1 class="text-2xl font-semibold">任务看板</h1>
      <p class="mt-1 text-sm text-[var(--muted)]">拖拽卡片更新状态 · 灵感 → 任务可追溯</p>
    </header>

    <div class="grid gap-4 lg:grid-cols-3">
      <section
        v-for="col in columns"
        :key="col.key"
        class="panel flex min-h-[420px] flex-col p-3"
        @dragover.prevent
        @drop.prevent="onDrop(col.key, $event)"
      >
        <div class="mb-3 flex items-center justify-between px-1">
          <div>
            <div class="text-sm font-medium">{{ col.title }}</div>
            <div class="text-xs text-[var(--muted)]">{{ col.hint }}</div>
          </div>
          <span class="rounded-md bg-white/5 px-2 py-0.5 text-xs">
            {{ store.columns[col.key].length }}
          </span>
        </div>

        <div class="flex flex-1 flex-col gap-2">
          <article
            v-for="task in store.columns[col.key]"
            :key="task.id"
            draggable="true"
            class="cursor-grab rounded-xl border border-[var(--border)] bg-[var(--panel-2)] px-3 py-3 active:cursor-grabbing"
            @dragstart="onDragStart(task.id, $event)"
          >
            <h3 class="text-sm font-medium">{{ task.title }}</h3>
            <p v-if="task.notes" class="mt-1 line-clamp-2 text-xs text-[var(--muted)]">
              {{ task.notes }}
            </p>
            <div class="mt-2 space-y-1 text-[11px] text-[var(--muted)]">
              <div v-if="task.idea_path" class="inline-flex items-center gap-1">
                <Icon icon="lucide:lightbulb" />
                {{ task.idea_path }}
              </div>
              <div v-if="task.output_url" class="inline-flex items-center gap-1">
                <Icon icon="lucide:external-link" />
                <a :href="task.output_url" class="text-blue-300 hover:underline" target="_blank">
                  {{ task.output_title || task.output_url }}
                </a>
              </div>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>
