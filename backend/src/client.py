from __future__ import annotations

import argparse
import queue
import socket
import threading
import time
import tkinter as tk
from tkinter import messagebox
from typing import Any

from .net import iter_json_messages, send_json


class TriviaClientApp:
    def __init__(self, root: tk.Tk, *, host: str, port: int, username: str) -> None:
        self.root = root
        self.root.title("TrivialTrivia")
        self.root.geometry("720x420")
        self.root.minsize(640, 380)

        self.host = host
        self.port = port
        self.username = username

        self.sock: socket.socket | None = None
        self.rx_thread: threading.Thread | None = None
        self.rx_queue: queue.Queue[dict[str, Any]] = queue.Queue()

        self.current_question_id: int | None = None
        self.cooldown_until: float = 0.0

        self._build_ui()
        self._set_connected(False)
        self.root.after(50, self._drain_rx_queue)

    def _build_ui(self) -> None:
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=12, pady=10)

        self.status_var = tk.StringVar(value="Not connected")
        tk.Label(top, textvariable=self.status_var, anchor="w").pack(side="left", fill="x", expand=True)

        self.start_btn = tk.Button(top, text="Start Game", command=self.start_game, state="disabled")
        self.start_btn.pack(side="right", padx=(0, 8))
        self.connect_btn = tk.Button(top, text="Connect", command=self.connect)
        self.connect_btn.pack(side="right")

        mid = tk.Frame(self.root)
        mid.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        left = tk.Frame(mid)
        left.pack(side="left", fill="both", expand=True)

        self.question_var = tk.StringVar(value="Press Connect to join the game.")
        tk.Label(left, textvariable=self.question_var, justify="left", wraplength=420, font=("Segoe UI", 12, "bold")).pack(
            anchor="w", pady=(0, 8)
        )

        self.info_var = tk.StringVar(value="")
        tk.Label(left, textvariable=self.info_var, justify="left", wraplength=420).pack(anchor="w", pady=(0, 10))

        self.answer_buttons: list[tk.Button] = []
        grid = tk.Frame(left)
        grid.pack(anchor="w")

        for i in range(4):
            letter = ["A", "B", "C", "D"][i]
            btn = tk.Button(
                grid,
                text=f"{letter}) ...",
                width=46,
                command=lambda l=letter: self.send_answer(l),
                state="disabled",
                anchor="w",
            )
            btn.grid(row=i // 2, column=i % 2, padx=4, pady=4, sticky="w")
            self.answer_buttons.append(btn)

        right = tk.Frame(mid, bd=1, relief="groove")
        right.pack(side="right", fill="y", padx=(10, 0))

        tk.Label(right, text="Leaderboard", font=("Segoe UI", 11, "bold")).pack(padx=10, pady=(8, 4))
        self.leader_text = tk.Text(right, width=24, height=16, state="disabled")
        self.leader_text.pack(padx=10, pady=(0, 10))

    def _set_connected(self, connected: bool) -> None:
        if connected:
            self.connect_btn.config(state="disabled")
            self.status_var.set(f"Connected as {self.username} → {self.host}:{self.port}")
        else:
            self.connect_btn.config(state="normal")
            self.start_btn.config(state="disabled")
            self.status_var.set("Not connected")
            self.current_question_id = None
            self._set_answer_buttons_enabled(False)

    def _set_answer_buttons_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for b in self.answer_buttons:
            b.config(state=state)

    def connect(self) -> None:
        if self.sock:
            return
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            self.sock = s
            send_json(self.sock, {"type": "hello", "username": self.username})
        except OSError as e:
            self.sock = None
            messagebox.showerror("Connection failed", str(e))
            return

        self.rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
        self.rx_thread.start()
        self._set_connected(True)
        self.info_var.set("Connected. Waiting in lobby...")

    def start_game(self) -> None:
        if not self.sock:
            return
        try:
            send_json(self.sock, {"type": "start_game"})
        except OSError:
            pass

    def _rx_loop(self) -> None:
        assert self.sock is not None
        try:
            for msg in iter_json_messages(self.sock):
                if isinstance(msg, dict):
                    self.rx_queue.put(msg)
        except Exception:
            self.rx_queue.put({"type": "__disconnected__"})

    def send_answer(self, letter: str) -> None:
        if not self.sock:
            return
        if self.current_question_id is None:
            return
        now = time.time()
        if now < self.cooldown_until:
            return

        # Local cooldown mirrors server rule (server still enforces truth).
        self.cooldown_until = now + 2.0
        self._set_answer_buttons_enabled(False)
        self.root.after(200, self._refresh_button_state)

        try:
            send_json(
                self.sock,
                {"type": "answer", "question_id": self.current_question_id, "value": letter},
            )
        except OSError:
            pass

    def _refresh_button_state(self) -> None:
        if self.current_question_id is None:
            self._set_answer_buttons_enabled(False)
            return
        if time.time() >= self.cooldown_until:
            self._set_answer_buttons_enabled(True)
        else:
            self.root.after(200, self._refresh_button_state)

    def _drain_rx_queue(self) -> None:
        try:
            while True:
                msg = self.rx_queue.get_nowait()
                self._handle_message(msg)
        except queue.Empty:
            pass
        self.root.after(50, self._drain_rx_queue)

    def _handle_message(self, msg: dict[str, Any]) -> None:
        mtype = msg.get("type")
        if mtype == "__disconnected__":
            self.info_var.set("Disconnected from server.")
            self._disconnect_local()
            return

        if mtype == "error":
            messagebox.showerror("Server error", str(msg.get("message", "Unknown error")))
            self._disconnect_local()
            return

        if mtype == "leaderboard":
            self._update_leaderboard(msg.get("scores") or {})
            return

        if mtype == "lobby_update":
            players = msg.get("players") or []
            can_start = bool(msg.get("can_start"))
            started = bool(msg.get("started"))
            if started:
                self.start_btn.config(state="disabled")
            else:
                self.start_btn.config(state="normal" if can_start else "disabled")
                names = ", ".join(str(p) for p in players) if players else "(none)"
                self.question_var.set("Lobby")
                self.info_var.set(
                    f"Players in lobby ({len(players)}): {names}. Any player can press Start Game."
                )
            return

        if mtype == "info":
            self.info_var.set(str(msg.get("message", "")))
            return

        if mtype == "game_started":
            self.start_btn.config(state="disabled")
            self.question_var.set("Game in progress")
            self.info_var.set("Game started. Waiting for question...")
            return

        if mtype == "question":
            self.current_question_id = int(msg.get("question_id"))
            self.question_var.set(str(msg.get("text", "")))
            options = msg.get("options") or ["", "", "", ""]
            for i, opt in enumerate(options[:4]):
                letter = ["A", "B", "C", "D"][i]
                self.answer_buttons[i].config(text=f"{letter}) {opt}")
            self.info_var.set("Choose an answer. First correct wins the point.")
            if time.time() >= self.cooldown_until:
                self._set_answer_buttons_enabled(True)
            return

        if mtype == "round_result":
            winner = msg.get("winner")
            correct = msg.get("correct")
            if winner:
                self.info_var.set(f"Round over. Winner: {winner}. Correct: {correct}.")
            else:
                self.info_var.set(f"Round over. No winner. Correct: {correct}.")
            self.current_question_id = None
            self._set_answer_buttons_enabled(False)
            scores = msg.get("scores") or {}
            self._update_leaderboard(scores)
            return

        if mtype == "game_over":
            winners = msg.get("winners") or []
            scores = msg.get("scores") or {}
            board_lines = self._format_leaderboard_lines(scores)
            if winners:
                self.info_var.set(f"Game over. Winner(s): {', '.join(str(w) for w in winners)}.")
            else:
                self.info_var.set("Game over.")
            self.question_var.set("Final Leaderboard:\n" + ("\n".join(board_lines) if board_lines else "(no players)"))
            self.current_question_id = None
            self._set_answer_buttons_enabled(False)
            self._update_leaderboard(scores)
            return

    def _update_leaderboard(self, scores: dict[str, Any]) -> None:
        lines = []
        for i, (name, score) in enumerate(scores.items(), start=1):
            lines.append(f"{i:>2}. {name}: {score}")
        text = "\n".join(lines) if lines else "(no players)"

        self.leader_text.config(state="normal")
        self.leader_text.delete("1.0", "end")
        self.leader_text.insert("1.0", text)
        self.leader_text.config(state="disabled")

    def _format_leaderboard_lines(self, scores: dict[str, Any]) -> list[str]:
        lines = []
        for i, (name, score) in enumerate(scores.items(), start=1):
            lines.append(f"{i:>2}. {name}: {score}")
        return lines

    def _disconnect_local(self) -> None:
        if self.sock:
            try:
                send_json(self.sock, {"type": "quit"})
            except OSError:
                pass
            try:
                self.sock.close()
            except OSError:
                pass
        self.sock = None
        self._set_connected(False)


def main() -> None:
    parser = argparse.ArgumentParser(description="TrivialTrivia GUI client")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5555)
    parser.add_argument("--username", default="")
    args = parser.parse_args()

    username = (args.username or "").strip()
    if not username:
        username = input("Enter username: ").strip()

    root = tk.Tk()
    app = TriviaClientApp(root, host=args.host, port=args.port, username=username)
    root.protocol("WM_DELETE_WINDOW", lambda: (app._disconnect_local(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
