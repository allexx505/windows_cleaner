<template>
  <div class="settings">
    <div class="card">
      <h2>常规</h2>
      <div class="form-group">
        <label>
          <input type="checkbox" v-model="config.start_with_windows" @change="save" />
          开机自启动
        </label>
      </div>
      <div class="form-group">
        <label>关闭主窗口时</label>
        <select v-model="config.on_close" @change="save">
          <option value="minimize_to_tray">最小化到托盘</option>
          <option value="quit">直接退出</option>
        </select>
      </div>
    </div>
    <div class="card">
      <h2>磁盘警戒阈值</h2>
      <p class="muted">当某盘剩余空间低于设定百分比时发送提醒（可添加多条，按盘符或全局）。</p>
      <div v-for="(t, i) in config.disk_thresholds" :key="i" class="form-row">
        <input v-model="t.drive_letter" placeholder="盘符留空=全部" class="short" />
        <input v-model.number="t.free_percent_alert_below" type="number" min="0" max="100" step="1" class="short" />
        <span>% 以下提醒</span>
        <button class="btn btn-secondary small" @click="removeThreshold(i)">删除</button>
      </div>
      <button class="btn btn-secondary" @click="addThreshold">添加阈值</button>
    </div>
    <div class="card">
      <h2>通知</h2>
      <div class="form-group">
        <label>
          <input type="checkbox" v-model="config.notification.use_windows_toast" @change="save" />
          Windows 通知栏
        </label>
      </div>
      <div class="form-group">
        <label>
          <input type="checkbox" v-model="config.notification.email_enabled" @change="save" />
          邮件通知
        </label>
      </div>
      <template v-if="config.notification.email_enabled">
        <div class="form-group">
          <label>SMTP 主机</label>
          <input v-model="config.notification.smtp_host" @blur="save" placeholder="smtp.example.com" />
        </div>
        <div class="form-group">
          <label>端口</label>
          <input v-model.number="config.notification.smtp_port" @blur="save" type="number" />
        </div>
        <div class="form-group">
          <label>用户名</label>
          <input v-model="config.notification.smtp_user" @blur="save" />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="config.notification.smtp_password" @blur="save" type="password" />
        </div>
        <div class="form-group">
          <label>接收通知邮箱</label>
          <input v-model="config.notification.notify_email_to" @blur="save" placeholder="you@example.com" />
        </div>
      </template>
      <button class="btn" @click="save">保存设置</button>
    </div>
    <p v-if="message" :class="messageOk ? 'ok' : 'error'">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getConfig, updateConfig } from '@/api/client'

const config = reactive({
  start_with_windows: false,
  on_close: 'minimize_to_tray',
  disk_thresholds: [],
  notification: {
    use_windows_toast: true,
    email_enabled: false,
    smtp_host: '',
    smtp_port: 465,
    smtp_user: '',
    smtp_password: '',
    notify_email_to: '',
  },
})
const message = ref('')
const messageOk = ref(true)

function addThreshold() {
  config.disk_thresholds.push({ drive_letter: '', free_percent_alert_below: 10 })
  save()
}
function removeThreshold(i) {
  config.disk_thresholds.splice(i, 1)
  save()
}

async function load() {
  try {
    const data = await getConfig()
    Object.assign(config, data)
    if (!config.disk_thresholds) config.disk_thresholds = []
    if (!config.notification) config.notification = { use_windows_toast: true, email_enabled: false, smtp_host: '', smtp_port: 465, smtp_user: '', smtp_password: '', notify_email_to: '' }
  } catch (e) {
    message.value = '加载配置失败'
    messageOk.value = false
  }
}

async function save() {
  message.value = ''
  try {
    await updateConfig({
      start_with_windows: config.start_with_windows,
      on_close: config.on_close,
      disk_thresholds: config.disk_thresholds,
      notification: config.notification,
    })
    message.value = '已保存'
    messageOk.value = true
  } catch (e) {
    message.value = '保存失败'
    messageOk.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.form-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
.form-row .short { width: 6rem; }
.small { padding: 0.25rem 0.5rem; font-size: 0.8rem; }
.muted { color: #718096; font-size: 0.875rem; margin-bottom: 0.75rem; }
.ok { color: #68d391; }
.error { color: #fc8181; }
</style>
