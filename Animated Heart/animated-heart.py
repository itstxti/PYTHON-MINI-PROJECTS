import math
import os
import random
import time
import tkinter as tk
from tkinter import font as tkfont
import wave
import winsound
import ctypes

from dataclasses import dataclass


# ============================================================
# CONFIGURATION
# ============================================================

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

BACKGROUND_COLOR = "#000000"

FPS = 60
FULLSCREEN = True

SOUNDS_DIR = os.path.join(
    os.path.dirname(__file__),
    "sounds"
)

KEY_SOUND = os.path.join(
    SOUNDS_DIR,
    "enter.wav"
)

LOVE_SOUND = os.path.join(
    SOUNDS_DIR,
    "love_you.wav"
)

MENU_SOUND = os.path.join(
    SOUNDS_DIR,
    "menu.wav"
)

HEART_START_DELAY = 1000


# ============================================================
# HEART ANIMATION TIMING
# ============================================================
# All values are percentages of the audio duration.

OUTLINE_END_PERCENT = 0.20

FILL_START_PERCENT = 0.18

FILL_END_PERCENT = 0.50

CENTER_START_PERCENT = 0.40


# ============================================================
# HEART CONFIGURATION
# ============================================================

SCALE = 20

OUTLINE_PARTICLES = 150
FILL_PARTICLES = 90

OUTLINE_MIN_GAP = 30
FILL_MIN_GAP = 25

WORDS = [
    "love you",
    "Love You",
    "LOVE YOU"
]

CENTER_TEXT = " I Love You "


# ============================================================
# COLORS
# ============================================================

COLORS = [
    "#8B0000",
    "#A00000",
    "#B00000",
    "#C00000",
    "#D00000",
    "#E00000",
    "#FF0000",
    "#FF1A1A",
    "#FF3333"
]

CENTER_COLOR = "#FFF5F5EA"


# ============================================================
# FONTS
# ============================================================

FONT_DIR = os.path.join(
    os.path.dirname(__file__),
    "font"
)


# ------------------------------------------------------------
# FONT FAMILIES
# ------------------------------------------------------------

OUTLINE_FONT_FAMILY = "Matrix"
FILL_FONT_FAMILY = "Matrix"
CENTER_FONT_FAMILY = "Matrix"

MATRIX_FONT_FAMILY = "Matrix"

INTRO_TITLE_FONT_FAMILY = "Matrix"
INTRO_INFO_FONT_FAMILY = "Matrix"

TRANSITION_TITLE_FONT_FAMILY = "Matrix"
TRANSITION_INFO_FONT_FAMILY = "Matrix"


# ------------------------------------------------------------
# FONT FILES
# ------------------------------------------------------------

OUTLINE_FONT_FILE = "matrix.ttf"
FILL_FONT_FILE = "matrix.ttf"
CENTER_FONT_FILE = "matrix.ttf"

MATRIX_FONT_FILE = "matrix.ttf"

INTRO_TITLE_FONT_FILE = "matrix.ttf"
INTRO_INFO_FONT_FILE = "matrix.ttf"

TRANSITION_TITLE_FONT_FILE = "matrix.ttf"
TRANSITION_INFO_FONT_FILE = "matrix.ttf"


# ------------------------------------------------------------
# FONT SIZES
# ------------------------------------------------------------

OUTLINE_FONT_SIZE = 14
FILL_FONT_SIZE = 10
CENTER_FONT_SIZE = 38

MATRIX_FONT_SIZE = 13

# Arial font used only for Matrix glitch characters
MATRIX_GLITCH_FONT_SIZE = 13

INTRO_TITLE_FONT_SIZE = 48
INTRO_INFO_FONT_SIZE = 18

TRANSITION_TITLE_FONT_SIZE = 26
TRANSITION_INFO_FONT_SIZE = 18


# ------------------------------------------------------------
# FONT WEIGHTS
# ------------------------------------------------------------

OUTLINE_FONT_WEIGHT = "bold"
FILL_FONT_WEIGHT = "bold"
CENTER_FONT_WEIGHT = "bold"

MATRIX_FONT_WEIGHT = "bold"

# Arial glitch font
MATRIX_GLITCH_FONT_WEIGHT = "bold"

INTRO_TITLE_FONT_WEIGHT = "bold"
INTRO_INFO_FONT_WEIGHT = "normal"

