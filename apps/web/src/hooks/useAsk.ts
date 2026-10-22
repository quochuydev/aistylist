import { useState } from 'react'
import type { Look, Msg } from '../types'
import { askStylist } from '../utils/api'

export function useAsk(looks: Look[]) {
  const [msgs, setMsgs] = useState<Msg[]>([])
  const [asking, setAsking] = useState(false)

  async function ask(question: string) {
    const q = question.trim()
    if (asking || q.length < 3) return
    setAsking(true)
    setMsgs((m) => [...m, { from: 'customer', text: q }])
    const text = await askStylist(q, looks)
    setMsgs((m) => [...m, { from: 'stylist', text }])
    setAsking(false)
  }

  return { msgs, asking, ask }
}
