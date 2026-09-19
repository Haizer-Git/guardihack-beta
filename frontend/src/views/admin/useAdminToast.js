import { reactive } from 'vue'

export const toast = reactive({ show: false, message: '', type: 'success' })

export function showToast(msg, type = 'success') {
  Object.assign(toast, { show: true, message: msg, type })
  setTimeout(() => (toast.show = false), 3500)
}
