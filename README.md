# center-collect-show

个人工程师效能控制台：把 **灵感 → 任务 → 输出 → 周复盘** 串成可追溯看板。

技术栈：

- **桌面壳**：Python + pywebview（JS Bridge）
- **UI**：Vue 3 + Vite + TailwindCSS + Pinia
- **数据**：Obsidian Vault Markdown 解析 + SQLite 任务状态

## 快速开始

### 1. 配置 Vault

复制并编辑根目录 `config.json`：

```json
{
  "vault_path": "./sample_vault"
}
```

也可指向你的真实 Obsidian 库，例如 `~/Documents/Obsidian/MyVault`。

示例库已放在 `sample_vault/`（含 inbox 灵感与 `Weekly-2026-33.md`）。

### 2. 安装依赖

```bash
# Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 3. 开发模式（推荐）

终端 A：

```bash
cd frontend && npm run dev
```

终端 B：

```bash
source .venv/bin/activate
python backend/main.py --dev
```

### 4. 生产模式

```bash
cd frontend && npm run build
source .venv/bin/activate
python backend/main.py
```

仅预览 UI（无桌面壳，使用浏览器 Mock API）：

```bash
cd frontend && npm run dev
```

## Bridge API

| 方法 | 说明 |
|------|------|
| `get_obsidian_summary()` | 灵感 / 输出 / 周记指标 |
| `get_tasks()` / `update_task_status()` | 看板状态 |
| `create_task_from_idea()` | 灵感转任务 |
| `set_vault_path()` | 运行时更新 Vault 路径 |
| `trigger_automation_script()` | 后台跑 `scripts/` 下脚本 |

## 目录结构

```
backend/
  main.py                 # pywebview 入口
  api.py                  # JS Bridge
  config.py
  services/
    obsidian_service.py   # Vault 解析
    task_service.py       # SQLite 任务
frontend/                 # Vue 3 Dashboard
sample_vault/             # 示例 Obsidian 库
scripts/                  # 自动化脚本
config.json               # 本地配置
```

## Inbox 约定

笔记带有以下 tag 会被收入 Inbox：

- `#inbox/demand`
- `#inbox/traffic`
- `#inbox/tech`
- `#inbox/resources`

周记文件名默认匹配 `Weekly-*.md`，统计 `- [x]` / `- [ ]` 与输出链接。
