import { api as request } from './api'

export interface FavoriteItem {
  favorite_id: number
  favorited_at: string
  id: number
  name: string
  price: number
  image_url: string
  stock: number
  category_id: number
  category_name: string
}

export interface FavoriteListResponse {
  items: FavoriteItem[]
  total: number
  page: number
  size: number
}

export const favoriteApi = {
  /** 添加收藏 */
  add(productId: number) {
    return request.post(`/c-endpoint/favorites/${productId}`)
  },

  /** 取消收藏 */
  remove(productId: number) {
    return request.delete(`/c-endpoint/favorites/${productId}`)
  },

  /** 获取收藏列表 */
  list(page = 1, size = 20) {
    return request.get(`/c-endpoint/favorites`, { params: { page, size } })
  },

  /** 检查是否已收藏 */
  check(productId: number) {
    return request.get(`/c-endpoint/favorites/check/${productId}`)
  },
}
