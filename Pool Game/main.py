import math
import pygame

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

screen = pygame.display.set_mode(
    (
        WINDOW_WIDTH,
        WINDOW_HEIGHT
    )
)

pygame.display.set_caption(
    "Pool AI"
)

clock = pygame.time.Clock()


# =========================================================
# COLORS
# =========================================================

BACKGROUND = (25, 25, 25)

YELLOW = (255, 220, 0)
ORANGE = (255, 150, 0)

WHITE = (245, 245, 245)
GREY = (210, 210, 210)

RED = (220, 70, 70)

# HUD
HUD_BACKGROUND = (8, 8, 10)
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
# TABLE
# =========================================================

table = Table()


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


for number, position in zip(
    range(1, 16),
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
    "QUIT"
]

game_over = False
game_won = False
game_lost = False

game_over_selected = 0

game_over_options = [
    "PLAY AGAIN",
    "QUIT"
]


# =========================================================
# PAUSE STATE
# =========================================================

paused = False

pause_selected = 0

pause_options = [
    "RESUME",
    "RESTART",
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


# =========================================================
# HUMAN PLAYER POWER
# =========================================================

HUMAN_MIN_POWER = 4.0
HUMAN_MAX_POWER = 18.0

human_power = 10.0


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
# START MENU
# =========================================================

def draw_start_screen():

    overlay = pygame.Surface(
        (
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 175)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    title_font = pygame.font.SysFont(
        "arial",
        56,
        bold=True
    )

    option_font = pygame.font.SysFont(
        "arial",
        28,
        bold=True
    )

    hint_font = pygame.font.SysFont(
        "arial",
        16
    )

    title = title_font.render(
        "POOL AI",
        True,
        WHITE
    )

    title_rect = title.get_rect(
        center=(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 - 110
        )
    )

    screen.blit(
        title,
        title_rect
    )

    for index, option in enumerate(
        menu_options
    ):

        if index == menu_selected:

            color = YELLOW

        else:

            color = GREY

        text = option_font.render(
            option,
            True,
            color
        )

        text_rect = text.get_rect(
            center=(
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 2 +
                index * 55
            )
        )

        screen.blit(
            text,
            text_rect
        )

    hint = hint_font.render(
        "Use ↑ ↓ and ENTER",
        True,
        GREY
    )

    hint_rect = hint.get_rect(
        center=(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 115
        )
    )

    screen.blit(
        hint,
        hint_rect
    )


# =========================================================
# GAME OVER MENU
# =========================================================

def draw_game_over():

    overlay = pygame.Surface(
        (
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 185)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    title_font = pygame.font.SysFont(
        "arial",
        52,
        bold=True
    )

    option_font = pygame.font.SysFont(
        "arial",
        25,
        bold=True
    )

    hint_font = pygame.font.SysFont(
        "arial",
        17
    )

    if game_won:

        message = "YOU WIN"
        message_color = YELLOW

    else:

        message = "AI WINS"
        message_color = RED

    title = title_font.render(
        message,
        True,
        message_color
    )

    title_rect = title.get_rect(
        center=(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 - 80
        )
    )

    screen.blit(
        title,
        title_rect
    )

    for index, option in enumerate(
        game_over_options
    ):

        if index == game_over_selected:

            color = YELLOW

        else:

            color = GREY

        text = option_font.render(
            option,
            True,
            color
        )

        text_rect = text.get_rect(
            center=(
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 2 +
                index * 50
            )
        )

        screen.blit(
            text,
            text_rect
        )

    hint = hint_font.render(
        "Use ↑ ↓ and ENTER",
        True,
        GREY
    )

    hint_rect = hint.get_rect(
        center=(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 120
        )
    )

    screen.blit(
        hint,
        hint_rect
    )


# =========================================================
# PAUSE MENU
# =========================================================

def draw_pause_menu():

    overlay = pygame.Surface(
        (
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 185)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    panel_width = 330
    panel_height = 310

    panel_rect = pygame.Rect(
        (
            WINDOW_WIDTH - panel_width
        ) // 2,
        (
            WINDOW_HEIGHT - panel_height
        ) // 2,
        panel_width,
        panel_height
    )

    panel = pygame.Surface(
        panel_rect.size,
        pygame.SRCALPHA
    )

    panel.fill(
        (10, 10, 12, 235)
    )

    pygame.draw.rect(
        panel,
        PANEL_BORDER,
        panel.get_rect(),
        1,
        border_radius=12
    )

    screen.blit(
        panel,
        panel_rect
    )

    title_font = pygame.font.SysFont(
        "arial",
        42,
        bold=True
    )

    option_font = pygame.font.SysFont(
        "arial",
        22,
        bold=True
    )

    hint_font = pygame.font.SysFont(
        "arial",
        15
    )

    title = title_font.render(
        "PAUSED",
        True,
        WHITE
    )

    title_rect = title.get_rect(
        center=(
            WINDOW_WIDTH // 2,
            panel_rect.top + 55
        )
    )

    screen.blit(
        title,
        title_rect
    )

    for index, option in enumerate(
        pause_options
    ):

        selected = (
            index == pause_selected
        )

        if selected:

            color = YELLOW

            selection_rect = pygame.Rect(
                panel_rect.left + 65,
                panel_rect.top + 95 + index * 50,
                panel_rect.width - 130,
                38
            )

            pygame.draw.rect(
                screen,
                (45, 40, 10),
                selection_rect,
                border_radius=8
            )

        else:

            color = GREY

        text = option_font.render(
            option,
            True,
            color
        )

        text_rect = text.get_rect(
            center=(
                WINDOW_WIDTH // 2,
                panel_rect.top + 114 + index * 50
            )
        )

        screen.blit(
            text,
            text_rect
        )

    hint = hint_font.render(
        "↑ ↓ Select     ENTER Confirm     ESC Resume",
        True,
        TEXT_SECONDARY
    )

    hint_rect = hint.get_rect(
        center=(
            WINDOW_WIDTH // 2,
            panel_rect.bottom - 27
        )
    )

    screen.blit(
        hint,
        hint_rect
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

    # -----------------------------------------------------
    # STRIPED BALL
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # SOLID BALL
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # NUMBER
    # -----------------------------------------------------

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

    # Outer empty silhouette
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

    # Inner subtle circle
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

    # -----------------------------------------------------
    # GROUP NOT ASSIGNED
    # -----------------------------------------------------

    if group is None:

        for index in range(7):

            draw_empty_hud_ball(
                x + index * spacing,
                y,
                ball_radius
            )

        return

    # -----------------------------------------------------
    # GROUP ASSIGNED
    # -----------------------------------------------------

    numbers = get_hud_ball_numbers(
        group
    )

    remaining = set(
        remaining_numbers(group)
    )

    # -----------------------------------------------------
    # DRAW REMAINING GROUP BALLS
    # -----------------------------------------------------

    for index, number in enumerate(numbers):

        if number in remaining:

            draw_hud_ball(
                x + index * spacing,
                y,
                number,
                ball_radius
            )

        else:

            # Pocketed ball:
            # leave its position empty.
            draw_empty_hud_ball(
                x + index * spacing,
                y,
                ball_radius
            )

    # -----------------------------------------------------
    # ALL GROUP BALLS CLEARED
    # -----------------------------------------------------

    if not remaining:

        # Replace the first silhouette with the 8-ball
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

    # White number circle
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

    rect = text_surface.get_rect(
        center=(
            WINDOW_WIDTH // 2,
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

    # =====================================================
    # TOP BAR
    # =====================================================

    hud_height = 78

    hud = pygame.Surface(
        (
            WINDOW_WIDTH,
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

    pygame.draw.line(
        screen,
        HUD_BORDER,
        (
            0,
            hud_height - 1
        ),
        (
            WINDOW_WIDTH,
            hud_height - 1
        ),
        1
    )

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

    normal_font = pygame.font.SysFont(
        "arial",
        12
    )

    # =====================================================
    # PLAYER
    # =====================================================

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

    # =====================================================
    # PLAYER BALLS
    # =====================================================

    draw_group_balls(
        player_x + 10,
        66,
        player_group,
        ball_radius=7,
        spacing=18
    )

    # =====================================================
    # CENTER GROUP
    # =====================================================

    center_x = WINDOW_WIDTH // 2

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

    screen.blit(
        group_surface,
        group_rect
    )

    # =====================================================
    # AI
    # =====================================================

    right_x = WINDOW_WIDTH - 25

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

    screen.blit(
        ai_title,
        ai_title_rect
    )

    screen.blit(
        ai_status_surface,
        ai_status_rect
    )

    # =====================================================
    # AI BALLS
    # =====================================================

    ai_ball_numbers = (
        get_hud_ball_numbers(ai_group)
        if ai_group is not None
        else list(range(7))
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

    # =====================================================
    # BOTTOM POWER PANEL
    # =====================================================

    if current_player == PLAYER_HUMAN:

        panel_width = 250
        panel_height = 64

        panel_x = 22
        panel_y = WINDOW_HEIGHT - panel_height - 18

        panel_rect = pygame.Rect(
            panel_x,
            panel_y,
            panel_width,
            panel_height
        )

        draw_panel(
            panel_rect,
            fill=(8, 8, 10, 225),
            border=(55, 55, 60),
            radius=9
        )

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

        # -------------------------------------------------
        # POWER BAR
        # -------------------------------------------------

        bar_x = panel_x + 12
        bar_y = panel_y + 33

        bar_width = panel_width - 24
        bar_height = 9

        pygame.draw.rect(
            screen,
            (30, 30, 34),
            (
                bar_x,
                bar_y,
                bar_width,
                bar_height
            ),
            border_radius=4
        )

        progress = (
            human_power -
            HUMAN_MIN_POWER
        ) / (
            HUMAN_MAX_POWER -
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

            pygame.draw.rect(
                screen,
                YELLOW,
                (
                    bar_x + 2,
                    bar_y + 2,
                    fill_width,
                    bar_height - 4
                ),
                border_radius=3
            )

        # -------------------------------------------------
        # POWER CONTROLS
        # -------------------------------------------------

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

    # =====================================================
    # BOTTOM RIGHT CONTROLS
    # =====================================================

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
            WINDOW_WIDTH - 22,
            WINDOW_HEIGHT - 24
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

    # =====================================================
    # GEOMETRY HELPERS
    # =====================================================

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

    # =====================================================
    # FIND FIRST BALL HIT BY THE WHITE BALL
    # =====================================================

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

    # =====================================================
    # FIND CUSHION
    # =====================================================

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

    if hit_first:
        white_line_distance = nearest_distance
    else:
        white_line_distance = table_distance

    white_end_x = (
        cue_ball.x +
        dx * white_line_distance
    )

    white_end_y = (
        cue_ball.y +
        dy * white_line_distance
    )

    # =====================================================
    # INCOMING WHITE-BALL TRAJECTORY
    # =====================================================

    cue_line_start_x = (
        cue_ball.x +
        dx * (cue_ball.radius + 1)
    )

    cue_line_start_y = (
        cue_ball.y +
        dy * (cue_ball.radius + 1)
    )

    pygame.draw.line(
        screen,
        WHITE,
        (
            int(cue_line_start_x),
            int(cue_line_start_y)
        ),
        (
            int(white_end_x),
            int(white_end_y)
        ),
        2
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (
            int(white_end_x),
            int(white_end_y)
        ),
        3
    )

    if not hit_first:
        return

    ghost_x = white_end_x
    ghost_y = white_end_y

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

    # =====================================================
    # TARGET BALL OUTGOING DIRECTION
    # =====================================================

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

    # =====================================================
    # TARGET BALL TRAJECTORY
    # =====================================================

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
        target_dx * (hit_ball.radius + 1)
    )

    target_line_start_y = (
        hit_ball.y +
        target_dy * (hit_ball.radius + 1)
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

    # =====================================================
    # CUE-BALL DEFLECTION AFTER IMPACT
    # =====================================================

    normal_speed = (
        dx * target_dx +
        dy * target_dy
    )

    cue_deflect_vx = (
        dx -
        (1 + BALL_RESTITUTION)
        * normal_speed
        * target_dx
    )

    cue_deflect_vy = (
        dy -
        (1 + BALL_RESTITUTION)
        * normal_speed
        * target_dy
    )

    cue_deflect_length = math.hypot(
        cue_deflect_vx,
        cue_deflect_vy
    )

    if cue_deflect_length > 1e-6:

        cue_deflect_dx = (
            cue_deflect_vx /
            cue_deflect_length
        )

        cue_deflect_dy = (
            cue_deflect_vy /
            cue_deflect_length
        )

        cue_deflect_distance = ray_box_distance(
            ghost_x,
            ghost_y,
            cue_deflect_dx,
            cue_deflect_dy,
            cue_ball.radius
        )

        if cue_deflect_distance != float("inf"):

            cue_deflect_end_x = (
                ghost_x +
                cue_deflect_dx * cue_deflect_distance
            )

            cue_deflect_end_y = (
                ghost_y +
                cue_deflect_dy * cue_deflect_distance
            )

            cue_deflect_start_x = (
                ghost_x +
                cue_deflect_dx *
                (cue_ball.radius + 1)
            )

            cue_deflect_start_y = (
                ghost_y +
                cue_deflect_dy *
                (cue_ball.radius + 1)
            )

            cue_deflection_color = (
                120,
                220,
                255
            )

            pygame.draw.line(
                screen,
                cue_deflection_color,
                (
                    int(cue_deflect_start_x),
                    int(cue_deflect_start_y)
                ),
                (
                    int(cue_deflect_end_x),
                    int(cue_deflect_end_y)
                ),
                2
            )

    # =====================================================
    # REAL CONTACT POINT ON TARGET SURFACE
    # =====================================================

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

    shot_in_progress = True
    shot_shooter = shooter
    shot_pocketed = []

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

    global human_power

    waiting_for_start = False

    paused = False

    menu_selected = 0
    game_over_selected = 0
    pause_selected = 0

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

    human_power = 10.0

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
        range(1, 16),
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

        if shooter_group is not None and all_group_cleared(
            shooter_group
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

    start_shot(
        PLAYER_AI
    )

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

            # ---------------------------------------------
            # START MENU
            # ---------------------------------------------

            if waiting_for_start:

                if event.key == pygame.K_UP:

                    menu_selected = (
                        menu_selected - 1
                    ) % len(menu_options)

                elif event.key == pygame.K_DOWN:

                    menu_selected = (
                        menu_selected + 1
                    ) % len(menu_options)

                elif event.key == pygame.K_RETURN:

                    if menu_options[
                        menu_selected
                    ] == "PLAY":

                        waiting_for_start = False

                    elif menu_options[
                        menu_selected
                    ] == "QUIT":

                        running = False

            # ---------------------------------------------
            # GAME OVER MENU
            # ---------------------------------------------

            elif game_over:

                if event.key == pygame.K_UP:

                    game_over_selected = (
                        game_over_selected - 1
                    ) % len(game_over_options)

                elif event.key == pygame.K_DOWN:

                    game_over_selected = (
                        game_over_selected + 1
                    ) % len(game_over_options)

                elif event.key == pygame.K_RETURN:

                    if game_over_options[
                        game_over_selected
                    ] == "QUIT":

                        running = False

                    elif game_over_options[
                        game_over_selected
                    ] == "PLAY AGAIN":

                        reset_game()

                elif event.key == pygame.K_ESCAPE:

                    running = False

            # ---------------------------------------------
            # PAUSE MENU
            # ---------------------------------------------

            elif paused:

                if event.key == pygame.K_UP:

                    pause_selected = (
                        pause_selected - 1
                    ) % len(pause_options)

                elif event.key == pygame.K_DOWN:

                    pause_selected = (
                        pause_selected + 1
                    ) % len(pause_options)

                elif event.key == pygame.K_RETURN:

                    selected_option = (
                        pause_options[
                            pause_selected
                        ]
                    )

                    if selected_option == "RESUME":

                        paused = False

                    elif selected_option == "RESTART":

                        reset_game()

                    elif selected_option == "QUIT":

                        running = False

                elif event.key == pygame.K_ESCAPE:

                    paused = False

            # ---------------------------------------------
            # ACTIVE GAME
            # ---------------------------------------------

            else:

                if event.key == pygame.K_ESCAPE:

                    paused = True
                    pause_selected = 0

        elif event.type == pygame.MOUSEBUTTONDOWN:

            # ---------------------------------------------
            # HUMAN SHOOT
            # ---------------------------------------------

            if (
                event.button == 1
                and not waiting_for_start
                and not game_over
                and not paused
                and current_player == PLAYER_HUMAN
                and not shot_pending
                and not shot_in_progress
                and all_balls_stopped(balls)
            ):

                fire_human_shot()

            # ---------------------------------------------
            # POWER UP
            # ---------------------------------------------

            elif (
                event.button == 4
                and current_player == PLAYER_HUMAN
                and not paused
                and not game_over
            ):

                human_power = min(
                    HUMAN_MAX_POWER,
                    human_power + 0.5
                )

            # ---------------------------------------------
            # POWER DOWN
            # ---------------------------------------------

            elif (
                event.button == 5
                and current_player == PLAYER_HUMAN
                and not paused
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
    ):

        # -------------------------------------------------
        # AI TURN
        # -------------------------------------------------

        if current_player == PLAYER_AI:

            start_ai_turn()

        # -------------------------------------------------
        # AI PREVIEW
        # -------------------------------------------------

        if shot_pending:

            shot_preview_timer -= dt

            if shot_preview_timer <= 0:

                fire_ai_shot()

        # -------------------------------------------------
        # PHYSICS
        # -------------------------------------------------

        if (
            shot_in_progress
            and not all_balls_stopped(balls)
        ):

            pocketed = update_physics(
                balls,
                table
            )

            if pocketed:

                shot_pocketed.extend(
                    pocketed
                )

        # -------------------------------------------------
        # SHOT FINISHED
        # -------------------------------------------------

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

    # -----------------------------------------------------
    # HUMAN AIM
    # -----------------------------------------------------

    draw_human_aim()

    # -----------------------------------------------------
    # AI AIM
    # -----------------------------------------------------

    draw_ai_prediction()

    # -----------------------------------------------------
    # HUD
    # -----------------------------------------------------

    if not waiting_for_start:

        draw_hud()

        draw_game_status()

    # -----------------------------------------------------
    # START SCREEN
    # -----------------------------------------------------

    if waiting_for_start:

        draw_start_screen()

    # -----------------------------------------------------
    # GAME OVER
    # -----------------------------------------------------

    elif game_over:

        draw_game_over()

    # -----------------------------------------------------
    # PAUSE
    # -----------------------------------------------------

    elif paused:

        draw_pause_menu()

    # =====================================================
    # DISPLAY
    # =====================================================

    pygame.display.flip()


# =========================================================
# CLEANUP
# =========================================================

pygame.quit()