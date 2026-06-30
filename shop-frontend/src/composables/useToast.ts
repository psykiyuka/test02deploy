import { inject, type InjectionKey } from 'vue'

export interface ToastAPI {
  show: (type: 'success' | 'error' | 'warning' | 'info', message: string, duration?: number) => void
}

export const TOAST_KEY: InjectionKey<ToastAPI> = Symbol('toast')

export function useToast(): ToastAPI {
  const toast = inject(TOAST_KEY)
  if (!toast) throw new Error('useToast() must be used within a component that provides TOAST_KEY')
  return toast
}
