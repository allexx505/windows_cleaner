# Cursor 配置说明（本项目）

## Rules 显示说明

Cursor 的 **User（全局）Rules** 不是从 `~/.cursor/rules/` 读取的，而是保存在 Cursor 设置里（本地数据库或云端）。因此放在用户目录下的 `~/.cursor/rules/` 里的文件**不会**出现在 Cursor Settings → Rules 的列表中。

本项目的 **Project Rules** 来自本目录下的 `rules/*.mdc`。当前包含：

- **通用（可复用到其他项目）**：`python-standards.mdc`、`vue-components.mdc`、`api-conventions.mdc`
- **项目专属**：`windows-cleaner-conventions.mdc`

在 Cursor 中打开本项目时，上述 4 条规则都会在 **Settings → Rules** 里显示（筛选「windows_cleaner」或「All」）。

## 在其他项目中复用通用 Rules

若希望在其他项目里也使用那 3 条通用规则，可以任选其一：

1. **复制文件**：将 `rules/python-standards.mdc`、`rules/vue-components.mdc`、`rules/api-conventions.mdc` 复制到新项目的 `.cursor/rules/` 下。
2. **在 Cursor 里添加为 User Rules**：打开 **Cursor Settings → Rules → + New**，选择 User Rule，把 3 条规则的内容分别粘贴进去保存，即可在所有项目中生效（不依赖项目内文件）。

## Commands / Skills / Agents

- **Commands**：全局的 5 个在 `~/.cursor/commands/`，Cursor 会读取并显示；本项目的 3 个在本目录 `commands/`。
- **Agents（Subagents）**：全局的 4 个在 `~/.cursor/agents/`，本项目的 1 个在本目录 `agents/`。
- **Skills**：本项目的 `windows-cleaner-iteration` 在本目录 `skills/`。
