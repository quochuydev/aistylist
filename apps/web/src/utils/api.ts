import type { Look } from '../types'

export type StylistEvent =
  | { type: 'step'; agent: string | null; kb: string | null; label: string }
  | { type: 'looks'; summary: string; looks: Look[] }
  | { type: 'error'; message: string }
  | { type: 'done' }

/** Streams stylist events; returns a function that closes the stream. */
export function streamStylist(prompt: string, onEvent: (e: StylistEvent) => void, onLost: () => void) {
  const es = new EventSource(`/api/stylist?prompt=${encodeURIComponent(prompt)}`)
  es.onmessage = (ev) => {
    const msg: StylistEvent = JSON.parse(ev.data)
    if (msg.type === 'done') es.close()
    onEvent(msg)
  }
  es.onerror = () => {
    es.close()
    onLost()
  }
  return () => es.close()
}

export async function askStylist(question: string, looks: Look[]): Promise<string> {
  try {
    const r = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, looks }),
    })
    const data = await r.json()
    return data.answer ?? data.error ?? 'The stylist could not answer.'
  } catch {
    return 'Lost connection to the stylist API.'
  }
}
