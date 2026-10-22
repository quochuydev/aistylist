import { useState } from 'react'
import { useAsk } from '../../hooks/useAsk'
import type { Result } from '../../types'

export function LooksView({ summary, looks, onBack }: Result & { onBack: () => void }) {
  const { msgs, asking, ask } = useAsk(looks)
  const [question, setQuestion] = useState(looks[0] ? `What do people like about the ${looks[0].name.toLowerCase()} look?` : '')

  function submit(e: React.FormEvent) {
    e.preventDefault()
    ask(question)
    setQuestion('')
  }

  return (
    <div className="compare">
      <aside className="hero">
        <h1>Compare and edit your looks</h1>
        <p>
          The AI Stylist saves our customer time and effort by looking across the product catalog and fashion trends
          knowledge bases. Instead of suggesting a single item or a static outfit, the AI Stylist generates
          individualized looks across several catalog items within seconds.
        </p>
      </aside>

      <section className="chat">
        <button className="back" onClick={onBack} aria-label="Back to the agent flow">
          ←
        </button>

        <div className="msg">
          <span className="avatar" aria-hidden>
            ✦
          </span>
          <div>
            <b>AI Stylist</b>
            <p>{summary}</p>
          </div>
        </div>

        <div className="compare-row">
          <div className="look-grid">
            {looks.map((look) => (
              <article key={look.name} className="look">
                <h3>{look.name}</h3>
                {look.image ? (
                  <img className="look-img" src={look.image} alt={look.image_prompt ?? look.name} />
                ) : (
                  <div className="look-img placeholder">
                    <span className="muted">{look.image_prompt ?? 'No image'}</span>
                  </div>
                )}
                <p>{look.description}</p>
                <details>
                  <summary>{look.products.length} catalog items</summary>
                  <ul>
                    {look.products.map((p) => (
                      <li key={p.id}>
                        {p.name} <span className="muted">· {p.category} · ${p.price}</span>
                      </li>
                    ))}
                  </ul>
                </details>
              </article>
            ))}
          </div>
          <div className="callouts" aria-hidden>
            <span className="callout">Image generation from product catalog</span>
            <span className="callout">Text generation from fashion trends</span>
          </div>
        </div>

        {msgs.map((m, i) => (
          <div key={i} className={`msg ${m.from}`}>
            {m.from === 'stylist' && (
              <span className="avatar" aria-hidden>
                ✦
              </span>
            )}
            <div>
              <b>{m.from === 'stylist' ? 'AI Stylist' : 'You'}</b>
              <p>{m.text}</p>
            </div>
          </div>
        ))}
        {asking && <p className="muted">AI Stylist is thinking…</p>}

        <form className="ask" onSubmit={submit}>
          <label htmlFor="ask">Suggested prompt</label>
          <div className="ask-box">
            <input id="ask" value={question} onChange={(e) => setQuestion(e.target.value)} maxLength={1000} />
            <button className="btn-primary" disabled={asking || question.trim().length < 3}>
              Send
            </button>
          </div>
        </form>
      </section>
    </div>
  )
}
