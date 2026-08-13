export type TaskStatus = 'todo' | 'doing' | 'done'

export interface Idea {
  id: string
  title: string
  path: string
  tags: string[]
  all_tags?: string[]
  preview: string
  mtime: string
  source: string
}

export interface OutputItem {
  id: string
  title: string
  url: string
  note_path: string
  note_title: string
  kind: string
  mtime: string
}

export interface WeeklyNote {
  id: string
  name: string
  path: string
  planned: number
  completed: number
  execution_rate: number
  outputs_count: number
  outputs: OutputItem[]
}

export interface DashboardStats {
  ideas_count: number
  outputs_count: number
  weekly_notes: number
  tasks_planned: number
  tasks_completed: number
  execution_rate: number
  tag_distribution: Record<string, number>
  files_scanned: number
}

export interface ObsidianSummary {
  ok: boolean
  error?: string
  message?: string
  vault_path: string
  ideas: Idea[]
  outputs: OutputItem[]
  weekly: WeeklyNote[]
  stats: DashboardStats
  scanned_at: string
}

export interface Task {
  id: string
  title: string
  status: TaskStatus
  idea_path?: string | null
  idea_title?: string | null
  output_url?: string | null
  output_title?: string | null
  notes?: string | null
  created_at: string
  updated_at: string
}

export interface TasksPayload {
  ok: boolean
  tasks: Task[]
  columns: Record<TaskStatus, Task[]>
  count: number
}

export interface AppConfigPayload {
  ok: boolean
  config: {
    vault_path: string
    weekly_note_pattern: string
    inbox_tags: string[]
    window: { title: string; width: number; height: number }
  }
  vault_ready: boolean
  vault_resolved: string
}
