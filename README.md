# CMPT 371 Assignment 3 — TrivialTrivia

Calvin Weng (301556001) dyw7@sfu.ca

Alex Jiang (301566792) aja102@sfu.ca 

---

## Project Overview

TrivialTrivia is a real-time multiplayer trivia game. Players join a lobby, start a game, answer questions, and receive scores based on correctness.

The system uses:
- **Python TCP backend**: game logic + player state
- **Node.js bridge server**: WebSocket ↔ TCP relay between frontend and backend
- **React frontend**: interactive UI for players

---

## Video Demo

`https://youtu.be/GDl-JiDYjak`

---

## Project Structure

```text
backend/    Python TCP server and game logic
bridge/     Node.js bridge (WebSocket ↔ TCP)
frontend/   React frontend
README.md   Setup and run instructions
```

---

## System Requirements

Install the following before running the project:
- Node.js **18+**
- Python **3.10+**
- npm (bundled with Node.js)

---

## Installation Guide

### Step 1. Clone the repository

```bash
git clone https://github.com/sheepalx/CMPT371_A3_TrivialTrivia.git
cd CMPT371_A3_TrivialTrivia
```

### Step 2. Backend setup

No external Python libraries are required.

### Step 3. Bridge setup

```bash
cd bridge
npm install
```

Note: `node_modules` is not included in the repository. Running `npm install` will generate it automatically.

### Step 4. Frontend setup

```bash
cd ../frontend
npm install
```

---

## Running the Application

You must open **three separate terminals** and keep all three components running.

Starting from the root of the repository:

### Terminal 1. Backend

```bash
cd backend
python -m src.server
```

Expected output:

```text
Server listening on 127.0.0.1:5555
```

### Terminal 2. Bridge

```bash
cd bridge
node server.js
```

Expected output:

```text
Bridge running on http://localhost:8080
```

### Terminal 3. Frontend

```bash
cd frontend
npm run dev
```

Open your browser and go to:

`http://localhost:5173`

Create more concurrent users by reclicking on the link. 

---

## How to Use

1. Open the frontend in your browser.
2. Enter a username to join the game.
3. Create more users by clicking link again and repeating 1 and 2 until satisfied.
4. Start the game.
5. Answer questions by selecting options.
6. View round results and leaderboard updates.
7. At the end of the game, view final winners and scores.

---

## Technical Protocol Details (JSON over TCP)
We designed a custom application-layer protocol for data exchange using JSON over TCP.

The browser does not speak TCP to the Python server directly. The React app uses WebSocket to the bridge; the bridge opens a TCP connection to the Python server and forwards newline-delimited JSON in both directions.

Transport Framing: newline-delimited JSON (\n)
Message Format: {"type": <string>, ...}

Handshake Phase:
Client sends: {"type":"hello","username":"Player1"}
Server responds: {"type":"welcome","username":"Player1"}

Gameplay Phase:
Server broadcasts question:
{"type":"question","question_id":1,"text":"...","options":["...","...","...","..."],"timeout_s":12}

Client sends answer:
{"type":"answer","question_id":1,"value":"A"}

Server broadcasts round result:
{"type":"round_result","question_id":1,"winner":"Player2","correct":"B","scores":{"Player2":1,"Player1":0}}

Server broadcasts leaderboard updates:
{"type":"leaderboard","scores":{"Player2":1,"Player1":0}}

Optional/utility events:
{"type":"player_joined","username":"Player3"}
{"type":"player_left","username":"Player3","reason":"disconnected"}
{"type":"info","message":"Player2 answered correctly!"}

---

## System Limitations & Edge Cases

Handling Multiple Clients Concurrently:
We use Python's threading module with one thread per connected client. This allows multiple players to stay connected and submit answers concurrently while the game loop continues to broadcast rounds.
Limitation: Thread-per-client is limited by host resources. A production design would likely use asyncio or a worker/thread pool architecture.

TCP Stream Buffering:
TCP is a continuous byte stream, so we implemented newline-delimited JSON framing (\n) in both client and server. This ensures each payload is processed as a complete message.

Input Validation & Security:
The server validates message type, answer format (A/B/C/D), and question ID before awarding points. Score updates are guarded by a lock to avoid race conditions when answers arrive nearly simultaneously.
Limitation: This assignment-level implementation does not include authentication, encryption, or anti-cheat protections against a modified custom client.

Graceful Exit Handling:
Server-side try/except around each client handler detects disconnects and removes players cleanly from active state. Updated leaderboard/player state is then broadcast to remaining players.

Answer Cooldown:
After each answer attempt, a player enters a short cooldown period (2 seconds) where additional answers are ignored. This is enforced on the server and mirrored on the GUI client.

---

## Academic Integrity & References

Code Origin:
The socket communication approach follows standard TCP examples that can be found online in python socket documentation (listed below). 
The core game loop, JSON protocol handling, TCP networking logic, leaderboard logic, and class and method implementations were written by our group.

GenAI Usage:
ChatGPT was used to help structure protocol design, create the frontend react UI, create base skeleton classes and their methods in the backend, and writing parts of the README.
Gemini was used for learning about sockets and threading in python, idea brainstorming and accounting for system limitations and edge cases.
Gemini was also used for debugging and helping implement certain functions we were stuck on.

References:

Google Gemini 
Python Socket Programming HOWTO - https://docs.python.org/3/howto/sockets.html 
Real Python: Intro to Python Threading - https://realpython.com/intro-to-python-threading/
React documentation - https://react.dev/

