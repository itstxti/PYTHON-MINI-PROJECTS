import json
import os
import random
import time
import tkinter as tk
from tkinter import simpledialog


# Configuration

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700

SCORES_FILE = "memory_scores.json"

DIFFICULTIES = {
    "Easy (4x4)": {
        "rows": 4,
        "cols": 4,
        "time_limit": 60
    },
    "Medium (4x6)": {
        "rows": 4,
        "cols": 6,
        "time_limit": 90
    },
    "Hard (6x6)": {
        "rows": 6,
        "cols": 6,
        "time_limit": 120
    }
}

MODES = ["solo", "vs", "challenge"]


# Symbol Sets

SYMBOL_SETS = {
    "Animals": [
        "🐶", "🐱", "🐭", "🐹", "🐰", "🦊",
        "🐻", "🐼", "🐨", "🐯", "🦁", "🐮",
        "🐷", "🐸", "🐵", "🐙", "🦄", "🐝"
    ],

    "Food": [
        "🍎", "🍊", "🍋", "🍉", "🍇", "🍓",
        "🍒", "🍑", "🍍", "🥝", "🍌", "🥭",
        "🍕", "🍔", "🍟", "🌭", "🍩", "🍪"
    ],

    "Nature": [
        "🌸", "🌺", "🌻", "🌹", "🌷", "🌱",
        "🍀", "🌿", "🍁", "🍂", "🌴", "🌵",
        "🌈", "☀️", "🌙", "⭐", "🔥", "❄️"
    ],

    "Space": [
        "🚀", "🛸", "🌍", "🌎", "🌕", "🌑",
        "⭐", "🌟", "☄️", "🪐", "👽", "🌌",
        "🌠", "🛰️", "🌞", "🌙", "✨", "🔭"
    ],

    "Objects": [
        "🎮", "🎧", "📱", "💻", "⌚", "📷",
        "🎸", "🎹", "🎨", "⚽", "🏀", "🎯",
        "🚲", "🚗", "✈️", "🚀", "🎁", "🔑"
    ]
}


# Score Board

