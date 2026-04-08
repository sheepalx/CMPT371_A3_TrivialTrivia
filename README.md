# CMPT 371 Assignment 3 — TrivialTrivia

**Authors**
- Calvin Weng (301556001)
- Alex Jiang (301566792)

## Overview

TrivialTrivia is a real-time multiplayer trivia game. Players join a lobby, start a game, answer questions, and receive scores based on correctness.

**Architecture**
- **Backend**: Python TCP server (game logic + player state)
- **Bridge**: Node.js server (WebSocket ↔ TCP relay)
- **Frontend**: React (interactive UI)

## Video demo

`https://youtu.be/GDl-JiDYjak`

## Requirements

- Node.js 18+
- Python 3.10+
- npm (bundled with Node.js)

## Installation

### 1) Clone the repository

```bash
git clone https://github.com/sheepalx/CMPT371_A3_TrivialTrivia.git
cd CMPT371_A3_TrivialTrivia
```

### 2) Backend setup

No external Python libraries are required.

### 3) Bridge setup

```bash
cd bridge
npm install
```

Note: `node_modules` is not included in the repository. Running `npm install` will generate it automatically.

### 4) Frontend setup

```bash
cd ../frontend
npm install
```

## Running the application

You must run **three components** in **three separate terminals**.

### Terminal 1 — Backend (Python TCP server)

```bash
cd backend
python -m src.server
```

Expected output:

```text
Server listening on 127.0.0.1:5555
```

### Terminal 2 — Bridge (Node.js WebSocket server)

```bash
cd bridge
node server.js
```

Expected output:

```text
Bridge running on http://localhost:8080
```

### Terminal 3 — Frontend (React dev server)

```bash
cd frontend
npm run dev
```

Open the app in your browser:

`http://localhost:5173`

Add other concurrent players by reclicking on the link.

## How to use

1. Open the frontend in your browser.
2. Enter a username to join the game.
3. Add players to the lobby by reclicking on the link.
4. Start the game.
5. Answer questions by selecting options.
6. View round results and leaderboard updates.
7. At the end of the game, view the final winners.
8. Restart the game from the end screen.

## Notes

- This repository does not include `node_modules` or build/cache artifacts; install dependencies with `npm install`.
- All three components (**backend**, **bridge**, **frontend**) must be running at the same time for the game to function.

## Project structure

```text
backend/    Python TCP server and game logic
bridge/     Node.js bridge (WebSocket ↔ TCP)
frontend/   React frontend
README.md   Setup and run instructions
```
