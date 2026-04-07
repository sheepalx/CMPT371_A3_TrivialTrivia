import { useEffect, useMemo, useState } from "react"
import { GameSocket } from "../lib/socket"

type Scores = Record<string, number>
type Phase = "join" | "lobby" | "question" | "result" | "end"

export function useGameSocket() {
  // single websocket instance for the whole app
  const socket = useMemo(() => new GameSocket(), [])

  // core app state
  const [connected, setConnected] = useState(false)
  const [phase, setPhase] = useState<Phase>("join")
  const [info, setInfo] = useState("Enter a username to join")
  const [players, setPlayers] = useState<string[]>([])
  const [scores, setScores] = useState<Scores>({})
  const [canStart, setCanStart] = useState(false)

  // question state
  const [questionId, setQuestionId] = useState<number | null>(null)
  const [questionText, setQuestionText] = useState("")
  const [options, setOptions] = useState<string[]>([])

  // result state
  const [correct, setCorrect] = useState("")
  const [winner, setWinner] = useState<string | null>(null)
  const [winners, setWinners] = useState<string[]>([])

  // local UI helpers
  const [hasJoined, setHasJoined] = useState(false)
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const [username, setUsername] = useState("")

  useEffect(() => {
    // connect once on mount
    socket.connect(
      handleMessage,
      () => {
        setConnected(false)
        setInfo("Disconnected")
      },
      () => {
        setConnected(true)
      }
    )

    return () => socket.disconnect()
  }, [socket])

  // handles all incoming server messages
  const handleMessage = (msg: any) => {
    if (msg.type === "bridge_connected") return

    if (msg.type === "bridge_tcp_closed") {
      setConnected(false)
      setInfo("Server connection closed")
      return
    }

    if (msg.type === "welcome") {
      setHasJoined(true)
      setUsername(msg.username || "")
      setPhase("lobby")
      setInfo(`Joined as ${msg.username}`)
      return
    }

    if (msg.type === "leaderboard") {
      setScores(msg.scores || {})
      return
    }

    if (msg.type === "lobby_update") {
      setPlayers(msg.players || [])
      setCanStart(Boolean(msg.can_start))

      // if game already started, push user into question phase
      if (msg.started) {
        if (questionId == null) setPhase("question")
      } else {
        setPhase("lobby")
      }

      return
    }

    if (msg.type === "info") {
      const text = msg.message || ""
      setInfo(text)

      if (text.toLowerCase().includes("match in progress")) {
        setPhase("question")
      }

      return
    }

    if (msg.type === "game_started") {
      setPhase("question")
      setInfo("Game started")
      return
    }

    if (msg.type === "question") {
      // reset answer state each new question
      setQuestionId(msg.question_id)
      setQuestionText(msg.text || "")
      setOptions(msg.options || [])
      setSelectedAnswer(null)
      setPhase("question")
      setInfo("Choose an answer")
      return
    }

    if (msg.type === "round_result") {
      setWinner(msg.winner ?? null)
      setCorrect(msg.correct || "")
      setScores(msg.scores || {})
      setQuestionId(null)
      setSelectedAnswer(null)
      setPhase("result")
      return
    }

    if (msg.type === "game_over") {
      setScores(msg.scores || {})
      setWinners(msg.winners || [])
      setQuestionId(null)
      setSelectedAnswer(null)
      setPhase("end")
      setInfo("Game finished")
      return
    }

    if (msg.type === "error") {
      setInfo(msg.message || "Something went wrong")
    }
  }

  // sends username to backend
  const join = (name: string) => {
    const cleaned = name.trim()
    if (!cleaned || hasJoined) return
    socket.send({ type: "connect_tcp", username: cleaned })
  }

  const startGame = () => {
    socket.send({ type: "start_game" })
  }

  // sends answer + updates UI instantly
  const answer = (value: string) => {
    if (questionId == null) return
    setSelectedAnswer(value)
    socket.send({ type: "answer", question_id: questionId, value })
  }

  // resets frontend state only (not backend yet)
  const backToHome = () => {
    socket.disconnect()

    setConnected(false)
    setPhase("join")
    setInfo("Enter a username to join")
    setPlayers([])
    setScores({})
    setCanStart(false)
    setQuestionId(null)
    setQuestionText("")
    setOptions([])
    setCorrect("")
    setWinner(null)
    setWinners([])
    setHasJoined(false)
    setSelectedAnswer(null)
    setUsername("")

    // reconnect fresh socket
    setTimeout(() => {
      socket.connect(handleMessage, () => {}, () => setConnected(true))
    }, 150)
  }

  return {
    connected,
    phase,
    info,
    players,
    scores,
    canStart,
    questionText,
    options,
    correct,
    winner,
    winners,
    selectedAnswer,
    username,
    join,
    startGame,
    answer,
    backToHome
  }
}