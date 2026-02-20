<template>
  <div class="overview">
    <div class="card">
      <h2>磁盘概览</h2>
      <p v-if="loading">加载中…</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <ul v-else class="drive-list">
        <li v-for="d in drives" :key="d.drive" class="drive-item">
          <span class="drive-name">{{ d.drive }}</span>
          <span class="drive-free">剩余 {{ d.free_percent.toFixed(1) }}%</span>
          <span class="drive-size">{{ formatBytes(d.free_bytes) }} 可用 / {{ formatBytes(d.total_bytes) }} 总量</span>
          <span v-if="d.usn_available" class="badge">USN</span>
        </li>
      </ul>
    </div>
    <div class="card">
      <h2>大文件扫描</h2>
      <p class="muted">重建索引后即可在此查看大文件。请先在「清理规则」或本页触发索引重建。</p>
      <button class="btn btn-secondary" :disabled="rebuilding" @click="doRebuildIndex">
        {{ rebuilding ? '重建中…' : '重建索引 (C:)' }}
      </button>
      <div v-if="largeFiles.items?.length" class="large-files">
        <h3>大文件 (≥500MB)</h3>
        <ul>
          <li v-for="f in largeFiles.items" :key="f.path" class="file-row">
            {{ f.path }} — {{ formatBytes(f.size_bytes) }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDiskDrives, getLargeFiles, rebuildIndex } from '@/api/client'

const loading = ref(true)
const error = ref('')
const drives = ref([])
const largeFiles = ref({ items: [] })
const rebuilding = ref(false)

function formatBytes(n) {
  if (n >= 1e9) return (n / 1e9).toFixed(2) + ' GB'
  if (n >= 1e6) return (n / 1e6).toFixed(2) + ' MB'
  if (n >= 1e3) return (n / 1e3).toFixed(2) + ' KB'
  return n + ' B'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    drives.value = await getDiskDrives()
    const res = await getLargeFiles({ min_size_mb: 500, limit: 20 })
    largeFiles.value = res
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function doRebuildIndex() {
  rebuilding.value = true
  try {
    await rebuildIndex('C:')
    await load()
  } catch (e) {
    error.value = e.message || '重建失败'
  } finally {
    rebuilding.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.drive-list { list-style: none; padding: 0; margin: 0; }
.drive-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #2d3748;
}
.drive-item:last-child { border-bottom: none; }
.drive-name { font-weight: 600; min-width: 2rem; }
.drive-free { color: #68d391; }
.drive-size { color: #a0aec0; font-size: 0.875rem; }
.badge { font-size: 0.7rem; background: #2b6cb0; padding: 0.2rem 0.4rem; border-radius: 4px; }
.error { color: #fc8181; }
.muted { color: #718096; font-size: 0.875rem; margin-bottom: 0.75rem; }
.large-files { margin-top: 1rem; }
.large-files h3 { font-size: 0.875rem; margin-bottom: 0.5rem; }
.file-row { font-size: 0.8rem; word-break: break-all; padding: 0.25rem 0; color: #a0aec0; }
</style>
