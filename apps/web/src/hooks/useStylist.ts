import { useState } from 'react'
import type { Result, Status } from '../types'
import { streamStylist } from '../utils/api'

export function useStylist() {
  const [status, setStatus] = useState<Status>('idle')
  const [used, setUsed] = useState<Set<string>>(new Set())
  const [steps, setSteps] = useState<string[]>([])
  const [result, setResult] = useState<Result | null>(null)
  const [error, setError] = useState('')

  function generate(prompt: string) {
    if (status === 'running' || prompt.trim().length < 3) return
    setStatus('running')
    setUsed(new Set())
    setSteps([])
    setResult(null)
    setError('')

    let failed = false
    streamStylist(
      prompt.trim(),
      (msg) => {
        if (msg.type === 'step') {
          setUsed((u) => new Set([...u, `agent:${msg.agent}`, `kb:${msg.kb}`]))
          setSteps((s) => [...s, msg.label])
        } else if (msg.type === 'looks') {
          setResult({ summary: msg.summary, looks: msg.looks })
        } else if (msg.type === 'error') {
          failed = true
          setError(msg.message)
        } else if (msg.type === 'done') {
          setStatus(failed ? 'error' : 'done')
        }
      },
      () => {
        setError('Lost connection to the stylist API.')
        setStatus('error')
      },
    )
  }

  return { status, used, steps, result, error, generate }
}
