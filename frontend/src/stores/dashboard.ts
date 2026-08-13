import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { bridge } from '@/api/bridge'
import type { AppConfigPayload, Idea, ObsidianSummary, Task, TaskStatus } from '@/types'

export const useDashboardStore = defineStore('dashboard', () => {
  const loading = ref(false)
  const bridgeReady = ref(false)
  const error = ref('')
  const config = ref<AppConfigPayload | null>(null)
  const summary = ref<ObsidianSummary | null>(null)
  const tasks = ref<Task[]>([])

  const stats = computed(() => summary.value?.stats)
  const ideas = computed(() => summary.value?.ideas ?? [])
  const outputs = computed(() => summary.value?.outputs ?? [])
  const weekly = computed(() => summary.value?.weekly ?? [])

  const columns = computed(() => ({
    todo: tasks.value.filter((t) => t.status === 'todo'),
    doing: tasks.value.filter((t) => t.status === 'doing'),
    done: tasks.value.filter((t) => t.status === 'done'),
  }))

  async function refreshAll() {
    loading.value = true
    error.value = ''
    try {
      const ping = await bridge.ping()
      bridgeReady.value = Boolean(ping?.ok)

      const [cfg, sum, taskPayload] = await Promise.all([
        bridge.getConfig(),
        bridge.getObsidianSummary(),
        bridge.getTasks(),
      ])

      config.value = cfg
      summary.value = sum
      tasks.value = taskPayload?.tasks ?? []

      if (sum && !sum.ok && sum.message) {
        error.value = sum.message
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
    } finally {
      loading.value = false
    }
  }

  async function setVaultPath(path: string) {
    await bridge.setVaultPath(path)
    await refreshAll()
  }

  async function moveTask(taskId: string, status: TaskStatus) {
    const res = await bridge.updateTaskStatus(taskId, status)
    if (res?.ok && res.task) {
      const idx = tasks.value.findIndex((t) => t.id === taskId)
      if (idx >= 0) tasks.value[idx] = res.task
      else tasks.value.unshift(res.task)
    }
  }

  async function promoteIdea(idea: Idea) {
    const res = await bridge.createTaskFromIdea(idea)
    if (res?.ok && res.task) {
      const exists = tasks.value.some((t) => t.id === res.task!.id)
      if (!exists) tasks.value.unshift(res.task)
    }
    return res
  }

  return {
    loading,
    bridgeReady,
    error,
    config,
    summary,
    tasks,
    stats,
    ideas,
    outputs,
    weekly,
    columns,
    refreshAll,
    setVaultPath,
    moveTask,
    promoteIdea,
  }
})
