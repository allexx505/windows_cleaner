<template>
  <div class="rules">
    <div class="card">
      <h2>清理规则</h2>
      <p class="muted">按路径、大小或扩展名定期扫描并提醒或自动清理。</p>
      <ul class="rule-list">
        <li v-for="r in config.cleanup_rules" :key="r.id" class="rule-item">
          <input type="checkbox" v-model="r.enabled" @change="save" />
          <span class="path">{{ r.target_path || '(未设置路径)' }}</span>
          <span class="type">{{ r.rule_type }} — {{ r.auto_clean ? '自动清理' : '仅提醒' }}</span>
          <button class="btn btn-secondary small" @click="removeRule(r.id)">删除</button>
        </li>
      </ul>
      <button class="btn" @click="showAdd = true">添加规则</button>
    </div>
    <div v-if="showAdd" class="card overlay">
      <h2>添加规则</h2>
      <div class="form-group">
        <label>目标路径</label>
        <div class="path-input">
          <input v-model="newRule.target_path" placeholder="例如 D:\Downloads" readonly />
          <button type="button" class="btn btn-secondary" @click="browsePath">选择文件夹</button>
        </div>
      </div>
      <div class="form-group">
        <label>类型</label>
        <select v-model="newRule.rule_type">
          <option value="large_file">大文件 (≥MB)</option>
          <option value="by_extension">按扩展名</option>
          <option value="junk">垃圾目录</option>
        </select>
      </div>
      <div class="form-group" v-if="newRule.rule_type === 'large_file'">
        <label>最小大小 (MB)</label>
        <input v-model.number="newRule.size_mb_min" type="number" min="0" />
      </div>
      <div class="form-group" v-if="newRule.rule_type === 'by_extension'">
        <label>扩展名 (逗号分隔)</label>
        <input v-model="newRule.extensionsStr" placeholder=".mp4, .avi, .mkv" />
      </div>
      <div class="form-group">
        <label>
          <input type="checkbox" v-model="newRule.auto_clean" />
          自动清理（否则仅提醒）
        </label>
      </div>
      <button class="btn" @click="addRule">添加</button>
      <button class="btn btn-secondary" @click="showAdd = false">取消</button>
    </div>
    <p v-if="msg" :class="msgOk ? 'ok' : 'error'">{{ msg }}</p>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getConfig, updateConfig, pickFolder } from '@/api/client'

const config = reactive({ cleanup_rules: [] })
const showAdd = ref(false)
const msg = ref('')
const msgOk = ref(true)
const newRule = reactive({
  target_path: '',
  rule_type: 'large_file',
  size_mb_min: 500,
  extensionsStr: '.mp4, .avi',
  auto_clean: false,
})

async function load() {
  try {
    const data = await getConfig()
    config.cleanup_rules = data.cleanup_rules || []
  } catch (e) {
    msg.value = '加载失败'
    msgOk.value = false
  }
}

async function browsePath() {
  try {
    const path = await pickFolder(newRule.target_path)
    if (path) {
      newRule.target_path = path
    }
  } catch (e) {
    msg.value = '选择文件夹失败'
    msgOk.value = false
  }
}

function addRule() {
  const id = 'r' + Date.now()
  const extensions = newRule.extensionsStr
    ? newRule.extensionsStr.split(',').map((e) => e.trim()).filter(Boolean)
    : ['.mp4', '.avi']
  config.cleanup_rules.push({
    id,
    enabled: true,
    target_path: newRule.target_path,
    rule_type: newRule.rule_type,
    size_mb_min: newRule.size_mb_min,
    extensions,
    cron_expr: '0 3 * * *',
    auto_clean: newRule.auto_clean,
  })
  showAdd.value = false
  newRule.target_path = ''
  save()
}

function removeRule(id) {
  config.cleanup_rules = config.cleanup_rules.filter((r) => r.id !== id)
  save()
}

async function save() {
  msg.value = ''
  try {
    await updateConfig({ cleanup_rules: config.cleanup_rules })
    msg.value = '已保存'
    msgOk.value = true
  } catch (e) {
    msg.value = '保存失败'
    msgOk.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.rule-list { list-style: none; padding: 0; margin: 0 0 1rem 0; }
.rule-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #2d3748;
}
.rule-item .path { flex: 1; word-break: break-all; font-size: 0.9rem; }
.rule-item .type { color: #a0aec0; font-size: 0.85rem; }
.small { padding: 0.25rem 0.5rem; font-size: 0.8rem; }
.muted { color: #718096; font-size: 0.875rem; margin-bottom: 0.75rem; }
.ok { color: #68d391; }
.error { color: #fc8181; }
.overlay { border: 1px solid #3182ce; }
.path-input { display: flex; gap: 0.5rem; align-items: center; }
.path-input input { flex: 1; }
</style>
