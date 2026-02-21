/**
 * API client for Windows Cleaner backend. Base URL is same origin when
 * served by FastAPI, or proxy in dev (Vite proxy /api -> 127.0.0.1:8765).
 */
import axios from 'axios'

const client = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

export async function getDiskDrives() {
  const { data } = await client.get('/api/disk/drives')
  return data
}

export async function getDiskUsage(drive) {
  const { data } = await client.get(`/api/disk/usage/${encodeURIComponent(drive)}`)
  return data
}

export async function getConfig() {
  const { data } = await client.get('/api/config')
  return data
}

export async function updateConfig(partial) {
  const { data } = await client.post('/api/config', partial)
  return data
}

export async function getLargeFiles(params = {}) {
  const { data } = await client.get('/api/scan/large-files', { params })
  return data
}

export async function rebuildIndex(drive) {
  const { data } = await client.post('/api/scan/rebuild-index', { drive })
  return data
}

export async function health() {
  const { data } = await client.get('/api/health')
  return data
}

export async function pickFolder(initialDir = '') {
  const { data } = await client.get('/api/pick-folder', { params: { initial_dir: initialDir } })
  return data.path || ''
}
