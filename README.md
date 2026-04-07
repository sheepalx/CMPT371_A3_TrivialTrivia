CMPT 371 A3 Socket Programming Trivia Game
Course: CMPT 371 - Data Communications & Networking
Instructor: Mirza Zaeem Baig
Semester: Spring 2026
RUBRIC NOTE: As per submission guidelines, only one group member will submit the link to this repository on Canvas.

Group Members
Name	Student ID	Email
Jane Doe	301111111	jane.doe@university.edu
John Smith	301222222	john.smith@university.edu

1. Project Overview & Description
This project is a competitive multiplayer Trivia Game built using Python's Socket API (TCP). Multiple clients connect to one central server, receive the same question at the same time, and race to answer. The first player to submit the correct answer wins the point for that round. The server manages all game state (questions, scoring, and leaderboard updates), while clients provide a simple GUI for answering.

Core behavior in this implementation:
- Supports multiple concurrent players (tested design target: at least 6 clients).
- Real-time leaderboard updates after each round.
- Graceful handling when a client disconnects during an active game.
- Short answer cooldown per player after each attempt.
- Hardcoded trivia question bank (10 questions) to keep scope focused on sockets/concurrency.

2. System Limitations & Edge Cases
As required by the project specifications, we have identified and handled (or defined) the following limitations and potential issues within our application scope:

Handling Multiple Clients Concurrently:
Solution: We use Python's threading module with one thread per connected client. This allows multiple players to stay connected and submit answers concurrently while the game loop continues to broadcast rounds.
Limitation: Thread-per-client is limited by host resources. A production design would likely use asyncio or a worker/thread pool architecture.

TCP Stream Buffering:
Solution: TCP is a continuous byte stream, so we implemented newline-delimited JSON framing (\n) in both client and server. This ensures each payload is processed as a complete message.

Input Validation & Security:
Solution: The server validates message type, answer format (A/B/C/D), and question ID before awarding points. Score updates are guarded by a lock to avoid race conditions when answers arrive nearly simultaneously.
Limitation: This assignment-level implementation does not include authentication, encryption, or anti-cheat protections against a modified custom client.

Graceful Exit Handling:
Solution: Server-side try/except around each client handler detects disconnects and removes players cleanly from active state. Updated leaderboard/player state is then broadcast to remaining players.

Answer Cooldown:
Solution: After each answer attempt, a player enters a short cooldown period (2 seconds) where additional answers are ignored. This is enforced on the server and mirrored on the GUI client.

3. Video Demo
RUBRIC NOTE: Include a clickable link.
Our 2-minute video demonstration covering connection establishment, data exchange, real-time gameplay, leaderboard changes, and process termination can be viewed below:
▶️ Watch Project Demo on YouTube

4. Prerequisites (Fresh Environment)
To run this project, you need:

Python 3.10 or higher.
No external pip installations are required (uses standard libraries including socket, threading, json, tkinter, argparse, and dataclasses).
(Optional) VS Code or Terminal.
RUBRIC NOTE: No external libraries are required. Therefore, a requirements.txt file is not strictly necessary for dependency installation, though one might be included for environment completeness.

5. Step-by-Step Run Guide
RUBRIC NOTE: The grader must be able to copy-paste these commands.

Step 1: Start the Server
Open your terminal and navigate to the project folder. The server binds to 127.0.0.1 on port 5555 by default.

python -m src.server
# Console output: "[STARTING] Server listening on 127.0.0.1:5555"

Step 2: Connect Player 1
Open a new terminal window (keep the server running). Run the GUI client and choose a username.

python -m src.client --username Player1
# GUI connects and waits for the next question

Step 3: Connect Additional Players
Open more terminals and run the client again with different usernames.

python -m src.client --username Player2
python -m src.client --username Player3
# Continue up to at least 6 players

Step 4: Gameplay
The server broadcasts each question and 4 options to all connected clients.
Players answer by clicking one of the GUI buttons (A/B/C/D).
The first correct answer receives the point for that round.
The leaderboard updates in real time after each round.
If a player disconnects mid-game, the server continues running for the remaining players.

6. Technical Protocol Details (JSON over TCP)
We designed a custom application-layer protocol for data exchange using JSON over TCP.

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

7. Academic Integrity & References
RUBRIC NOTE: List all references used and help you got. Below is an example.

Code Origin:
The socket communication approach follows course TCP examples. The core multithreaded trivia game loop, JSON protocol handling, leaderboard logic, and GUI client implementation were written for this assignment.

GenAI Usage:
ChatGPT/Cursor AI were used to help structure protocol design, edge-case handling notes, and README polishing.

References:
Python Socket Programming HOWTO
Real Python: Intro to Python Threading
Tkinter (Python Standard Library) Documentation