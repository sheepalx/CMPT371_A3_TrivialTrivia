import { motion } from "framer-motion"
import Leaderboard from "./Leaderboard"

type Props = {
  question: string
  options: string[]
  onAnswer: (value: string) => void
  scores: Record<string, number>
  info: string
  selectedAnswer?: string | null
}

export default function GameScreen({
  question,
  options,
  onAnswer,
  scores,
  info,
  selectedAnswer
}: Props) {
  const letters = ["A", "B", "C", "D"]

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      className="gameLayout"
    >
      <div className="panel">
        <div className="eyebrow">Live Question</div>
        <h2>{question}</h2>
        <p className="subtext">{info}</p>

        <div className="answerGrid">
          {options.map((opt, i) => {
            const letter = letters[i]
            const isSelected = selectedAnswer === letter

            return (
              <button
                key={letter}
                // adds visual feedback when user clicks
                className={`answerButton ${isSelected ? "answerButtonActive" : ""}`}
                onClick={() => onAnswer(letter)}
              >
                <span className="answerLetter">{letter}</span>
                <span>{opt}</span>
              </button>
            )
          })}
        </div>
      </div>

      <Leaderboard scores={scores} />
    </motion.div>
  )
}