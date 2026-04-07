type Props = {
    scores: Record<string, number>
  }
  
  export default function Leaderboard({ scores }: Props) {
    const entries = Object.entries(scores)
  
    return (
      <div className="leaderboardCard">
        <div className="eyebrow">Leaderboard</div>
        <div className="leaderboardList">
          {entries.length === 0 ? (
            <div className="muted">No scores yet</div>
          ) : (
            entries.map(([name, score], i) => (
              <div key={name} className="leaderRow">
                <span>{i + 1}. {name}</span>
                <span>{score}</span>
              </div>
            ))
          )}
        </div>
      </div>
    )
  }