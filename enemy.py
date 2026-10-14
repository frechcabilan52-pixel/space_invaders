import pygame
import random
import math


class Enemy:
    def __init__(self, index, total_enemies, screen_width):
        self.width = 100
        self.height = 100

        self.image = pygame.image.load(
            "assets/images/1.png"
        ).convert_alpha()

        self.image = pygame.transform.scale(
            self.image, (self.width, self.height)
        )

        spacing = screen_width / (total_enemies + 1)

        self.target_mid_x = spacing * (index + 1) - (
            self.width // 2
        )
        self.target_mid_y = 150 + (
            50 if index % 2 == 0 else 0
        )

        self.x = self.target_mid_x
        self.y = -random.randint(100, 500)

        # Enemy movement
        self.state = "entering"
        self.speed = random.uniform(2.5, 4.5)
        self.dx = random.choice([-1, 1]) * self.speed
        self.dy = self.speed

        self.screen_width = screen_width
        self.screen_height = 600

        # Aggressive movement
        self.direction_timer = random.randint(25, 65)
        self.dodge_timer = random.randint(50, 100)
        self.dodge_speed = random.uniform(3.0, 5.0)

        # Shooting
        self.shoot_timer = random.randint(40, 100)
        self.bullet_speed = random.uniform(4.0, 6.0)
        self.bullets = []

        self.hp = 1
        self.alive = True

    def start_drop(self, target_x, target_y):
        self.state = "dropping"

        distance_x = target_x - self.x
        distance_y = target_y - self.y

        distance = math.hypot(distance_x, distance_y)

        if distance > 0:
            self.dx = (distance_x / distance) * self.speed
            self.dy = (distance_y / distance) * self.speed
        else:
            self.dx = 0
            self.dy = self.speed

    def shoot(self, player):
        """Tira og bala padulong sa kasamtangang posisyon sa player."""
        if player is None:
            return

        player_rect = (
            player.get_rect()
            if hasattr(player, "get_rect")
            else pygame.Rect(
                player.x, player.y,
                getattr(player, "width", 50),
                getattr(player, "height", 50)
            )
        )

        enemy_center_x = self.x + self.width / 2
        enemy_center_y = self.y + self.height / 2

        target_x = player_rect.centerx
        target_y = player_rect.centery

        dx = target_x - enemy_center_x
        dy = target_y - enemy_center_y

        distance = math.hypot(dx, dy)

        if distance == 0:
            return

        speed = self.bullet_speed

        self.bullets.append({
            "x": enemy_center_x - 5,
            "y": enemy_center_y,
            "dx": (dx / distance) * speed,
            "dy": (dy / distance) * speed,
            "speed": speed,
            "radius": 6
        })

    def update(self, player=None):
        # Enter the battlefield
        if self.state == "entering":
            if self.y < self.target_mid_y:
                self.y += self.speed
            else:
                self.y = self.target_mid_y
                self.state = "waiting"

        elif self.state == "waiting":
            # Move immediately: zigzag and change direction
            self.direction_timer -= 1

            if self.direction_timer <= 0:
                self.direction_timer = random.randint(20, 55)
                self.dx = random.uniform(-3.5, 3.5)
                self.dy = random.uniform(-1.2, 1.8)

            self.x += self.dx
            self.y += self.dy

            # Keep enemy inside the screen
            if self.x <= 0:
                self.x = 0
                self.dx = abs(self.dx)

            elif self.x + self.width >= self.screen_width:
                self.x = self.screen_width - self.width
                self.dx = -abs(self.dx)

            if self.y < 60:
                self.y = 60
                self.dy = abs(self.dy)

            elif self.y > 330:
                self.y = 330
                self.dy = -abs(self.dy)

            # Random dodge movement
            self.dodge_timer -= 1

            if self.dodge_timer <= 0:
                self.dodge_timer = random.randint(45, 100)
                self.dx = random.choice([-1, 1]) * self.dodge_speed

            # Shoot toward the player
            self.shoot_timer -= 1

            if self.shoot_timer <= 0:
                if player is not None:
                    self.shoot(player)

                self.shoot_timer = random.randint(45, 90)

        elif self.state == "dropping":
            self.x += self.dx
            self.y += self.dy

            if (
                self.y > self.screen_height + 50
                or self.x < -100
                or self.x > self.screen_width + 100
            ):
                self.state = "offscreen"

        # Update enemy bullets
        for bullet in self.bullets[:]:
            bullet["x"] += bullet["dx"]
            bullet["y"] += bullet["dy"]

            if (
                bullet["y"] < -20
                or bullet["y"] > self.screen_height + 20
                or bullet["x"] < -20
                or bullet["x"] > self.screen_width + 20
            ):
                self.bullets.remove(bullet)

    def draw(self, screen):
        if self.state != "offscreen":
            screen.blit(self.image, (int(self.x), int(self.y)))

        # Draw enemy bullets
        for bullet in self.bullets:
            bx = int(bullet["x"])
            by = int(bullet["y"])
            radius = bullet["radius"]

            pygame.draw.circle(
                screen, (255, 65, 65),
                (bx, by), radius
            )

            pygame.draw.circle(
                screen, (255, 190, 100),
                (bx, by), max(2, radius // 2)
            )

    def get_rect(self):
        return pygame.Rect(
            int(self.x), int(self.y),
            self.width, self.height
        )