TRANSITION_TITLE_FONT_WEIGHT = "bold"
TRANSITION_INFO_FONT_WEIGHT = "bold"


# ============================================================
# CUSTOM FONT LOADING
# ============================================================

_registered_fonts = []


def register_font(filename):

    path = os.path.join(
        FONT_DIR,
        filename
    )

    if not os.path.exists(path):

        print(
            f"Font not found: {path}"
        )

        return False

    try:

        AddFontResourceExW = (
            ctypes.windll.gdi32.AddFontResourceExW
        )

        AddFontResourceExW.argtypes = [
            ctypes.c_wchar_p,
            ctypes.c_uint,
            ctypes.c_void_p
        ]

        AddFontResourceExW.restype = ctypes.c_int

        # FR_PRIVATE:
        # Makes the font available to this process
        # without permanently installing it in Windows.

        FR_PRIVATE = 0x10

        result = AddFontResourceExW(
            path,
            FR_PRIVATE,
            0
        )

        if result == 0:

            print(
                f"Could not register font: {path}"
            )

            return False

        _registered_fonts.append(path)

        print(
            f"Font loaded: {filename}"
        )

        return True

    except Exception as error:

        print(
            f"Font loading error: {error}"
        )

        return False


def load_font(
    filename,
    family,
    size,
    weight="normal"
):

    loaded = register_font(
        filename
    )

    if not loaded:

        print(
            f"Using Arial fallback for: {filename}"
        )

        return tkfont.Font(
            family="Arial",
            size=size,
            weight=weight
        )

    return tkfont.Font(
        family=family,
        size=size,
        weight=weight
    )


# ============================================================
# FONT VARIABLES
# ============================================================

OUTLINE_FONT = None
FILL_FONT = None
CENTER_FONT = None

MATRIX_FONT = None

# Arial font used exclusively by glitch characters
MATRIX_GLITCH_FONT = None

INTRO_TITLE_FONT = None
INTRO_INFO_FONT = None

TRANSITION_TITLE_FONT = None
TRANSITION_INFO_FONT = None


# ============================================================
# PARTICLE FADE
# ============================================================

FADE_SPEED_MIN = 14
FADE_SPEED_RANDOM = 4


# ============================================================
# GLOW
# ============================================================

GLOW_ENABLED = True
GLOW_LAYERS = 3


# ============================================================
# MATRIX
# ============================================================

MATRIX_CHARACTERS = list(
    "ILOVEYOU"
)

MATRIX_COLUMN_WIDTH = 50

MATRIX_ROW_SPACING = 20

MATRIX_SPEED_MIN = 4
MATRIX_SPEED_MAX = 10

MATRIX_GLITCH_CHANCE = 0.012

MATRIX_GLITCH_MIN_FRAMES = 5
MATRIX_GLITCH_MAX_FRAMES = 10

MATRIX_GLITCH_CHARACTERS = (
    "!@#$%^&*+-=_<>?/\\|~"
    "[]{}()"
    "§±×÷"
)


# ============================================================
# HEART MATRIX
# ============================================================

HEART_MATRIX_SPEED_MIN = 3
HEART_MATRIX_SPEED_MAX = 8

HEART_MATRIX_DENSITY = 1.0
HEART_MATRIX_OPACITY = 0.55


# ============================================================
# PARTICLE
# ============================================================

@dataclass
class Particle:

    x: float
    y: float
    text: str

    color: str
    font: tuple

    order: int

    alpha: int = 0

    delay: int = 0

    flicker: float = 0.0

    canvas_ids: list = None

    def __post_init__(self):

        if self.canvas_ids is None:

            self.canvas_ids = []


# ============================================================
# AUDIO
# ============================================================

def get_wav_duration(path):

    try:

        with wave.open(path, "rb") as audio:

            frames = audio.getnframes()
            frame_rate = audio.getframerate()

            return frames / float(frame_rate)

    except Exception as error:

        print(
            "Could not read audio duration:",
            error
        )

        return 5.0


def play_sound(path, loop=False):

    try:

        flags = (
            winsound.SND_FILENAME
            | winsound.SND_ASYNC
        )

        if loop:

            flags |= winsound.SND_LOOP

        winsound.PlaySound(
            path,
            flags
        )

    except Exception as error:

        print(
            "Could not play sound:",
            error
        )


