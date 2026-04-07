import { useEffect } from "react"
import confetti from "canvas-confetti"
import { motion } from "framer-motion"
import Leaderboard from "./Leaderboard"

type Props = {
  winners: string[]
  scores: Record<string, number>
  onBackToHome: () => void
}

export default function EndScreen({ winners, scores, onBackToHome }: Props) {
  useEffect(() => {
    // small confetti burst when game ends
    const duration = 1400
    const end = Date.now() + duration

    const fire = () => {
      confetti({
        particleCount: 6,
        startVelocity: 24,
        spread: 70,
        origin: { y: 0.2 }
      })

      if (Date.now() < end) {
        requestAnimationFrame(fire)
      }
    }

    fire()
  }, [])

  return (
    <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} className="gameLayout">
      <div className="panel">
        <div className="eyebrow">Game Over</div>
        <h2>{winners.length ? `Winner: ${winners.join(", ")}` : "Game finished"}</h2>
        <p className="subtext">You can go back and play again</p>

        <div className="endActions">
          {/* resets frontend to initial state */}
          <button className="primaryButton" onClick={onBackToHome}>
            Back to Home
          </button>
        </div>
      </div>

      <Leaderboard scores={scores} />
    </motion.div>
  )
}