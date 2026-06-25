export interface User {
  id: number
  email: string
  nickname: string
  role: 'user' | 'admin' | 'merchant'
  merchant_status?: 'pending' | 'approved' | 'rejected'
  address: string | null
  shop_name?: string
  avatar_url?: string | null
}

export interface Product {
  id: number
  name: string
  description: string
  price: number
  stock: number
  image_url: string
  category_id: number
  status: 'on_sale' | 'off_sale'
  created_at: string
  updated_at: string
  discount?: number
  sales?: number
  category_name?: string
  merchant_id?: number
  shop_name?: string
  approval_status?: string
}

export interface Category {
  id: number
  name: string
  parent_id: number | null
  sort_order: number
  children?: Category[]
}

export interface CartItem {
  product_id: number
  product_name: string
  price: number
  quantity: number
  image_url: string
  stock: number
  merchant_id?: number
  shop_name?: string
}

export interface OrderItem {
  product_name: string
  price: number
  quantity: number
}

export interface Order {
  id: number
  total_amount: number
  status: 'pending' | 'paid' | 'shipped' | 'delivered' | 'cancelled' | 'rejected'
  address: string
  created_at: string
  paid_at: string | null
  cancelled_at: string | null
  items: OrderItem[]
  merchant_id?: number
}

export interface LogisticsRecord {
  id: number
  order_id: number
  tracking_number: string
  carrier: string
  status: string
  estimated_delivery: string
  timeline: { time: string; status: string; description: string }[]
}

export interface AfterSaleRequest {
  id: number
  order_id: number
  user_id?: number
  merchant_id?: number
  type: string
  reason: string
  status: string
  return_tracking_number?: string | null
  return_carrier?: string | null
  return_status?: string | null
  resend_tracking_number?: string | null
  resend_carrier?: string | null
  approved_at?: string | null
  returned_at?: string | null
  received_at?: string | null
  completed_at?: string | null
  created_at: string
  updated_at: string
  buyer_name?: string
  buyer_email?: string
  seller_name?: string
  seller_shop_name?: string
}