class ScoreBoard:
    def __init__(self):
        self.scores = {
            difficulty: {
                "solo": [],
                "vs": [],
                "challenge": []
            }
            for difficulty in DIFFICULTIES
        }

        self.load_scores()

    def load_scores(self):
        if not os.path.exists(SCORES_FILE):
            return

        try:
            with open(SCORES_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                return

            # Load only the new leaderboard format
            for difficulty in DIFFICULTIES:
                difficulty_data = data.get(difficulty)

                if not isinstance(difficulty_data, dict):
                    continue

                for mode in MODES:
                    scores = difficulty_data.get(mode, [])

                    if isinstance(scores, list):
                        self.scores[difficulty][mode] = scores[:5]

        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass

    def save_scores(self):
        try:
            with open(SCORES_FILE, "w", encoding="utf-8") as file:
                json.dump(
                    self.scores,
                    file,
                    indent=4,
                    ensure_ascii=False
                )
        except OSError:
            pass

    def add_solo_score(
        self,
        difficulty,
        name,
        time_taken,
        attempts
    ):
        score = {
            "name": name,
            "time": round(time_taken, 2),
            "attempts": attempts
        }

        scores = self.scores[difficulty]["solo"]

        scores.append(score)

        # Primary: fewer attempts
        # Tie-breaker: lower time
        scores.sort(
            key=lambda item: (
                item["attempts"],
                item["time"]
            )
        )

        self.scores[difficulty]["solo"] = scores[:5]

        self.save_scores()

    def add_vs_score(
        self,
        difficulty,
        player1,
        player1_attempts,
        player1_time,
        player2,
        player2_attempts,
        player2_time
    ):
        score1 = {
            "name": player1,
            "attempts": player1_attempts,
            "time": round(player1_time, 2)
        }

        score2 = {
            "name": player2,
            "attempts": player2_attempts,
            "time": round(player2_time, 2)
        }

        scores = self.scores[difficulty]["vs"]

        # Each player gets an individual leaderboard entry
        scores.append(score1)
        scores.append(score2)

        # Primary: fewer attempts
        # Tie-breaker: lower time
        scores.sort(
            key=lambda item: (
                item["attempts"],
                item["time"]
            )
        )

        self.scores[difficulty]["vs"] = scores[:5]

        self.save_scores()

    def add_challenge_score(
        self,
        difficulty,
        name,
        time_taken,
        attempts
    ):
        score = {
            "name": name,
            "time": round(time_taken, 2),
            "attempts": attempts
        }

        scores = self.scores[difficulty]["challenge"]

        scores.append(score)

        # Primary: lower time
        # Tie-breaker: fewer attempts
        scores.sort(
            key=lambda item: (
                item["time"],
                item["attempts"]
            )
        )

        self.scores[difficulty]["challenge"] = scores[:5]

        self.save_scores()

    def get_scores(self, difficulty, mode):
        return self.scores[difficulty][mode]


# Memory Game

class MemoryGame:
    def __init__(self, root):
        self.root = root

        self.root.title("Memory Game")
        self.root.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )
        self.root.minsize(
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        )
        self.root.maxsize(
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        )
        self.root.resizable(False, False)

        # Colors
        self.bg_color = "#f5f5f7"
        self.card_color = "#ffffff"
        self.card_back = "#dce8f5"
        self.card_front = "#ffffff"
        self.text_color = "#1d1d1f"
        self.secondary_text = "#6e6e73"
        self.accent_color = "#007aff"
        self.danger_color = "#ff3b30"
        self.success_color = "#34c759"
        self.border_color = "#d2d2d7"

        self.scoreboard = ScoreBoard()

        self.current_difficulty = None
        self.current_mode = None
        self.current_symbol_category = None

        self.players = []
        self.current_player = 0

        self.showing_cards = []
        self.matched_cards = set()

        self.board = []
        self.cards = []

        self.attempts = 0
        self.player_attempts = [0, 0]

        self.start_time = None
        self.game_finished = False

        # Two-player timing
        self.player_times = [0.0, 0.0]
        self.turn_start_time = None

        # Challenge timer
        self.remaining_time = 0
        self.timer_job = None

        self.show_main_menu()

    # ========================================================
    # General UI
    # ========================================================

    def clear_screen(self):
        self.stop_timer()

        for widget in self.root.winfo_children():
            widget.destroy()

    def create_button(
        self,
        parent,
        text,
        command,
        width=20,
        font=("Segoe UI", 12, "bold")
    ):
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            font=font,
            bg=self.card_color,
            fg=self.text_color,
            activebackground="#e5e5ea",
            activeforeground=self.text_color,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=10,
            pady=10
        )

    # ========================================================
    # Main Menu
    # ========================================================

    def show_main_menu(self):
        self.stop_timer()

        self.clear_screen()

        self.current_difficulty = None
        self.current_mode = None

        frame = tk.Frame(
            self.root,
            bg=self.bg_color
        )
        frame.pack(
            fill="both",
            expand=True
        )

        title = tk.Label(
            frame,
            text="MEMORY GAME",
            font=("Segoe UI", 32, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        title.pack(pady=(110, 10))

        subtitle = tk.Label(
            frame,
            text="Test your memory and climb the leaderboard",
            font=("Segoe UI", 13),
            bg=self.bg_color,
            fg=self.secondary_text
        )
        subtitle.pack(pady=(0, 50))

        play_button = self.create_button(
            frame,
            "Play",
            self.show_difficulty_menu,
            width=22
        )
        play_button.pack(pady=8)

        scores_button = self.create_button(
            frame,
            "Top Scores",
            self.show_difficulty_scores,
            width=22
        )
        scores_button.pack(pady=8)

        exit_button = self.create_button(
            frame,
            "Exit",
            self.root.destroy,
            width=22
        )
        exit_button.pack(pady=8)

    # ========================================================
    # Difficulty Menu
    # ========================================================

    def show_difficulty_menu(self):
        self.clear_screen()

        frame = tk.Frame(
            self.root,
            bg=self.bg_color
        )
        frame.pack(
            fill="both",
            expand=True
        )

        title = tk.Label(
            frame,
            text="Choose Difficulty",
            font=("Segoe UI", 28, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        title.pack(pady=(90, 15))

        subtitle = tk.Label(
            frame,
            text="Select the board size",
            font=("Segoe UI", 13),
            bg=self.bg_color,
            fg=self.secondary_text
        )
        subtitle.pack(pady=(0, 40))

        for difficulty in DIFFICULTIES:
            button = self.create_button(
                frame,
                difficulty,
                lambda d=difficulty: self.select_difficulty(d),
                width=22
            )
            button.pack(pady=7)

        back_button = self.create_button(
            frame,
            "← Back",
            self.show_main_menu,
            width=22
        )
        back_button.pack(pady=(25, 7))

    def select_difficulty(self, difficulty):
        self.current_difficulty = difficulty
        self.show_mode_menu()

    # ========================================================
    # Mode Menu
    # ========================================================

    def show_mode_menu(self):
        self.clear_screen()

        frame = tk.Frame(
            self.root,
            bg=self.bg_color
        )
        frame.pack(
            fill="both",
            expand=True
        )

        title = tk.Label(
            frame,
            text="Game Mode",
            font=("Segoe UI", 28, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        title.pack(pady=(90, 15))

        difficulty_label = tk.Label(
            frame,
            text=self.current_difficulty,
            font=("Segoe UI", 13, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        difficulty_label.pack(pady=(0, 35))

        solo_button = self.create_button(
            frame,
            "Solo",
            lambda: self.start_game("solo"),
            width=22
        )
        solo_button.pack(pady=7)

        vs_button = self.create_button(
            frame,
            "Two Players",
            lambda: self.start_game("vs"),
            width=22
        )
        vs_button.pack(pady=7)

        challenge_button = self.create_button(
            frame,
            "Time Challenge",
            lambda: self.start_game("challenge"),
            width=22
        )
        challenge_button.pack(pady=7)

        back_button = self.create_button(
            frame,
            "← Back",
            self.show_difficulty_menu,
            width=22
        )
        back_button.pack(pady=(25, 7))

    # ========================================================
    # Start Game
    # ========================================================

    def start_game(self, mode):
        self.current_mode = mode

        # Choose a random symbol category for every new game
        self.current_symbol_category = random.choice(
            list(SYMBOL_SETS.keys())
        )

        if mode == "vs":
            self.ask_player_names()
        else:
            self.players = ["Player"]
            self.show_game_screen()

    def ask_player_names(self):
        player1 = simpledialog.askstring(
            "Player 1",
            "Enter Player 1 name:",
            parent=self.root
        )

        if player1 is None:
            return

        player1 = player1.strip()

        if not player1:
            player1 = "Player 1"

        player2 = simpledialog.askstring(
            "Player 2",
            "Enter Player 2 name:",
            parent=self.root
        )

        if player2 is None:
            return

        player2 = player2.strip()

        if not player2:
            player2 = "Player 2"

        self.players = [
            player1,
            player2
        ]

        self.show_game_screen()

    # ========================================================
    # Game Screen
    # ========================================================

    def show_game_screen(self):
        self.clear_screen()

        settings = DIFFICULTIES[
            self.current_difficulty
        ]

        self.rows = settings["rows"]
        self.cols = settings["cols"]

        self.showing_cards = []
        self.matched_cards = set()

        self.attempts = 0
        self.player_attempts = [0, 0]

        self.current_player = 0

        self.game_finished = False

        self.player_times = [0.0, 0.0]

        self.start_time = time.time()
        self.remaining_time = settings["time_limit"]

        # Main game container
        game_frame = tk.Frame(
            self.root,
            bg=self.bg_color
        )
        game_frame.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        header_frame = tk.Frame(
            game_frame,
            bg=self.bg_color,
            height=75
        )
        header_frame.pack(
            fill="x",
            padx=20,
            pady=(15, 5)
        )

        header_frame.pack_propagate(False)

        # Menu button
        menu_button = tk.Button(
            header_frame,
            text="← Menu",
            command=self.show_main_menu,
            font=("Segoe UI", 10, "bold"),
            bg=self.card_color,
            fg=self.text_color,
            activebackground="#e5e5ea",
            activeforeground=self.text_color,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=14,
            pady=7
        )

        menu_button.place(
            x=0,
            rely=0.5,
            anchor="w"
        )

        # Centered title
        title_frame = tk.Frame(
            header_frame,
            bg=self.bg_color
        )

        title_frame.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        title = tk.Label(
            title_frame,
            text="Memory Game",
            font=("Segoe UI", 22, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        title.pack()

        mode_text = {
            "solo": "Solo",
            "vs": "Two Players",
            "challenge": "Time Challenge"
        }

        mode_label = tk.Label(
            title_frame,
            text=(
                f"{self.current_difficulty}  •  "
                f"{mode_text[self.current_mode]}  •  "
                f"{self.current_symbol_category}"
            ),
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg=self.secondary_text
        )
        mode_label.pack(
            pady=(2, 0)
        )

        # ----------------------------------------------------
        # Game information
        # ----------------------------------------------------

        info_frame = tk.Frame(
            game_frame,
            bg=self.bg_color
        )
        info_frame.pack(
            fill="x",
            padx=30,
            pady=5
        )

        if self.current_mode == "vs":

            self.info_label = tk.Label(
                info_frame,
                text="",
                font=("Segoe UI", 11, "bold"),
                bg=self.bg_color,
                fg=self.text_color
            )
            self.info_label.pack()

            self.attempts_label = tk.Label(
                info_frame,
                text="Attempts: 0",
                font=("Segoe UI", 10),
                bg=self.bg_color,
                fg=self.secondary_text
            )
            self.attempts_label.pack(
                pady=(2, 0)
            )

        elif self.current_mode == "challenge":

            self.info_label = tk.Label(
                info_frame,
                text=(
                    f"Time: "
                    f"{settings['time_limit']}s"
                ),
                font=("Segoe UI", 12, "bold"),
                bg=self.bg_color,
                fg=self.accent_color
            )
            self.info_label.pack()

            self.attempts_label = tk.Label(
                info_frame,
                text="Attempts: 0",
                font=("Segoe UI", 10),
                bg=self.bg_color,
                fg=self.secondary_text
            )
            self.attempts_label.pack(
                pady=(2, 0)
            )

        else:

            self.info_label = tk.Label(
                info_frame,
                text="Time: 0.00s",
                font=("Segoe UI", 12, "bold"),
                bg=self.bg_color,
                fg=self.accent_color
            )
            self.info_label.pack()

            self.attempts_label = tk.Label(
                info_frame,
                text="Attempts: 0",
                font=("Segoe UI", 10),
                bg=self.bg_color,
                fg=self.secondary_text
            )
            self.attempts_label.pack(
                pady=(2, 0)
            )

        # ----------------------------------------------------
        # Board
        # ----------------------------------------------------

        board_container = tk.Frame(
            game_frame,
            bg=self.bg_color
        )
        board_container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(5, 15)
        )

        self.board_canvas = tk.Canvas(
            board_container,
            bg=self.bg_color,
            highlightthickness=0
        )
        self.board_canvas.pack(
            fill="both",
            expand=True
        )

        self.create_board()

        if self.current_mode == "vs":
            self.turn_start_time = time.time()

        self.update_game_info()

        if self.current_mode == "challenge":
            self.update_challenge_timer()

        elif self.current_mode == "solo":
            self.update_solo_timer()

    # ========================================================
    # Board Creation
    # ========================================================

    def create_board(self):
        settings = DIFFICULTIES[
            self.current_difficulty
        ]

        rows = settings["rows"]
        cols = settings["cols"]

        pair_count = (rows * cols) // 2

        symbol_set = SYMBOL_SETS[
            self.current_symbol_category
        ]

        selected_symbols = symbol_set[:pair_count]

        deck = selected_symbols * 2

        random.shuffle(deck)

        self.board = deck
        self.cards = []

        self.root.update_idletasks()

        canvas_width = self.board_canvas.winfo_width()
        canvas_height = self.board_canvas.winfo_height()

        if canvas_width <= 1:
            canvas_width = 850

        if canvas_height <= 1:
            canvas_height = 480

        gap = 8

        card_width = (
            canvas_width -
            (cols - 1) * gap
        ) / cols

        card_height = (
            canvas_height -
            (rows - 1) * gap
        ) / rows

        # Keep cards square
        card_size = min(
            card_width,
            card_height
        )

        total_width = (
            cols * card_size +
            (cols - 1) * gap
        )

        total_height = (
            rows * card_size +
            (rows - 1) * gap
        )

        start_x = (
            canvas_width - total_width
        ) / 2

        start_y = (
            canvas_height - total_height
        ) / 2

        for index in range(rows * cols):

            row = index // cols
            col = index % cols

            x1 = (
                start_x +
                col * (card_size + gap)
            )

            y1 = (
                start_y +
                row * (card_size + gap)
            )

            x2 = x1 + card_size
            y2 = y1 + card_size

            rectangle = self.board_canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill=self.card_back,
                outline=self.border_color,
                width=1
            )

            text = self.board_canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text="?",
                font=(
                    "Segoe UI Emoji",
                    int(card_size * 0.30),
                    "bold"
                ),
                fill=self.text_color
            )

            self.cards.append({
                "rectangle": rectangle,
                "text": text,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "flipped": False,
                "matched": False
            })

            self.board_canvas.tag_bind(
                rectangle,
                "<Button-1>",
                lambda event, i=index:
                    self.click_card(i)
            )

            self.board_canvas.tag_bind(
                text,
                "<Button-1>",
                lambda event, i=index:
                    self.click_card(i)
            )

    # ========================================================
    # Card Interaction
    # ========================================================

    def click_card(self, index):
        if self.game_finished:
            return

        if index in self.matched_cards:
            return

        if index in self.showing_cards:
            return

        if len(self.showing_cards) >= 2:
            return

        card = self.cards[index]

        if card["flipped"]:
            return

        card["flipped"] = True

        self.board_canvas.itemconfig(
            card["rectangle"],
            fill=self.card_front
        )

        self.board_canvas.itemconfig(
            card["text"],
            text=self.board[index],
            fill=self.text_color
        )

        self.showing_cards.append(index)

        if len(self.showing_cards) == 2:

            self.attempts += 1

            if self.current_mode == "vs":
                self.player_attempts[
                    self.current_player
                ] += 1

            self.attempts_label.config(
                text=f"Attempts: {self.attempts}"
            )

            first = self.showing_cards[0]
            second = self.showing_cards[1]

            if self.board[first] == self.board[second]:

                self.handle_match(
                    first,
                    second
                )

            else:

                self.root.after(
                    750,
                    self.hide_pair,
                    first,
                    second
                )

    # ========================================================
    # Match
    # ========================================================

    def handle_match(self, first, second):
        self.matched_cards.add(first)
        self.matched_cards.add(second)

        self.cards[first]["matched"] = True
        self.cards[second]["matched"] = True

        self.board_canvas.itemconfig(
            self.cards[first]["rectangle"],
            fill="#dff7e5"
        )

        self.board_canvas.itemconfig(
            self.cards[second]["rectangle"],
            fill="#dff7e5"
        )

        self.showing_cards = []

        if len(self.matched_cards) == len(self.board):
            self.finish_game()

    # ========================================================
    # Hide Mismatched Pair
    # ========================================================

    def hide_pair(self, first, second):
        if self.game_finished:
            return

        for index in (first, second):

            card = self.cards[index]

            if card["matched"]:
                continue

            card["flipped"] = False

            self.board_canvas.itemconfig(
                card["rectangle"],
                fill=self.card_back
            )

            self.board_canvas.itemconfig(
                card["text"],
                text="?",
                fill=self.text_color
            )

        self.showing_cards = []

        # Switch player only in Two Players mode
        if self.current_mode == "vs":
            self.switch_player()

    # ========================================================
    # Two Player Turn
    # ========================================================

    def switch_player(self):
        now = time.time()

        if self.turn_start_time is not None:
            self.player_times[
                self.current_player
            ] += (
                now - self.turn_start_time
            )

        self.current_player = 1 - self.current_player

        self.turn_start_time = now

        self.update_game_info()

    # ========================================================
    # Game Information
    # ========================================================

    def update_game_info(self):
        if self.game_finished:
            return

        if self.current_mode == "vs":

            player_name = self.players[
                self.current_player
            ]

            self.info_label.config(
                text=f"Turn: {player_name}"
            )

            self.attempts_label.config(
                text=(
                    f"Attempts: {self.attempts}   •   "
                    f"{self.players[0]}: "
                    f"{self.player_attempts[0]}   "
                    f"{self.players[1]}: "
                    f"{self.player_attempts[1]}"
                )
            )

        elif self.current_mode == "challenge":

            self.info_label.config(
                text=f"Time: {self.remaining_time}s"
            )

        else:

            elapsed = (
                time.time() -
                self.start_time
            )

            self.info_label.config(
                text=f"Time: {elapsed:.2f}s"
            )

    # ========================================================
    # Solo Timer
    # ========================================================

    def update_solo_timer(self):
        if self.game_finished:
            return

        if self.current_mode != "solo":
            return

        elapsed = (
            time.time() -
            self.start_time
        )

        self.info_label.config(
            text=f"Time: {elapsed:.2f}s"
        )

        self.timer_job = self.root.after(
            100,
            self.update_solo_timer
        )

    # ========================================================
    # Challenge Timer
    # ========================================================

    def update_challenge_timer(self):
        if self.game_finished:
            return

        if self.current_mode != "challenge":
            return

        elapsed = (
            time.time() -
            self.start_time
        )

        remaining = max(
            0,
            int(
                DIFFICULTIES[
                    self.current_difficulty
                ]["time_limit"] -
                elapsed
            )
        )

        self.remaining_time = remaining

        self.info_label.config(
            text=f"Time: {remaining}s"
        )

        if remaining <= 0:
            self.time_expired()
            return

        self.timer_job = self.root.after(
            250,
            self.update_challenge_timer
        )

    # ========================================================
    # Stop Timer
    # ========================================================

    def stop_timer(self):
        if self.timer_job is not None:

            try:
                self.root.after_cancel(
                    self.timer_job
                )

            except (
                tk.TclError,
                ValueError
            ):
                pass

            self.timer_job = None

    # ========================================================
    # Time Expired
    # ========================================================

    def time_expired(self):
        if self.game_finished:
            return

        self.game_finished = True

        self.stop_timer()

        self.info_label.config(
            text="Time's Up!"
        )

        self.root.after(
            700,
            self.show_time_expired_screen
        )

    def show_time_expired_screen(self):
        self.clear_screen()

        frame = tk.Frame(
            self.root,
            bg=self.bg_color
        )
        frame.pack(
            fill="both",
            expand=True
        )

        title = tk.Label(
            frame,
            text="Time's Up!",
            font=("Segoe UI", 32, "bold"),
            bg=self.bg_color,
            fg=self.danger_color
        )
        title.pack(
            pady=(150, 15)
        )

        subtitle = tk.Label(
            frame,
            text=(
                f"You completed "
                f"{len(self.matched_cards) // 2} pairs."
            ),
            font=("Segoe UI", 14),
            bg=self.bg_color,
            fg=self.secondary_text
        )
        subtitle.pack(
            pady=10
        )

        attempts = tk.Label(
            frame,
            text=f"Attempts: {self.attempts}",
            font=("Segoe UI", 12),
            bg=self.bg_color,
            fg=self.text_color
        )
        attempts.pack(
            pady=5
        )

        menu_button = self.create_button(
            frame,
            "Main Menu",
            self.show_main_menu,
            width=22
        )
        menu_button.pack(
            pady=(35, 8)
        )

        retry_button = self.create_button(
            frame,
            "Play Again",
            self.restart_game,
            width=22
        )
        retry_button.pack(
            pady=8
        )

    # ========================================================
    # Finish Game
    # ========================================================

    def finish_game(self):
        if self.game_finished:
            return

        self.game_finished = True

        self.stop_timer()

        if self.current_mode == "vs":

            now = time.time()

            if self.turn_start_time is not None:
                self.player_times[
                    self.current_player
                ] += (
                    now - self.turn_start_time
                )

        total_time = (
            time.time() -
            self.start_time
        )

        if self.current_mode == "solo":
            self.show_solo_result(
                total_time
            )

        elif self.current_mode == "vs":
            self.show_vs_result()

        elif self.current_mode == "challenge":
            self.show_challenge_result(
                total_time
            )

    # ========================================================
    # Solo Result
    # ========================================================

    def show_solo_result(self, total_time):
        name = simpledialog.askstring(
            "Game Complete",
            "Enter your name for the leaderboard:",
            parent=self.root
        )

        if name is None:
            name = "Player"

        name = name.strip()

        if not name:
            name = "Player"

        self.scoreboard.add_solo_score(
            self.current_difficulty,
            name,
            total_time,
            self.attempts
        )

        self.show_result_screen(
            title="You Win!",
            subtitle=f"Great job, {name}!",
            details=[
                f"Attempts: {self.attempts}",
                f"Time: {total_time:.2f}s"
            ]
        )

    # ========================================================
    # Two Player Result
    # ========================================================

    def show_vs_result(self):
        player1 = self.players[0]
        player2 = self.players[1]

        player1_attempts = (
            self.player_attempts[0]
        )

        player2_attempts = (
            self.player_attempts[1]
        )

        player1_time = (
            self.player_times[0]
        )

        player2_time = (
            self.player_times[1]
        )

        self.scoreboard.add_vs_score(
            self.current_difficulty,
            player1,
            player1_attempts,
            player1_time,
            player2,
            player2_attempts,
            player2_time
        )

        if player1_attempts < player2_attempts:
            winner = player1

        elif player2_attempts < player1_attempts:
            winner = player2

        elif player1_time < player2_time:
            winner = player1

        elif player2_time < player1_time:
            winner = player2

        else:
            winner = "It's a tie!"

        if winner == "It's a tie!":
            title = "It's a Tie!"

        else:
            title = f"{winner} Wins!"

        self.show_result_screen(
            title=title,
            subtitle="Game Complete",
            details=[
                (
                    f"{player1}: "
                    f"{player1_attempts} attempts • "
                    f"{player1_time:.2f}s"
                ),
                (
                    f"{player2}: "
                    f"{player2_attempts} attempts • "
                    f"{player2_time:.2f}s"
                )
            ]
        )

    # ========================================================
    # Challenge Result
    # ========================================================

    def show_challenge_result(self, total_time):
        name = simpledialog.askstring(
            "Challenge Complete",
            "Enter your name for the leaderboard:",
            parent=self.root
        )

        if name is None:
            name = "Player"

        name = name.strip()

        if not name:
            name = "Player"

        self.scoreboard.add_challenge_score(
            self.current_difficulty,
            name,
            total_time,
            self.attempts
        )

        self.show_result_screen(
            title="Challenge Complete!",
            subtitle=f"Well done, {name}!",
            details=[
                f"Time: {total_time:.2f}s",
                f"Attempts: {self.attempts}"
            ]
        )

    # ========================================================
    # Result Screen
    # ========================================================

    def show_result_screen(
        self,
        title,
        subtitle,
        details
    ):
        self.clear_screen()

        frame = tk.Frame(
            self.root,
            bg=self.bg_color
        )
        frame.pack(
            fill="both",
            expand=True
        )

        title_label = tk.Label(
            frame,
            text=title,
            font=("Segoe UI", 32, "bold"),
            bg=self.bg_color,
            fg=self.success_color
        )
        title_label.pack(
            pady=(120, 10)
        )

        subtitle_label = tk.Label(
            frame,
            text=subtitle,
            font=("Segoe UI", 14),
            bg=self.bg_color,
            fg=self.secondary_text
        )
        subtitle_label.pack(
            pady=(0, 35)
        )

        for detail in details:

            label = tk.Label(
                frame,
                text=detail,
                font=("Segoe UI", 12),
                bg=self.bg_color,
                fg=self.text_color
            )

            label.pack(
                pady=5
            )

        button_frame = tk.Frame(
            frame,
            bg=self.bg_color
        )
        button_frame.pack(
            pady=40
        )

        play_again = self.create_button(
            button_frame,
            "Play Again",
            self.restart_game,
            width=18
        )
        play_again.pack(
            side="left",
            padx=8
        )

        scores_button = self.create_button(
            button_frame,
            "Top Scores",
            lambda: self.show_top_scores(
                self.current_difficulty
            ),
            width=18
        )
        scores_button.pack(
            side="left",
            padx=8
        )

        menu_button = self.create_button(
            frame,
            "Main Menu",
            self.show_main_menu,
            width=22
        )
        menu_button.pack(
            pady=5
        )

    # ========================================================
    # Restart
    # ========================================================

    def restart_game(self):
        self.start_game(
            self.current_mode
        )

    # ========================================================
    # Top Scores - Difficulty Selection
    # ========================================================

    def show_difficulty_scores(self):
        self.clear_screen()

        frame = tk.Frame(
            self.root,
            bg=self.bg_color
        )
        frame.pack(
            fill="both",
            expand=True
        )

        title = tk.Label(
            frame,
            text="Top Scores",
            font=("Segoe UI", 30, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        title.pack(
            pady=(75, 10)
        )

        subtitle = tk.Label(
            frame,
            text="Choose a difficulty",
            font=("Segoe UI", 13),
            bg=self.bg_color,
            fg=self.secondary_text
        )
        subtitle.pack(
            pady=(0, 35)
        )

        for difficulty in DIFFICULTIES:

            button = self.create_button(
                frame,
                difficulty,
                lambda d=difficulty:
                    self.show_top_scores(d),
                width=22
            )

            button.pack(
                pady=7
            )

        back_button = self.create_button(
            frame,
            "← Back",
            self.show_main_menu,
            width=22
        )

        back_button.pack(
            pady=(25, 7)
        )

    # ========================================================
    # Top Scores
    # ========================================================

    def show_top_scores(self, difficulty):
        self.clear_screen()

        frame = tk.Frame(
            self.root,
            bg=self.bg_color
        )
        frame.pack(
            fill="both",
            expand=True
        )

        title = tk.Label(
            frame,
            text="Top Scores",
            font=("Segoe UI", 28, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        title.pack(
            pady=(35, 5)
        )

        difficulty_label = tk.Label(
            frame,
            text=difficulty,
            font=("Segoe UI", 13, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        difficulty_label.pack(
            pady=(0, 20)
        )

        cards_frame = tk.Frame(
            frame,
            bg=self.bg_color
        )
        cards_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=5
        )

        self.create_score_card(
            cards_frame,
            "SOLO",
            "solo",
            difficulty
        )

        self.create_score_card(
            cards_frame,
            "TWO PLAYERS",
            "vs",
            difficulty
        )

        self.create_score_card(
            cards_frame,
            "TIME CHALLENGE",
            "challenge",
            difficulty
        )

        navigation_frame = tk.Frame(
            frame,
            bg=self.bg_color
        )
        navigation_frame.pack(
            pady=(5, 20)
        )

        back_button = self.create_button(
            navigation_frame,
            "← Back",
            self.show_difficulty_scores,
            width=18
        )
        back_button.pack(
            side="left",
            padx=5
        )

        menu_button = self.create_button(
            navigation_frame,
            "Main Menu",
            self.show_main_menu,
            width=18
        )
        menu_button.pack(
            side="left",
            padx=5
        )

    # ========================================================
    # Score Card
    # ========================================================

    def create_score_card(
            self,
            parent,
            title,
            mode,
            difficulty
        ):
        card = tk.Frame(
            parent,
            bg=self.card_color,
            width=275,
            height=300,
            highlightbackground=self.border_color,
            highlightthickness=1
        )

        card.pack(
            side="left",
            padx=5,
            pady=5
        )

        # Prevent the card from resizing to its contents
        card.pack_propagate(False)

        title_label = tk.Label(
            card,
            text=title,
            font=("Segoe UI", 12, "bold"),
            bg=self.card_color,
            fg=self.text_color
        )

        title_label.pack(
            pady=(15, 8)
        )

        scores = self.scoreboard.get_scores(
            difficulty,
            mode
        )

        if not scores:

            empty_label = tk.Label(
                card,
                text="No scores yet",
                font=("Segoe UI", 10),
                bg=self.card_color,
                fg=self.secondary_text
            )

            empty_label.pack(
                pady=30
            )

            return

        if mode == "challenge":

            self.create_challenge_score_table(
                card,
                scores
            )

        else:

            self.create_standard_score_table(
                card,
                scores
            )

    def create_standard_score_table(
            self,
            parent,
            scores
        ):
        table_frame = tk.Frame(
            parent,
            bg=self.card_color
        )

        table_frame.pack(
            fill="x",
            padx=15,
            pady=5
        )

        header = tk.Label(
            table_frame,
            text=f"{'#':<4}{'PLAYER':<14}{'ATT.':<8}{'TIME':>8}",
            font=("Consolas", 10, "bold"),
            bg=self.card_color,
            fg=self.secondary_text,
            anchor="w"
        )

        header.pack(
            fill="x",
            pady=(0, 8)
        )

        for index, score in enumerate(scores, 1):

            row = tk.Label(
                table_frame,
                text=(
                    f"{index:<4}"
                    f"{score['name']:<14}"
                    f"{score['attempts']:<8}"
                    f"{score['time']:>7.2f}s"
                ),
                font=("Consolas", 10),
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            )

            row.pack(
                fill="x",
                pady=2
            )

    def create_challenge_score_table(
            self,
            parent,
            scores
        ):
        table_frame = tk.Frame(
            parent,
            bg=self.card_color
        )

        table_frame.pack(
            fill="x",
            padx=15,
            pady=5
        )

        header = tk.Label(
            table_frame,
            text=f"{'#':<4}{'PLAYER':<14}{'TIME':>8}{'ATT.':>8}",
            font=("Consolas", 10, "bold"),
            bg=self.card_color,
            fg=self.secondary_text,
            anchor="w"
        )

        header.pack(
            fill="x",
            pady=(0, 8)
        )

        for index, score in enumerate(scores, 1):

            row = tk.Label(
                table_frame,
                text=(
                    f"{index:<4}"
                    f"{score['name']:<14}"
                    f"{score['time']:>7.2f}s"
                    f"{score['attempts']:>8}"
                ),
                font=("Consolas", 10),
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            )

            row.pack(
                fill="x",
                pady=2
            )

# Run Application

if __name__ == "__main__":
    root = tk.Tk()

    game = MemoryGame(root)

    root.mainloop()