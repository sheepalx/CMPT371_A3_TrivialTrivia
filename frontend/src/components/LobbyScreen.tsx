import { motion } from "framer-motion"

type Props = {
  players: string[]
  canStart: boolean
  onStart: () => void
  info: string
}

export default function LobbyScreen({ players, canStart, onStart, info }: Props) {
  return (
    <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} className="panel">
      <div className="sectionHeader">
        <div>
          <div className="eyebrow">Lobby</div>
          <h2>Waiting room</h2>
        </div>
        <button onClick={onStart} disabled={!canStart} className="primaryButton">
          Start Game
        </button>
      </div>

      <p className="subtext">{info}</p>

      <div className="pillGrid">
        {players.map((p) => (
          <div key={p} className="pill">{p}</div>
        ))}
      </div>
    </motion.div>
  )
}