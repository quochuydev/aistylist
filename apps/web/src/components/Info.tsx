export function Info({ text }: { text: string }) {
  return (
    <span className="info" title={text} aria-label={text}>
      i
    </span>
  )
}
