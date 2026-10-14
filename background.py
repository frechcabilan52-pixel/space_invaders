import pygame
import random
import math


class SpaceBackground:
    """
    Premium animated space background for Cabilan Space Invaders.

    Features:
    - Deep space gradient
    - Animated nebula clouds
    - Hundreds of stars
    - Twinkling stars
    - Parallax stars
    - Shooting stars
    - Glowing planet
    - Planet ring
    - Floating particles
    - Animated energy waves
    """

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.time = 0

        self.random = random.Random(77)

        

        self.background = pygame.Surface(
            (self.width, self.height)
        )

        self.create_gradient()

        

        self.nebula = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA
        )

        self.create_nebula()

        # ---------------------------------------------------------
        # STARS
        # ---------------------------------------------------------

        self.stars = []

        for _ in range(220):

            self.stars.append({
                "x": self.random.uniform(0, self.width),
                "y": self.random.uniform(0, self.height),

                "speed": self.random.uniform(
                    8,
                    70
                ),

                "size": self.random.choice(
                    [1, 1, 1, 2, 2, 3]
                ),

                "brightness": self.random.uniform(
                    0.5,
                    1.0
                ),

                "twinkle": self.random.uniform(
                    1,
                    4
                ),

                "phase": self.random.uniform(
                    0,
                    math.pi * 2
                )
            })


       

        self.particles = []

        for _ in range(70):

            self.particles.append({
                "x": self.random.uniform(
                    0,
                    self.width
                ),

                "y": self.random.uniform(
                    0,
                    self.height
                ),

                "speed": self.random.uniform(
                    5,
                    25
                ),

                "size": self.random.uniform(
                    0.5,
                    2
                ),

                "phase": self.random.uniform(
                    0,
                    math.pi * 2
                )
            })

        # ---------------------------------------------------------
        # SHOOTING STARS
        # ---------------------------------------------------------

        self.shooting_stars = []

        self.shooting_timer = 2.0

        # ---------------------------------------------------------
        # PLANET
        # ---------------------------------------------------------

        self.planet_surface = self.create_planet(
            75
        )

        self.planet_x = int(
            self.width * 0.82
        )

        self.planet_y = int(
            self.height * 0.25
        )

        
        self.small_planet = self.create_small_planet(
            25
        )

        self.small_planet_x = int(
            self.width * 0.18
        )

        self.small_planet_y = int(
            self.height * 0.72
        )

    # =============================================================
    # GRADIENT
    # =============================================================

    def create_gradient(self):

        top_color = (
            3,
            5,
            25
        )

        middle_color = (
            12,
            8,
            50
        )

        bottom_color = (
            35,
            8,
            65
        )

        for y in range(self.height):

            t = y / max(
                1,
                self.height - 1
            )

            if t < 0.55:

                ratio = t / 0.55

                color = self.interpolate(
                    top_color,
                    middle_color,
                    ratio
                )

            else:

                ratio = (
                    t - 0.55
                ) / 0.45

                color = self.interpolate(
                    middle_color,
                    bottom_color,
                    ratio
                )

            pygame.draw.line(
                self.background,
                color,
                (0, y),
                (self.width, y)
            )

    # =============================================================
    # COLOR INTERPOLATION
    # =============================================================

    def interpolate(
        self,
        color1,
        color2,
        amount
    ):

        return tuple(
            int(
                color1[i]
                + (
                    color2[i]
                    - color1[i]
                )
                * amount
            )

            for i in range(3)
        )

    # =============================================================
    # NEBULA
    # =============================================================

    def create_nebula(self):

        colors = [
            (
                90,
                40,
                220
            ),

            (
                20,
                100,
                255
            ),

            (
                210,
                30,
                160
            ),

            (
                0,
                180,
                220
            )
        ]

        for _ in range(14):

            x = self.random.randint(
                -150,
                self.width + 150
            )

            y = self.random.randint(
                -150,
                self.height + 150
            )

            radius = self.random.randint(
                100,
                260
            )

            color = self.random.choice(
                colors
            )

            cloud = pygame.Surface(
                (
                    radius * 2,
                    radius * 2
                ),
                pygame.SRCALPHA
            )

            center = radius

            for r in range(
                radius,
                5,
                -8
            ):

                alpha = int(
                    1
                    + 18
                    * (
                        1
                        - r / radius
                    )
                )

                pygame.draw.circle(
                    cloud,
                    (
                        color[0],
                        color[1],
                        color[2],
                        alpha
                    ),
                    (
                        center,
                        center
                    ),
                    r
                )

            self.nebula.blit(
                cloud,
                (
                    x - radius,
                    y - radius
                )
            )

    # =============================================================
    # PLANET
    # =============================================================

    def create_planet(
        self,
        radius
    ):

        size = radius * 4

        surface = pygame.Surface(
            (
                size,
                size
            ),
            pygame.SRCALPHA
        )

        center = size // 2

        # ---------------------------------------------------------
        # GLOW
        # ---------------------------------------------------------

        for r in range(
            int(radius * 1.8),
            radius,
            -4
        ):

            distance = (
                r - radius
            ) / radius

            alpha = int(
                30
                * (
                    1
                    - distance
                )
            )

            pygame.draw.circle(
                surface,
                (
                    100,
                    80,
                    255,
                    alpha
                ),
                (
                    center,
                    center
                ),
                r
            )

        # ---------------------------------------------------------
        # RING BACK
        # ---------------------------------------------------------

        ring_rect = pygame.Rect(
            center - int(radius * 1.8),
            center - int(radius * 0.55),
            int(radius * 3.6),
            int(radius * 1.1)
        )

        pygame.draw.ellipse(
            surface,
            (
                120,
                180,
                255,
                150
            ),
            ring_rect,
            5
        )

        # ---------------------------------------------------------
        # PLANET BODY
        # ---------------------------------------------------------

        for r in range(
            radius,
            0,
            -1
        ):

            ratio = (
                radius - r
            ) / radius

            red = int(
                20
                + 100
                * ratio
            )

            green = int(
                40
                + 90
                * ratio
            )

            blue = int(
                120
                + 120
                * ratio
            )

            pygame.draw.circle(
                surface,
                (
                    red,
                    green,
                    blue
                ),
                (
                    center - int(
                        ratio * 20
                    ),
                    center - int(
                        ratio * 15
                    )
                ),
                r
            )

        # ---------------------------------------------------------
        # PLANET HIGHLIGHT
        # ---------------------------------------------------------

        pygame.draw.circle(
            surface,
            (
                180,
                220,
                255,
                70
            ),
            (
                center - radius // 3,
                center - radius // 3
            ),
            radius // 3
        )

        # ---------------------------------------------------------
        # RING FRONT
        # ---------------------------------------------------------

        pygame.draw.arc(
            surface,
            (
                180,
                220,
                255,
                180
            ),
            ring_rect,
            math.pi,
            math.pi * 2,
            5
        )

        return surface

    # =============================================================
    # SMALL PLANET
    # =============================================================

    def create_small_planet(
        self,
        radius
    ):

        size = radius * 4

        surface = pygame.Surface(
            (
                size,
                size
            ),
            pygame.SRCALPHA
        )

        center = size // 2

        for r in range(
            radius,
            0,
            -1
        ):

            ratio = (
                radius - r
            ) / radius

            color = (
                int(120 + 80 * ratio),
                int(40 + 70 * ratio),
                int(80 + 100 * ratio)
            )

            pygame.draw.circle(
                surface,
                color,
                (
                    center,
                    center
                ),
                r
            )

        return surface

    # =============================================================
    # UPDATE
    # =============================================================

    def update(
        self,
        dt
    ):

        self.time += dt

        # ---------------------------------------------------------
        # STARS
        # ---------------------------------------------------------

        for star in self.stars:

            star["y"] += (
                star["speed"]
                * dt
            )

            if star["y"] > self.height:

                star["y"] = -5

                star["x"] = self.random.uniform(
                    0,
                    self.width
                )

        # ---------------------------------------------------------
        # PARTICLES
        # ---------------------------------------------------------

        for particle in self.particles:

            particle["y"] += (
                particle["speed"]
                * dt
            )

            if particle["y"] > self.height:

                particle["y"] = -5

                particle["x"] = self.random.uniform(
                    0,
                    self.width
                )

        # ---------------------------------------------------------
        # SHOOTING STAR TIMER
        # ---------------------------------------------------------

        self.shooting_timer -= dt

        if self.shooting_timer <= 0:

            self.spawn_shooting_star()

            self.shooting_timer = self.random.uniform(
                2.0,
                5.0
            )

        # ---------------------------------------------------------
        # SHOOTING STARS
        # ---------------------------------------------------------

        for star in self.shooting_stars:

            star["x"] += (
                star["vx"]
                * dt
            )

            star["y"] += (
                star["vy"]
                * dt
            )

            star["life"] -= dt

        self.shooting_stars = [
            star
            for star in self.shooting_stars
            if star["life"] > 0
        ]

    # =============================================================
    # SHOOTING STAR
    # =============================================================

    def spawn_shooting_star(self):

        speed = self.random.uniform(
            500,
            850
        )

        self.shooting_stars.append(
            {
                "x": self.random.uniform(
                    self.width * 0.3,
                    self.width
                ),

                "y": self.random.uniform(
                    -50,
                    self.height * 0.25
                ),

                "vx": -speed,

                "vy": speed * 0.65,

                "life": 1.5
            }
        )

    # =============================================================
    # DRAW
    # =============================================================

    def draw(
        self,
        screen
    ):

        # ---------------------------------------------------------
        # BASE
        # ---------------------------------------------------------

        screen.blit(
            self.background,
            (0, 0)
        )

        # ---------------------------------------------------------
        # NEBULA
        # ---------------------------------------------------------

        screen.blit(
            self.nebula,
            (0, 0)
        )

        # ---------------------------------------------------------
        # ANIMATED SPACE GLOW
        # ---------------------------------------------------------

        glow = pygame.Surface(
            (
                self.width,
                self.height
            ),
            pygame.SRCALPHA
        )

        glow_alpha = int(
            18
            + 8
            * math.sin(
                self.time * 0.7
            )
        )

        pygame.draw.circle(
            glow,
            (
                40,
                80,
                255,
                glow_alpha
            ),
            (
                int(self.width * 0.5),
                int(self.height * 0.35)
            ),
            int(
                self.width * 0.45
            )
        )

        screen.blit(
            glow,
            (0, 0)
        )

        # ---------------------------------------------------------
        # STARS
        # ---------------------------------------------------------

        for star in self.stars:

            twinkle = (
                0.65
                + 0.35
                * math.sin(
                    self.time
                    * star["twinkle"]
                    + star["phase"]
                )
            )

            brightness = (
                star["brightness"]
                * twinkle
            )

            color = (
                int(
                    180
                    * brightness
                ),

                int(
                    210
                    * brightness
                ),

                int(
                    255
                    * brightness
                )
            )

            x = int(
                star["x"]
            )

            y = int(
                star["y"]
            )

            size = star["size"]

            pygame.draw.circle(
                screen,
                color,
                (
                    x,
                    y
                ),
                size
            )

            # Glow for bigger stars
            if size >= 2:

                pygame.draw.line(
                    screen,
                    (
                        int(color[0] * 0.4),
                        int(color[1] * 0.4),
                        int(color[2] * 0.4)
                    ),
                    (
                        x - 5,
                        y
                    ),
                    (
                        x + 5,
                        y
                    ),
                    1
                )

                pygame.draw.line(
                    screen,
                    (
                        int(color[0] * 0.4),
                        int(color[1] * 0.4),
                        int(color[2] * 0.4)
                    ),
                    (
                        x,
                        y - 5
                    ),
                    (
                        x,
                        y + 5
                    ),
                    1
                )

        # ---------------------------------------------------------
        # FLOATING PARTICLES
        # ---------------------------------------------------------

        for particle in self.particles:

            pulse = (
                0.5
                + 0.5
                * math.sin(
                    self.time * 2
                    + particle["phase"]
                )
            )

            alpha = int(
                80
                + 100 * pulse
            )

            particle_surface = pygame.Surface(
                (
                    5,
                    5
                ),
                pygame.SRCALPHA
            )

            pygame.draw.circle(
                particle_surface,
                (
                    80,
                    200,
                    255,
                    alpha
                ),
                (
                    2,
                    2
                ),
                int(
                    particle["size"]
                ) + 1
            )

            screen.blit(
                particle_surface,
                (
                    int(particle["x"]),
                    int(particle["y"])
                )
            )

        # ---------------------------------------------------------
        # BIG PLANET
        # ---------------------------------------------------------

        planet_y = (
            self.planet_y
            + math.sin(
                self.time * 0.5
            ) * 8
        )

        planet_rect = (
            self.planet_surface.get_rect(
                center=(
                    self.planet_x,
                    int(planet_y)
                )
            )
        )

        screen.blit(
            self.planet_surface,
            planet_rect
        )

        # ---------------------------------------------------------
        # SMALL PLANET
        # ---------------------------------------------------------

        small_y = (
            self.small_planet_y
            + math.sin(
                self.time * 0.8
            ) * 5
        )

        small_rect = (
            self.small_planet.get_rect(
                center=(
                    self.small_planet_x,
                    int(small_y)
                )
            )
        )

        screen.blit(
            self.small_planet,
            small_rect
        )

        # ---------------------------------------------------------
        # SHOOTING STARS
        # ---------------------------------------------------------

        for meteor in self.shooting_stars:

            length = math.hypot(
                meteor["vx"],
                meteor["vy"]
            )

            if length == 0:
                continue

            dx = (
                meteor["vx"]
                / length
            )

            dy = (
                meteor["vy"]
                / length
            )

            for i in range(18):

                fade = (
                    1
                    - i / 18
                )

                alpha = int(
                    255
                    * fade
                )

                start_x = (
                    meteor["x"]
                    - dx
                    * i
                    * 7
                )

                start_y = (
                    meteor["y"]
                    - dy
                    * i
                    * 7
                )

                end_x = (
                    meteor["x"]
                    - dx
                    * (i + 1)
                    * 7
                )

                end_y = (
                    meteor["y"]
                    - dy
                    * (i + 1)
                    * 7
                )

                line_surface = pygame.Surface(
                    (
                        self.width,
                        self.height
                    ),
                    pygame.SRCALPHA
                )

                pygame.draw.line(
                    line_surface,
                    (
                        150,
                        220,
                        255,
                        alpha
                    ),
                    (
                        int(start_x),
                        int(start_y)
                    ),
                    (
                        int(end_x),
                        int(end_y)
                    ),
                    3 if i < 5 else 1
                )

                screen.blit(
                    line_surface,
                    (0, 0)
                )