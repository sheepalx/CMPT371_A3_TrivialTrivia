import { useState } from "react"
import { motion } from "framer-motion"

type Props = {
  onJoin: (name: string) => void
  connected: boolean
}

export default function JoinScreen({ onJoin, connected }: Props) {
  const [name, setName] = useState("")

  return (
    <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} className="panel hero">
      <div className="eyebrow">TrivialTrivia</div>
      <h1>Minimal trivia, fast rounds, clean play</h1>
      <p className="subtext">Enter a name and join the game</p>

      <div className="joinRow">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter username"
          className="input"
        />
        <button onClick={() => onJoin(name)} className="primaryButton">
          Join
        </button>
      </div>

      <div className="statusLine">
        <span className={connected ? "dot live" : "dot"} />
        {connected ? "Connected" : "Connecting"}
      </div>
    </motion.div>
  )
}