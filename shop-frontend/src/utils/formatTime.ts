/**
 * 时间格式化工具函数
 */

/**
 * 将 ISO 时间戳格式化为 "YYYY-MM-DD HH:mm"
 * @param t ISO 时间字符串或 Date 对象，如 "2026-06-30T10:24:15"
 * @returns 格式化后的字符串，如 "2026-06-30 10:24"；无效输入返回原值或 "--"
 */
export function formatTime(t: string | Date | null | undefined): string {
  if (!t) return '--'
  try {
    const d = typeof t === 'string' ? new Date(t) : t
    if (isNaN(d.getTime())) return typeof t === 'string' ? t : '--'
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    const hours = String(d.getHours()).padStart(2, '0')
    const mins = String(d.getMinutes()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${mins}`
  } catch {
    return typeof t === 'string' ? t : '--'
  }
}

/**
 * 将 ISO 时间戳格式化为 "YYYY-MM-DD HH:mm:ss"
 */
export function formatTimeFull(t: string | Date | null | undefined): string {
  if (!t) return '--'
  try {
    const d = typeof t === 'string' ? new Date(t) : t
    if (isNaN(d.getTime())) return typeof t === 'string' ? t : '--'
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    const hours = String(d.getHours()).padStart(2, '0')
    const mins = String(d.getMinutes()).padStart(2, '0')
    const secs = String(d.getSeconds()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${mins}:${secs}`
  } catch {
    return typeof t === 'string' ? t : '--'
  }
}
