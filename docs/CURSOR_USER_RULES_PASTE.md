# 复制到 Cursor User Rules 的 3 条通用规则

在 **Cursor Settings → Rules → + New** 中选择 **User**，每次创建一条规则，将下面对应内容粘贴进内容框保存即可。规则名称可自定，或使用下方标题。

---

## 规则 1：Python Standards

**名称建议**：python-standards

**粘贴内容**：

```
# Python Standards

- Follow PEP 8 for style (naming, line length, imports). Use a formatter (e.g. Black, Ruff) where the project adopts one.
- Add docstrings for public modules, classes, and functions; keep them concise.
- Do not use bare `except:`; catch specific exceptions and log or re-raise. Prefer `logger.exception` or `logger.error` with traceback when handling errors.
- Avoid leaving commented-out code or debug print statements in committed code; use proper logging with levels instead.
```

---

## 规则 2：Vue 3 Conventions

**名称建议**：vue-components

**粘贴内容**：

```
# Vue 3 Conventions

- Prefer Composition API with `<script setup>` for new components.
- Use clear component names (PascalCase) and keep single-file components focused.
- Prefer Pinia for shared state; use provide/inject only for narrow, local concerns.
- Keep templates readable: extract complex expressions into computed properties or methods.
- Use kebab-case for custom events and props in templates when multi-word.
```

---

## 规则 3：API Conventions

**名称建议**：api-conventions

**粘贴内容**：

```
# API Conventions

- Use consistent route naming: nouns for resources, HTTP methods for actions (e.g. GET /api/users, POST /api/orders).
- Return structured JSON: success with consistent shape (e.g. `{"data": ...}` or direct array/object); errors with clear message and appropriate HTTP status (4xx/5xx).
- Validate request body with Pydantic models; return 422 with validation details when invalid.
- Prefer standard status codes: 200 (OK), 201 (Created), 400 (Bad Request), 404 (Not Found), 500 (Internal Server Error).
```

---

操作步骤简述：
1. 打开 Cursor → **Settings**（Ctrl+,）→ **Plugins** → **Rules, Skills, Subagents**。
2. 在 **Rules** 区域点击 **+ New**，选择 **User**（或“用户规则”）。
3. 名称填如 `python-standards`，内容粘贴上面对应规则全文，保存。
4. 重复 2–3，分别创建 `vue-components` 和 `api-conventions`。

保存后这 3 条会作为 User Rules 在所有项目中生效。
