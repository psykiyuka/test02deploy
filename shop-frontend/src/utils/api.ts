const BASE = import.meta.env.VITE_API_BASE || '/api/shop'

export interface ApiResponse<T = any> {
  code: number
  data: T
  message: string
  detail?: any
}

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function request<T>(method: string, path: string, body?: any): Promise<ApiResponse<T>> {
  const headers: Record<string, string> = {}
  const token = localStorage.getItem('token')
  if (token) headers['Authorization'] = `Bearer ${token}`

  // FormData 不手动设置 Content-Type，让浏览器自动处理 multipart/form-data + boundary
  const isFormData = body instanceof FormData
  if (!isFormData) {
    headers['Content-Type'] = 'application/json'
  }

  let res: Response
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: isFormData ? body : body ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new ApiError('网络连接失败，请检查网络后重试', 0, -1)
  }

  // 尝试解析响应体
  let data: ApiResponse<T>
  try {
    data = await res.json()
  } catch {
    throw new ApiError(`请求失败 (${res.status})`, res.status, -1)
  }

  // 处理 422 错误：区分业务错误（BusinessError）和 FastAPI 参数验证错误
  if (res.status === 422) {
    // 后端 BusinessError：code=42201，message 包含具体业务错误信息
    if (data.code && data.code !== 0) {
      throw new ApiError(data.message || '操作失败', 422, data.code)
    }
    // FastAPI 原生参数验证错误：detail 为数组格式
    if (data.detail && Array.isArray(data.detail)) {
      const firstError = data.detail[0]
      const field = firstError.loc ? firstError.loc[firstError.loc.length - 1] : ''
      const message = firstError.msg || '验证失败'
      throw new ApiError(`${field ? field + ' ' : ''}${message}`, 422, -1)
    }
    throw new ApiError('请求参数验证失败', 422, -1)
  }

  // 业务错误（code != 0）不抛出异常，直接返回，让调用方处理
  if (data.code !== 0) {
    // 如果是 401 状态码且不是登录接口，说明是登录过期
    if (res.status === 401 && path !== '/c-endpoint/user/login') {
      const currentPath = window.location.pathname
      if (currentPath !== '/login') {
        localStorage.removeItem('token')
        localStorage.removeItem('role')
        window.location.href = '/login'
      }
    }
    return data
  }

  if (!res.ok) {
    throw new ApiError(`请求失败 (${res.status})`, res.status, -1)
  }

  return data
}

export const api = {
  get: <T>(path: string, config?: { params?: Record<string, any> }) => {
    let url = path
    if (config?.params) {
      const cleanParams: Record<string, string> = {}
      for (const [k, v] of Object.entries(config.params)) {
        if (v !== undefined && v !== null && v !== '') cleanParams[k] = String(v)
      }
      const qs = new URLSearchParams(cleanParams).toString()
      if (qs) url += '?' + qs
    }
    return request<T>('GET', url)
  },
  post: <T>(path: string, body?: any, config?: { params?: Record<string, any> }) => {
    let url = path
    if (config?.params) {
      const cleanParams: Record<string, string> = {}
      for (const [k, v] of Object.entries(config.params)) {
        if (v !== undefined && v !== null && v !== '') cleanParams[k] = String(v)
      }
      const qs = new URLSearchParams(cleanParams).toString()
      if (qs) url += '?' + qs
    }
    return request<T>('POST', url, body)
  },
  put: <T>(path: string, body?: any, config?: { params?: Record<string, any> }) => {
    let url = path
    if (config?.params) {
      const cleanParams: Record<string, string> = {}
      for (const [k, v] of Object.entries(config.params)) {
        if (v !== undefined && v !== null && v !== '') cleanParams[k] = String(v)
      }
      const qs = new URLSearchParams(cleanParams).toString()
      if (qs) url += '?' + qs
    }
    return request<T>('PUT', url, body)
  },
  delete: <T>(path: string, config?: { params?: Record<string, any> }) => {
    let url = path
    if (config?.params) {
      const cleanParams: Record<string, string> = {}
      for (const [k, v] of Object.entries(config.params)) {
        if (v !== undefined && v !== null && v !== '') cleanParams[k] = String(v)
      }
      const qs = new URLSearchParams(cleanParams).toString()
      if (qs) url += '?' + qs
    }
    return request<T>('DELETE', url)
  },
}
