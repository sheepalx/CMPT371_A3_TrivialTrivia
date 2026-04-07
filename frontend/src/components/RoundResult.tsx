import { motion } from "framer-motion"
import Leaderboard from "./Leaderboard"

type Props = {
  winner: string | null
  correct: string
  scores: Record<string, number>
}

export default function RoundResult({ winner, correct, scores }: Props) {
  return (
    <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} className="gameLayout">
      <div className="panel">
        <div className="eyebrow">Round Result</div>
        <h2>{winner ? `${winner} got it first` : "No winner this round"}</h2>
        <p className="subtext">Correct answer: {correct}</p>
      </div>

      <Leaderboard scores={scores} />
    </motion.div>
  )
}