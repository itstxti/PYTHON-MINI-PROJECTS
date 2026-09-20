import math

from settings import (
    MAX_POWER,
    BALL_RADIUS,
    TABLE_X,
    TABLE_Y,
    TABLE_WIDTH,
    TABLE_HEIGHT
)

from physics import update_physics


class PoolAI:

    def __init__(self):
        self.best_shot = None

    # =========================================================
    # GEOMETRY
    # =========================================================

    @staticmethod
    def distance(x1, y1, x2, y2):
        return math.hypot(
            x2 - x1,
            y2 - y1
        )

    @staticmethod
    def angle_between(x1, y1, x2, y2):
        return math.atan2(
            y2 - y1,
            x2 - x1
        )

    @staticmethod
    def normalize(x, y):

        length = math.hypot(
            x,
            y
        )

        if length == 0:
            return 0.0, 0.0

        return (
            x / length,
            y / length
        )

    @staticmethod
    def angle_difference(
        angle_a,
        angle_b
    ):

        return abs(
            math.atan2(
                math.sin(
                    angle_a - angle_b
                ),
                math.cos(
                    angle_a - angle_b
                )
            )
        )

    # =========================================================
    # POCKETS
    # =========================================================

    @staticmethod
    def get_pockets():

        return [
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
            )
        ]

    # =========================================================
    # GHOST BALL
    # =========================================================

    def ghost_ball_position(
        self,
        target,
        pocket
    ):

        dx = (
            pocket[0] -
            target.x
        )

        dy = (
            pocket[1] -
            target.y
        )

        dx, dy = self.normalize(
            dx,
            dy
        )

        ghost_distance = (
            BALL_RADIUS * 2
        )

        return (
            target.x -
            dx * ghost_distance,

            target.y -
            dy * ghost_distance
        )

    # =========================================================
    # CONTACT POINT
    # =========================================================

    def contact_point(
        self,
        target,
        pocket
    ):

        dx = (
            pocket[0] -
            target.x
        )

        dy = (
            pocket[1] -
            target.y
        )

        dx, dy = self.normalize(
            dx,
            dy
        )

        return (
            target.x -
            dx * BALL_RADIUS,

            target.y -
            dy * BALL_RADIUS
        )

    # =========================================================
    # POWER
    # =========================================================

    def calculate_power(
        self,
        cue_distance,
        target_distance,
        cut_angle,
        shot_type
    ):

        total_distance = (
            cue_distance +
            target_distance
        )

        power = (
            3.5 +
            total_distance * 0.032
        )

        cut_factor = (
            cut_angle / 90.0
        )

        power += (
            cut_factor * 2.0
        )

        if shot_type == "bank":

            power += 2.0

        power = max(
            3.5,
            power
        )

        power = min(
            MAX_POWER,
            power
        )

        return power

    # =========================================================
    # DIRECT SHOT
    # =========================================================

    def generate_direct_shot(
        self,
        cue_ball,
        target,
        pocket
    ):

        ghost_x, ghost_y = (
            self.ghost_ball_position(
                target,
                pocket
            )
        )

        contact_x, contact_y = (
            self.contact_point(
                target,
                pocket
            )
        )

        angle = self.angle_between(
            cue_ball.x,
            cue_ball.y,
            ghost_x,
            ghost_y
        )

        cue_distance = self.distance(
            cue_ball.x,
            cue_ball.y,
            ghost_x,
            ghost_y
        )

        target_distance = self.distance(
            target.x,
            target.y,
            pocket[0],
            pocket[1]
        )

        pocket_angle = self.angle_between(
            target.x,
            target.y,
            pocket[0],
            pocket[1]
        )

        cut_angle = math.degrees(
            self.angle_difference(
                angle,
                pocket_angle
            )
        )

        power = self.calculate_power(
            cue_distance,
            target_distance,
            cut_angle,
            "direct"
        )

        distance_score = (
            cue_distance +
            target_distance
        )

        cut_penalty = (
            cut_angle ** 1.35
        )

        score = (
            distance_score +
            cut_penalty * 1.5
        )

        return {
            "type": "direct",

            "target": target,

            "pocket": pocket,

            "contact": (
                contact_x,
                contact_y
            ),

            "ghost": (
                ghost_x,
                ghost_y
            ),

            "aim_point": (
                ghost_x,
                ghost_y
            ),

            "angle": angle,

            "power": power,

            "cut_angle": cut_angle,

            "score": score
        }

    # =========================================================
    # BANK SHOT
    # =========================================================

    def generate_bank_shot(
        self,
        cue_ball,
        target,
        pocket
    ):

        candidates = []

        # -----------------------------------------------------
        # TOP
        # -----------------------------------------------------

        top_y = TABLE_Y

        mirrored_y = (
            2 * top_y -
            pocket[1]
        )

        dx = (
            pocket[0] -
            target.x
        )

        dy = (
            mirrored_y -
            target.y
        )

        if dy != 0:

            t = (
                top_y -
                target.y
            ) / dy

            if 0 < t < 1:

                bank_x = (
                    target.x +
                    dx * t
                )

                if (
                    TABLE_X + BALL_RADIUS
                    <
                    bank_x
                    <
                    TABLE_X +
                    TABLE_WIDTH -
                    BALL_RADIUS
                ):

                    shot = self.build_bank_shot(
                        cue_ball,
                        target,
                        pocket,
                        (
                            bank_x,
                            top_y
                        ),
                        "top"
                    )

                    if shot is not None:

                        candidates.append(
                            shot
                        )

        # -----------------------------------------------------
        # BOTTOM
        # -----------------------------------------------------

        bottom_y = (
            TABLE_Y +
            TABLE_HEIGHT
        )

        mirrored_y = (
            2 * bottom_y -
            pocket[1]
        )

        dx = (
            pocket[0] -
            target.x
        )

        dy = (
            mirrored_y -
            target.y
        )

        if dy != 0:

            t = (
                bottom_y -
                target.y
            ) / dy

            if 0 < t < 1:

                bank_x = (
                    target.x +
                    dx * t
                )

                if (
                    TABLE_X + BALL_RADIUS
                    <
                    bank_x
                    <
                    TABLE_X +
                    TABLE_WIDTH -
                    BALL_RADIUS
                ):

                    shot = self.build_bank_shot(
                        cue_ball,
                        target,
                        pocket,
                        (
                            bank_x,
                            bottom_y
                        ),
                        "bottom"
                    )

                    if shot is not None:

                        candidates.append(
                            shot
                        )

        if not candidates:
            return None

        candidates.sort(
            key=lambda shot:
            shot["score"]
        )

        return candidates[0]

    # =========================================================
    # BUILD BANK SHOT
    # =========================================================

    def build_bank_shot(
        self,
        cue_ball,
        target,
        pocket,
        bank_point,
        side
    ):

        bx, by = bank_point

        dx = (
            bx -
            target.x
        )

        dy = (
            by -
            target.y
        )

        dx, dy = self.normalize(
            dx,
            dy
        )

        ghost_distance = (
            BALL_RADIUS * 2
        )

        ghost_x = (
            target.x -
            dx * ghost_distance
        )

        ghost_y = (
            target.y -
            dy * ghost_distance
        )

        contact_x = (
            target.x -
            dx * BALL_RADIUS
        )

        contact_y = (
            target.y -
            dy * BALL_RADIUS
        )

        angle = self.angle_between(
            cue_ball.x,
            cue_ball.y,
            ghost_x,
            ghost_y
        )

        cue_distance = self.distance(
            cue_ball.x,
            cue_ball.y,
            ghost_x,
            ghost_y
        )

        target_to_bank = self.distance(
            target.x,
            target.y,
            bx,
            by
        )

        bank_to_pocket = self.distance(
            bx,
            by,
            pocket[0],
            pocket[1]
        )

        total_distance = (
            cue_distance +
            target_to_bank +
            bank_to_pocket
        )

        pocket_angle = self.angle_between(
            target.x,
            target.y,
            pocket[0],
            pocket[1]
        )

        target_angle = self.angle_between(
            target.x,
            target.y,
            bx,
            by
        )

        cut_angle = math.degrees(
            self.angle_difference(
                target_angle,
                pocket_angle
            )
        )

        power = self.calculate_power(
            cue_distance,
            target_to_bank +
            bank_to_pocket,
            cut_angle,
            "bank"
        )

        score = (
            total_distance +
            150 +
            cut_angle * 2.0
        )

        return {
            "type": "bank",

            "target": target,

            "pocket": pocket,

            "contact": (
                contact_x,
                contact_y
            ),

            "ghost": (
                ghost_x,
                ghost_y
            ),

            "aim_point": (
                ghost_x,
                ghost_y
            ),

            "bank_point": (
                bx,
                by
            ),

            "side": side,

            "angle": angle,

            "power": power,

            "cut_angle": cut_angle,

            "score": score
        }

    # =========================================================
    # GENERATE SHOTS
    # =========================================================

    def generate_shots(
        self,
        cue_ball,
        balls,
        allowed_numbers=None
    ):

        pockets = self.get_pockets()

        targets = [
            ball
            for ball in balls
            if (
                ball.active
                and not ball.is_cue
                and (
                    allowed_numbers is None
                    or ball.number in allowed_numbers
                )
            )
        ]

        shots = []

        for target in targets:

            for pocket in pockets:

                direct = (
                    self.generate_direct_shot(
                        cue_ball,
                        target,
                        pocket
                    )
                )

                shots.append(
                    direct
                )

                bank = (
                    self.generate_bank_shot(
                        cue_ball,
                        target,
                        pocket
                    )
                )

                if bank is not None:

                    shots.append(
                        bank
                    )

        return shots

    # =========================================================
    # SIMULATE SHOT
    # =========================================================

    def simulate_shot(
        self,
        shot,
        balls,
        table
    ):

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
            shot["angle"],
            shot["power"]
        )

        pocketed = []

        for _ in range(500):

            newly_pocketed = (
                update_physics(
                    simulated_balls,
                    table
                )
            )

            pocketed.extend(
                newly_pocketed
            )

            if all(
                ball.speed == 0
                for ball in simulated_balls
                if ball.active
            ):
                break

        return (
            simulated_balls,
            pocketed
        )

    # =========================================================
    # BLACK BALL
    # =========================================================

    @staticmethod
    def black_ball_is_bad(
        pocketed,
        allowed_numbers
    ):

        black_pocketed = any(
            ball.number == 8
            for ball in pocketed
        )

        if not black_pocketed:
            return False

        if (
            allowed_numbers is not None
            and set(allowed_numbers) == {8}
        ):
            return False

        return True

    # =========================================================
    # CUE POSITION SCORE
    # =========================================================

    def cue_position_score(
        self,
        simulated_cue,
        simulated_balls,
        allowed_numbers
    ):

        if simulated_cue is None:
            return -500

        targets = [
            ball
            for ball in simulated_balls
            if (
                ball.active
                and not ball.is_cue
                and ball.number != 8
                and (
                    allowed_numbers is None
                    or ball.number in allowed_numbers
                )
            )
        ]

        if not targets:
            return 0

        distances = [
            self.distance(
                simulated_cue.x,
                simulated_cue.y,
                ball.x,
                ball.y
            )
            for ball in targets
        ]

        nearest = min(
            distances
        )

        position_score = max(
            -100,
            140 -
            nearest * 0.45
        )

        return position_score

    # =========================================================
    # SECOND SHOT ANALYSIS
    # =========================================================

    def estimate_next_shot(
        self,
        simulated_balls,
        table,
        allowed_numbers
    ):

        simulated_cue = next(
            (
                ball
                for ball in simulated_balls
                if (
                    ball.is_cue
                    and ball.active
                )
            ),
            None
        )

        if simulated_cue is None:
            return -500

        # If there are no targets left,
        # the current shot has effectively
        # cleared the group.

        targets = [
            ball
            for ball in simulated_balls
            if (
                ball.active
                and not ball.is_cue
                and (
                    allowed_numbers is None
                    or ball.number in allowed_numbers
                )
            )
        ]

        if not targets:
            return 300

        best_future_score = float("-inf")

        # We deliberately only inspect direct
        # future shots here. This keeps the
        # lookahead affordable.

        for target in targets:

            for pocket in self.get_pockets():

                ghost_x, ghost_y = (
                    self.ghost_ball_position(
                        target,
                        pocket
                    )
                )

                cue_distance = self.distance(
                    simulated_cue.x,
                    simulated_cue.y,
                    ghost_x,
                    ghost_y
                )

                target_distance = self.distance(
                    target.x,
                    target.y,
                    pocket[0],
                    pocket[1]
                )

                pocket_angle = self.angle_between(
                    target.x,
                    target.y,
                    pocket[0],
                    pocket[1]
                )

                cue_angle = self.angle_between(
                    simulated_cue.x,
                    simulated_cue.y,
                    ghost_x,
                    ghost_y
                )

                cut_angle = math.degrees(
                    self.angle_difference(
                        cue_angle,
                        pocket_angle
                    )
                )

                future_distance = (
                    cue_distance +
                    target_distance
                )

                # A lower value means an easier
                # future shot.

                difficulty = (
                    future_distance +
                    cut_angle * 3.0
                )

                future_score = (
                    500 -
                    difficulty
                )

                if future_score > best_future_score:

                    best_future_score = (
                        future_score
                    )

        return max(
            -150,
            min(
                300,
                best_future_score
            )
        )

    # =========================================================
    # EVALUATION
    # =========================================================

    def evaluate_shot(
        self,
        shot,
        balls,
        table,
        allowed_numbers=None
    ):

        simulated_balls, pocketed = (
            self.simulate_shot(
                shot,
                balls,
                table
            )
        )

        # -----------------------------------------------------
        # SCRATCH
        # -----------------------------------------------------

        if any(
            ball.is_cue
            for ball in pocketed
        ):

            return float("-inf")

        # -----------------------------------------------------
        # ILLEGAL 8
        # -----------------------------------------------------

        if self.black_ball_is_bad(
            pocketed,
            allowed_numbers
        ):

            return float("-inf")

        target_number = (
            shot["target"].number
        )

        target_pocketed = False

        score = 0.0

        # -----------------------------------------------------
        # POCKETED BALLS
        # -----------------------------------------------------

        for ball in pocketed:

            if ball.is_cue:
                continue

            if ball.number == 8:

                score += 1200

                continue

            if ball.number == target_number:

                score += 700

                target_pocketed = True

                continue

            if (
                allowed_numbers is None
                or ball.number in allowed_numbers
            ):

                score += 100

        # -----------------------------------------------------
        # TARGET RESULT
        # -----------------------------------------------------

        if target_pocketed:

            score += 350

        else:

            score -= 180

        # -----------------------------------------------------
        # SHOT DIFFICULTY
        # -----------------------------------------------------

        score -= (
            shot["score"] *
            0.22
        )

        # Direct shots are preferred,
        # but not overwhelmingly.

        if shot["type"] == "direct":

            score += 65

        else:

            score -= 40

        # -----------------------------------------------------
        # CUT ANGLE
        # -----------------------------------------------------

        cut_angle = (
            shot["cut_angle"]
        )

        if cut_angle > 60:

            score -= (
                cut_angle -
                60
            ) * 4.0

        # -----------------------------------------------------
        # POWER
        # -----------------------------------------------------

        if shot["power"] > 15:

            score -= (
                shot["power"] -
                15
            ) * 12

        # -----------------------------------------------------
        # CUE POSITION
        # -----------------------------------------------------

        simulated_cue = next(
            (
                ball
                for ball in simulated_balls
                if (
                    ball.is_cue
                    and ball.active
                )
            ),
            None
        )

        if target_pocketed:

            score += self.cue_position_score(
                simulated_cue,
                simulated_balls,
                allowed_numbers
            )

        # -----------------------------------------------------
        # SECOND SHOT
        # -----------------------------------------------------

        if target_pocketed:

            next_shot_score = (
                self.estimate_next_shot(
                    simulated_balls,
                    table,
                    allowed_numbers
                )
            )

            score += (
                next_shot_score *
                0.65
            )

        # -----------------------------------------------------
        # BALLS LEFT
        # -----------------------------------------------------

        remaining_targets = [
            ball
            for ball in simulated_balls
            if (
                ball.active
                and not ball.is_cue
                and ball.number != 8
                and (
                    allowed_numbers is None
                    or ball.number in allowed_numbers
                )
            )
        ]

        if target_pocketed:

            if not remaining_targets:

                score += 500

            else:

                nearest = min(
                    self.distance(
                        simulated_cue.x,
                        simulated_cue.y,
                        ball.x,
                        ball.y
                    )
                    for ball in remaining_targets
                )

                if nearest < 120:

                    score += 80

                elif nearest > 500:

                    score -= 50

        return score

    # =========================================================
    # FIND BEST SHOT
    # =========================================================

    def find_best_shot(
        self,
        cue_ball,
        balls,
        table,
        allowed_numbers=None
    ):

        candidates = (
            self.generate_shots(
                cue_ball,
                balls,
                allowed_numbers
            )
        )

        print(
            "AI | candidates:",
            len(candidates)
        )

        if not candidates:

            print(
                "AI | NO CANDIDATES"
            )

            self.best_shot = None

            return None

        best = None

        valid_shots = 0

        for shot in candidates:

            score = (
                self.evaluate_shot(
                    shot,
                    balls,
                    table,
                    allowed_numbers
                )
            )

            shot["evaluation"] = score

            if score == float("-inf"):

                continue

            valid_shots += 1

            if (
                best is None
                or score >
                best["evaluation"]
            ):

                best = shot

        print(
            "AI | valid:",
            valid_shots,
            "| best:",
            (
                f"ball {best['target'].number}"
                if best is not None
                else "NONE"
            )
        )

        if best is not None:

            print(
                "AI | type:",
                best["type"],
                "| power:",
                round(
                    best["power"],
                    2
                ),
                "| angle:",
                round(
                    math.degrees(
                        best["angle"]
                    ),
                    2
                ),
                "| cut:",
                round(
                    best["cut_angle"],
                    2
                ),
                "| score:",
                round(
                    best["evaluation"],
                    2
                )
            )

        self.best_shot = best

        return best