import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/inbox' },
    {
      path: '/inbox',
      name: 'inbox',
      component: () => import('@/views/InboxView.vue'),
      meta: { title: '灵感 Inbox' },
    },
    {
      path: '/kanban',
      name: 'kanban',
      component: () => import('@/views/KanbanView.vue'),
      meta: { title: '任务看板' },
    },
    {
      path: '/outputs',
      name: 'outputs',
      component: () => import('@/views/OutputsView.vue'),
      meta: { title: '输出追溯' },
    },
    {
      path: '/weekly',
      name: 'weekly',
      component: () => import('@/views/WeeklyReviewView.vue'),
      meta: { title: '周复盘' },
    },
  ],
})

export default router