# ============================================================
# HEART EQUATION
# ============================================================

def heart_function(x, y):

    return (
        (x * x + y * y - 1) ** 3
        - x * x * y ** 3
    )


def heart_point(t):

    x = (
        16
        * math.sin(t) ** 3
    )

    y = (
        13 * math.cos(t)
        - 5 * math.cos(2 * t)
        - 2 * math.cos(3 * t)
        - math.cos(4 * t)
    )

    return x, y


# ============================================================
# BUILD OUTLINE PARTICLES
# ============================================================

def build_outline_particles(
    count,
    min_gap,
    center_x,
    center_y
):

    candidates = []

    samples = 5000

    for i in range(samples):

        t = (
            2
            * math.pi
            * i
            / samples
        )

        x, y = heart_point(t)

        candidates.append(
            (x, y)
        )

    selected = []

    for point in candidates:

        if not selected:

            selected.append(point)

            continue

        too_close = False

        for existing in selected:

            distance = math.sqrt(
                (
                    point[0]
                    - existing[0]
                ) ** 2
                +
                (
                    point[1]
                    - existing[1]
                ) ** 2
            )

            if distance < min_gap / SCALE:

                too_close = True

                break

        if not too_close:

            selected.append(point)

        if len(selected) >= count:

            break

    random.shuffle(
        selected
    )

    particles = []

    for index, (x, y) in enumerate(selected):

        screen_x = (
            center_x
            + x * SCALE
        )

        screen_y = (
            center_y
            - y * SCALE
        )

        particles.append(
            Particle(
                x=screen_x,
                y=screen_y,
                text=random.choice(WORDS),
                color=random.choice(COLORS),
                font=OUTLINE_FONT,
                order=index,
                flicker=random.uniform(
                    0,
                    math.pi * 2
                )
            )
        )

    particles.sort(
        key=lambda p:
        math.atan2(
            -(
                p.y
                - center_y
            ),
            p.x
            - center_x
        )
    )

    for index, particle in enumerate(particles):

        particle.order = index

    return particles


# ============================================================
# BUILD FILL PARTICLES
# ============================================================

def build_fill_particles(
    count,
    min_gap,
    center_x,
    center_y
):

    selected = []

    attempts = 0
    max_attempts = count * 300

    HEART_WIDTH = 16
    HEART_HEIGHT = 13

    INNER_SCALE = 0.88

    while (
        len(selected) < count
        and attempts < max_attempts
    ):

        attempts += 1

        x = random.uniform(
            -HEART_WIDTH * INNER_SCALE,
            HEART_WIDTH * INNER_SCALE
        )

        y = random.uniform(
            -HEART_HEIGHT * INNER_SCALE,
            HEART_HEIGHT * INNER_SCALE
        )

        screen_x = (
            center_x
            + x * SCALE
        )

        screen_y = (
            center_y
            - y * SCALE
        )

        normalized_x = (
            x / INNER_SCALE
        )

        normalized_y = (
            y / INNER_SCALE
        )

        inside = False

        samples = 120

        previous_x, previous_y = heart_point(0)

        for i in range(1, samples + 1):

            t = (
                2
                * math.pi
                * i
                / samples
            )

            current_x, current_y = (
                heart_point(t)
            )

            if (
                (previous_y > normalized_y)
                != (current_y > normalized_y)
            ):

                intersection_x = (
                    previous_x
                    + (
                        (
                            normalized_y
                            - previous_y
                        )
                        / (
                            current_y
                            - previous_y
                        )
                    )
                    * (
                        current_x
                        - previous_x
                    )
                )

                if normalized_x < intersection_x:

                    inside = not inside

            previous_x = current_x
            previous_y = current_y

        if not inside:

            continue

        valid = True

        for existing in selected:

            distance = math.sqrt(
                (x - existing[0]) ** 2
                + (y - existing[1]) ** 2
            )

            if distance < min_gap / SCALE:

                valid = False

                break

        if not valid:

            continue

        selected.append(
            (x, y)
        )

    particles = []

    random.shuffle(
        selected
    )

    for index, (x, y) in enumerate(selected):

        screen_x = (
            center_x
            + x * SCALE
        )

        screen_y = (
            center_y
            - y * SCALE
        )

        particles.append(
            Particle(
                x=screen_x,
                y=screen_y,
                text=random.choice(WORDS),
                color=random.choice(COLORS),
                font=FILL_FONT,
                order=index,
                flicker=random.uniform(
                    0,
                    math.pi * 2
                )
            )
        )

    return particles


