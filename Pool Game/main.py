import math
import pygame
import os

from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    TABLE_X,
    TABLE_Y,
    TABLE_WIDTH,
    TABLE_HEIGHT,
    BALL_RADIUS,
    BALL_RESTITUTION
)

from ball import Ball
from table import Table
from physics import (
    update_physics,
    all_balls_stopped
)
from ai import PoolAI


# =========================================================
# INITIALIZATION
# =========================================================

pygame.init()

try:

    pygame.mixer.init()

    mixer_available = True

except pygame.error:

    mixer_available = False


screen = pygame.display.set_mode(
    (
        WINDOW_WIDTH,
        WINDOW_HEIGHT
    )
)

pygame.display.set_caption(
    "POOL GAME"
)

clock = pygame.time.Clock()


# =========================================================
# COLORS
# =========================================================

BACKGROUND = (18, 28, 32)

YELLOW = (255, 220, 0)
ORANGE = (255, 150, 0)

WHITE = (245, 245, 245)
GREY = (210, 210, 210)

RED = (220, 70, 70)

# HUD
HUD_BACKGROUND = (12, 20, 24)
HUD_BORDER = (55, 55, 60)

TEXT_PRIMARY = (245, 245, 245)
TEXT_SECONDARY = (145, 145, 150)

SOLID_COLOR = (255, 190, 70)
STRIPE_COLOR = (120, 180, 255)

PANEL_BACKGROUND = (12, 12, 15)
PANEL_BORDER = (70, 70, 75)

STATUS_GREEN = (100, 220, 150)
STATUS_BLUE = (120, 180, 255)

# Empty ball silhouette
EMPTY_BALL_FILL = (20, 20, 23)
EMPTY_BALL_BORDER = (85, 85, 90)
EMPTY_BALL_INNER = (48, 48, 52)


# =========================================================
# MENU COLORS
# =========================================================

MENU_OVERLAY = (0, 0, 0, 205)

MENU_PANEL = (10, 10, 13, 245)
MENU_PANEL_BORDER = (55, 55, 62)

MENU_SELECTED = (255, 220, 0)
MENU_NORMAL = (185, 185, 190)

MENU_MUTED = (110, 110, 118)

SETTINGS_TRACK = (38, 38, 43)
SETTINGS_FILL = (135, 135, 140)


# =========================================================
# TABLE
# =========================================================

table = Table(
    screen
)
# =========================================================
# BALL COLORS
# =========================================================

BALL_COLORS = {
    1: (245, 205, 40),
    2: (40, 80, 210),
    3: (210, 45, 45),
    4: (125, 50, 170),
    5: (235, 100, 35),
    6: (40, 150, 70),
    7: (125, 45, 35),

    9: (245, 205, 40),
    10: (40, 80, 210),
    11: (210, 45, 45),
    12: (125, 50, 170),
    13: (235, 100, 35),
    14: (40, 150, 70),
    15: (125, 45, 35)
}


# =========================================================
# CREATE BALLS
# =========================================================

balls = []

cue_ball = Ball(
    TABLE_X + TABLE_WIDTH * 0.25,
    TABLE_Y + TABLE_HEIGHT / 2,
    (245, 245, 245),
    is_cue=True
)

balls.append(cue_ball)


# =========================================================
# RACK
# =========================================================

rack_x = (
    TABLE_X +
    TABLE_WIDTH * 0.68
)

rack_y = (
    TABLE_Y +
    TABLE_HEIGHT / 2
)

spacing = 23

rack_positions = []

for row in range(5):

    for column in range(row + 1):

        x = (
            rack_x +
            row * spacing * 0.866
        )

        y = (
            rack_y +
            (
                column -
                row / 2
            ) * spacing
        )

        rack_positions.append(
            (
                x,
                y
            )
        )


# Order of the balls inside the rack.
#
#                  1
#               10   2
#             3   8   11
#          12   4   9   5
#        6   13   7   14   15
#
# The 8-ball stays in the center and solids/stripes
# are mixed.

RACK_ORDER = [
    1,
    10, 2,
    3, 8, 11,
    12, 4, 9, 5,
    6, 13, 7, 14, 15
]


for number, position in zip(
    RACK_ORDER,
    rack_positions
):

    x, y = position

    color = BALL_COLORS.get(
        number,
        (20, 20, 20)
    )

    ball = Ball(
        x,
        y,
        color,
        number=number
    )

    balls.append(ball)


# =========================================================
# AI
# =========================================================

ai = PoolAI()


# =========================================================
# GAME STATE
# =========================================================

waiting_for_start = True

menu_selected = 0

menu_options = [
    "PLAY",
    "SETTINGS",
    "QUIT"
]

game_over = False
game_won = False
game_lost = False

game_over_selected = 0

game_over_options = [
    "PLAY AGAIN",
    "SETTINGS",
    "QUIT"
]


# =========================================================
# SETTINGS STATE
# =========================================================

settings_open = False

settings_selected = 0

settings_options = [
    "FULLSCREEN",
    "SOUND VOLUME",
    "MUSIC VOLUME",
    "BACK"
]

fullscreen_enabled = False

sound_volume = 100
music_volume = 100


# =========================================================
# AUDIO
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MUSIC_PATH = os.path.join(
    BASE_DIR,
    "assets",
    "music",
    "background.mp3"
)

MENU_MOVE_PATH = os.path.join(
    BASE_DIR,
    "assets",
    "sounds",
    "menu_move.mp3"
)

MENU_SELECT_PATH = os.path.join(
    BASE_DIR,
    "assets",
    "sounds",
    "menu_select.mp3"
)

MENU_PAUSE_PATH = os.path.join(
    BASE_DIR,
    "assets",
    "sounds",
    "menu_pause.mp3"
)

SHOT_PATH = os.path.join(
    BASE_DIR,
    "assets",
    "sounds",
    "shot.mp3"
)

BALL_HIT_PATH = os.path.join(
    BASE_DIR,
    "assets",
    "sounds",
    "ball_hit.mp3"
)

BALL_POCKET_PATH = os.path.join(
    BASE_DIR,
    "assets",
    "sounds",
    "ball_pocket.mp3"
)

menu_move_sound = None
menu_select_sound = None
menu_pause_sound = None

shot_sound = None
ball_hit_sound = None
ball_pocket_sound = None


if mixer_available:

    # -----------------------------------------------------
    # MENU MOVE
    # -----------------------------------------------------

    if os.path.exists(MENU_MOVE_PATH):

        try:

            menu_move_sound = pygame.mixer.Sound(
                MENU_MOVE_PATH
            )

            menu_move_sound.set_volume(
                sound_volume / 100
            )

        except pygame.error as error:

            print(
                f"Could not load menu move sound: {error}"
            )

    else:

        print(
            f"Menu move sound not found: {MENU_MOVE_PATH}"
        )

    # -----------------------------------------------------
    # MENU SELECT
    # -----------------------------------------------------

    if os.path.exists(MENU_SELECT_PATH):

        try:

            menu_select_sound = pygame.mixer.Sound(
                MENU_SELECT_PATH
            )

            menu_select_sound.set_volume(
                sound_volume / 100
            )

        except pygame.error as error:

            print(
                f"Could not load menu select sound: {error}"
            )

    else:

        print(
            f"Menu select sound not found: {MENU_SELECT_PATH}"
        )

    # -----------------------------------------------------
    # MENU PAUSE
    # -----------------------------------------------------

    if os.path.exists(MENU_PAUSE_PATH):

        try:

            menu_pause_sound = pygame.mixer.Sound(
                MENU_PAUSE_PATH
            )

            menu_pause_sound.set_volume(
                sound_volume / 100
            )

        except pygame.error as error:

            print(
                f"Could not load menu pause sound: {error}"
            )

    else:

        print(
            f"Menu pause sound not found: {MENU_PAUSE_PATH}"
        )

    # -----------------------------------------------------
    # SHOT
    # -----------------------------------------------------

    if os.path.exists(SHOT_PATH):

        try:

            shot_sound = pygame.mixer.Sound(
                SHOT_PATH
            )

            shot_sound.set_volume(
                sound_volume / 100
            )

        except pygame.error as error:

            print(
                f"Could not load shot sound: {error}"
            )

    else:

        print(
            f"Shot sound not found: {SHOT_PATH}"
        )

    # -----------------------------------------------------
    # BALL HIT
    # -----------------------------------------------------

    if os.path.exists(BALL_HIT_PATH):

        try:

            ball_hit_sound = pygame.mixer.Sound(
                BALL_HIT_PATH
            )

            ball_hit_sound.set_volume(
                sound_volume / 100
            )

        except pygame.error as error:

            print(
                f"Could not load ball hit sound: {error}"
            )

    else:

        print(
            f"Ball hit sound not found: {BALL_HIT_PATH}"
        )

    # -----------------------------------------------------
    # BALL POCKET
    # -----------------------------------------------------

    if os.path.exists(BALL_POCKET_PATH):

        try:

            ball_pocket_sound = pygame.mixer.Sound(
                BALL_POCKET_PATH
            )

            ball_pocket_sound.set_volume(
                sound_volume / 100
            )

        except pygame.error as error:

            print(
                f"Could not load ball pocket sound: {error}"
            )

    else:

        print(
            f"Ball pocket sound not found: {BALL_POCKET_PATH}"
        )

    # -----------------------------------------------------
    # BACKGROUND MUSIC
    # -----------------------------------------------------

    if os.path.exists(MUSIC_PATH):

        try:

            pygame.mixer.music.load(
                MUSIC_PATH
            )

            pygame.mixer.music.set_volume(
                music_volume / 100
            )

            pygame.mixer.music.play(
                loops=-1
            )

        except pygame.error as error:

            print(
                f"Could not load background music: {error}"
            )

    else:

        print(
            f"Background music not found: {MUSIC_PATH}"
        )


