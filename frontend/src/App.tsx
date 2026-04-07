import JoinScreen from "./components/JoinScreen"
import LobbyScreen from "./components/LobbyScreen"
import GameScreen from "./components/GameScreen"
import RoundResult from "./components/RoundResult"
import EndScreen from "./components/EndScreen"
import { useGameSocket } from "./hooks/useGameSocket"

export default function App() {
  // main state for the entire app comes from this hook
  const {
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
    join,
    startGame,
    answer,
    backToHome
  } = useGameSocket()

  return (
    <div className="appShell">
      {/* top navigation / status */}
      <div className="topBar">
        <div className="brand">TrivialTrivia</div>
        {/* dynamic message coming from backend */}
        <div className="topMeta">{info}</div>
      </div>

      <main className="mainWrap">
        {/* render different screens based on game phase */}
        
        {phase === "join" && (
          <JoinScreen onJoin={join} connected={connected} />
        )}

        {phase === "lobby" && (
          <LobbyScreen
            players={players}
            canStart={canStart}
            onStart={startGame}
            info={info}
          />
        )}

        {phase === "question" && (
          <GameScreen
            question={questionText}
            options={options}
            onAnswer={answer}
            scores={scores}
            info={info}
            selectedAnswer={selectedAnswer} // used to highlight selected option
          />
        )}

        {phase === "result" && (
          <RoundResult
            winner={winner}
            correct={correct}
            scores={scores}
          />
        )}

        {phase === "end" && (
          <EndScreen
            winners={winners}
            scores={scores}
            onBackToHome={backToHome} // resets frontend state
          />
        )}
      </main>
    </div>
  )
}