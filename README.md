CMPT 371 Assignment 3  
TrivialTrivia  

Calvin Weng 301556001  
Alex Jiang 301566792  

Project Overview  

TrivialTrivia is a real-time multiplayer trivia game. Players join a lobby, start a game, answer questions, and receive scores based on correctness. The system uses a Python TCP backend, a Node.js bridge server, and a React frontend.

The backend handles game logic and player state. The bridge connects the frontend to the backend using WebSockets. The frontend provides an interactive interface for users.

Video Demo  

https://youtu.be/GDl-JiDYjak  

---

System Requirements  

The following must be installed before running the project  

Node.js version 18 or higher  
Python version 3.10 or higher  
npm (comes with Node.js)  

---

Installation Guide  

Step 1. Clone the repository  

git clone https://github.com/sheepalx/CMPT371_A3_TrivialTrivia.git  
cd CMPT371_A3_TrivialTrivia  

---

Step 2. Backend setup  

No external libraries are required.  

---

Step 3. Bridge setup  

cd bridge  
npm install  

Note  
node_modules is not included in the repository. npm install will generate it automatically.  

---

Step 4. Frontend setup  

cd ../frontend  
npm install  

---

Running the Application  

You must open three separate terminals.

---

Terminal 1 Backend  

cd backend  
python -m src.server  

Expected output  

Server listening on 127.0.0.1:5555  

---

Terminal 2 Bridge  

cd bridge  
node server.js  

Expected output  

Bridge running on http://localhost:8080  

---

Terminal 3 Frontend  

cd frontend  
npm run dev  

Open your browser and go to  

http://localhost:5173  

---

How to Use  

1. Open the frontend in your browser  
2. Enter a username to join the game  
3. Wait in the lobby until enough players join  
4. Start the game  
5. Answer questions by selecting options  
6. View round results and leaderboard updates  
7. At the end of the game, view final winners  
8. Restart the game from the end screen  

---

Notes  

The repository does not include node_modules or cache files. All dependencies are installed using npm install.  

The system requires three running components  
backend server  
bridge server  
frontend application  

All components must be running at the same time for the game to function properly.  

---

Project Structure  

backend/  
Contains Python TCP server and game logic  

bridge/  
Contains Node.js server that connects frontend and backend  

frontend/  
Contains React application for the user interface  

README.md  
Instructions for setup and execution  

---

End of README  