# ============================================================
# LOVE HEART APPLICATION
# ============================================================

class LoveHeart:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "LOVE.EXE"
        )

        self.root.configure(
            bg=BACKGROUND_COLOR
        )

        if FULLSCREEN:

            self.root.attributes(
                "-fullscreen",
                True
            )

        else:

            self.root.geometry(
                f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
            )

        self.root.bind(
            "<Key>",
            self.handle_key
        )

        self.root.bind(
            "<Escape>",
            self.close
        )

        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg=BACKGROUND_COLOR,
            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        self.state = "intro"

        self.starting = False

        self.running = False

        self.frame = 0

        self.particles = []

        self.previous_center = None

        self.center_start = 0

        self.audio_duration = 5.0

        self.animation_end_frame = 1

        self.audio_start_time = None

        self.heart_center_x = 0
        self.heart_center_y = 0

        self.heart_matrix_columns = []

        self.matrix_columns = []

        self.root.update_idletasks()

        self.matrix_columns = (
            self.create_matrix_columns()
        )

        self.draw_intro()

        self.animate_matrix()

        play_sound(
            MENU_SOUND,
            loop=True
        )

    # ========================================================
    # KEY HANDLER
    # ========================================================

    def handle_key(self, event):

        if self.state != "intro":

            return

        if self.starting:

            return

        self.starting = True

        winsound.PlaySound(
            None,
            0
        )

        play_sound(
            KEY_SOUND
        )

        self.show_transition()

    # ========================================================
    # MATRIX COLUMNS
    # ========================================================

    def create_matrix_columns(
        self,
        heart_mode=False
    ):

        width = self.canvas.winfo_width()

        if width <= 1:

            width = self.root.winfo_width()

        if width <= 1:

            width = WINDOW_WIDTH

        column_count = max(
            1,
            int(
                width
                / MATRIX_COLUMN_WIDTH
            )
            + 1
        )

        columns = []

        for index in range(column_count):

            letters = []

            for character in MATRIX_CHARACTERS:

                letters.append(
                    {
                        "character": character,
                        "glitch_character": None,
                        "glitch_frames": 0
                    }
                )

            columns.append(
                {
                    "x":
                        index
                        * MATRIX_COLUMN_WIDTH,

                    "y":
                        random.randint(
                            -WINDOW_HEIGHT,
                            0
                        ),

                    "speed":
                        random.randint(
                            HEART_MATRIX_SPEED_MIN
                            if heart_mode
                            else MATRIX_SPEED_MIN,

                            HEART_MATRIX_SPEED_MAX
                            if heart_mode
                            else MATRIX_SPEED_MAX
                        ),

                    "letters":
                        letters
                }
            )

        return columns

    # ========================================================
    # MATRIX
    # ========================================================

    def draw_matrix(
        self,
        heart_mode=False
    ):

        self.canvas.delete(
            "matrix"
        )

        width = self.root.winfo_width()

        height = self.root.winfo_height()

        if width <= 1:

            width = WINDOW_WIDTH

        if height <= 1:

            height = WINDOW_HEIGHT

        columns = (
            self.heart_matrix_columns
            if heart_mode
            else self.matrix_columns
        )

        for column in columns:

            x = column["x"]

            y = column["y"]

            speed = column["speed"]

            letters = column["letters"]

            for index, letter_data in enumerate(
                letters
            ):

                char_y = (
                    y
                    + index
                    * MATRIX_ROW_SPACING
                )

                if (
                    char_y < -MATRIX_ROW_SPACING
                    or char_y > height
                    + MATRIX_ROW_SPACING
                ):

                    continue

                if (
                    letter_data["glitch_frames"] <= 0
                    and random.random()
                    < MATRIX_GLITCH_CHANCE
                ):

                    letter_data[
                        "glitch_character"
                    ] = random.choice(
                        MATRIX_GLITCH_CHARACTERS
                    )

                    letter_data[
                        "glitch_frames"
                    ] = random.randint(
                        MATRIX_GLITCH_MIN_FRAMES,
                        MATRIX_GLITCH_MAX_FRAMES
                    )

                # ------------------------------------------------
                # Determine character and font
                # ------------------------------------------------

                if (
                    letter_data["glitch_frames"]
                    > 0
                ):

                    character = (
                        letter_data[
                            "glitch_character"
                        ]
                    )

                    color = "#FF3030"

                    font = MATRIX_GLITCH_FONT

                    letter_data[
                        "glitch_frames"
                    ] -= 1

                else:

                    character = (
                        letter_data[
                            "character"
                        ]
                    )

                    font = MATRIX_FONT

                    if index == 0:

                        color = "#D81010"

                    else:

                        fade_colors = [
                            "#C41010",
                            "#AE0D0D",
                            "#980B0B",
                            "#820909",
                            "#6C0707",
                            "#560505",
                            "#400303"
                        ]

                        color = fade_colors[
                            min(
                                index - 1,
                                len(
                                    fade_colors
                                ) - 1
                            )
                        ]

                self.canvas.create_text(
                    x,
                    char_y,
                    text=character,
                    fill=color,
                    font=font,
                    anchor="center",
                    tags="matrix"
                )

            column["y"] += speed

            sequence_height = (
                len(MATRIX_CHARACTERS)
                * MATRIX_ROW_SPACING
            )

            if (
                column["y"]
                - sequence_height
                > height
            ):

                column["y"] = random.randint(
                    -(
                        height
                        + sequence_height
                    ),
                    -MATRIX_ROW_SPACING
                )

                column["speed"] = random.randint(
                    HEART_MATRIX_SPEED_MIN
                    if heart_mode
                    else MATRIX_SPEED_MIN,

                    HEART_MATRIX_SPEED_MAX
                    if heart_mode
                    else MATRIX_SPEED_MAX
                )

                for letter_data in column["letters"]:

                    letter_data[
                        "glitch_character"
                    ] = None

                    letter_data[
                        "glitch_frames"
                    ] = 0

    # ========================================================
    # INTRO MATRIX
    # ========================================================

    def animate_matrix(self):

        if self.state != "intro":

            return

        self.draw_matrix(
            heart_mode=False
        )

        self.draw_intro_text()

        self.root.after(
            int(1000 / FPS),
            self.animate_matrix
        )

    # ========================================================
    # INTRO SCREEN
    # ========================================================

    def draw_intro(self):

        self.canvas.delete(
            "all"
        )

        self.draw_matrix(
            heart_mode=False
        )

        self.draw_intro_text()

    def draw_intro_text(self):

        self.canvas.delete(
            "intro_text"
        )

        center_x = (
            self.root.winfo_width()
            / 2
        )

        center_y = (
            self.root.winfo_height()
            / 2
        )

        # LOVE
        self.canvas.create_text(
            center_x - 10,
            center_y - 80,
            text="LOVE",
            fill="#FF0000",
            font=INTRO_TITLE_FONT,
            anchor="e",
            tags="intro_text"
        )

        # .
        self.canvas.create_text(
            center_x,
            center_y - 85,
            text=".",
            fill="#FF0000",
            font=("Arial", 48, "bold"),
            anchor="w",
            tags="intro_text"
        )

        # EXE
        self.canvas.create_text(
            center_x + 25,
            center_y - 80,
            text="EXE",
            fill="#FF0000",
            font=INTRO_TITLE_FONT,
            anchor="w",
            tags="intro_text"
        )

        self.canvas.create_text(
            center_x,
            center_y,
            text="[ SYSTEM READY ]",
            fill="#FFFFFF",
            font=INTRO_INFO_FONT,
            anchor="center",
            tags="intro_text"
        )

        self.canvas.create_text(
            center_x,
            center_y + 70,
            text="[ PRESS ANY KEY ]",
            fill="#FF3333",
            font=INTRO_INFO_FONT,
            anchor="center",
            tags="intro_text"
        )

    # ========================================================
    # TRANSITION SCREEN
    # ========================================================

    def show_transition(self):

        self.state = "transition"

        self.canvas.delete(
            "all"
        )

        self.draw_matrix(
            heart_mode=False
        )

        center_x = (
            self.root.winfo_width()
            / 2
        )

        center_y = (
            self.root.winfo_height()
            / 2
        )

        self.canvas.create_text(
            center_x,
            center_y - 120,
            text="CONNECTION ESTABLISHED",
            fill="#FF0000",
            font=TRANSITION_TITLE_FONT,
            anchor="center"
        )

        self.canvas.create_text(
            center_x,
            center_y - 40,
            text="> ACCESS GRANTED",
            fill="#FF3333",
            font=TRANSITION_INFO_FONT,
            anchor="center"
        )

        self.canvas.create_text(
            center_x,
            center_y + 10,
            text="> INITIALIZING...",
            fill="#FF3333",
            font=TRANSITION_INFO_FONT,
            anchor="center"
        )

        self.canvas.create_text(
            center_x,
            center_y + 60,
            text="> PLEASE WAIT...",
            fill="#FF3333",
            font=TRANSITION_INFO_FONT,
            anchor="center"
        )

        bar_width = 420

        bar_height = 18

        bar_x = (
            center_x
            - bar_width / 2
        )

        bar_y = (
            center_y
            + 120
        )

        self.canvas.create_rectangle(
            bar_x,
            bar_y,
            bar_x + bar_width,
            bar_y + bar_height,
            outline="#660000",
            width=2
        )

        self.canvas.create_rectangle(
            bar_x + 4,
            bar_y + 4,
            bar_x + bar_width - 4,
            bar_y + bar_height - 4,
            fill="#990000",
            outline=""
        )

        self.root.after(
            HEART_START_DELAY,
            self.start_animation
        )

    # ========================================================
    # START HEART ANIMATION
    # ========================================================

    def start_animation(self):

        self.starting = False

        self.state = "animation"

        self.canvas.delete(
            "all"
        )

        self.frame = 0

        self.running = True

        self.previous_center = None

        canvas_width = self.canvas.winfo_width()

        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1:

            canvas_width = WINDOW_WIDTH

        if canvas_height <= 1:

            canvas_height = WINDOW_HEIGHT

        self.heart_center_x = (
            canvas_width / 2
        )

        self.heart_center_y = (
            canvas_height / 2
        )

        self.audio_duration = (
            get_wav_duration(
                LOVE_SOUND
            )
        )

        self.animation_end_frame = max(
            1,
            round(
                self.audio_duration
                * FPS
            )
        )

        self.heart_matrix_columns = (
            self.create_matrix_columns(
                heart_mode=True
            )
        )

        self.animate_heart_matrix()

        self.outline = (
            build_outline_particles(
                OUTLINE_PARTICLES,
                OUTLINE_MIN_GAP,
                self.heart_center_x,
                self.heart_center_y
            )
        )

        self.fill = (
            build_fill_particles(
                FILL_PARTICLES,
                FILL_MIN_GAP,
                self.heart_center_x,
                self.heart_center_y
            )
        )

        total_frames = (
            self.animation_end_frame
        )

        outline_span = (
            max(
                (
                    p.order
                    for p in self.outline
                ),
                default=0
            )
        )

        outline_end_frame = int(
            total_frames
            * OUTLINE_END_PERCENT
        )

        self.frames_per_step = (
            outline_end_frame
            / max(
                1,
                outline_span
            )
        )

        for particle in self.outline:

            particle.delay = int(
                particle.order
                * self.frames_per_step
            )

        self.fill_start_frame = int(
            total_frames
            * FILL_START_PERCENT
        )

        fill_end_frame = int(
            total_frames
            * FILL_END_PERCENT
        )

        fill_available = max(
            1,
            fill_end_frame
            - self.fill_start_frame
        )

        fill_span = (
            max(
                (
                    p.order
                    for p in self.fill
                ),
                default=0
            )
        )

        for particle in self.fill:

            normalized = (
                particle.order
                / max(
                    1,
                    fill_span
                )
            )

            particle.delay = (
                self.fill_start_frame
                + int(
                    normalized
                    * fill_available
                )
            )

        self.center_start = int(
            total_frames
            * CENTER_START_PERCENT
        )

        self.particles = (
            self.outline
            + self.fill
        )

        self.audio_start_time = (
            time.perf_counter()
        )

        play_sound(
            LOVE_SOUND
        )

        self.animate()

    # ========================================================
    # HEART MATRIX
    # ========================================================

    def animate_heart_matrix(self):

        if self.state != "animation":

            return

        self.draw_matrix(
            heart_mode=True
        )

        self.root.after(
            int(1000 / FPS),
            self.animate_heart_matrix
        )

    # ========================================================
    # CREATE PARTICLE
    # ========================================================

    def create_particle(
        self,
        particle
    ):

        particle.canvas_ids = []

        if GLOW_ENABLED:

            for layer in range(
                GLOW_LAYERS,
                0,
                -1
            ):

                size = (
                    particle.font.cget("size")
                    + layer * 4
                )

                glow_font = tkfont.Font(
                    font=particle.font,
                    size=size
                )

                if layer == 3:

                    glow_color = "#220000"

                elif layer == 2:

                    glow_color = "#330000"

                else:

                    glow_color = "#550000"

                glow_id = (
                    self.canvas.create_text(
                        particle.x,
                        particle.y,
                        text=particle.text,
                        font=glow_font,
                        fill=glow_color,
                        anchor="center"
                    )
                )

                particle.canvas_ids.append(
                    glow_id
                )

        text_id = (
            self.canvas.create_text(
                particle.x,
                particle.y,
                text=particle.text,
                font=particle.font,
                fill=particle.color,
                anchor="center"
            )
        )

        particle.canvas_ids.append(
            text_id
        )

    # ========================================================
    # PARTICLE ALPHA
    # ========================================================

    def set_particle_alpha(
        self,
        particle,
        alpha
    ):

        if not particle.canvas_ids:

            return

        value = (
            max(
                0,
                min(
                    255,
                    alpha
                )
            )
            / 255
        )

        if GLOW_ENABLED:

            for index, canvas_id in enumerate(
                particle.canvas_ids[:-1]
            ):

                if index == 0:

                    base = 20

                elif index == 1:

                    base = 30

                else:

                    base = 50

                red = int(
                    base * value
                )

                color = (
                    f"#{red:02x}0000"
                )

                self.canvas.itemconfig(
                    canvas_id,
                    fill=color
                )

        main_id = (
            particle.canvas_ids[-1]
        )

        hex_color = (
            particle.color
            .replace("#", "")
        )

        red = int(
            int(
                hex_color[0:2],
                16
            )
            * value
        )

        green = int(
            int(
                hex_color[2:4],
                16
            )
            * value
        )

        blue = int(
            int(
                hex_color[4:6],
                16
            )
            * value
        )

        color = (
            f"#{red:02x}"
            f"{green:02x}"
            f"{blue:02x}"
        )

        self.canvas.itemconfig(
            main_id,
            fill=color
        )

    # ========================================================
    # CENTER TEXT
    # ========================================================

    def draw_center_text(self):

        if (
            self.frame
            <= self.center_start
        ):

            return

        progress = min(
            1.0,
            (
                self.frame
                - self.center_start
            ) / 60
        )

        center_alpha = int(
            255
            * (
                1
                - math.exp(
                    -progress * 8
                )
            )
        )

        size = CENTER_FONT.cget(
            "size"
        )

        if self.previous_center:

            self.canvas.delete(
                self.previous_center
            )

        glow_font = tkfont.Font(
            font=CENTER_FONT,
            size=size + 14
        )

        glow_id = (
            self.canvas.create_text(
                self.heart_center_x,
                self.heart_center_y,
                text=CENTER_TEXT,
                font=glow_font,
                fill="#440000",
                anchor="center"
            )
        )

        value = (
            center_alpha / 255
        )

        red = int(
            255 * value
            + 80 * (1 - value)
        )

        green = int(
            245 * value
        )

        blue = int(
            245 * value
        )

        color = (
            f"#{red:02x}"
            f"{green:02x}"
            f"{blue:02x}"
        )

        center_id = (
            self.canvas.create_text(
                self.heart_center_x,
                self.heart_center_y,
                text=CENTER_TEXT,
                font=CENTER_FONT,
                fill=color,
                anchor="center"
            )
        )

        self.canvas.tag_lower(
            glow_id,
            center_id
        )

        self.previous_center = (
            center_id
        )

    # ========================================================
    # ANIMATE
    # ========================================================

    def animate(self):

        if not self.running:

            return

        self.frame += 1

        for particle in self.particles:

            if (
                self.frame
                > particle.delay
                and particle.alpha < 255
            ):

                particle.alpha = min(
                    255,
                    particle.alpha
                    + FADE_SPEED_MIN
                    + random.randint(
                        0,
                        FADE_SPEED_RANDOM
                    )
                )

                if not particle.canvas_ids:

                    self.create_particle(
                        particle
                    )

            if particle.alpha >= 255:

                flick = (
                    0.75
                    + 0.25
                    * math.sin(
                        self.frame
                        * 0.04
                        + particle.flicker
                    )
                )

            else:

                flick = 1.0

            alpha = int(
                particle.alpha
                * flick
            )

            if particle.canvas_ids:

                self.set_particle_alpha(
                    particle,
                    alpha
                )

        self.draw_center_text()

        if self.animation_finished():

            time.sleep(1)

            self.show_finished()

            return

        self.root.after(
            int(1000 / FPS),
            self.animate
        )

    # ========================================================
    # FINISH CHECK
    # ========================================================

    def animation_finished(self):

        if self.audio_start_time is not None:

            elapsed = (
                time.perf_counter()
                - self.audio_start_time
            )

            return (
                elapsed
                >= self.audio_duration
            )

        return (
            self.frame
            >= self.animation_end_frame
        )

    # ========================================================
    # FINISHED
    # ========================================================

    def show_finished(self):

        self.running = False

        self.root.destroy()

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self, event=None):

        self.running = False

        try:

            winsound.PlaySound(
                None,
                0
            )

        except Exception:

            pass

        self.root.destroy()


