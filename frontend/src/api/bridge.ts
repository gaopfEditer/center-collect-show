import type { AppConfigPayload, Idea, ObsidianSummary, Task, TasksPayload, TaskStatus } from '@/types'

type ApiMethod =
  | 'ping'
  | 'get_config'
  | 'set_vault_path'
  | 'get_obsidian_summary'
  | 'get_tasks'
  | 'update_task_status'
  | 'create_task_from_idea'
  | 'link_task_output'
  | 'trigger_automation_script'
  | 'get_job_status'

declare global {
  interface Window {
    pywebview?: {
      api?: Record<string, (...args: unknown[]) => Promise<unknown>>
    }
  }
}

const mockTasks: Task[] = [
  {
    id: 'mock-1',
    title: '解析 Obsidian Inbox 灵感',
    status: 'doing',
    idea_path: 'demo/inbox-parser.md',
    idea_title: '解析 Obsidian Inbox 灵感',
    notes: '浏览器 Mock（未连接 pywebview）',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'mock-2',
    title: '搭建效能看板',
    status: 'todo',
    idea_path: 'demo/kanban.md',
    idea_title: '搭建效能看板',
    notes: 'Vue 3 Kanban',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'mock-3',
    title: '输出周复盘指标',
    status: 'done',
    idea_path: 'demo/weekly.md',
    idea_title: '输出周复盘指标',
    output_url: 'https://github.com/example/center-collect-show',
    output_title: 'Repo',
    notes: 'execution rate / outputs',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

function mockSummary(): ObsidianSummary {
  return {
    ok: false,
    error: 'browser_mock',
    message: '当前为浏览器开发模式，请通过 pywebview 启动以读取 Vault',
    vault_path: '',
    ideas: [
      {
        id: 'demo/idea-1.md',
        title: '用本地控制台串联灵感与输出',
        path: 'demo/idea-1.md',
        tags: ['inbox/tech'],
        preview: '把 Obsidian inbox 变成可执行看板……',
        mtime: new Date().toISOString(),
        source: 'mock',
      },
    ],
    outputs: [
      {
        id: 'demo:repo',
        title: 'center-collect-show',
        url: 'https://github.com/example/center-collect-show',
        note_path: 'demo/weekly.md',
        note_title: 'weekly',
        kind: 'repo',
        mtime: new Date().toISOString(),
      },
    ],
    weekly: [
      {
        id: 'Weekly-2026-33.md',
        name: 'Weekly-2026-33',
        path: 'Weekly-2026-33.md',
        planned: 10,
        completed: 6,
        execution_rate: 60,
        outputs_count: 1,
        outputs: [],
      },
    ],
    stats: {
      ideas_count: 1,
      outputs_count: 1,
      weekly_notes: 1,
      tasks_planned: 10,
      tasks_completed: 6,
      execution_rate: 60,
      tag_distribution: { 'inbox/tech': 1 },
      files_scanned: 0,
    },
    scanned_at: new Date().toISOString(),
  }
}

async function mockCall(method: ApiMethod, args: unknown[]): Promise<unknown> {
  switch (method) {
    case 'ping':
      return { ok: true, message: 'browser mock' }
    case 'get_config':
      return {
        ok: true,
        config: {
          vault_path: '',
          weekly_note_pattern: 'Weekly-*.md',
          inbox_tags: ['inbox/demand', 'inbox/traffic', 'inbox/tech', 'inbox/resources'],
          window: { title: 'Engineer Control Panel', width: 1440, height: 900 },
        },
        vault_ready: false,
        vault_resolved: '',
      } satisfies AppConfigPayload
    case 'set_vault_path':
      return { ok: false, message: '浏览器模式无法写配置，请用桌面端' }
    case 'get_obsidian_summary':
      return mockSummary()
    case 'get_tasks': {
      const columns = {
        todo: mockTasks.filter((t) => t.status === 'todo'),
        doing: mockTasks.filter((t) => t.status === 'doing'),
        done: mockTasks.filter((t) => t.status === 'done'),
      }
      return { ok: true, tasks: mockTasks, columns, count: mockTasks.length } satisfies TasksPayload
    }
    case 'update_task_status': {
      const [taskId, status] = args as [string, TaskStatus]
      const task = mockTasks.find((t) => t.id === taskId)
      if (!task) return { ok: false, error: 'not_found' }
      task.status = status
      task.updated_at = new Date().toISOString()
      return { ok: true, task }
    }
    case 'create_task_from_idea': {
      const idea = args[0] as Idea
      const task: Task = {
        id: `mock-${Date.now()}`,
        title: idea.title,
        status: 'todo',
        idea_path: idea.path,
        idea_title: idea.title,
        notes: idea.preview,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      mockTasks.unshift(task)
      return { ok: true, created: true, task }
    }
    case 'trigger_automation_script':
      return { ok: true, job_id: 'mock-job', status: 'started' }
    default:
      return { ok: false, error: 'unsupported_in_mock', method }
  }
}

export async function callApi<T = unknown>(method: ApiMethod, ...args: unknown[]): Promise<T | null> {
  if (window.pywebview?.api?.[method]) {
    return (await window.pywebview.api[method](...args)) as T
  }

  // pywebview injects API slightly after DOM ready
  await waitForPywebview(1200)
  if (window.pywebview?.api?.[method]) {
    return (await window.pywebview.api[method](...args)) as T
  }

  console.warn(`pywebview API not ready — using mock for ${method}`)
  return (await mockCall(method, args)) as T
}

function waitForPywebview(timeoutMs: number): Promise<void> {
  return new Promise((resolve) => {
    if (window.pywebview?.api) {
      resolve()
      return
    }
    const started = Date.now()
    const timer = window.setInterval(() => {
      if (window.pywebview?.api || Date.now() - started > timeoutMs) {
        window.clearInterval(timer)
        resolve()
      }
    }, 50)
  })
}

export const bridge = {
  ping: () => callApi<{ ok: boolean; message: string }>('ping'),
  getConfig: () => callApi<AppConfigPayload>('get_config'),
  setVaultPath: (path: string) => callApi('set_vault_path', path),
  getObsidianSummary: () => callApi<ObsidianSummary>('get_obsidian_summary'),
  getTasks: () => callApi<TasksPayload>('get_tasks'),
  updateTaskStatus: (taskId: string, status: TaskStatus) =>
    callApi<{ ok: boolean; task?: Task }>('update_task_status', taskId, status),
  createTaskFromIdea: (idea: Idea) =>
    callApi<{ ok: boolean; created?: boolean; task?: Task; message?: string }>(
      'create_task_from_idea',
      idea,
    ),
  triggerAutomation: (scriptName: string) =>
    callApi('trigger_automation_script', scriptName),
}
