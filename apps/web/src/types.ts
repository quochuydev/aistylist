export type Product = { id: string; name: string; category: string; price: number }
export type Look = { name: string; description: string; products: Product[]; image_prompt?: string; image?: string | null }
export type Result = { summary: string; looks: Look[] }
export type Msg = { from: 'stylist' | 'customer'; text: string }
export type Status = 'idle' | 'running' | 'done' | 'error'