# ============================================================
# MAIN
# ============================================================

def main():

    root = tk.Tk()

    # --------------------------------------------------------
    # Load fonts
    # --------------------------------------------------------

    global OUTLINE_FONT
    global FILL_FONT
    global CENTER_FONT

    global MATRIX_FONT
    global MATRIX_GLITCH_FONT

    global INTRO_TITLE_FONT
    global INTRO_INFO_FONT

    global TRANSITION_TITLE_FONT
    global TRANSITION_INFO_FONT

    OUTLINE_FONT = load_font(
        OUTLINE_FONT_FILE,
        OUTLINE_FONT_FAMILY,
        OUTLINE_FONT_SIZE,
        OUTLINE_FONT_WEIGHT
    )

    FILL_FONT = load_font(
        FILL_FONT_FILE,
        FILL_FONT_FAMILY,
        FILL_FONT_SIZE,
        FILL_FONT_WEIGHT
    )

    CENTER_FONT = load_font(
        CENTER_FONT_FILE,
        CENTER_FONT_FAMILY,
        CENTER_FONT_SIZE,
        CENTER_FONT_WEIGHT
    )

    MATRIX_FONT = load_font(
        MATRIX_FONT_FILE,
        MATRIX_FONT_FAMILY,
        MATRIX_FONT_SIZE,
        MATRIX_FONT_WEIGHT
    )

    # --------------------------------------------------------
    # Matrix glitch font
    # Uses Arial directly — no custom font loading required.
    # --------------------------------------------------------

    MATRIX_GLITCH_FONT = tkfont.Font(
        family="Arial",
        size=MATRIX_GLITCH_FONT_SIZE,
        weight=MATRIX_GLITCH_FONT_WEIGHT
    )

    INTRO_TITLE_FONT = load_font(
        INTRO_TITLE_FONT_FILE,
        INTRO_TITLE_FONT_FAMILY,
        INTRO_TITLE_FONT_SIZE,
        INTRO_TITLE_FONT_WEIGHT
    )

    INTRO_INFO_FONT = load_font(
        INTRO_INFO_FONT_FILE,
        INTRO_INFO_FONT_FAMILY,
        INTRO_INFO_FONT_SIZE,
        INTRO_INFO_FONT_WEIGHT
    )

    TRANSITION_TITLE_FONT = load_font(
        TRANSITION_TITLE_FONT_FILE,
        TRANSITION_TITLE_FONT_FAMILY,
        TRANSITION_TITLE_FONT_SIZE,
        TRANSITION_TITLE_FONT_WEIGHT
    )

    TRANSITION_INFO_FONT = load_font(
        TRANSITION_INFO_FONT_FILE,
        TRANSITION_INFO_FONT_FAMILY,
        TRANSITION_INFO_FONT_SIZE,
        TRANSITION_INFO_FONT_WEIGHT
    )

    LoveHeart(
        root
    )

    root.mainloop()


if __name__ == "__main__":

    main()