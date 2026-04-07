from __future__ import annotations

import argparse
import random
import socket
import threading
import time
from dataclasses import dataclass
from typing import Any

from .net import iter_json_messages, send_json
from .questions import QUESTIONS, Question


@dataclass
class Player:
    username: str
    sock: socket.socket
    addr: tuple[str, int]
    score: int = 0
    cooldown_until: float = 0.0


@dataclass
class RoundState:
    question: Question
    winner_username: str | None = None


class TriviaServer:
    def __init__(
        self,
        host: str,
        port: int,
        *,
        min_players_to_start: int = 1,
        answer_timeout_s: float = 12.0,
        inter_round_pause_s: float = 2.0,
        cooldown_s: float = 2.0,
    ) -> None:
        self.host = host
        self.port = port
        self.min_players_to_start = min_players_to_start
        self.answer_timeout_s = answer_timeout_s
        self.inter_round_pause_s = inter_round_pause_s
        self.cooldown_s = cooldown_s

        self._lock = threading.Lock()
        self._players: dict[socket.socket, Player] = {}
        self._round: RoundState | None = None
        self._shutdown = threading.Event()
        self._game_started = False
        self._game_finished = False
        self._start_requested = False

    def _broadcast(self, message: dict[str, Any]) -> None:
        dead: list[socket.socket] = []
        for s, p in list(self._players.items()):
            try:
                send_json(s, message)
            except OSError:
                dead.append(s)
        for s in dead:
            self._remove_player_socket(s, reason="disconnected")

    def _leaderboard_payload(self) -> dict[str, int]:
        # sorted for stable display client-side
        scores = {p.username: p.score for p in self._players.values()}
        return dict(sorted(scores.items(), key=lambda kv: (-kv[1], kv[0].lower())))

    def _broadcast_leaderboard(self) -> None:
        self._broadcast({"type": "leaderboard", "scores": self._leaderboard_payload()})

    def _lobby_payload(self) -> dict[str, Any]:
        players = sorted((p.username for p in self._players.values()), key=str.lower)
        return {
            "type": "lobby_update",
            "players": players,
            "started": self._game_started,
            "can_start": len(players) >= 1 and not self._game_started,
            "min_players": self.min_players_to_start,
        }

    def _broadcast_lobby_state(self) -> None:
        self._broadcast(self._lobby_payload())

    def _remove_player_socket(self, sock: socket.socket, *, reason: str) -> None:
        with self._lock:
            player = self._players.pop(sock, None)
        if not player:
            return
        try:
            sock.close()
        except OSError:
            pass
        print(f"[LEAVE] {player.username} ({player.addr[0]}:{player.addr[1]}) reason={reason}")
        self._broadcast({"type": "player_left", "username": player.username, "reason": reason})
        self._broadcast_leaderboard()
        self._broadcast_lobby_state()

    def _on_start_game_request(self, username: str) -> None:
        with self._lock:
            if self._game_started:
                return
            if len(self._players) < 1:
                return
            self._start_requested = True
        self._broadcast({"type": "info", "message": f"{username} started the game."})
        self._broadcast_lobby_state()

    def _handle_client(self, client_sock: socket.socket, addr: tuple[str, int]) -> None:
        client_sock.settimeout(None)
        username: str | None = None
        try:
            # First message must be hello.
            msg_iter = iter_json_messages(client_sock)
            first = next(msg_iter)
            if not isinstance(first, dict) or first.get("type") != "hello":
                send_json(client_sock, {"type": "error", "message": "Expected hello"})
                raise ConnectionError("Bad handshake")
            username = str(first.get("username") or "").strip()
            if not username:
                send_json(client_sock, {"type": "error", "message": "Username required"})
                raise ConnectionError("Missing username")

            with self._lock:
                if any(p.username.lower() == username.lower() for p in self._players.values()):
                    send_json(
                        client_sock,
                        {"type": "error", "message": "Username already taken"},
                    )
                    raise ConnectionError("Duplicate username")
                player = Player(username=username, sock=client_sock, addr=addr)
                self._players[client_sock] = player

            send_json(client_sock, {"type": "welcome", "username": username})
            self._broadcast({"type": "player_joined", "username": username})
            self._broadcast_leaderboard()
            print(f"[JOIN] {username} ({addr[0]}:{addr[1]})")
            with self._lock:
                started = self._game_started
            if started:
                send_json(client_sock, {"type": "info", "message": "Match in progress. Waiting for next question."})
            else:
                self._broadcast_lobby_state()

            for msg in msg_iter:
                if not isinstance(msg, dict):
                    continue
                if msg.get("type") == "answer":
                    self._on_answer(username, msg)
                elif msg.get("type") == "start_game":
                    self._on_start_game_request(username)
                elif msg.get("type") == "quit":
                    raise ConnectionError("Client quit")
        except (ConnectionError, StopIteration, OSError, ValueError) as e:
            reason = "disconnected"
            if str(e):
                reason = str(e)
            if username is not None:
                self._remove_player_socket(client_sock, reason=reason)
            else:
                try:
                    client_sock.close()
                except OSError:
                    pass

    def _on_answer(self, username: str, msg: dict[str, Any]) -> None:
        now = time.time()
        with self._lock:
            round_state = self._round
            player = next((p for p in self._players.values() if p.username == username), None)
            if not round_state or not player:
                return

            # Cooldown applies whenever they attempt an answer.
            if now < player.cooldown_until:
                return
            player.cooldown_until = now + self.cooldown_s

            if round_state.winner_username is not None:
                return

            qid = msg.get("question_id")
            value = str(msg.get("value") or "").strip().upper()
            if qid != round_state.question.id:
                return

            option_map = {"A": 0, "B": 1, "C": 2, "D": 3}
            if value not in option_map:
                return

            if option_map[value] == round_state.question.answer_index:
                round_state.winner_username = username
                player.score += 1
                winner = username
            else:
                winner = None

        if winner:
            self._broadcast_leaderboard()
            self._broadcast({"type": "info", "message": f"{winner} answered correctly!"})

    def serve_forever(self) -> None:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen()
        print(f"[STARTING] Server listening on {self.host}:{self.port}")

        accept_thread = threading.Thread(
            target=self._accept_loop,
            args=(server_sock,),
            daemon=True,
        )
        accept_thread.start()

        try:
            self._game_loop()
        finally:
            self._shutdown.set()
            try:
                server_sock.close()
            except OSError:
                pass

    def _accept_loop(self, server_sock: socket.socket) -> None:
        while not self._shutdown.is_set():
            try:
                client_sock, addr = server_sock.accept()
            except OSError:
                break
            t = threading.Thread(target=self._handle_client, args=(client_sock, addr), daemon=True)
            t.start()

    def _game_loop(self) -> None:
        # Shuffle once so question order is random but without repeats.
        question_order = list(QUESTIONS)
        random.shuffle(question_order)

        while not self._shutdown.is_set():
            with self._lock:
                game_started = self._game_started
                game_finished = self._game_finished
                start_requested = self._start_requested
                player_count = len(self._players)

            if game_finished:
                # Keep server and clients connected after game-over.
                time.sleep(0.2)
                continue

            if not game_started:
                # Lobby phase: wait for someone to press start.
                if player_count >= 1 and start_requested:
                    with self._lock:
                        self._game_started = True
                    self._broadcast({"type": "game_started"})
                    self._broadcast({"type": "info", "message": "Game started."})
                    continue
                time.sleep(0.2)
                continue

            for q in question_order:
                with self._lock:
                    self._round = RoundState(question=q)

                self._broadcast(
                    {
                        "type": "question",
                        "question_id": q.id,
                        "text": q.text,
                        "options": q.options,
                        "timeout_s": self.answer_timeout_s,
                    }
                )

                deadline = time.time() + self.answer_timeout_s
                while time.time() < deadline and not self._shutdown.is_set():
                    with self._lock:
                        winner = self._round.winner_username if self._round else None
                    if winner:
                        break
                    time.sleep(0.05)

                with self._lock:
                    round_state = self._round
                    self._round = None

                if not round_state:
                    continue

                correct_letter = ["A", "B", "C", "D"][round_state.question.answer_index]
                self._broadcast(
                    {
                        "type": "round_result",
                        "question_id": round_state.question.id,
                        "winner": round_state.winner_username,
                        "correct": correct_letter,
                        "scores": self._leaderboard_payload(),
                    }
                )
                time.sleep(self.inter_round_pause_s)

            final_scores = self._leaderboard_payload()
            top_score = max(final_scores.values(), default=0)
            winners = [name for name, score in final_scores.items() if score == top_score]
            self._broadcast(
                {
                    "type": "game_over",
                    "scores": final_scores,
                    "winners": winners,
                }
            )
            print("[GAME OVER] All questions asked.")
            self._broadcast_leaderboard()
            with self._lock:
                self._game_finished = True


def main() -> None:
    parser = argparse.ArgumentParser(description="TrivialTrivia TCP server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5555)
    parser.add_argument("--min-players", type=int, default=1)
    args = parser.parse_args()

    TriviaServer(args.host, args.port, min_players_to_start=args.min_players).serve_forever()


if __name__ == "__main__":
    main()
