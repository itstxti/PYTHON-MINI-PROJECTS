import math
import pygame

from settings import (
    TABLE_X,
    TABLE_Y,
    TABLE_WIDTH,
    TABLE_HEIGHT,
    POCKET_RADIUS
)


CUSHION_RESTITUTION = 0.92


class Table:

    def __init__(self):

        self.rect = pygame.Rect(
            TABLE_X,
            TABLE_Y,
            TABLE_WIDTH,
            TABLE_HEIGHT
        )

        self.pockets = [

            (
                TABLE_X,
                TABLE_Y
            ),

            (
                TABLE_X + TABLE_WIDTH // 2,
                TABLE_Y
            ),

            (
                TABLE_X + TABLE_WIDTH,
                TABLE_Y
            ),

            (
                TABLE_X,
                TABLE_Y + TABLE_HEIGHT
            ),

            (
                TABLE_X + TABLE_WIDTH // 2,
                TABLE_Y + TABLE_HEIGHT
            ),

            (
                TABLE_X + TABLE_WIDTH,
                TABLE_Y + TABLE_HEIGHT
            ),
        ]

    # =====================================================
    # DRAW
    # =====================================================

    def draw(
        self,
        screen
    ):

        # Wood

        pygame.draw.rect(
            screen,
            (105, 62, 30),
            self.rect.inflate(
                35,
                35
            ),
            border_radius=12
        )

        # Cloth

        pygame.draw.rect(
            screen,
            (24, 105, 65),
            self.rect,
            border_radius=5
        )

        # Pockets

        for x, y in self.pockets:

            pygame.draw.circle(
                screen,
                (15, 15, 15),
                (
                    x,
                    y
                ),
                POCKET_RADIUS
            )

    # =====================================================
    # POCKET CHECK
    # =====================================================

    def ball_in_pocket(
        self,
        ball
    ):

        for px, py in self.pockets:

            distance = math.hypot(
                ball.x - px,
                ball.y - py
            )

            if distance < POCKET_RADIUS:

                return True

        return False

    # =====================================================
    # CUSHION
    # =====================================================

    def bounce_ball(
        self,
        ball
    ):

        left = (
            TABLE_X +
            ball.radius
        )

        right = (
            TABLE_X +
            TABLE_WIDTH -
            ball.radius
        )

        top = (
            TABLE_Y +
            ball.radius
        )

        bottom = (
            TABLE_Y +
            TABLE_HEIGHT -
            ball.radius
        )

        if (
            ball.x <= left
            and ball.vx < 0
        ):

            ball.x = left
            ball.vx *= -CUSHION_RESTITUTION

        elif (
            ball.x >= right
            and ball.vx > 0
        ):

            ball.x = right
            ball.vx *= -CUSHION_RESTITUTION

        if (
            ball.y <= top
            and ball.vy < 0
        ):

            ball.y = top
            ball.vy *= -CUSHION_RESTITUTION

        elif (
            ball.y >= bottom
            and ball.vy > 0
        ):

            ball.y = bottom
            ball.vy *= -CUSHION_RESTITUTION