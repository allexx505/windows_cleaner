<template>
  <div class="app">
    <header class="header">
      <h1>Windows 文件清理工具</h1>
      <nav>
        <router-link to="/">概览</router-link>
        <router-link to="/settings">设置</router-link>
        <router-link to="/rules">清理规则</router-link>
      </nav>
    </header>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style>
* { box-sizing: border-box; }
body { margin: 0; font-family: 'Segoe UI', system-ui, sans-serif; background: #1a1a2e; color: #eee; }
.app { min-height: 100vh; display: flex; flex-direction: column; }
.header {
  padding: 0.75rem 1.5rem;
  background: #16213e;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.header h1 { margin: 0; font-size: 1.25rem; font-weight: 600; }
.header nav { display: flex; gap: 1rem; }
.header a { color: #a0aec0; text-decoration: none; }
.header a.router-link-active { color: #63b3ed; }
.main { flex: 1; padding: 1.5rem; max-width: 900px; margin: 0 auto; width: 100%; }
.card {
  background: #16213e;
  border-radius: 8px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}
.card h2 { margin: 0 0 0.75rem 0; font-size: 1rem; color: #a0aec0; }
.btn {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: #3182ce;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
}
.btn:hover { background: #2b6cb0; }
.btn-secondary { background: #4a5568; }
.btn-secondary:hover { background: #2d3748; }
input, select, textarea {
  padding: 0.5rem;
  border: 1px solid #2d3748;
  border-radius: 6px;
  background: #1a1a2e;
  color: #eee;
  font-size: 0.875rem;
}
label { display: block; margin-bottom: 0.25rem; font-size: 0.875rem; color: #a0aec0; }
.form-group { margin-bottom: 1rem; }
</style>
