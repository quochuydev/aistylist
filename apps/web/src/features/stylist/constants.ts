export const KBS = [
  { id: 'catalog', name: 'Product catalog', access: 'private data' },
  { id: 'trends', name: 'Fashion trends', access: 'public data' },
  { id: 'orders', name: 'Order history', access: 'private data' },
  { id: 'reviews', name: 'Customer reviews', access: 'private data' },
]

export const MODEL = 'DeepSeek-V3, a FM for content creation and complex reasoning from DeepSeek.'
export const AGENTS = [
  {
    id: 'catalog',
    name: 'Product catalog agent',
    desc: 'You are designed to extract the relevant entities from the prompt and invoke the product catalog to generate relevant outfit descriptions.',
  },
  {
    id: 'image',
    name: 'Image generation agent',
    desc: 'You are designed to create a prompt using text and invoke the text to image model to generate an image.',
  },
  { id: 'inventory', name: 'Inventory management agent', desc: 'You are designed to help track and process inventory for the store.' },
  { id: 'weather', name: 'Weather API agent', desc: 'You are designed to help suggest items based on weather or event type.' },
]

export const DEFAULT_PROMPT =
  'I am a consultant traveling to New York next week. What kind of outfit should I wear on my first day in the office?'
