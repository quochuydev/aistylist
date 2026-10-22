import { useState } from 'react'
import { Info } from '../../components/Info'
import type { useStylist } from '../../hooks/useStylist'
import { AGENTS, DEFAULT_PROMPT, KBS, MODEL } from './constants'

type Props = ReturnType<typeof useStylist> & { onViewLooks: () => void }

export function StylistFlow({ status, used, steps, result, error, generate, onViewLooks }: Props) {
  const [prompt, setPrompt] = useState(DEFAULT_PROMPT)

  function submit(e: React.FormEvent) {
    e.preventDefault()
    generate(prompt)
  }

  return (
    <>
      <header className="topbar">
        <span className="brand">AI Stylist</span>
        <a className="btn-outline" href="https://platform.deepseek.com" target="_blank" rel="noreferrer">
          Visit DeepSeek ↗
        </a>
      </header>

      <main className="page">
        <h1>Generating your looks</h1>
        <p className="lead">
          The AI Stylist uses an agent to interact with the customer. With a mix of customer prompts and the fashion
          trends and product catalog knowledge bases, the product catalog agent creates a prompt for its foundation
          model to generate outfits. The product catalog agent extracts information from the fashion trends knowledge
          base and sends this information to the image generation agent to generate images of the relevant outfits.
        </p>
        <a href="https://api-docs.deepseek.com" target="_blank" rel="noreferrer">
          Documentation ↗
        </a>

        <div className="view-row">
          <button className="btn-primary" disabled={!result} onClick={onViewLooks}>
            View your looks
          </button>
        </div>

        <div className="flow">
          <div className="col">
            <h2>
              Customer prompts <Info text="What the customer asks the stylist." />
            </h2>
            <form className="dashed" onSubmit={submit}>
              <textarea
                className="card prompt"
                aria-label="Customer prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={3}
                maxLength={1000}
              />
              <button className="btn-primary generate" disabled={status === 'running'}>
                {status === 'running' ? 'Generating…' : 'Generate looks'}
              </button>
            </form>

            <h2>
              Knowledge bases/APIs <Info text="Data sources the agents can query." />
            </h2>
            <ul className="dashed list">
              {KBS.map((kb) => (
                <li key={kb.id} className={`card kb ${used.has(`kb:${kb.id}`) ? 'active' : ''}`}>
                  <span>
                    <span aria-hidden>⛁</span> {kb.name}
                  </span>
                  <i>{kb.access}</i>
                </li>
              ))}
            </ul>
          </div>

          <div className="connector" aria-hidden>
            <span style={{ top: '18%' }}>→</span>
            <span style={{ top: '60%' }}>→</span>
            <span style={{ top: '76%' }}>←</span>
          </div>

          <div className="col">
            <h2>
              Agent(s) <Info text="Each agent runs on DeepSeek with its own tools." />
            </h2>
            <ul className="dashed list">
              {AGENTS.map((a) => (
                <li key={a.id} className={`card agent ${used.has(`agent:${a.id}`) ? 'active' : ''}`}>
                  <div>
                    <b>{a.name}</b>
                    <p>{a.desc}</p>
                  </div>
                  <div>
                    <b>Model details</b>
                    <p>{MODEL}</p>
                  </div>
                  <span className="badge" aria-hidden>
                    DS
                  </span>
                </li>
              ))}
            </ul>
          </div>

          <div className="connector" aria-hidden>
            <span style={{ top: '45%' }}>→</span>
          </div>

          <section className="result" aria-live="polite">
            {status === 'idle' && <p className="muted">Enter a prompt and generate looks.</p>}
            {status === 'running' && (
              <>
                <div className="spinner" />
                <p>Generating…</p>
                <ol className="steps">
                  {steps.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ol>
              </>
            )}
            {status === 'done' && (
              <>
                <span className="check">✓</span>
                <p>Content Generated</p>
              </>
            )}
            {status === 'error' && <p className="error">{error}</p>}
          </section>
        </div>

      </main>
    </>
  )
}
