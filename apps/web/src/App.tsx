import { useState } from 'react'
import { LooksView } from './features/looks/LooksView'
import { StylistFlow } from './features/stylist/StylistFlow'
import { useStylist } from './hooks/useStylist'

function App() {
  const stylist = useStylist()
  const [showLooks, setShowLooks] = useState(false)

  if (showLooks && stylist.result) return <LooksView {...stylist.result} onBack={() => setShowLooks(false)} />
  return <StylistFlow {...stylist} onViewLooks={() => setShowLooks(true)} />
}

export default App
