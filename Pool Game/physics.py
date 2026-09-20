import math

from settings import (
    BALL_RESTITUTION,
    BALL_RADIUS
)


# Cada subpaso recorre menos de la mitad del radio,
# evitando que bolas rápidas atraviesen otras bolas.
MAX_STEP_DISTANCE = BALL_RADIUS * 0.35
MAX_SUBSTEPS = 24
COLLISION_SLOP = 0.01


def resolve_ball_collision(
    ball_a,
    ball_b
):

    if not ball_a.active:
        return False

    if not ball_b.active:
        return False

    dx = (
        ball_b.x -
        ball_a.x
    )

    dy = (
        ball_b.y -
        ball_a.y
    )

    distance_squared = (
        dx * dx +
        dy * dy
    )

    minimum_distance = (
        ball_a.radius +
        ball_b.radius
    )

    if distance_squared >= minimum_distance ** 2:
        return False

    distance = math.sqrt(
        distance_squared
    )

    # Posición degenerada: separar en una dirección estable.
    if distance < 1e-9:

        nx = 1.0
        ny = 0.0

    else:

        nx = dx / distance
        ny = dy / distance

    # =====================================================
    # FIRST CUE-BALL CONTACT
    # =====================================================

    if ball_a.is_cue and not ball_b.is_cue:

        if ball_a.first_hit_number is None:

            ball_a.first_hit_number = (
                ball_b.number
            )

    elif ball_b.is_cue and not ball_a.is_cue:

        if ball_b.first_hit_number is None:

            ball_b.first_hit_number = (
                ball_a.number
            )

    # =====================================================
    # POSITION CORRECTION
    # =====================================================

    overlap = (
        minimum_distance -
        distance
    )

    if overlap > 0:

        correction = max(
            overlap - COLLISION_SLOP,
            0.0
        ) * 0.5

        ball_a.x -= (
            nx * correction
        )

        ball_a.y -= (
            ny * correction
        )

        ball_b.x += (
            nx * correction
        )

        ball_b.y += (
            ny * correction
        )

    # =====================================================
    # RELATIVE VELOCITY
    # =====================================================

    rvx = (
        ball_b.vx -
        ball_a.vx
    )

    rvy = (
        ball_b.vy -
        ball_a.vy
    )

    velocity_along_normal = (
        rvx * nx +
        rvy * ny
    )

    # Las bolas ya se están separando.
    if velocity_along_normal > 0:
        return True

    # =====================================================
    # IMPULSE FOR EQUAL MASSES
    # =====================================================

    impulse = (
        -(1 + BALL_RESTITUTION)
        * velocity_along_normal
        / 2
    )

    ball_a.vx -= (
        impulse *
        nx
    )

    ball_a.vy -= (
        impulse *
        ny
    )

    ball_b.vx += (
        impulse *
        nx
    )

    ball_b.vy += (
        impulse *
        ny
    )

    return True


def update_physics(
    balls,
    table
):

    pocketed = []

    active_balls = [
        ball
        for ball in balls
        if ball.active
    ]

    if not active_balls:
        return pocketed

    max_speed = max(
        ball.speed
        for ball in active_balls
    )

    if max_speed == 0:
        return pocketed

    substeps = max(
        1,
        math.ceil(
            max_speed /
            MAX_STEP_DISTANCE
        )
    )

    substeps = min(
        substeps,
        MAX_SUBSTEPS
    )

    step_scale = 1.0 / substeps

    for _ in range(substeps):

        # =================================================
        # MOVE, POCKET AND CUSHION
        # =================================================

        for ball in balls:

            if not ball.active:
                continue

            ball.update(
                step_scale
            )

            if table.ball_in_pocket(
                ball
            ):

                pocketed.append(
                    ball
                )

                ball.active = False

                ball.vx = 0
                ball.vy = 0

                continue

            table.bounce_ball(
                ball
            )

        # =================================================
        # BALL-BALL COLLISIONS
        # =================================================

        for i in range(
            len(balls)
        ):

            for j in range(
                i + 1,
                len(balls)
            ):

                resolve_ball_collision(
                    balls[i],
                    balls[j]
                )

    return pocketed


def all_balls_stopped(
    balls
):

    return all(
        ball.speed == 0
        for ball in balls
        if ball.active
    )