def play_menu_move():

    if not mixer_available:
        return

    if menu_move_sound is None:
        return

    menu_move_sound.play()


def play_menu_select():

    if not mixer_available:
        return

    if menu_select_sound is None:
        return

    menu_select_sound.play()


def play_menu_pause():

    if not mixer_available:
        return

    if menu_pause_sound is None:
        return

    menu_pause_sound.play()


def play_shot():

    if not mixer_available:
        return

    if shot_sound is None:
        return

    shot_sound.play()


def play_ball_hit():

    if not mixer_available:
        return

    if ball_hit_sound is None:
        return

    ball_hit_sound.play()


def play_ball_pocket():

    if not mixer_available:
        return

    if ball_pocket_sound is None:
        return

    ball_pocket_sound.play()


def update_audio_volume():

    if not mixer_available:
        return

    pygame.mixer.music.set_volume(
        music_volume / 100
    )

    if menu_move_sound is not None:

        menu_move_sound.set_volume(
            sound_volume / 100
        )

    if menu_select_sound is not None:

        menu_select_sound.set_volume(
            sound_volume / 100
        )

    if menu_pause_sound is not None:

        menu_pause_sound.set_volume(
            sound_volume / 100
        )

    if shot_sound is not None:

        shot_sound.set_volume(
            sound_volume / 100
        )

    if ball_hit_sound is not None:

        ball_hit_sound.set_volume(
            sound_volume / 100
        )

    if ball_pocket_sound is not None:

        ball_pocket_sound.set_volume(
            sound_volume / 100
        )


# =========================================================
# PAUSE STATE
# =========================================================

paused = False

pause_selected = 0

pause_options = [
    "RESUME",
    "RESTART",
    "SETTINGS",
    "QUIT"
]


# =========================================================
# PLAYER STATE
# =========================================================

PLAYER_HUMAN = "player"
PLAYER_AI = "ai"

current_player = PLAYER_HUMAN

player_group = None
ai_group = None


# =========================================================
# SHOT STATE
# =========================================================

SHOT_PREVIEW_TIME = 700

shot_pending = False
shot_preview_timer = 0

current_shot = None

shot_in_progress = False

shot_shooter = None

shot_pocketed = []

human_shot_pending = False

shot_hit_sound_played = False


# =========================================================
# HUMAN PLAYER POWER
# =========================================================

HUMAN_MIN_POWER = 4.0
HUMAN_MAX_POWER = 18.0

human_power = 18.0


# =========================================================
# HUMAN AIM PREDICTION CACHE
# =========================================================

_aim_prediction_cache = None


def predict_cue_path(angle):

    global _aim_prediction_cache

    state_key = (
        round(angle, 4),
        round(human_power, 3),
        tuple(
            (
                ball.active,
                round(ball.x, 3),
                round(ball.y, 3)
            )
            for ball in balls
        )
    )

    if (
        _aim_prediction_cache is not None
        and _aim_prediction_cache[0] == state_key
    ):

        return _aim_prediction_cache[1]

    simulated_balls = [
        ball.clone()
        for ball in balls
    ]

    simulated_cue = next(
        ball
        for ball in simulated_balls
        if ball.is_cue
    )

    simulated_cue.shoot(
        angle,
        human_power
    )

    cue_path = [
        (
            simulated_cue.x,
            simulated_cue.y
        )
    ]

    for _ in range(500):

        update_physics(
            simulated_balls,
            table
        )

        cue_path.append(
            (
                simulated_cue.x,
                simulated_cue.y
            )
        )

        if not simulated_cue.active:
            break

        if all(
            ball.speed == 0
            for ball in simulated_balls
            if ball.active
        ):

            break

    prediction = (
        cue_path,
        simulated_cue.active
    )

    _aim_prediction_cache = (
        state_key,
        prediction
    )

    return prediction


# =========================================================
# GROUP HELPERS
# =========================================================

def solid_numbers():

    return set(
        range(1, 8)
    )


def stripe_numbers():

    return set(
        range(9, 16)
    )


def ball_group(number):

    if number in solid_numbers():

        return "solid"

    if number in stripe_numbers():

        return "stripe"

    if number == 8:

        return "eight"

    return None


def remaining_numbers(group):

    if group == "solid":

        numbers = solid_numbers()

    elif group == "stripe":

        numbers = stripe_numbers()

    else:

        return []

    return [
        ball.number
        for ball in balls
        if (
            ball.active
            and ball.number in numbers
        )
    ]


def all_group_cleared(group):

    return len(
        remaining_numbers(group)
    ) == 0


def allowed_target_numbers(group):

    if group is None:

        return [
            ball.number
            for ball in balls
            if (
                ball.active
                and not ball.is_cue
                and ball.number != 8
            )
        ]

    remaining = remaining_numbers(
        group
    )

    if not remaining:

        if any(
            ball.active
            and ball.number == 8
            for ball in balls
        ):

            return [8]

    return remaining


# =========================================================
# FIRST HIT VALIDATION
# =========================================================

def first_hit_is_legal(
    first_hit,
    shooter
):

    if first_hit is None:
        return False

    if first_hit == 8:

        shooter_group = (
            player_group
            if shooter == PLAYER_HUMAN
            else ai_group
        )

        if shooter_group is None:
            return False

        return all_group_cleared(
            shooter_group
        )

    shooter_group = (
        player_group
        if shooter == PLAYER_HUMAN
        else ai_group
    )

    if shooter_group is None:

        return first_hit in (
            solid_numbers() |
            stripe_numbers()
        )

    return (
        ball_group(first_hit) ==
        shooter_group
    )


# =========================================================
# TURN HELPERS
# =========================================================

def get_current_group():

    if current_player == PLAYER_HUMAN:

        return player_group

    return ai_group


def switch_player():

    global current_player

    if current_player == PLAYER_HUMAN:

        current_player = PLAYER_AI

    else:

        current_player = PLAYER_HUMAN


# =========================================================
# MENU DRAW HELPERS
# =========================================================

