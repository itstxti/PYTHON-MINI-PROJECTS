import math
import pygame

from settings import (
    BALL_RADIUS,
    BALL_FRICTION,
    BALL_STOP_SPEED
)


class Ball:

    def __init__(
        self,
        x,
        y,
        color,
        number=None,
        is_cue=False
    ):
        self.x = float(x)
        self.y = float(y)

        self.vx = 0.0
        self.vy = 0.0

        self.color = color
        self.number = number
        self.is_cue = is_cue

        self.radius = BALL_RADIUS
        self.active = True

        # First object ball hit by the cue ball
        # during the current shot.
        self.first_hit_number = None

    @property
    def speed(self):

        return math.hypot(
            self.vx,
            self.vy
        )

    def update(
        self,
        scale=1.0
    ):

        if not self.active:
            return

        self.x += self.vx * scale
        self.y += self.vy * scale

        # Con subdivisiones se conserva la fricción total
        # del fotograma completo.
        friction = BALL_FRICTION ** scale

        self.vx *= friction
        self.vy *= friction

        if self.speed < BALL_STOP_SPEED:

            self.vx = 0.0
            self.vy = 0.0

    def shoot(
        self,
        angle,
        power
    ):

        self.vx = (
            math.cos(angle) *
            power
        )

        self.vy = (
            math.sin(angle) *
            power
        )

        # A new shot starts.
        self.first_hit_number = None

    def clone(self):

        new_ball = Ball(
            self.x,
            self.y,
            self.color,
            self.number,
            self.is_cue
        )

        new_ball.vx = self.vx
        new_ball.vy = self.vy

        new_ball.active = self.active

        new_ball.first_hit_number = (
            self.first_hit_number
        )

        return new_ball

    def draw(
        self,
        screen
    ):

        if not self.active:
            return

        center = (
            int(self.x),
            int(self.y)
        )

        # =================================================
        # CUE BALL
        # =================================================

        if self.is_cue:

            pygame.draw.circle(
                screen,
                (245, 245, 245),
                center,
                self.radius
            )

        # =================================================
        # 8-BALL
        # =================================================

        elif self.number == 8:

            pygame.draw.circle(
                screen,
                (15, 15, 15),
                center,
                self.radius
            )

        # =================================================
        # STRIPED BALLS 9-15
        # =================================================

        elif self.number >= 9:

            pygame.draw.circle(
                screen,
                (245, 245, 245),
                center,
                self.radius
            )

            size = (
                self.radius * 2 +
                4
            )

            stripe_surface = pygame.Surface(
                (
                    size,
                    size
                ),
                pygame.SRCALPHA
            )

            stripe_center = (
                size // 2,
                size // 2
            )

            pygame.draw.rect(
                stripe_surface,
                self.color,
                (
                    0,
                    stripe_center[1] - 4,
                    size,
                    8
                )
            )

            mask = pygame.Surface(
                (
                    size,
                    size
                ),
                pygame.SRCALPHA
            )

            pygame.draw.circle(
                mask,
                (255, 255, 255, 255),
                stripe_center,
                self.radius
            )

            stripe_surface.blit(
                mask,
                (
                    0,
                    0
                ),
                special_flags=pygame.BLEND_RGBA_MULT
            )

            screen.blit(
                stripe_surface,
                (
                    int(
                        self.x -
                        size / 2
                    ),
                    int(
                        self.y -
                        size / 2
                    )
                )
            )

        # =================================================
        # SOLID BALLS 1-7
        # =================================================

        else:

            pygame.draw.circle(
                screen,
                self.color,
                center,
                self.radius
            )

        # =================================================
        # OUTLINE
        # =================================================

        pygame.draw.circle(
            screen,
            (20, 20, 20),
            center,
            self.radius,
            1
        )

        # =================================================
        # NUMBER
        # =================================================

        if self.number is not None:

            font = pygame.font.SysFont(
                "arial",
                10,
                bold=True
            )

            text_color = (
                (20, 20, 20)
                if self.number >= 9
                else (255, 255, 255)
            )

            text = font.render(
                str(self.number),
                True,
                text_color
            )

            text_rect = text.get_rect(
                center=center
            )

            screen.blit(
                text,
                text_rect
            )