def draw_fullscreen_overlay():

    screen_width, screen_height = screen.get_size()

    overlay = pygame.Surface(
        (
            screen_width,
            screen_height
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        MENU_OVERLAY
    )

    screen.blit(
        overlay,
        (0, 0)
    )


def draw_menu_panel(
    width=520,
    height=430
):

    screen_width, screen_height = screen.get_size()

    panel_rect = pygame.Rect(
        (
            screen_width - width
        ) // 2,
        (
            screen_height - height
        ) // 2,
        width,
        height
    )

    panel = pygame.Surface(
        panel_rect.size,
        pygame.SRCALPHA
    )

    panel.fill(
        MENU_PANEL
    )

    pygame.draw.rect(
        panel,
        MENU_PANEL_BORDER,
        panel.get_rect(),
        1,
        border_radius=16
    )

    screen.blit(
        panel,
        panel_rect
    )

    return panel_rect


def draw_menu_title(
    text,
    y,
    size=48,
    color=WHITE
):

    font = pygame.font.SysFont(
        "arial",
        size,
        bold=True
    )

    surface = font.render(
        text,
        True,
        color
    )

    screen_width = screen.get_width()

    rect = surface.get_rect(
        center=(
            screen_width // 2,
            y
        )
    )

    screen.blit(
        surface,
        rect
    )


def draw_menu_option(
    text,
    y,
    selected=False,
    width=300
):

    font = pygame.font.SysFont(
        "arial",
        23,
        bold=True
    )

    screen_width = screen.get_width()

    if selected:

        color = MENU_SELECTED

        rect = pygame.Rect(
            (
                screen_width - width
            ) // 2,
            y - 22,
            width,
            44
        )

        pygame.draw.rect(
            screen,
            (
                25,
                25,
                28
            ),
            rect,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            (
                85,
                75,
                20
            ),
            rect,
            1,
            border_radius=8
        )

    else:

        color = MENU_NORMAL

    surface = font.render(
        text,
        True,
        color
    )

    text_rect = surface.get_rect(
        center=(
            screen_width // 2,
            y
        )
    )

    screen.blit(
        surface,
        text_rect
    )


def draw_menu_hint(
    text,
    y
):

    font = pygame.font.SysFont(
        "arial",
        14
    )

    surface = font.render(
        text,
        True,
        MENU_MUTED
    )

    screen_width = screen.get_width()

    rect = surface.get_rect(
        center=(
            screen_width // 2,
            y
        )
    )

    screen.blit(
        surface,
        rect
    )


# =========================================================
# START MENU
# =========================================================

def draw_start_screen():

    draw_fullscreen_overlay()

    panel_rect = draw_menu_panel(
        560,
        470
    )

    draw_menu_title(
        "POOL GAME",
        panel_rect.top + 82,
        52
    )

    draw_menu_title(
        "Player VS AI",
        panel_rect.top + 125,
        13,
        MENU_MUTED
    )

    option_start_y = (
        panel_rect.top + 205
    )

    for index, option in enumerate(
        menu_options
    ):

        draw_menu_option(
            option,
            option_start_y + index * 55,
            selected=(
                index == menu_selected
            )
        )

    draw_menu_hint(
        "↑ ↓  SELECT     ENTER  CONFIRM",
        panel_rect.bottom - 35
    )


# =========================================================
# SETTINGS HELPERS
# =========================================================

def draw_setting_value(
    text,
    x,
    y,
    selected=False
):

    font = pygame.font.SysFont(
        "arial",
        17,
        bold=True
    )

    color = (
        MENU_SELECTED
        if selected
        else TEXT_PRIMARY
    )

    surface = font.render(
        text,
        True,
        color
    )

    rect = surface.get_rect(
        center=(
            x,
            y
        )
    )

    screen.blit(
        surface,
        rect
    )


def draw_volume_slider(
    x,
    y,
    width,
    value,
    selected
):

    track_rect = pygame.Rect(
        x,
        y - 4,
        width,
        8
    )

    pygame.draw.rect(
        screen,
        SETTINGS_TRACK,
        track_rect,
        border_radius=4
    )

    fill_width = int(
        width * (
            value / 100
        )
    )

    if fill_width > 0:

        fill_rect = pygame.Rect(
            x,
            y - 4,
            fill_width,
            8
        )

        pygame.draw.rect(
            screen,
            SETTINGS_FILL if selected else (
                150,
                150,
                150
            ),
            fill_rect,
            border_radius=4
        )

    knob_x = (
        x +
        fill_width
    )

    pygame.draw.circle(
        screen,
        (
            SETTINGS_FILL
            if selected
            else MENU_NORMAL
        ),
        (
            knob_x,
            y
        ),
        6
    )


def draw_settings_screen():

    draw_fullscreen_overlay()

    panel_rect = draw_menu_panel(
        700,
        540
    )

    draw_menu_title(
        "SETTINGS",
        panel_rect.top + 65,
        42
    )

    label_font = pygame.font.SysFont(
        "arial",
        17,
        bold=True
    )

    # -----------------------------------------------------
    # LAYOUT
    # -----------------------------------------------------

    center_x = panel_rect.centerx

    row_start = panel_rect.top + 150
    row_spacing = 75

    label_x = center_x - 280
    control_x = center_x - 120
    value_x = center_x + 245

    # -----------------------------------------------------
    # FULLSCREEN
    # -----------------------------------------------------

    selected = (
        settings_selected == 0
    )

    label = label_font.render(
        "FULLSCREEN",
        True,
        (
            MENU_SELECTED
            if selected
            else TEXT_PRIMARY
        )
    )

    screen.blit(
        label,
        (
            label_x,
            row_start
        )
    )

    draw_setting_value(
        "ON" if fullscreen_enabled else "OFF",
        value_x,
        row_start + 18,
        selected
    )

    # -----------------------------------------------------
    # SOUND VOLUME
    # -----------------------------------------------------

    sound_y = row_start + row_spacing

    selected = (
        settings_selected == 1
    )

    label = label_font.render(
        "SOUND VOLUME",
        True,
        (
            MENU_SELECTED
            if selected
            else TEXT_PRIMARY
        )
    )

    screen.blit(
        label,
        (
            label_x,
            sound_y
        )
    )

    draw_volume_slider(
        control_x,
        sound_y + 9,
        320,
        sound_volume,
        selected
    )

    draw_setting_value(
        f"{sound_volume}%",
        value_x,
        sound_y + 8,
        selected
    )

    # -----------------------------------------------------
    # MUSIC VOLUME
    # -----------------------------------------------------

    music_y = sound_y + row_spacing

    selected = (
        settings_selected == 2
    )

    label = label_font.render(
        "MUSIC VOLUME",
        True,
        (
            MENU_SELECTED
            if selected
            else TEXT_PRIMARY
        )
    )

    screen.blit(
        label,
        (
            label_x,
            music_y
        )
    )

    draw_volume_slider(
        control_x,
        music_y + 9,
        320,
        music_volume,
        selected
    )

    draw_setting_value(
        f"{music_volume}%",
        value_x,
        music_y + 8,
        selected
    )

    # -----------------------------------------------------
    # BACK
    # -----------------------------------------------------

    back_y = music_y + row_spacing

    draw_menu_option(
        "BACK",
        back_y,
        selected=(
            settings_selected == 3
        ),
        width=240
    )

    # -----------------------------------------------------
    # HINT
    # -----------------------------------------------------

    draw_menu_hint(
        "↑ ↓  SELECT     ← →  ADJUST     ENTER  CONFIRM     ESC  BACK",
        panel_rect.bottom - 35
    )


# =========================================================
# SETTINGS ACTIONS
# =========================================================

def toggle_fullscreen():

    global fullscreen_enabled
    global screen
    global table

    fullscreen_enabled = not fullscreen_enabled

    if fullscreen_enabled:

        info = pygame.display.Info()

        screen = pygame.display.set_mode(
            (
                info.current_w,
                info.current_h
            ),
            pygame.FULLSCREEN
        )

    else:

        screen = pygame.display.set_mode(
            (
                WINDOW_WIDTH,
                WINDOW_HEIGHT
            )
        )

    table.update_position(
        screen
    )

def adjust_setting(direction):

    global sound_volume
    global music_volume

    if settings_selected == 0:

        toggle_fullscreen()

    elif settings_selected == 1:

        sound_volume = max(
            0,
            min(
                100,
                sound_volume + direction * 5
            )
        )

        update_audio_volume()

    elif settings_selected == 2:

        music_volume = max(
            0,
            min(
                100,
                music_volume + direction * 5
            )
        )

        update_audio_volume()


# =========================================================
# GAME OVER MENU
# =========================================================

def draw_game_over():

    draw_fullscreen_overlay()

    panel_rect = draw_menu_panel(
        560,
        450
    )

    if game_won:

        message = "YOU WIN"
        message_color = YELLOW

    else:

        message = "AI WINS"
        message_color = RED

    draw_menu_title(
        message,
        panel_rect.top + 90,
        50,
        message_color
    )

    draw_menu_title(
        "GAME OVER",
        panel_rect.top + 130,
        13,
        MENU_MUTED
    )

    option_start_y = (
        panel_rect.top + 215
    )

    for index, option in enumerate(
        game_over_options
    ):

        draw_menu_option(
            option,
            option_start_y + index * 55,
            selected=(
                index == game_over_selected
            )
        )

    draw_menu_hint(
        "↑ ↓  SELECT     ENTER  CONFIRM",
        panel_rect.bottom - 35
    )


# =========================================================
# PAUSE MENU
# =========================================================

def draw_pause_menu():

    draw_fullscreen_overlay()

    panel_rect = draw_menu_panel(
        560,
        500
    )

    draw_menu_title(
        "PAUSED",
        panel_rect.top + 75,
        45
    )

    draw_menu_title(
        "POOL GAME",
        panel_rect.top + 113,
        13,
        MENU_MUTED
    )

    option_start_y = (
        panel_rect.top + 190
    )

    for index, option in enumerate(
        pause_options
    ):

        draw_menu_option(
            option,
            option_start_y + index * 55,
            selected=(
                index == pause_selected
            )
        )

    draw_menu_hint(
        "↑ ↓  SELECT     ENTER  CONFIRM     ESC  RESUME",
        panel_rect.bottom - 35
    )


# =========================================================
# UI HELPERS
# =========================================================

def draw_panel(
    rect,
    fill=(10, 10, 12, 220),
    border=PANEL_BORDER,
    radius=10
):

    surface = pygame.Surface(
        rect.size,
        pygame.SRCALPHA
    )

    surface.fill(
        fill
    )

    pygame.draw.rect(
        surface,
        border,
        surface.get_rect(),
        1,
        border_radius=radius
    )

    screen.blit(
        surface,
        rect
    )


# =========================================================
# BALL HUD
# =========================================================

def draw_hud_ball(
    x,
    y,
    number,
    radius=10
):

    color = BALL_COLORS.get(
        number,
        GREY
    )

    is_stripe = (
        number in stripe_numbers()
    )

    if is_stripe:

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(x),
                int(y)
            ),
            radius
        )

        stripe_height = max(
            4,
            radius // 2
        )

        pygame.draw.rect(
            screen,
            color,
            (
                int(x - radius),
                int(y - stripe_height // 2),
                radius * 2,
                stripe_height
            )
        )

        pygame.draw.circle(
            screen,
            (35, 35, 38),
            (
                int(x),
                int(y)
            ),
            radius,
            1
        )

    else:

        pygame.draw.circle(
            screen,
            color,
            (
                int(x),
                int(y)
            ),
            radius
        )

        pygame.draw.circle(
            screen,
            (35, 35, 38),
            (
                int(x),
                int(y)
            ),
            radius,
            1
        )

    number_font = pygame.font.SysFont(
        "arial",
        7,
        bold=True
    )

    number_surface = number_font.render(
        str(number),
        True,
        (20, 20, 20)
    )

    number_rect = number_surface.get_rect(
        center=(
            int(x),
            int(y)
        )
    )

    screen.blit(
        number_surface,
        number_rect
    )


def draw_empty_hud_ball(
    x,
    y,
    radius=10
):

    pygame.draw.circle(
        screen,
        EMPTY_BALL_FILL,
        (
            int(x),
            int(y)
        ),
        radius
    )

    pygame.draw.circle(
        screen,
        EMPTY_BALL_BORDER,
        (
            int(x),
            int(y)
        ),
        radius,
        1
    )

    pygame.draw.circle(
        screen,
        EMPTY_BALL_INNER,
        (
            int(x),
            int(y)
        ),
        max(
            2,
            radius - 4
        ),
        1
    )


def get_hud_ball_numbers(group):

    if group == "solid":

        return list(
            range(1, 8)
        )

    if group == "stripe":

        return list(
            range(9, 16)
        )

    return []


def draw_group_balls(
    x,
    y,
    group,
    ball_radius=10,
    spacing=25
):

    if group is None:

        for index in range(7):

            draw_empty_hud_ball(
                x + index * spacing,
                y,
                ball_radius
            )

        return

    numbers = get_hud_ball_numbers(
        group
    )

    remaining = set(
        remaining_numbers(group)
    )

    for index, number in enumerate(numbers):

        if number in remaining:

            draw_hud_ball(
                x + index * spacing,
                y,
                number,
                ball_radius
            )

        else:

            draw_empty_hud_ball(
                x + index * spacing,
                y,
                ball_radius
            )

    if not remaining:

        draw_hud_eight_ball(
            x,
            y,
            ball_radius
        )


def draw_hud_eight_ball(
    x,
    y,
    radius=10
):

    pygame.draw.circle(
        screen,
        (15, 15, 17),
        (
            int(x),
            int(y)
        ),
        radius
    )

    pygame.draw.circle(
        screen,
        (85, 85, 90),
        (
            int(x),
            int(y)
        ),
        radius,
        1
    )

    inner_radius = max(
        4,
        radius - 4
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (
            int(x),
            int(y)
        ),
        inner_radius
    )

    font = pygame.font.SysFont(
        "arial",
        7,
        bold=True
    )

    text = font.render(
        "8",
        True,
        (15, 15, 15)
    )

    text_rect = text.get_rect(
        center=(
            int(x),
            int(y)
        )
    )

    screen.blit(
        text,
        text_rect
    )


def draw_group_label(
    x,
    y,
    group
):

    font = pygame.font.SysFont(
        "arial",
        10,
        bold=True
    )

    if group == "solid":

        text = "SOLIDS"
        color = SOLID_COLOR

    elif group == "stripe":

        text = "STRIPES"
        color = STRIPE_COLOR

    else:

        text = "OPEN TABLE"
        color = TEXT_SECONDARY

    surface = font.render(
        text,
        True,
        color
    )

    screen.blit(
        surface,
        (
            x,
            y
        )
    )


# =========================================================
# GAME STATUS
# =========================================================

def draw_game_status():

    font = pygame.font.SysFont(
        "arial",
        10,
        bold=True
    )

    if current_player == PLAYER_HUMAN:

        if shot_in_progress:

            text = "SHOT IN PROGRESS"
            color = YELLOW

        elif shot_pending:

            text = "GET READY"
            color = YELLOW

        else:

            text = "YOUR TURN"
            color = STATUS_GREEN

    else:

        if shot_in_progress:

            text = "AI SHOOTING"
            color = STATUS_BLUE

        elif shot_pending:

            text = "AI IS THINKING..."
            color = STATUS_BLUE

        else:

            text = "AI TURN"
            color = STATUS_BLUE

    text_surface = font.render(
        text,
        True,
        color
    )

    padding_x = 14
    padding_y = 6

    screen_width = screen.get_width()

    rect = text_surface.get_rect(
        center=(
            screen_width // 2,
            TABLE_Y - 27
        )
    )

    background_rect = pygame.Rect(
        rect.left - padding_x,
        rect.top - padding_y,
        rect.width + padding_x * 2,
        rect.height + padding_y * 2
    )

    surface = pygame.Surface(
        background_rect.size,
        pygame.SRCALPHA
    )

    surface.fill(
        (5, 5, 7, 210)
    )

    pygame.draw.rect(
        surface,
        color,
        surface.get_rect(),
        1,
        border_radius=8
    )

    screen.blit(
        surface,
        background_rect
    )

    screen.blit(
        text_surface,
        rect
    )


# =========================================================
# HUD
# =========================================================

def draw_hud():

    hud_height = 85

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # =========================================================
    # TOP HUD
    # =========================================================

    hud = pygame.Surface(
        (
            screen_width,
            hud_height
        ),
        pygame.SRCALPHA
    )

    hud.fill(
        (
            HUD_BACKGROUND[0],
            HUD_BACKGROUND[1],
            HUD_BACKGROUND[2],
            238
        )
    )

    screen.blit(
        hud,
        (0, 0)
    )

    # Subtle bottom shadow
    pygame.draw.line(
        screen,
        (0, 0, 0),
        (
            0,
            hud_height
        ),
        (
            screen_width,
            hud_height
        ),
        2
    )

    pygame.draw.line(
        screen,
        HUD_BORDER,
        (
            0,
            hud_height - 1
        ),
        (
            screen_width,
            hud_height - 1
        ),
        1
    )

    # =========================================================
    # FONTS
    # =========================================================

    player_font = pygame.font.SysFont(
        "arial",
        19,
        bold=True
    )

    small_font = pygame.font.SysFont(
        "arial",
        12,
        bold=True
    )

    # =========================================================
    # PLAYER
    # =========================================================

    player_x = 25

    if current_player == PLAYER_HUMAN:

        player_color = YELLOW
        player_status = "YOUR TURN"

    else:

        player_color = TEXT_SECONDARY
        player_status = "WAITING"

    player_title = player_font.render(
        "PLAYER",
        True,
        TEXT_PRIMARY
    )

    player_status_surface = small_font.render(
        player_status,
        True,
        player_color
    )

    # Subtle title shadow
    player_shadow = player_font.render(
        "PLAYER",
        True,
        (0, 0, 0)
    )

    screen.blit(
        player_shadow,
        (
            player_x + 1,
            14
        )
    )

    screen.blit(
        player_title,
        (
            player_x,
            13
        )
    )

    screen.blit(
        player_status_surface,
        (
            player_x + 1,
            40
        )
    )

    draw_group_balls(
        player_x + 10,
        66,
        player_group,
        ball_radius=7,
        spacing=18
    )

    # =========================================================
    # CENTER GROUP
    # =========================================================

    center_x = screen_width // 2

    if player_group == "solid":

        group_text = "SOLIDS"
        group_color = SOLID_COLOR

    elif player_group == "stripe":

        group_text = "STRIPES"
        group_color = STRIPE_COLOR

    else:

        group_text = "OPEN TABLE"
        group_color = TEXT_PRIMARY

    group_surface = player_font.render(
        group_text,
        True,
        group_color
    )

    group_rect = group_surface.get_rect(
        center=(
            center_x,
            25
        )
    )

    # Subtle shadow
    group_shadow = player_font.render(
        group_text,
        True,
        (0, 0, 0)
    )

    group_shadow_rect = group_shadow.get_rect(
        center=(
            center_x + 1,
            26
        )
    )

    screen.blit(
        group_shadow,
        group_shadow_rect
    )

    screen.blit(
        group_surface,
        group_rect
    )

    # =========================================================
    # AI
    # =========================================================

    right_x = screen_width - 25

    if current_player == PLAYER_AI:

        ai_color = YELLOW
        ai_status = "YOUR OPPONENT'S TURN"

    else:

        ai_color = TEXT_SECONDARY
        ai_status = "WAITING"

    ai_title = player_font.render(
        "AI",
        True,
        TEXT_PRIMARY
    )

    ai_status_surface = small_font.render(
        ai_status,
        True,
        ai_color
    )

    ai_title_rect = ai_title.get_rect(
        top=13,
        right=right_x
    )

    ai_status_rect = ai_status_surface.get_rect(
        top=40,
        right=right_x
    )

    # AI shadow
    ai_shadow = player_font.render(
        "AI",
        True,
        (0, 0, 0)
    )

    ai_shadow_rect = ai_shadow.get_rect(
        top=14,
        right=right_x - 1
    )

    screen.blit(
        ai_shadow,
        ai_shadow_rect
    )

    screen.blit(
        ai_title,
        ai_title_rect
    )

    screen.blit(
        ai_status_surface,
        ai_status_rect
    )

    ai_start_x = (
        right_x -
        (
            7 * 18
        ) +
        9
    )

    draw_group_balls(
        ai_start_x,
        66,
        ai_group,
        ball_radius=7,
        spacing=18
    )

    # =========================================================
    # POWER PANEL
    # =========================================================

    if current_player == PLAYER_HUMAN:

        panel_width = 250
        panel_height = 64

        panel_x = 22
        panel_y = screen_height - panel_height - 18

        panel_rect = pygame.Rect(
            panel_x,
            panel_y,
            panel_width,
            panel_height
        )

        # Outer shadow
        shadow_rect = panel_rect.move(
            0,
            3
        )

        pygame.draw.rect(
            screen,
            HUD_BACKGROUND,
            shadow_rect,
            border_radius=9
        )

        # Main panel
        draw_panel(
            panel_rect,
            fill=(22, 34, 39),
            border=(65, 75, 78),
            radius=9
        )

        # Subtle top highlight
        pygame.draw.line(
            screen,
            (85, 95, 98),
            (
                panel_x + 10,
                panel_y + 1
            ),
            (
                panel_x + panel_width - 10,
                panel_y + 1
            ),
            1
        )

        # =====================================================
        # POWER TEXT
        # =====================================================

        power_font = pygame.font.SysFont(
            "arial",
            12,
            bold=True
        )

        power_text = power_font.render(
            f"POWER  {human_power:.1f}",
            True,
            TEXT_PRIMARY
        )

        screen.blit(
            power_text,
            (
                panel_x + 12,
                panel_y + 10
            )
        )

        # =====================================================
        # POWER BAR
        # =====================================================

        bar_x = panel_x + 12
        bar_y = panel_y + 33

        bar_width = panel_width - 24
        bar_height = 9

        # Outer bar
        pygame.draw.rect(
            screen,
            (5, 7, 8),
            (
                bar_x - 1,
                bar_y - 1,
                bar_width + 2,
                bar_height + 2
            ),
            border_radius=5
        )

        # Inner background
        pygame.draw.rect(
            screen,
            (28, 34, 37),
            (
                bar_x,
                bar_y,
                bar_width,
                bar_height
            ),
            border_radius=4
        )

        progress = (
            3 + human_power -
            HUMAN_MIN_POWER
        ) / (
            3+ HUMAN_MAX_POWER -
            HUMAN_MIN_POWER
        )

        progress = max(
            0.0,
            min(
                1.0,
                progress
            )
        )

        fill_width = int(
            (bar_width - 4) *
            progress
        )

        if fill_width > 0:

            # Power glow
            pygame.draw.rect(
                screen,
                (135, 72, 32),
                (
                    bar_x + 1,
                    bar_y + 1,
                    fill_width + 2,
                    bar_height - 2
                ),
                border_radius=4
            )

            # Main power fill
            pygame.draw.rect(
                screen,
                (135, 72, 32),
                (
                    bar_x + 2,
                    bar_y + 2,
                    fill_width,
                    bar_height - 4
                ),
                border_radius=3
            )

            # Highlight
            if fill_width > 3:

                pygame.draw.line(
                    screen,
                    (255, 240, 150),
                    (
                        bar_x + 3,
                        bar_y + 3
                    ),
                    (
                        bar_x + 1 + fill_width,
                        bar_y + 3
                    ),
                    1
                )

                pygame.draw.rect(
                    screen,
                    (0, 0, 0),
                    (
                    bar_x + 1 + fill_width - 17,
                    bar_y + 1,
                    15,
                    bar_height - 2
                    ),
                    border_radius=2
                )  

                # White tip
                pygame.draw.rect(
                    screen,
                    (255, 255, 255),
                    (
                        bar_x + 1 + fill_width - 2,
                        bar_y + 1,
                        4,
                        bar_height - 2
                    ),
                    border_radius=2
                )

                  

        # =====================================================
        # POWER CONTROLS
        # =====================================================

        controls = pygame.font.SysFont(
            "arial",
            10
        )

        controls_surface = controls.render(
            "WHEEL  POWER",
            True,
            TEXT_SECONDARY
        )

        controls_rect = controls_surface.get_rect(
            bottomright=(
                panel_x + panel_width - 10,
                panel_y + panel_height - 7
            )
        )

        screen.blit(
            controls_surface,
            controls_rect
        )

    # =========================================================
    # BOTTOM CONTROLS
    # =========================================================

    controls_font = pygame.font.SysFont(
        "arial",
        11
    )

    controls = controls_font.render(
        "MOUSE  AIM     CLICK  SHOOT     ESC  PAUSE",
        True,
        TEXT_SECONDARY
    )

    controls_rect = controls.get_rect(
        bottomright=(
            screen_width - 22,
            screen_height - 24
        )
    )

    screen.blit(
        controls,
        controls_rect
    )

# =========================================================
# HUMAN AIM PREVIEW
# =========================================================

def draw_human_aim():

    if waiting_for_start:
        return

    if game_over:
        return

    if paused:
        return

    if settings_open:
        return

    if current_player != PLAYER_HUMAN:
        return

    if not all_balls_stopped(balls):
        return

    if shot_pending:
        return

    if shot_in_progress:
        return

    if not cue_ball.active:
        return

    mouse_x, mouse_y = pygame.mouse.get_pos()

    dx = (
        mouse_x -
        cue_ball.x
    )

    dy = (
        mouse_y -
        cue_ball.y
    )

    length = math.hypot(
        dx,
        dy
    )

    if length == 0:
        return

    dx /= length
    dy /= length

    angle = math.atan2(
        dy,
        dx
    )

    def ray_box_distance(
        origin_x,
        origin_y,
        direction_x,
        direction_y,
        ball_radius
    ):

        left = (
            TABLE_X +
            ball_radius
        )

        right = (
            TABLE_X +
            TABLE_WIDTH -
            ball_radius
        )

        top = (
            TABLE_Y +
            ball_radius
        )

        bottom = (
            TABLE_Y +
            TABLE_HEIGHT -
            ball_radius
        )

        t_min = 0.0
        t_max = float("inf")

        if abs(direction_x) < 1e-12:

            if (
                origin_x < left
                or origin_x > right
            ):

                return float("inf")

        else:

            tx1 = (
                left -
                origin_x
            ) / direction_x

            tx2 = (
                right -
                origin_x
            ) / direction_x

            tx_near = min(
                tx1,
                tx2
            )

            tx_far = max(
                tx1,
                tx2
            )

            t_min = max(
                t_min,
                tx_near
            )

            t_max = min(
                t_max,
                tx_far
            )

        if abs(direction_y) < 1e-12:

            if (
                origin_y < top
                or origin_y > bottom
            ):

                return float("inf")

        else:

            ty1 = (
                top -
                origin_y
            ) / direction_y

            ty2 = (
                bottom -
                origin_y
            ) / direction_y

            ty_near = min(
                ty1,
                ty2
            )

            ty_far = max(
                ty1,
                ty2
            )

            t_min = max(
                t_min,
                ty_near
            )

            t_max = min(
                t_max,
                ty_far
            )

        if t_max < t_min:
            return float("inf")

        if t_max < 0:
            return float("inf")

        if t_min > 0:
            return t_min

        return t_max

    nearest_distance = float("inf")
    hit_ball = None

    for ball in balls:

        if not ball.active:
            continue

        if ball.is_cue:
            continue

        collision_radius = (
            cue_ball.radius +
            ball.radius
        )

        bx = (
            ball.x -
            cue_ball.x
        )

        by = (
            ball.y -
            cue_ball.y
        )

        projection = (
            bx * dx +
            by * dy
        )

        if projection <= 0:
            continue

        closest_x = (
            cue_ball.x +
            dx * projection
        )

        closest_y = (
            cue_ball.y +
            dy * projection
        )

        perpendicular_squared = (
            (ball.x - closest_x) ** 2 +
            (ball.y - closest_y) ** 2
        )

        if (
            perpendicular_squared >
            collision_radius ** 2
        ):

            continue

        offset = math.sqrt(
            max(
                collision_radius ** 2 -
                perpendicular_squared,
                0.0
            )
        )

        hit_distance = (
            projection -
            offset
        )

        if hit_distance <= 0:
            continue

        if hit_distance < nearest_distance:

            nearest_distance = hit_distance
            hit_ball = ball

    table_distance = ray_box_distance(
        cue_ball.x,
        cue_ball.y,
        dx,
        dy,
        cue_ball.radius
    )

    if table_distance == float("inf"):
        return

    hit_first = (
        hit_ball is not None
        and nearest_distance < table_distance
    )

    predicted_cue_path, predicted_cue_active = predict_cue_path(
        angle
    )

    if len(predicted_cue_path) >= 2:

        cue_path_color = (
            120,
            220,
            255
        )

        pygame.draw.lines(
            screen,
            cue_path_color,
            False,
            [
                (
                    int(point_x),
                    int(point_y)
                )
                for point_x, point_y in predicted_cue_path
            ],
            2
        )

        final_x, final_y = predicted_cue_path[-1]

        if predicted_cue_active:

            pygame.draw.circle(
                screen,
                cue_path_color,
                (
                    int(final_x),
                    int(final_y)
                ),
                4
            )

        else:

            pygame.draw.line(
                screen,
                RED,
                (
                    int(final_x - 5),
                    int(final_y - 5)
                ),
                (
                    int(final_x + 5),
                    int(final_y + 5)
                ),
                2
            )

            pygame.draw.line(
                screen,
                RED,
                (
                    int(final_x + 5),
                    int(final_y - 5)
                ),
                (
                    int(final_x - 5),
                    int(final_y + 5)
                ),
                2
            )

    if not hit_first:
        return

    ghost_x = (
        cue_ball.x +
        dx * nearest_distance
    )

    ghost_y = (
        cue_ball.y +
        dy * nearest_distance
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (
            int(ghost_x),
            int(ghost_y)
        ),
        cue_ball.radius,
        1
    )

    target_dx = (
        hit_ball.x -
        ghost_x
    )

    target_dy = (
        hit_ball.y -
        ghost_y
    )

    target_length = math.hypot(
        target_dx,
        target_dy
    )

    if target_length == 0:
        return

    target_dx /= target_length
    target_dy /= target_length

    target_table_distance = ray_box_distance(
        hit_ball.x,
        hit_ball.y,
        target_dx,
        target_dy,
        hit_ball.radius
    )

    if target_table_distance == float("inf"):
        return

    target_end_x = (
        hit_ball.x +
        target_dx * target_table_distance
    )

    target_end_y = (
        hit_ball.y +
        target_dy * target_table_distance
    )

    target_line_start_x = (
        hit_ball.x +
        target_dx * (
            hit_ball.radius + 1
        )
    )

    target_line_start_y = (
        hit_ball.y +
        target_dy * (
            hit_ball.radius + 1
        )
    )

    pygame.draw.line(
        screen,
        YELLOW,
        (
            int(target_line_start_x),
            int(target_line_start_y)
        ),
        (
            int(target_end_x),
            int(target_end_y)
        ),
        2
    )

    contact_x = (
        hit_ball.x -
        target_dx * hit_ball.radius
    )

    contact_y = (
        hit_ball.y -
        target_dy * hit_ball.radius
    )

    pygame.draw.circle(
        screen,
        YELLOW,
        (
            int(contact_x),
            int(contact_y)
        ),
        3
    )

    pygame.draw.circle(
        screen,
        YELLOW,
        (
            int(hit_ball.x),
            int(hit_ball.y)
        ),
        BALL_RADIUS + 3,
        1
    )


# =========================================================
# AI PREDICTION
# =========================================================

def draw_ai_prediction():

    if paused:
        return

    if settings_open:
        return

    if not shot_pending:
        return

    if current_shot is None:
        return

    aim_point = current_shot.get(
        "aim_point"
    )

    if aim_point is not None:

        pygame.draw.line(
            screen,
            YELLOW,
            (
                int(cue_ball.x),
                int(cue_ball.y)
            ),
            (
                int(aim_point[0]),
                int(aim_point[1])
            ),
            2
        )

        pygame.draw.circle(
            screen,
            YELLOW,
            (
                int(aim_point[0]),
                int(aim_point[1])
            ),
            BALL_RADIUS,
            1
        )

    target = current_shot.get(
        "target"
    )

    if target is not None:

        pocket = current_shot.get(
            "pocket"
        )

        if pocket is not None:

            pygame.draw.line(
                screen,
                ORANGE,
                (
                    int(target.x),
                    int(target.y)
                ),
                (
                    int(pocket[0]),
                    int(pocket[1])
                ),
                2
            )

        pygame.draw.circle(
            screen,
            ORANGE,
            (
                int(target.x),
                int(target.y)
            ),
            BALL_RADIUS + 4,
            1
        )

        contact = current_shot.get(
            "contact"
        )

        if contact is not None:

            pygame.draw.circle(
                screen,
                ORANGE,
                (
                    int(contact[0]),
                    int(contact[1])
                ),
                3
            )

    bank_point = current_shot.get(
        "bank_point"
    )

    if bank_point is not None:

        pygame.draw.circle(
            screen,
            YELLOW,
            (
                int(bank_point[0]),
                int(bank_point[1])
            ),
            5,
            1
        )

        target = current_shot.get(
            "target"
        )

        if target is not None:

            pygame.draw.line(
                screen,
                YELLOW,
                (
                    int(target.x),
                    int(target.y)
                ),
                (
                    int(bank_point[0]),
                    int(bank_point[1])
                ),
                1
            )

        pocket = current_shot.get(
            "pocket"
        )

        if pocket is not None:

            pygame.draw.line(
                screen,
                YELLOW,
                (
                    int(bank_point[0]),
                    int(bank_point[1])
                ),
                (
                    int(pocket[0]),
                    int(pocket[1])
                ),
                1
            )


# =========================================================
# START SHOT
# =========================================================

def start_shot(shooter):

    global shot_in_progress
    global shot_shooter
    global shot_pocketed
    global shot_hit_sound_played

    shot_in_progress = True
    shot_shooter = shooter
    shot_pocketed = []

    shot_hit_sound_played = False

    cue_ball.first_hit_number = None


# =========================================================
# FIRE HUMAN SHOT
# =========================================================

def fire_human_shot():

    global human_shot_pending

    if current_player != PLAYER_HUMAN:
        return

    if game_over:
        return

    if paused:
        return

    if settings_open:
        return

    if shot_in_progress:
        return

    if not cue_ball.active:
        return

    if not all_balls_stopped(balls):
        return

    mouse_x, mouse_y = pygame.mouse.get_pos()

    dx = (
        mouse_x -
        cue_ball.x
    )

    dy = (
        mouse_y -
        cue_ball.y
    )

    distance = math.hypot(
        dx,
        dy
    )

    if distance < 5:
        return

    angle = math.atan2(
        dy,
        dx
    )

    start_shot(
        PLAYER_HUMAN
    )

    play_shot()

    cue_ball.shoot(
        angle,
        human_power
    )

    human_shot_pending = True


# =========================================================
# RESPAWN CUE BALL
# =========================================================

def respawn_cue_ball():

    cue_ball.active = True

    cue_ball.x = (
        TABLE_X +
        TABLE_WIDTH * 0.25
    )

    cue_ball.y = (
        TABLE_Y +
        TABLE_HEIGHT / 2
    )

    cue_ball.vx = 0
    cue_ball.vy = 0

    cue_ball.first_hit_number = None


# =========================================================
# RESET GAME
# =========================================================

def reset_game():

    global ai

    global waiting_for_start

    global menu_selected

    global game_over
    global game_won
    global game_lost

    global game_over_selected

    global paused
    global pause_selected

    global settings_open
    global settings_selected

    global current_player

    global player_group
    global ai_group

    global shot_pending
    global shot_preview_timer
    global current_shot

    global shot_in_progress
    global shot_shooter
    global shot_pocketed

    global human_shot_pending
    global shot_hit_sound_played

    global human_power

    global _aim_prediction_cache

    waiting_for_start = False

    paused = False

    settings_open = False

    menu_selected = 0
    game_over_selected = 0
    pause_selected = 0
    settings_selected = 0

    game_over = False
    game_won = False
    game_lost = False

    current_player = PLAYER_HUMAN

    player_group = None
    ai_group = None

    shot_pending = False
    shot_preview_timer = 0

    current_shot = None

    shot_in_progress = False
    shot_shooter = None
    shot_pocketed = []

    human_shot_pending = False
    shot_hit_sound_played = False

    human_power = 18.0

    _aim_prediction_cache = None

    cue_ball.active = True

    cue_ball.x = (
        TABLE_X +
        TABLE_WIDTH * 0.25
    )

    cue_ball.y = (
        TABLE_Y +
        TABLE_HEIGHT / 2
    )

    cue_ball.vx = 0
    cue_ball.vy = 0

    cue_ball.first_hit_number = None

    for number, position in zip(
        RACK_ORDER,
        rack_positions
    ):

        for ball in balls:

            if (
                not ball.is_cue
                and ball.number == number
            ):

                ball.active = True

                ball.x = position[0]
                ball.y = position[1]

                ball.vx = 0
                ball.vy = 0

                ball.first_hit_number = None

                break

    ai = PoolAI()


# =========================================================
# PROCESS SHOT RESULT
# =========================================================

def process_shot_result(
    pocketed,
    shooter
):

    global player_group
    global ai_group

    global game_over
    global game_won
    global game_lost

    global human_shot_pending

    global shot_in_progress
    global shot_shooter
    global shot_pocketed

    object_balls = [
        ball
        for ball in pocketed
        if not ball.is_cue
    ]

    cue_pocketed = any(
        ball.is_cue
        for ball in pocketed
    )

    if cue_pocketed:

        respawn_cue_ball()

        human_shot_pending = False

        shot_in_progress = False
        shot_shooter = None
        shot_pocketed = []

        switch_player()

        return

    first_hit = cue_ball.first_hit_number

    legal_first_hit = first_hit_is_legal(
        first_hit,
        shooter
    )

    if first_hit is None:

        human_shot_pending = False

        shot_in_progress = False
        shot_shooter = None
        shot_pocketed = []

        switch_player()

        return

    if not legal_first_hit:

        human_shot_pending = False

        shot_in_progress = False
        shot_shooter = None
        shot_pocketed = []

        switch_player()

        return

    if not object_balls:

        human_shot_pending = False

        shot_in_progress = False
        shot_shooter = None
        shot_pocketed = []

        switch_player()

        return

    black_pocketed = any(
        ball.number == 8
        for ball in object_balls
    )

    if black_pocketed:

        shooter_group = (
            player_group
            if shooter == PLAYER_HUMAN
            else ai_group
        )

        if (
            shooter_group is not None
            and all_group_cleared(
                shooter_group
            )
        ):

            if shooter == PLAYER_HUMAN:

                game_won = True
                game_lost = False

            else:

                game_won = False
                game_lost = True

        else:

            if shooter == PLAYER_HUMAN:

                game_won = False
                game_lost = True

            else:

                game_won = True
                game_lost = False

        game_over = True

        shot_in_progress = False
        shot_shooter = None
        shot_pocketed = []

        return

    if (
        player_group is None
        and ai_group is None
    ):

        first_group = None

        for ball in object_balls:

            group = ball_group(
                ball.number
            )

            if group in (
                "solid",
                "stripe"
            ):

                first_group = group

                break

        if first_group is not None:

            if shooter == PLAYER_HUMAN:

                player_group = first_group

                if first_group == "solid":

                    ai_group = "stripe"

                else:

                    ai_group = "solid"

            else:

                ai_group = first_group

                if first_group == "solid":

                    player_group = "stripe"

                else:

                    player_group = "solid"

    shooter_group = (
        player_group
        if shooter == PLAYER_HUMAN
        else ai_group
    )

    valid_pocketed = False

    for ball in object_balls:

        if ball.number == 8:
            continue

        if (
            shooter_group is not None
            and ball_group(
                ball.number
            ) == shooter_group
        ):

            valid_pocketed = True

            break

    if not valid_pocketed:

        switch_player()

    human_shot_pending = False

    shot_in_progress = False
    shot_shooter = None
    shot_pocketed = []


# =========================================================
# START AI TURN
# =========================================================

def start_ai_turn():

    global current_shot
    global shot_pending
    global shot_preview_timer

    if current_player != PLAYER_AI:
        return

    if game_over:
        return

    if paused:
        return

    if settings_open:
        return

    if shot_in_progress:
        return

    if not all_balls_stopped(balls):
        return

    if shot_pending:
        return

    allowed = allowed_target_numbers(
        ai_group
    )

    best_shot = ai.find_best_shot(
        cue_ball,
        balls,
        table,
        allowed
    )

    if best_shot is None:

        switch_player()

        return

    current_shot = best_shot

    current_shot[
        "cue_path"
    ] = [
        (
            cue_ball.x,
            cue_ball.y
        ),
        current_shot[
            "aim_point"
        ]
    ]

    shot_preview_timer = (
        SHOT_PREVIEW_TIME
    )

    shot_pending = True


# =========================================================
# FIRE AI SHOT
# =========================================================

def fire_ai_shot():

    global shot_pending
    global human_shot_pending

    if current_shot is None:
        return

    if paused:
        return

    if settings_open:
        return

    start_shot(
        PLAYER_AI
    )

    play_shot()

    cue_ball.shoot(
        current_shot["angle"],
        current_shot["power"]
    )

    shot_pending = False
    human_shot_pending = False


# =========================================================
# MAIN LOOP
# =========================================================

running = True

while running:

    dt = clock.tick(
        FPS
    )

    # =====================================================
    # EVENTS
    # =====================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_F11:

                toggle_fullscreen()

                continue

            if settings_open:

                if event.key == pygame.K_UP:

                    settings_selected = (
                        settings_selected - 1
                    ) % len(settings_options)

                    play_menu_move()

                elif event.key == pygame.K_DOWN:

                    settings_selected = (
                        settings_selected + 1
                    ) % len(settings_options)

                    play_menu_move()

                elif event.key == pygame.K_LEFT:

                    if settings_selected in (
                        1,
                        2
                    ):

                        adjust_setting(-1)

                        play_menu_move()

                elif event.key == pygame.K_RIGHT:

                    if settings_selected in (
                        1,
                        2
                    ):

                        adjust_setting(1)

                        play_menu_move()

                elif event.key == pygame.K_RETURN:

                    selected_option = (
                        settings_options[
                            settings_selected
                        ]
                    )

                    play_menu_select()

                    if selected_option == "FULLSCREEN":

                        toggle_fullscreen()

                    elif selected_option == "BACK":

                        settings_open = False

                        if waiting_for_start:

                            menu_selected = 0

                        elif paused:

                            pause_selected = 0

                        elif game_over:

                            game_over_selected = 0

                elif event.key == pygame.K_ESCAPE:

                    play_menu_pause()

                    settings_open = False

                    if waiting_for_start:

                        menu_selected = 0

                    elif paused:

                        pause_selected = 0

                    elif game_over:

                        game_over_selected = 0

                continue

            if waiting_for_start:

                if event.key == pygame.K_UP:

                    menu_selected = (
                        menu_selected - 1
                    ) % len(menu_options)

                    play_menu_move()

                elif event.key == pygame.K_DOWN:

                    menu_selected = (
                        menu_selected + 1
                    ) % len(menu_options)

                    play_menu_move()

                elif event.key == pygame.K_RETURN:

                    selected_option = (
                        menu_options[
                            menu_selected
                        ]
                    )

                    play_menu_select()

                    if selected_option == "PLAY":

                        waiting_for_start = False

                    elif selected_option == "SETTINGS":

                        settings_open = True
                        settings_selected = 0

                    elif selected_option == "QUIT":

                        running = False

            elif game_over:

                if event.key == pygame.K_UP:

                    game_over_selected = (
                        game_over_selected - 1
                    ) % len(game_over_options)

                    play_menu_move()

                elif event.key == pygame.K_DOWN:

                    game_over_selected = (
                        game_over_selected + 1
                    ) % len(game_over_options)

                    play_menu_move()

                elif event.key == pygame.K_RETURN:

                    selected_option = (
                        game_over_options[
                            game_over_selected
                        ]
                    )

                    play_menu_select()

                    if selected_option == "QUIT":

                        running = False

                    elif selected_option == "PLAY AGAIN":

                        reset_game()

                    elif selected_option == "SETTINGS":

                        settings_open = True
                        settings_selected = 0

                elif event.key == pygame.K_ESCAPE:

                    play_menu_pause()

                    running = False

            elif paused:

                if event.key == pygame.K_UP:

                    pause_selected = (
                        pause_selected - 1
                    ) % len(pause_options)

                    play_menu_move()

                elif event.key == pygame.K_DOWN:

                    pause_selected = (
                        pause_selected + 1
                    ) % len(pause_options)

                    play_menu_move()

                elif event.key == pygame.K_RETURN:

                    selected_option = (
                        pause_options[
                            pause_selected
                        ]
                    )

                    play_menu_select()

                    if selected_option == "RESUME":

                        paused = False

                    elif selected_option == "RESTART":

                        reset_game()

                    elif selected_option == "SETTINGS":

                        settings_open = True
                        settings_selected = 0

                    elif selected_option == "QUIT":

                        running = False

                elif event.key == pygame.K_ESCAPE:

                    play_menu_pause()

                    paused = False

            else:

                if event.key == pygame.K_ESCAPE:

                    paused = True
                    pause_selected = 0

                    play_menu_pause()

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if (
                event.button == 1
                and not waiting_for_start
                and not game_over
                and not paused
                and not settings_open
                and current_player == PLAYER_HUMAN
                and not shot_pending
                and not shot_in_progress
                and all_balls_stopped(balls)
            ):

                fire_human_shot()

            elif (
                event.button == 4
                and current_player == PLAYER_HUMAN
                and not paused
                and not settings_open
                and not game_over
            ):

                human_power = min(
                    HUMAN_MAX_POWER,
                    human_power + 0.5
                )

            elif (
                event.button == 5
                and current_player == PLAYER_HUMAN
                and not paused
                and not settings_open
                and not game_over
            ):

                human_power = max(
                    HUMAN_MIN_POWER,
                    human_power - 0.5
                )

    # =====================================================
    # GAME LOGIC
    # =====================================================

    if (
        not waiting_for_start
        and not game_over
        and not paused
        and not settings_open
    ):

        if current_player == PLAYER_AI:

            start_ai_turn()

        if shot_pending:

            shot_preview_timer -= dt

            if shot_preview_timer <= 0:

                fire_ai_shot()

        if (
            shot_in_progress
            and not all_balls_stopped(balls)
        ):

            previous_first_hit = cue_ball.first_hit_number

            pocketed = update_physics(
                balls,
                table
            )

            # -------------------------------------------------
            # FIRST BALL HIT
            # -------------------------------------------------

            if (
                not shot_hit_sound_played
                and cue_ball.first_hit_number is not None
                and previous_first_hit is None
            ):

                play_ball_hit()

                shot_hit_sound_played = True

            # -------------------------------------------------
            # BALL POCKET
            # -------------------------------------------------

            if pocketed:

                play_ball_pocket()

                shot_pocketed.extend(
                    pocketed
                )

        if (
            shot_in_progress
            and not shot_pending
            and all_balls_stopped(balls)
        ):

            process_shot_result(
                shot_pocketed,
                shot_shooter
            )

    # =====================================================
    # DRAW
    # =====================================================

    screen.fill(
        BACKGROUND
    )

    table.draw(
        screen
    )

    for ball in balls:

        ball.draw(
            screen
        )

    draw_human_aim()

    draw_ai_prediction()

    if not waiting_for_start:

        draw_hud()

        draw_game_status()

    if waiting_for_start:

        if settings_open:

            draw_settings_screen()

        else:

            draw_start_screen()

    elif game_over:

        if settings_open:

            draw_settings_screen()

        else:

            draw_game_over()

    elif paused:

        if settings_open:

            draw_settings_screen()

        else:

            draw_pause_menu()

    pygame.display.flip()


# =========================================================
# CLEANUP
# =========================================================

if mixer_available:

    pygame.mixer.music.stop()

    pygame.mixer.quit()

pygame.quit()