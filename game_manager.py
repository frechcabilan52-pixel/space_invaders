import math
from array import array
import pygame
import random
import os

from entities.player import Player
from entities.buttons import MobileButtons
from entities.enemy import Enemy
from entities.bullet import Bullet
from db_connection import db
from managers.account_manager import AccountManager
from settings_manager import settings


BG_COLOR = (6, 10, 20)
TEXT_COLOR = (220, 240, 250)
MUTED_COLOR = (120, 160, 185)
ACCENT_COLOR = (80, 220, 235)
ERROR_COLOR = (255, 120, 130)
SUCCESS_COLOR = (100, 255, 150)
BUTTON_COLOR = (20, 55, 75)
BORDER_COLOR = (60, 150, 190)

POWERUP_COLORS = {
    "life": (255, 120, 130),
    "rapid": (255, 220, 80),
    "shield": (90, 170, 255)
}

RAPID_DURATION = 600     # frames (10 seconds @ 60 FPS)
SHIELD_DURATION = 600
POWERUP_DROP_CHANCE = 0.18


class GameManager:

    def __init__(self, screen, screen_width, screen_height):

        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.font = pygame.font.SysFont("Arial", 36)
        self.small_font = pygame.font.SysFont("Arial", 22)
        self.big_font = pygame.font.SysFont("Arial", 64)

        # ==================================================
        # ACCOUNT MANAGER
        # ==================================================

        self.account_manager = AccountManager(
            screen,
            screen_width,
            screen_height,
            self.font,
            self.big_font
        )

        self.username = ""

        # ==================================================
        # GAME STATE
        # ==================================================

        self.game_state = "account"

        # ==================================================
        # GAME OVER BUTTONS
        # ==================================================

        self.reload_button_rect = pygame.Rect(
            screen_width // 2 - 100,
            screen_height // 2 + 50,
            200,
            50
        )

        self.leaderboard_button_rect = pygame.Rect(
            screen_width // 2 - 140,
            screen_height // 2 + 110,
            280,
            60
        )

        self.game_over_settings_button_rect = pygame.Rect(
            screen_width // 2 - 100,
            screen_height // 2 + 180,
            200,
            45
        )

        self.game_over_back_button_rect = pygame.Rect(
            screen_width // 2 - 100,
            screen_height // 2 + 235,
            200,
            45
        )

        # ==================================================
        # LEADERBOARD BUTTONS
        # ==================================================

        self.back_button_rect = pygame.Rect(
            screen_width // 2 - 210,
            screen_height - 80,
            190,
            50
        )

        self.settings_button_rect = pygame.Rect(
            screen_width // 2 + 20,
            screen_height - 80,
            190,
            50
        )

        # ==================================================
        # SETTINGS BACK
        # ==================================================

        self.settings_back_button_rect = pygame.Rect(
            screen_width // 2 - 100,
            screen_height - 50,
            200,
            45
        )

        # GAMEPLAY SETTINGS BUTTONS
        self.difficulty_minus_rect = pygame.Rect(
            screen_width // 2 - 125, 165, 55, 38
        )
        self.difficulty_plus_rect = pygame.Rect(
            screen_width // 2 + 70, 165, 55, 38
        )
        self.player_speed_minus_rect = pygame.Rect(
            screen_width // 2 - 125, 265, 55, 38
        )
        self.player_speed_plus_rect = pygame.Rect(
            screen_width // 2 + 70, 265, 55, 38
        )
        self.enemy_difficulty_minus_rect = pygame.Rect(
            screen_width // 2 - 125, 365, 55, 38
        )
        self.enemy_difficulty_plus_rect = pygame.Rect(
            screen_width // 2 + 70, 365, 55, 38
        )
        self.gameplay_music_minus_rect = pygame.Rect(
            screen_width // 2 - 125, 435, 55, 38
        )
        self.gameplay_music_plus_rect = pygame.Rect(
            screen_width // 2 + 70, 435, 55, 38
        )

        # Keep the original ON/OFF mobile-controls switch in gameplay settings.
        self.gameplay_mobile_controls_rect = pygame.Rect(
            screen_width // 2 - 70, 510, 140, 38
        )

        # ==================================================
        # VOLUME BUTTONS
        # ==================================================

        self.volume_minus_button_rect = pygame.Rect(
            screen_width // 2 - 130,
            270,
            70,
            55
        )

        self.volume_plus_button_rect = pygame.Rect(
            screen_width // 2 + 60,
            270,
            70,
            55
        )

        self.mobile_controls_button_rect = pygame.Rect(
            screen_width // 2 + 55,
            345,
            140,
            45
        )

        self.left_button_toggle_rect = pygame.Rect(
            screen_width // 2 + 55,
            355,
            140,
            45
        )

        self.right_button_toggle_rect = pygame.Rect(
            screen_width // 2 + 55,
            415,
            140,
            45
        )

        self.fire_button_toggle_rect = pygame.Rect(
            screen_width // 2 + 55,
            475,
            140,
            45
        )

        # ==================================================
        # MUSIC
        # ==================================================

        self.music_volume = settings.get("music_volume", 0.50)
        self.settings_return_state = "leaderboard"

        self.music_playing = False
        self.game_over_music_playing = False

        try:

            if not pygame.mixer.get_init():
                pygame.mixer.init()

            manager_folder = os.path.dirname(
                os.path.abspath(__file__)
            )

            self.space_music_path = os.path.join(
                manager_folder,
                "space_music.mp3"
            )

            self.game_over_music_path = os.path.join(
                manager_folder,
                "game_over_music.mp3"
            )

            print("[Music] Space music path:", self.space_music_path)
            print("[Music] Game over music path:", self.game_over_music_path)

        except pygame.error as e:

            print("[Music] Mixer error:", e)

            self.space_music_path = ""
            self.game_over_music_path = ""

        # ==================================================
        # SOUND EFFECTS (generated by code - no files needed)
        # ==================================================

        self.sounds = {}
        self._init_sounds()

        # ==================================================
        # PLAYER NAME SETTINGS
        # ==================================================

        self.name_input = ""
        self.name_message = ""

        self.name_input_rect = pygame.Rect(
            screen_width // 2 - 170,
            420,
            340,
            50
        )

        self.save_name_button_rect = pygame.Rect(
            screen_width // 2 - 120,
            480,
            240,
            45
        )

        self.score_saved = False

        # ==================================================
        # PAUSE MENU
        # ==================================================

        self.pause_button_rect = pygame.Rect(
            screen_width - 64,
            70,
            44,
            44
        )

        self.pause_anim = 0.0
        self.pause_blur = None

        # ==================================================
        # STARS
        # ==================================================

        self.stars = []

        for i in range(120):

            self.stars.append([
                random.randint(0, self.screen_width - 1),
                random.randint(0, self.screen_height - 1),
                random.randint(1, 3)
            ])

        self.reset_game()

        self.game_state = "account"

    # ======================================================
    # SOUND EFFECTS
    # ======================================================

    def _make_sound(self, f0, f1, duration, volume=0.4,
                    noise=0.0, wave="square"):

        init = pygame.mixer.get_init()

        if not init:
            return None

        freq, fmt, channels = init

        if fmt != -16:
            return None

        total = int(freq * duration)
        buf = array("h")
        phase = 0.0

        for i in range(total):

            t = i / total
            f = f0 + (f1 - f0) * t
            phase += 2 * math.pi * f / freq

            if wave == "square":
                s = 1.0 if math.sin(phase) >= 0 else -1.0
            elif wave == "saw":
                s = ((phase / (2 * math.pi)) % 1.0) * 2 - 1
            else:
                s = math.sin(phase)

            if noise > 0:
                s = s * (1 - noise) + random.uniform(-1, 1) * noise

            env = (1 - t) ** 2

            value = int(32767 * volume * env * s)

            for _ in range(channels):
                buf.append(value)

        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _init_sounds(self):

        try:

            specs = {
                "shoot": (950, 280, 0.13, 0.22, 0.0, "square"),
                "explosion": (220, 35, 0.45, 0.55, 0.85, "saw"),
                "boss_hit": (260, 120, 0.10, 0.30, 0.3, "square"),
                "hit": (170, 50, 0.55, 0.65, 0.7, "saw"),
                "click": (650, 900, 0.07, 0.30, 0.0, "sine"),
                "powerup": (400, 1300, 0.28, 0.30, 0.0, "square"),
                "boss_shoot": (520, 140, 0.20, 0.32, 0.25, "saw")
            }

            for name, args in specs.items():

                sound = self._make_sound(*args)

                if sound:
                    self.sounds[name] = sound

        except Exception as e:

            print("[SFX] Sound generation error:", e)

    def play_sound(self, name):

        sound = self.sounds.get(name)

        if sound:

            try:
                sound.play()
            except pygame.error:
                pass

    def _play_click_if_needed(self, events):

        if self.game_state == "pause":
            rects = list(self._pause_layout()[4].values())

        elif self.game_state == "game_over":
            rects = [
                self.reload_button_rect,
                self.leaderboard_button_rect,
                self.game_over_settings_button_rect,
                self.game_over_back_button_rect
            ]

        elif self.game_state == "leaderboard":
            rects = [self.back_button_rect, self.settings_button_rect]

        elif self.game_state == "settings":
            rects = [
                self.volume_minus_button_rect,
                self.volume_plus_button_rect,
                self.settings_back_button_rect
            ]

            if self.settings_return_state in ("game_over", "pause"):
                rects += [
                    self.difficulty_minus_rect,
                    self.difficulty_plus_rect,
                    self.player_speed_minus_rect,
                    self.player_speed_plus_rect,
                    self.enemy_difficulty_minus_rect,
                    self.enemy_difficulty_plus_rect,
                    self.gameplay_music_minus_rect,
                    self.gameplay_music_plus_rect
                ]
            else:
                rects += [
                    self.mobile_controls_button_rect,
                    self.save_name_button_rect
                ]

        elif self.game_state == "playing":
            rects = [self.pause_button_rect]

        else:
            return

        for event in events:

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and any(r.collidepoint(event.pos) for r in rects)
            ):
                self.play_sound("click")
                break

    # ======================================================
    # EFFECTS: PARTICLES / SHAKE / POWER-UPS
    # ======================================================

    def explode(self, x, y, palette, count=30, speed=6):

        for _ in range(count):

            angle = random.uniform(0, 6.2832)
            sp = random.uniform(speed * 0.3, speed)
            life = random.randint(25, 50)

            self.particles.append([
                x,
                y,
                math.cos(angle) * sp,
                math.sin(angle) * sp,
                life,
                life,
                random.choice(palette),
                random.randint(2, 5)
            ])

        # shockwave ring: x, y, age, max_age, max_radius, color
        self.rings.append([x, y, 0, 22, 30 + count, palette[0]])

    def add_shake(self, intensity, duration):

        if intensity >= self.shake_intensity or self.shake_timer <= 0:
            self.shake_intensity = intensity

        self.shake_duration = max(duration, 1)
        self.shake_timer = max(self.shake_timer, duration)

    def update_effects(self):

        for p in self.particles:

            p[0] += p[2]
            p[1] += p[3]
            p[2] *= 0.96
            p[3] *= 0.96
            p[4] -= 1

        self.particles = [p for p in self.particles if p[4] > 0]

        for r in self.rings:
            r[2] += 1

        self.rings = [r for r in self.rings if r[2] < r[3]]

        if self.boss_banner_timer > 0:
            self.boss_banner_timer -= 1

    def draw_effects(self):

        for r in self.rings:

            ratio = r[2] / r[3]
            radius = int(r[4] * (1 - (1 - ratio) ** 3))
            fade = 1 - ratio

            color = tuple(int(c * fade) for c in r[5])

            if radius > 1:
                pygame.draw.circle(
                    self.screen,
                    color,
                    (int(r[0]), int(r[1])),
                    radius,
                    max(1, int(4 * fade))
                )

        for p in self.particles:

            ratio = p[4] / p[5]
            color = tuple(int(c * ratio) for c in p[6])
            radius = max(1, int(p[7] * ratio + 0.5))

            pygame.draw.circle(
                self.screen,
                color,
                (int(p[0]), int(p[1])),
                radius
            )

    def apply_screen_shake(self):

        if self.shake_timer <= 0:
            return

        mag = int(
            self.shake_intensity
            * (self.shake_timer / self.shake_duration)
        )

        ox = random.randint(-mag, mag)
        oy = random.randint(-mag, mag)

        snap = self.screen.copy()
        self.screen.fill(BG_COLOR)
        self.screen.blit(snap, (ox, oy))

        self.shake_timer -= 1

    # ---------------- POWER-UPS ----------------

    def spawn_powerup(self, x, y, guaranteed_kind=None):

        if guaranteed_kind:
            kind = guaranteed_kind
        else:
            choices = ["rapid", "shield"]

            if self.lives < 3:
                choices.append("life")

            kind = random.choice(choices)

        self.powerups.append({
            "x": float(x),
            "y": float(y),
            "type": kind
        })

    def update_powerups(self):

        player_rect = self.player.get_rect()

        for p in self.powerups[:]:

            p["y"] += 3

            rect = pygame.Rect(
                int(p["x"]) - 17,
                int(p["y"]) - 17,
                34,
                34
            )

            if rect.colliderect(player_rect):

                self.collect_powerup(p["type"])
                self.powerups.remove(p)

            elif p["y"] > self.screen_height + 30:

                self.powerups.remove(p)

    def collect_powerup(self, kind):

        self.play_sound("powerup")

        px, py = self.player.get_rect().center

        self.explode(
            px,
            py,
            [POWERUP_COLORS[kind], (255, 255, 255)],
            count=18,
            speed=4
        )

        if kind == "life":
            self.lives = min(3, self.lives + 1)

        elif kind == "rapid":
            self.rapid_timer = RAPID_DURATION

        elif kind == "shield":
            self.shield_timer = SHIELD_DURATION

    def draw_powerup(self, p):

        kind = p["type"]
        x = int(p["x"])
        y = int(p["y"])
        color = POWERUP_COLORS[kind]

        pulse = (math.sin(pygame.time.get_ticks() / 150) + 1) / 2

        glow = pygame.Surface((70, 70), pygame.SRCALPHA)

        pygame.draw.circle(
            glow,
            (*color, int(45 + 60 * pulse)),
            (35, 35),
            int(23 + 5 * pulse)
        )

        self.screen.blit(glow, (x - 35, y - 35))

        pygame.draw.circle(self.screen, (10, 25, 40), (x, y), 17)
        pygame.draw.circle(self.screen, color, (x, y), 17, 3)

        if kind == "life":

            self.draw_heart(x - 9, y - 8, 18, color)

        elif kind == "rapid":

            pygame.draw.polygon(
                self.screen,
                color,
                [
                    (x + 3, y - 11),
                    (x - 7, y + 2),
                    (x - 1, y + 2),
                    (x - 4, y + 11),
                    (x + 7, y - 3),
                    (x + 1, y - 3)
                ]
            )

        else:

            pygame.draw.polygon(
                self.screen,
                color,
                [
                    (x - 8, y - 9),
                    (x + 8, y - 9),
                    (x + 8, y + 1),
                    (x, y + 10),
                    (x - 8, y + 1)
                ]
            )

    def draw_player_shield(self):

        if self.shield_timer <= 0:
            return

        rect = self.player.get_rect()
        radius = max(rect.width, rect.height) // 2 + 14

        pulse = (math.sin(pygame.time.get_ticks() / 120) + 1) / 2

        # blink when about to expire
        if self.shield_timer < 120 and (self.shield_timer // 6) % 2 == 0:
            return

        surf = pygame.Surface(
            (radius * 2 + 8, radius * 2 + 8),
            pygame.SRCALPHA
        )

        center = (radius + 4, radius + 4)

        pygame.draw.circle(
            surf,
            (90, 170, 255, int(40 + 30 * pulse)),
            center,
            radius
        )

        pygame.draw.circle(
            surf,
            (150, 210, 255, 220),
            center,
            radius,
            3
        )

        self.screen.blit(
            surf,
            (rect.centerx - radius - 4, rect.centery - radius - 4)
        )

    def draw_effect_bars(self):

        y = 62

        for label, timer, maximum, color in (
            ("SHIELD", self.shield_timer, SHIELD_DURATION,
             POWERUP_COLORS["shield"]),
            ("RAPID", self.rapid_timer, RAPID_DURATION,
             POWERUP_COLORS["rapid"])
        ):

            if timer <= 0:
                continue

            text = self.small_font.render(label, True, color)
            self.screen.blit(text, (20, y))

            bar_x = 20 + 78
            bar_w = 110

            pygame.draw.rect(
                self.screen,
                (25, 35, 50),
                (bar_x, y + 5, bar_w, 12),
                border_radius=6
            )

            pygame.draw.rect(
                self.screen,
                color,
                (bar_x, y + 5, int(bar_w * timer / maximum), 12),
                border_radius=6
            )

            y += 28

    # ---------------- COMBAT HELPERS ----------------

    def try_fire(self, rapid):

        if rapid:

            if self.fire_cooldown > 0:
                return

            self.fire_cooldown = 8

        elif self.bullets:

            return

        self.bullets.append(
            Bullet(
                self.player.x + self.player.width // 2 - 16,
                self.player.y
            )
        )

        self.play_sound("shoot")

    # ---------------- BIG BOSS ATTACKS ----------------

    def update_boss_attack(self, boss):

        if boss.flash_timer > 0:
            boss.flash_timer -= 1

        if boss.state != "boss_fighting" or boss.hp <= 0:
            return

        # ---------- PHASE CHANGE ----------
        ratio = boss.hp / self.boss_max_hp

        if ratio > 0.6:
            phase = 1
        elif ratio > 0.3:
            phase = 2
        else:
            phase = 3

        if phase != self.boss_phase:

            self.boss_phase = phase

            cx, cy = boss.get_rect().center

            self.explode(
                cx, cy,
                [(255, 80, 80), (255, 200, 80), (255, 255, 255)],
                count=45,
                speed=8
            )

            self.play_sound("explosion")
            self.add_shake(10, 22)

            self.boss_banner_text = (
                "BOSS POWERING UP!" if phase == 2 else "BOSS ENRAGED!"
            )
            self.boss_banner_timer = 100

            boss.boss_speed = boss.base_speed + (phase - 1)

            boss.charge_timer = 0
            boss.shoot_timer = 45

        # ---------- CHARGING -> FIRE ----------
        if boss.charge_timer > 0:

            boss.charge_timer -= 1

            if boss.charge_timer == 0:

                self.fire_boss_pattern(boss)

                cooldown = {1: 95, 2: 75, 3: 55}[self.boss_phase]

                boss.shoot_timer = int(cooldown / self.boss_difficulty)

            return

        boss.shoot_timer -= 1

        if boss.shoot_timer <= 0:

            boss.charge_timer = 24

    def _add_enemy_bullet(self, x, y, angle, speed, radius, color):

        self.enemy_bullets.append({
            "x": float(x),
            "y": float(y),
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "r": radius,
            "color": color
        })

    def fire_boss_pattern(self, boss):

        rect = boss.get_rect()

        cx = rect.centerx
        cy = rect.bottom - 40

        px, py = self.player.get_rect().center

        aim = math.atan2(py - cy, px - cx)

        phase = self.boss_phase

        speed = (4.5 + phase * 0.7) * (1.0 if self.level == 5 else 1.2)

        color = {
            1: (255, 150, 60),
            2: (255, 90, 120),
            3: (255, 60, 60)
        }[phase]

        def fan(center_angle, count, spread, spd=speed, radius=9):

            for i in range(count):

                angle = center_angle + (i - (count - 1) / 2) * spread

                self._add_enemy_bullet(
                    cx, cy, angle, spd, radius, color
                )

        alt = boss.attack_count % 2

        if phase == 1:

            if alt == 0:
                fan(aim, 1, 0, speed * 1.15, 11)
            else:
                fan(aim, 3, 0.20)

        elif phase == 2:

            if alt == 0:
                fan(math.pi / 2, 5, 0.38)
            else:
                fan(aim, 3, 0.16, speed * 1.1)

        else:

            if alt == 0:

                offset = (boss.attack_count // 2) * 0.26

                for i in range(12):

                    angle = offset + i * (6.2832 / 12)

                    self._add_enemy_bullet(
                        cx, cy, angle, speed * 0.85, 9, color
                    )

            else:

                fan(aim, 5, 0.14, speed * 1.2)

        boss.attack_count += 1

        self.play_sound("boss_shoot")

        self.explode(
            cx, cy,
            [color, (255, 255, 255)],
            count=10,
            speed=4
        )

    def damage_player(self, hit_x, hit_y):

        px, py = self.player.get_rect().center

        # SHIELD ABSORBS
        if self.shield_timer > 0:

            self.shield_timer = 0
            self.invuln_timer = 60

            self.explode(
                px, py,
                [(90, 170, 255), (200, 230, 255)],
                count=30,
                speed=6
            )

            self.play_sound("boss_hit")

            self.add_shake(5, 10)

            return

        # LOSE ONE LIFE
        self.lives -= 1

        self.enemy_bullets = []

        self.game_state = "blinking"

        self.player.is_blinking = True

        self.state_timer = 0

        self.invuln_timer = 60

        self.explode(
            px, py,
            [(255, 120, 130), (255, 255, 255), (80, 220, 235)],
            count=45,
            speed=7
        )

        self.explode(
            hit_x, hit_y,
            [(255, 200, 80), (255, 120, 60)],
            count=14,
            speed=5
        )

        self.play_sound("hit")

        self.add_shake(14, 28)

    def update_enemy_bullets(self):

        if not self.enemy_bullets:
            return

        player_rect = self.player.get_rect().inflate(-10, -10)

        W, H = self.screen_width, self.screen_height

        for b in self.enemy_bullets[:]:

            b["x"] += b["vx"]
            b["y"] += b["vy"]

            if (
                b["x"] < -30 or b["x"] > W + 30
                or b["y"] < -30 or b["y"] > H + 30
            ):

                self.enemy_bullets.remove(b)
                continue

            r = max(2, b["r"] - 2)

            rect = pygame.Rect(
                int(b["x"]) - r,
                int(b["y"]) - r,
                r * 2,
                r * 2
            )

            if rect.colliderect(player_rect):

                self.enemy_bullets.remove(b)

                if self.invuln_timer > 0:
                    continue

                self.damage_player(b["x"], b["y"])

                return

    def _glow_surface(self, color, radius):

        cache = self.__dict__.setdefault("_glow_cache", {})

        key = (color, radius)

        surf = cache.get(key)

        if surf is None:

            size = radius * 5
            surf = pygame.Surface((size, size), pygame.SRCALPHA)

            for i in range(4, 0, -1):

                pygame.draw.circle(
                    surf,
                    (*color, 28 + (4 - i) * 22),
                    (size // 2, size // 2),
                    int(radius * (1 + i * 0.45))
                )

            cache[key] = surf

        return surf

    def draw_enemy_bullets(self):

        for b in self.enemy_bullets:

            x = int(b["x"])
            y = int(b["y"])
            r = b["r"]

            glow = self._glow_surface(b["color"], r)

            self.screen.blit(
                glow,
                (x - glow.get_width() // 2, y - glow.get_height() // 2)
            )

            pygame.draw.circle(self.screen, b["color"], (x, y), r)
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), max(2, r // 2))

    def draw_boss_aura(self, boss):

        phase = self.boss_phase

        color = {
            1: (255, 120, 90),
            2: (255, 90, 140),
            3: (255, 50, 50)
        }[phase]

        speed = {1: 260, 2: 190, 3: 120}[phase]

        pulse = (math.sin(pygame.time.get_ticks() / speed) + 1) / 2

        radius = int(boss.width * 0.62 + 8 * pulse)

        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

        for i in range(4, 0, -1):

            pygame.draw.circle(
                surf,
                (*color, int((18 + 20 * pulse) * (5 - i) / 2)),
                (radius, radius),
                int(radius * i / 4)
            )

        center = boss.get_rect().center

        self.screen.blit(surf, (center[0] - radius, center[1] - radius))

    def draw_boss_overlay(self, boss):

        # HIT FLASH
        if boss.flash_timer > 0:

            flash = boss.image.copy()
            flash.fill((130, 130, 130, 0), special_flags=pygame.BLEND_RGB_ADD)

            self.screen.blit(flash, (boss.x, boss.y))

        # CHARGING WARNING
        if boss.charge_timer > 0:

            rect = boss.get_rect()

            cx = rect.centerx
            cy = rect.bottom - 40

            t = boss.charge_timer / 24

            pygame.draw.circle(
                self.screen,
                (255, 80, 80),
                (cx, cy),
                int(12 + 46 * t),
                3
            )

            pygame.draw.circle(
                self.screen,
                (255, 230, 200),
                (cx, cy),
                int(4 + 14 * (1 - t))
            )

    def draw_boss_banner(self):

        if self.boss_banner_timer <= 0 or not self.boss_banner_text:
            return

        fade = min(1.0, self.boss_banner_timer / 25)

        text = self.font.render(self.boss_banner_text, True, ERROR_COLOR)

        text.set_alpha(int(255 * fade))

        self.screen.blit(
            text,
            (
                self.screen_width // 2 - text.get_width() // 2,
                self.screen_height // 2 - 120
            )
        )

    def damage_enemy(self, enemy, hit_pos):

        # BIG BOSS
        if getattr(enemy, "is_boss", False):

            enemy.hp -= 1

            self.boss_hp = enemy.hp

            enemy.flash_timer = 6

            print(f"[BOSS] HP: {enemy.hp}/{self.boss_max_hp}")

            self.explode(
                hit_pos[0],
                hit_pos[1],
                [(255, 220, 120), (255, 150, 80)],
                count=8,
                speed=4
            )

            self.play_sound("boss_hit")

            if enemy.hp <= 0:

                cx, cy = enemy.get_rect().center

                enemy.state = "offscreen"

                self.score += 25

                self.boss_active = False

                self.boss_hp = 0

                # clear all boss bullets with little pops
                for eb in self.enemy_bullets:
                    self.explode(
                        eb["x"], eb["y"],
                        [eb["color"], (255, 255, 255)],
                        count=4,
                        speed=3
                    )

                self.enemy_bullets = []

                self.explode(
                    cx, cy,
                    [(255, 120, 130), (255, 220, 120), (255, 255, 255)],
                    count=90,
                    speed=9
                )

                self.explode(
                    cx, cy,
                    [(255, 160, 60), (255, 80, 60)],
                    count=50,
                    speed=6
                )

                self.play_sound("explosion")

                self.add_shake(14, 40)

                # boss always drops a reward
                self.spawn_powerup(
                    cx,
                    cy,
                    "life" if self.lives < 3 else "shield"
                )

                print("[BOSS] BIG BOSS DEFEATED!")

        # NORMAL ENEMY
        else:

            enemy.hp -= 1

            if enemy.hp <= 0:

                cx, cy = enemy.get_rect().center

                enemy.state = "offscreen"

                self.score += 1

                self.explode(
                    cx, cy,
                    [(255, 200, 80), (255, 120, 60), (255, 240, 200)],
                    count=26,
                    speed=5
                )

                self.play_sound("explosion")

                self.add_shake(3, 8)

                if random.random() < POWERUP_DROP_CHANCE:
                    self.spawn_powerup(cx, cy)

    # ======================================================
    # START SPACE MUSIC
    # ======================================================

    def start_space_music(self):

        try:

            if not self.space_music_path:
                return

            if not os.path.exists(self.space_music_path):

                print("[Music] ERROR: space_music.mp3 not found:")
                print(self.space_music_path)

                return

            if not pygame.mixer.get_init():
                pygame.mixer.init()

            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.space_music_path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops=-1)

            self.music_playing = True
            self.game_over_music_playing = False

            print("[Music] Space music started.")

        except pygame.error as e:

            print("[Music] Space music error:", e)

    # ======================================================
    # START GAME OVER MUSIC
    # ======================================================

    def start_game_over_music(self):

        try:

            if not self.game_over_music_path:
                return

            if not os.path.exists(self.game_over_music_path):

                print("[Music] ERROR: game_over_music.mp3 not found:")
                print(self.game_over_music_path)

                return

            if not pygame.mixer.get_init():
                pygame.mixer.init()

            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.game_over_music_path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops=0)

            self.music_playing = False
            self.game_over_music_playing = True

            print("[Music] Game over music started.")

        except pygame.error as e:

            print("[Music] Game over music error:", e)

    # ======================================================
    # STOP MUSIC
    # ======================================================

    def stop_music(self):

        try:

            if pygame.mixer.get_init():
                pygame.mixer.music.stop()

            self.music_playing = False
            self.game_over_music_playing = False

        except pygame.error:
            pass

    # ======================================================
    # BACKGROUND
    # ======================================================

    def draw_background(self):

        for y in range(self.screen_height):

            ratio = y / self.screen_height

            r = int(2 + 5 * ratio)
            g = int(5 + 12 * ratio)
            b = int(18 + 38 * ratio)

            pygame.draw.line(
                self.screen,
                (r, g, b),
                (0, y),
                (self.screen_width, y)
            )

        for star in self.stars:

            star[1] += star[2]

            if star[1] > self.screen_height:

                star[0] = random.randint(0, self.screen_width - 1)
                star[1] = 0
                star[2] = random.randint(1, 3)

            brightness = 100 + (star[2] * 50)

            pygame.draw.circle(
                self.screen,
                (
                    brightness // 2,
                    brightness,
                    min(255, brightness + 30)
                ),
                (int(star[0]), int(star[1])),
                star[2]
            )

        current_time = pygame.time.get_ticks()

        for i in range(20):

            x = (i * 173) % self.screen_width

            y = (
                (i * 91) + current_time // 6
            ) % self.screen_height

            pygame.draw.circle(
                self.screen,
                (25, 80, 130),
                (x, y),
                2
            )

    # ======================================================
    # RESET GAME
    # ======================================================

    def reset_game(self):

        self.player = Player(
            self.screen_width,
            self.screen_height
        )
        self.player.speed = int(settings.get("player_speed", 10))

        self.buttons = MobileButtons()

        self.bullets = []
        self.enemies = []

        self.score = 0

        # EFFECTS
        self.particles = []
        self.rings = []
        self.powerups = []

        # BOSS ATTACK SYSTEM
        self.enemy_bullets = []
        self.boss_phase = 1
        self.boss_difficulty = 1.0
        self.boss_banner_text = ""
        self.boss_banner_timer = 0

        self.rapid_timer = 0
        self.shield_timer = 0
        self.invuln_timer = 0
        self.fire_cooldown = 0

        self.shake_timer = 0
        self.shake_duration = 1
        self.shake_intensity = 0

        # LIVES depend on the selected gameplay difficulty.
        lives_by_difficulty = {"easy": 5, "normal": 3, "hard": 2}
        selected_difficulty = settings.get("difficulty", "normal")
        self.lives = lives_by_difficulty.get(selected_difficulty, 3)

        self.level = 1
        self.wave = 1

        self.spawn_number = 3

        self.boss_active = False
        self.boss_hp = 0
        self.boss_max_hp = 0

        self.score_saved = False

        self.player_history = []

        self.timer = 0
        self.state_timer = 0

        self.spawn_enemies()

    # ======================================================
    # ACCOUNT
    # ======================================================

    def sync_account(self):

        self.username = self.account_manager.username

    # ======================================================
    # CREATE NORMAL ENEMY
    # ======================================================

    def create_normal_enemy(self, index, total_enemies):

        enemy = Enemy(
            index,
            total_enemies,
            self.screen_width
        )

        enemy.is_boss = False
        enemy.hp = 1

        enemy_mode = settings.get("enemy_difficulty", "normal")
        enemy_multiplier = {"easy": 0.75, "normal": 1.0, "hard": 1.35}.get(enemy_mode, 1.0)
        if hasattr(enemy, "speed"):
            enemy.speed = max(1, enemy.speed * enemy_multiplier)

        return enemy

    # ======================================================
    # CREATE BIG BOSS
    # ======================================================

    def create_big_boss(self):

        boss = Enemy(0, 1, self.screen_width)

        boss.is_boss = True

        boss.width = 230
        boss.height = 230

        boss.image = pygame.transform.scale(
            boss.image,
            (boss.width, boss.height)
        )

        boss.x = self.screen_width // 2 - boss.width // 2
        boss.y = -boss.height

        boss.target_mid_y = 80

        boss.state = "entering"

        boss.speed = 2

        # BIG BOSS MOVEMENT
        boss.boss_direction = random.choice([-1, 1])
        boss.base_speed = 3 if self.level == 5 else 4
        enemy_mode = settings.get("enemy_difficulty", "normal")
        enemy_multiplier = {"easy": 0.75, "normal": 1.0, "hard": 1.35}.get(enemy_mode, 1.0)
        boss.boss_speed = max(1, int(boss.base_speed * enemy_multiplier))
        boss.boss_min_x = 20
        boss.boss_max_x = self.screen_width - boss.width - 20
        boss.boss_move_timer = 0
        boss.boss_change_time = random.randint(70, 150)
        boss.boss_y = 80

        # BOSS HEALTH
        self.boss_max_hp = 30 if self.level == 5 else 45
        self.boss_hp = self.boss_max_hp

        # BOSS ATTACKS
        base_boss_difficulty = 1.0 if self.level == 5 else 1.35
        self.boss_difficulty = base_boss_difficulty * enemy_multiplier
        self.boss_phase = 1
        self.enemy_bullets = []

        boss.shoot_timer = 100
        boss.charge_timer = 0
        boss.attack_count = 0
        boss.flash_timer = 0

        boss.hp = self.boss_max_hp

        return boss

    # ======================================================
    # UPDATE BIG BOSS
    # ======================================================

    def update_big_boss(self, boss):

        # ENTERING
        if boss.state == "entering":

            if boss.y < boss.target_mid_y:

                boss.y += 2

            else:

                boss.y = boss.target_mid_y
                boss.state = "boss_fighting"

            return

        # BOSS FIGHTING
        if boss.state == "boss_fighting":

            boss.x += boss.boss_speed * boss.boss_direction

            # Left wall
            if boss.x <= boss.boss_min_x:

                boss.x = boss.boss_min_x
                boss.boss_direction = 1
                boss.boss_change_time = random.randint(70, 150)

            # Right wall
            elif boss.x >= boss.boss_max_x:

                boss.x = boss.boss_max_x
                boss.boss_direction = -1
                boss.boss_change_time = random.randint(70, 150)

            # RANDOMLY CHANGE DIRECTION
            boss.boss_move_timer += 1

            if boss.boss_move_timer >= boss.boss_change_time:

                boss.boss_direction *= -1
                boss.boss_move_timer = 0
                boss.boss_change_time = random.randint(70, 150)

            # SMOOTH UP/DOWN MOVEMENT
            current_time = pygame.time.get_ticks()

            boss.y = (
                boss.boss_y
                + int(
                    20
                    * pygame.math.Vector2(1, 0).rotate(
                        current_time / 20
                    ).y
                )
            )

            if boss.y < 50:
                boss.y = 50

            if boss.y > 150:
                boss.y = 150

    # ======================================================
    # SPAWN ENEMIES
    # ======================================================

    def spawn_enemies(self):

        self.enemies = []

        # LEVEL 5 / 10 = BIG BOSS
        if self.level in (5, 10):

            self.boss_active = True

            boss = self.create_big_boss()

            self.enemies.append(boss)

            self.timer = 0

            print(f"[GameManager] BIG BOSS LEVEL {self.level}!")

            return

        # NORMAL LEVELS
        self.boss_active = False
        self.boss_hp = 0
        self.boss_max_hp = 0

        enemy_counts = {
            1: 3,
            2: 8,
            3: 10,
            4: 12
        }

        base_count = enemy_counts.get(self.level, 12)
        selected_difficulty = settings.get("difficulty", "normal")
        count_multiplier = {"easy": 0.8, "normal": 1.0, "hard": 1.25}.get(selected_difficulty, 1.0)
        self.spawn_number = max(1, int(round(base_count * count_multiplier)))

        for i in range(self.spawn_number):

            enemy = self.create_normal_enemy(i, self.spawn_number)

            self.enemies.append(enemy)

        self.timer = 0

        print(f"[GameManager] LEVEL {self.level}")

    # ======================================================
    # NEXT LEVEL
    # ======================================================

    def next_level(self):

        self.level += 1
        self.wave = self.level

        self.bullets = []
        self.enemy_bullets = []

        self.spawn_enemies()

    # ======================================================
    # RETURN TO LOGIN
    # ======================================================

    def return_to_login(self):

        self.stop_music()

        self.username = ""

        self.name_input = ""
        self.name_message = ""

        self.account_manager = AccountManager(
            self.screen,
            self.screen_width,
            self.screen_height,
            self.font,
            self.big_font
        )

        self.reset_game()

        self.game_state = "account"

        print("[GameManager] Returned to Login/Register screen.")

    # ======================================================
    # PAUSE SYSTEM
    # ======================================================

    @staticmethod
    def _ease_out_cubic(t):
        return 1 - (1 - t) ** 3

    @staticmethod
    def _ease_out_back(t):
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

    def pause_game(self):

        snap = self.screen.copy()

        small = pygame.transform.smoothscale(
            snap,
            (
                max(1, self.screen_width // 10),
                max(1, self.screen_height // 10)
            )
        )

        # Blur effect: paliton unya ibalik
        self.pause_blur = pygame.transform.smoothscale(
            small,
            (self.screen_width, self.screen_height)
        )

        self.pause_anim = 0.0
        self.game_state = "pause"

        try:
            pygame.mixer.music.pause()
        except pygame.error:
            pass

    def resume_game(self):

        self.game_state = "playing"

        try:
            pygame.mixer.music.unpause()
        except pygame.error:
            pass

    def _pause_layout(self):

        panel_w, panel_h = 440, 480

        panel_x = self.screen_width // 2 - panel_w // 2
        panel_y = max(20, self.screen_height // 2 - panel_h // 2)

        btn_w, btn_h, gap = 300, 56, 16
        start_y = panel_y + 200

        names = ["resume", "restart", "settings", "menu"]

        rects = {}

        for i, name in enumerate(names):
            rects[name] = pygame.Rect(
                self.screen_width // 2 - btn_w // 2,
                start_y + i * (btn_h + gap),
                btn_w,
                btn_h
            )

        return panel_x, panel_y, panel_w, panel_h, rects

    def handle_pause_events(self, events):

        rects = self._pause_layout()[4]

        for event in events:

            if event.type == pygame.KEYDOWN:

                if event.key in (pygame.K_ESCAPE, pygame.K_p):
                    self.resume_game()
                    return

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                if rects["resume"].collidepoint(event.pos):
                    self.resume_game()
                    return

                elif rects["restart"].collidepoint(event.pos):
                    self.reset_game()
                    self.game_state = "playing"
                    self.start_space_music()
                    return

                elif rects["settings"].collidepoint(event.pos):
                    self.settings_return_state = "pause"
                    self.game_state = "settings"
                    return

                elif rects["menu"].collidepoint(event.pos):
                    self.return_to_login()
                    return

        self.draw_pause_menu()

    def draw_pause_button(self):

        rect = self.pause_button_rect
        hover = rect.collidepoint(pygame.mouse.get_pos())

        center = rect.center

        pygame.draw.circle(
            self.screen,
            (20, 60, 85) if hover else (10, 30, 50),
            center,
            22
        )

        pygame.draw.circle(
            self.screen,
            (140, 255, 255) if hover else ACCENT_COLOR,
            center,
            22,
            2
        )

        for dx in (-8, 3):
            pygame.draw.rect(
                self.screen,
                TEXT_COLOR,
                (center[0] + dx, center[1] - 9, 5, 18),
                border_radius=2
            )

    def draw_pause_menu(self):

        self.pause_anim = min(1.0, self.pause_anim + 0.07)

        t = self.pause_anim
        e = self._ease_out_cubic(t)
        pop = self._ease_out_back(t)

        W, H = self.screen_width, self.screen_height

        # ---------------- BLURRED BACKGROUND ----------------
        if self.pause_blur:
            self.screen.blit(self.pause_blur, (0, 0))
        else:
            self.draw_background()

        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((2, 6, 16, int(170 * e)))
        self.screen.blit(overlay, (0, 0))

        panel_x, panel_y, panel_w, panel_h, rects = self._pause_layout()

        offset_y = int((1 - pop) * -70)

        pulse = (pygame.time.get_ticks() % 2000) / 2000
        pulse = (1 + math.sin(pulse * 6.2832)) / 2

        # ---------------- PANEL ----------------
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)

        pygame.draw.rect(
            panel,
            (8, 20, 38, 238),
            panel.get_rect(),
            border_radius=20
        )

        # glowing border (layered)
        for i in range(5):
            pygame.draw.rect(
                panel,
                (80, 220, 235, int((70 + 60 * pulse) / (i + 1))),
                panel.get_rect().inflate(-i * 4, -i * 4),
                2,
                border_radius=max(4, 20 - i * 2)
            )

        # corner accents
        c = (140, 255, 255, 255)
        L = 28
        for (x1, y1, dx, dy) in (
            (10, 10, 1, 1),
            (panel_w - 10, 10, -1, 1),
            (10, panel_h - 10, 1, -1),
            (panel_w - 10, panel_h - 10, -1, -1)
        ):
            pygame.draw.line(panel, c, (x1, y1), (x1 + dx * L, y1), 3)
            pygame.draw.line(panel, c, (x1, y1), (x1, y1 + dy * L), 3)

        # divider
        pygame.draw.line(
            panel,
            (80, 220, 235, 150),
            (40, 130),
            (panel_w - 40, 130),
            2
        )

        panel.set_alpha(int(255 * e))
        self.screen.blit(panel, (panel_x, panel_y + offset_y))

        if t < 0.35:
            return

        # ---------------- TITLE (with glow) ----------------
        title_main = self.big_font.render("PAUSED", True, TEXT_COLOR)
        title_glow = self.big_font.render("PAUSED", True, (30, 130, 150))

        tx = W // 2 - title_main.get_width() // 2
        ty = panel_y + 22 + offset_y

        for ox, oy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
            self.screen.blit(title_glow, (tx + ox, ty + oy))

        self.screen.blit(title_main, (tx, ty))

        # ---------------- STATS ----------------
        stats = self.small_font.render(
            f"SCORE  {self.score}      LEVEL  {self.level}",
            True,
            ACCENT_COLOR
        )

        self.screen.blit(
            stats,
            (
                W // 2 - stats.get_width() // 2,
                panel_y + 108 + offset_y
            )
        )

        self.draw_lives(
            W // 2 - 52,
            panel_y + 148 + offset_y
        )

        # ---------------- BUTTONS ----------------
        labels = {
            "resume": "RESUME",
            "restart": "RESTART",
            "settings": "SETTINGS",
            "menu": "MAIN MENU"
        }

        mouse = pygame.mouse.get_pos()

        for i, name in enumerate(["resume", "restart", "settings", "menu"]):

            local = max(0.0, min(1.0, t * 1.6 - 0.35 - i * 0.18))

            if local <= 0:
                continue

            eb = self._ease_out_cubic(local)

            rect = rects[name].copy()
            rect.x += int((1 - eb) * -90)

            hover = (
                local >= 1.0
                and rects[name].collidepoint(mouse)
            )

            is_primary = name == "resume"

            if hover:
                glow = pygame.Surface(
                    (rect.width + 24, rect.height + 24),
                    pygame.SRCALPHA
                )
                pygame.draw.rect(
                    glow,
                    (80, 220, 235, 55),
                    glow.get_rect(),
                    border_radius=18
                )
                self.screen.blit(glow, (rect.x - 12, rect.y - 12))

                fill = (40, 110, 140)
            elif is_primary:
                fill = (18, 95, 110)
            else:
                fill = BUTTON_COLOR

            pygame.draw.rect(
                self.screen, fill, rect, border_radius=12
            )

            pygame.draw.rect(
                self.screen,
                (140, 255, 255) if hover else ACCENT_COLOR,
                rect,
                3 if hover else 2,
                border_radius=12
            )

            # left accent bar
            pygame.draw.rect(
                self.screen,
                (140, 255, 255) if hover else ACCENT_COLOR,
                (rect.x + 8, rect.y + 12, 4, rect.height - 24),
                border_radius=2
            )

            label = self.font.render(labels[name], True, TEXT_COLOR)

            self.screen.blit(
                label,
                (
                    rect.centerx - label.get_width() // 2,
                    rect.centery - label.get_height() // 2
                )
            )

        # ---------------- HINT ----------------
        hint = self.small_font.render(
            "ESC / P  to resume",
            True,
            MUTED_COLOR
        )

        self.screen.blit(
            hint,
            (
                W // 2 - hint.get_width() // 2,
                panel_y + panel_h - 34 + offset_y
            )
        )

    # ======================================================
    # MAIN UPDATE
    # ======================================================

    def update(self, events):

        # ==================================================
        # ACCOUNT
        # ==================================================

        if self.game_state == "account":

            result = self.account_manager.update(events)

            self.sync_account()

            if result == "start_game":

                self.reset_game()

                self.game_state = "playing"

                self.start_space_music()

            return

        # ==================================================
        # BUTTON CLICK SOUND
        # ==================================================

        self._play_click_if_needed(events)

        # ==================================================
        # PAUSE
        # ==================================================

        if self.game_state == "pause":

            self.handle_pause_events(events)

            return

        # ==================================================
        # PARTICLES / RINGS
        # ==================================================

        if self.game_state in ("playing", "blinking"):

            self.update_effects()

        # ==================================================
        # PLAYER HISTORY
        # ==================================================

        if (
            self.game_state == "playing"
            or self.game_state == "blinking"
        ):

            self.player_history.append(
                (self.player.x, self.player.y)
            )

            if len(self.player_history) > 60:

                self.player_history.pop(0)

        # ==================================================
        # PLAYING
        # ==================================================

        if self.game_state == "playing":

            # ---------------- PAUSE TRIGGER ----------------
            for event in events:

                if (
                    event.type == pygame.KEYDOWN
                    and event.key in (pygame.K_ESCAPE, pygame.K_p)
                ) or (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and self.pause_button_rect.collidepoint(event.pos)
                ):
                    self.pause_game()
                    return

            keys = pygame.key.get_pressed()
            self.player.speed = int(settings.get("player_speed", 10))

            if keys[pygame.K_LEFT]:

                self.player.move_left()

            if keys[pygame.K_RIGHT]:

                self.player.move_right()

            screen_button_fired = False

            left_button_enabled = settings.get("left_button", False)
            right_button_enabled = settings.get("right_button", False)
            fire_button_enabled = settings.get("fire_button", False)

            if (
                left_button_enabled
                or right_button_enabled
                or fire_button_enabled
            ):

                screen_button_fired = self.buttons.handle_mouse(
                    self.player,
                    events,
                    left_button_enabled,
                    right_button_enabled,
                    fire_button_enabled
                )

            keyboard_fired = False

            for event in events:

                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_SPACE
                ):

                    keyboard_fired = True

            rapid_active = self.rapid_timer > 0

            held_fire = rapid_active and keys[pygame.K_SPACE]

            if self.fire_cooldown > 0:

                self.fire_cooldown -= 1

            if screen_button_fired or keyboard_fired or held_fire:

                self.try_fire(rapid_active)

            self.player.keep_inside_screen()

            for bullet in self.bullets:

                bullet.update()

            self.bullets = [
                b for b in self.bullets if b.is_active
            ]

            # POWER-UP TIMERS
            if self.rapid_timer > 0:
                self.rapid_timer -= 1

            if self.shield_timer > 0:
                self.shield_timer -= 1

            if self.invuln_timer > 0:
                self.invuln_timer -= 1

            self.update_powerups()

            self.timer += 1

            # ==================================================
            # NORMAL ENEMY ATTACK
            # ==================================================

            if self.level not in (5, 10):

                if self.timer >= 180:

                    waiting_enemies = [
                        e
                        for e in self.enemies
                        if e.state == "waiting"
                        and not getattr(e, "is_boss", False)
                    ]

                    if waiting_enemies:

                        chosen_enemy = random.choice(waiting_enemies)

                        if self.player_history:

                            target_x, target_y = self.player_history[0]

                            chosen_enemy.start_drop(
                                target_x,
                                target_y
                            )

                        self.timer = 0

            # ==================================================
            # UPDATE ENEMIES
            # ==================================================

            all_despawned = True

            for enemy in self.enemies:

                if getattr(enemy, "is_boss", False):

                    self.update_big_boss(enemy)

                    self.update_boss_attack(enemy)

                else:

                    enemy.update()

                if enemy.state != "offscreen":

                    all_despawned = False

            # LEVEL COMPLETE
            if all_despawned:

                self.next_level()

            self.update_enemy_bullets()

            if self.game_state == "playing":

                self.check_collisions()

        # ==================================================
        # BLINKING
        # ==================================================

        elif self.game_state == "blinking":

            self.player.update_blink()

            self.state_timer += 1

            for enemy in self.enemies:

                if getattr(enemy, "is_boss", False):

                    self.update_big_boss(enemy)

                else:

                    enemy.update()

            if self.state_timer >= 180:

                # CHECK IF STILL MAY LIVES
                if self.lives <= 0:

                    self.game_state = "game_over"

                    self.stop_music()

                    self.start_game_over_music()

                    if not self.score_saved:

                        saved = db.save_score(
                            self.username,
                            self.score
                        )

                        if saved:

                            print(
                                "[GameManager] Score saved: "
                                f"{self.username} - "
                                f"{self.score}"
                            )

                            self.score_saved = True

                        else:

                            print(
                                "[GameManager] "
                                "Failed to save score."
                            )

                else:

                    # Buhi pa -> balik playing
                    self.player.is_blinking = False

                    self.state_timer = 0

                    self.game_state = "playing"

        # ==================================================
        # LEADERBOARD
        # ==================================================

        elif self.game_state == "leaderboard":

            for event in events:

                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):

                    if self.back_button_rect.collidepoint(event.pos):

                        self.game_state = "game_over"

                    elif self.settings_button_rect.collidepoint(event.pos):

                        self.name_input = self.username

                        self.name_message = ""

                        self.settings_return_state = "leaderboard"
                        self.game_state = "settings"

            self.draw_leaderboard()

            return

        # ==================================================
        # SETTINGS
        # ==================================================

        elif self.game_state == "settings":

            if self.settings_return_state in ("game_over", "pause"):
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                            self.game_state = self.settings_return_state
                    elif (
                        event.type == pygame.MOUSEBUTTONDOWN
                        and event.button == 1
                    ):
                        if self.difficulty_minus_rect.collidepoint(event.pos):
                            self.cycle_difficulty(-1)
                        elif self.difficulty_plus_rect.collidepoint(event.pos):
                            self.cycle_difficulty(1)
                        elif self.player_speed_minus_rect.collidepoint(event.pos):
                            self.change_player_speed(-1)
                        elif self.player_speed_plus_rect.collidepoint(event.pos):
                            self.change_player_speed(1)
                        elif self.enemy_difficulty_minus_rect.collidepoint(event.pos):
                            self.cycle_enemy_difficulty(-1)
                        elif self.enemy_difficulty_plus_rect.collidepoint(event.pos):
                            self.cycle_enemy_difficulty(1)
                        elif self.gameplay_music_minus_rect.collidepoint(event.pos):
                            self.music_volume = round(max(0.0, self.music_volume - 0.1), 1)
                            settings.set("music_volume", self.music_volume)
                            if pygame.mixer.get_init():
                                pygame.mixer.music.set_volume(self.music_volume)
                        elif self.gameplay_music_plus_rect.collidepoint(event.pos):
                            self.music_volume = round(min(1.0, self.music_volume + 0.1), 1)
                            settings.set("music_volume", self.music_volume)
                            if pygame.mixer.get_init():
                                pygame.mixer.music.set_volume(self.music_volume)
                        elif self.gameplay_mobile_controls_rect.collidepoint(event.pos):
                            controls_enabled = not settings.get("mobile_controls", False)
                            settings.set("mobile_controls", controls_enabled)
                            for key in ("left_button", "right_button", "fire_button"):
                                settings.set(key, controls_enabled)
                        elif self.settings_back_button_rect.collidepoint(event.pos):
                            self.game_state = self.settings_return_state

                self.draw_game_over_settings()
                return

            for event in events:

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_BACKSPACE:

                        self.name_input = self.name_input[:-1]

                    elif event.key == pygame.K_RETURN:

                        self.save_player_name()

                    elif event.key == pygame.K_ESCAPE:

                        self.game_state = "leaderboard"

                    elif event.unicode.isprintable():

                        if len(self.name_input) < 20:

                            self.name_input += event.unicode

                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):

                    if self.volume_minus_button_rect.collidepoint(
                        event.pos
                    ):

                        self.music_volume -= 0.10

                        if self.music_volume < 0:

                            self.music_volume = 0

                        self.music_volume = round(self.music_volume, 1)

                        settings.set("music_volume", self.music_volume)

                        pygame.mixer.music.set_volume(self.music_volume)

                    elif self.volume_plus_button_rect.collidepoint(
                        event.pos
                    ):

                        self.music_volume += 0.10

                        if self.music_volume > 1:

                            self.music_volume = 1

                        self.music_volume = round(self.music_volume, 1)

                        settings.set("music_volume", self.music_volume)

                        pygame.mixer.music.set_volume(self.music_volume)

                    elif self.mobile_controls_button_rect.collidepoint(
                        event.pos
                    ):

                        settings.set(
                            "mobile_controls",
                            not settings.get("mobile_controls", False)
                        )
                        controls_enabled = settings.get(
                            "mobile_controls",
                            False
                        )
                        for key in (
                            "left_button",
                            "right_button",
                            "fire_button"
                        ):
                            settings.set(key, controls_enabled)

                    elif self.name_input_rect.collidepoint(event.pos):

                        pass

                    elif self.save_name_button_rect.collidepoint(
                        event.pos
                    ):

                        self.save_player_name()

                    elif self.settings_back_button_rect.collidepoint(
                        event.pos
                    ):

                        self.game_state = self.settings_return_state

            self.draw_settings()

            return

        # ==================================================
        # GAME OVER
        # ==================================================

        elif self.game_state == "game_over":

            for event in events:

                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):

                    # RELOAD
                    if self.reload_button_rect.collidepoint(event.pos):

                        self.reset_game()

                        self.game_state = "playing"

                        self.start_space_music()

                    # LEADERBOARD
                    elif self.leaderboard_button_rect.collidepoint(
                        event.pos
                    ):

                        self.game_state = "leaderboard"

                    elif self.game_over_settings_button_rect.collidepoint(
                        event.pos
                    ):

                        self.settings_return_state = "game_over"
                        self.game_state = "settings"

                    elif self.game_over_back_button_rect.collidepoint(
                        event.pos
                    ):

                        self.return_to_login()

        # ==================================================
        # DRAW GAME
        # ==================================================

        self.draw_background()

        if self.game_state != "game_over":

            self.player.draw(self.screen)

            self.draw_player_shield()

            for enemy in self.enemies:

                is_live_boss = (
                    getattr(enemy, "is_boss", False)
                    and enemy.state != "offscreen"
                )

                if is_live_boss:
                    self.draw_boss_aura(enemy)

                enemy.draw(self.screen)

                if is_live_boss:
                    self.draw_boss_overlay(enemy)

            self.draw_enemy_bullets()

            for p in self.powerups:

                self.draw_powerup(p)

            for bullet in self.bullets:

                bullet.draw(self.screen)

            self.draw_effects()

            left_button_enabled = settings.get("left_button", False)
            right_button_enabled = settings.get("right_button", False)
            fire_button_enabled = settings.get("fire_button", False)

            if (
                left_button_enabled
                or right_button_enabled
                or fire_button_enabled
            ):

                self.buttons.draw(
                    self.screen,
                    left_button_enabled,
                    right_button_enabled,
                    fire_button_enabled
                )

        # ==================================================
        # SCORE (CENTER)
        # ==================================================

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            TEXT_COLOR
        )

        self.screen.blit(
            score_text,
            (
                self.screen_width // 2
                - score_text.get_width() // 2,
                20
            )
        )

        # ==================================================
        # LIVES (SIDE - LEFT) - HEART ICONS
        # ==================================================

        if self.game_state != "game_over":

            self.draw_lives(20, 20)

            self.draw_effect_bars()

            self.draw_boss_banner()

        # ==================================================
        # LEVEL
        # ==================================================

        level_text = self.font.render(
            f"LEVEL {self.level}",
            True,
            ACCENT_COLOR
        )

        self.screen.blit(
            level_text,
            (
                self.screen_width
                - level_text.get_width()
                - 20,
                20
            )
        )

        # ==================================================
        # PAUSE BUTTON
        # ==================================================

        if self.game_state == "playing":

            self.draw_pause_button()

        # ==================================================
        # BIG BOSS DISPLAY
        # ==================================================

        if (
            self.level in (5, 10)
            and self.boss_active
            and self.game_state == "playing"
        ):

            boss_title = self.font.render(
                "BIG BOSS",
                True,
                ERROR_COLOR
            )

            self.screen.blit(
                boss_title,
                (
                    self.screen_width // 2
                    - boss_title.get_width() // 2,
                    20
                )
            )

            bar_width = 420
            bar_height = 25

            bar_x = self.screen_width // 2 - bar_width // 2

            bar_y = 65

            pygame.draw.rect(
                self.screen,
                (40, 20, 25),
                (bar_x, bar_y, bar_width, bar_height),
                border_radius=8
            )

            if self.boss_max_hp > 0:

                hp_width = int(
                    bar_width * (self.boss_hp / self.boss_max_hp)
                )

                if self.boss_phase == 1:
                    bar_color = ERROR_COLOR
                elif self.boss_phase == 2:
                    bar_color = (255, 170, 80)
                else:
                    flicker = (pygame.time.get_ticks() // 120) % 2
                    bar_color = (255, 70, 70) if flicker else (255, 130, 100)

                pygame.draw.rect(
                    self.screen,
                    bar_color,
                    (bar_x, bar_y, hp_width, bar_height),
                    border_radius=8
                )

            pygame.draw.rect(
                self.screen,
                TEXT_COLOR,
                (bar_x, bar_y, bar_width, bar_height),
                2,
                border_radius=8
            )

            for frac in (0.3, 0.6):

                tick_x = bar_x + int(bar_width * frac)

                pygame.draw.line(
                    self.screen,
                    TEXT_COLOR,
                    (tick_x, bar_y),
                    (tick_x, bar_y + bar_height),
                    2
                )

            hp_text = self.small_font.render(
                f"BOSS HP: {self.boss_hp}/{self.boss_max_hp}",
                True,
                TEXT_COLOR
            )

            self.screen.blit(
                hp_text,
                (
                    self.screen_width // 2
                    - hp_text.get_width() // 2,
                    92
                )
            )

        # ==================================================
        # GAME OVER SCREEN
        # ==================================================

        if self.game_state == "game_over":

            go_text = self.big_font.render(
                "GAME OVER",
                True,
                ERROR_COLOR
            )

            self.screen.blit(
                go_text,
                (
                    self.screen_width // 2
                    - go_text.get_width() // 2,
                    self.screen_height // 2 - 100
                )
            )

            final_score_text = self.font.render(
                f"Final Score: {self.score}",
                True,
                TEXT_COLOR
            )

            self.screen.blit(
                final_score_text,
                (
                    self.screen_width // 2
                    - final_score_text.get_width() // 2,
                    self.screen_height // 2 - 20
                )
            )

            self.draw_button(self.reload_button_rect, "RELOAD")
            self.draw_button(self.leaderboard_button_rect, "LEADERBOARD")
            self.draw_button(self.game_over_settings_button_rect, "SETTINGS")
            self.draw_button(self.game_over_back_button_rect, "BACK")

        # ==================================================
        # SCREEN SHAKE (applied last)
        # ==================================================

        self.apply_screen_shake()

    # ======================================================
    # SAVE PLAYER NAME
    # ======================================================

    def save_player_name(self):

        new_name = self.name_input.strip()

        if not new_name:

            self.name_message = "Name cannot be empty."

            return

        if len(new_name) < 3:

            self.name_message = "Name must be at least 3 characters."

            return

        if len(new_name) > 20:

            self.name_message = "Name is too long."

            return

        try:

            result = db.update_player_profile(
                self.username,
                new_name
            )

            if result:

                self.username = new_name

                self.account_manager.username = new_name

                self.name_input = new_name

                self.name_message = "Name updated successfully!"

                print(
                    "[GameManager] Player name "
                    f"changed to: {new_name}"
                )

            else:

                self.name_message = "Failed to update name."

        except Exception as e:

            print("[GameManager] Name update error:", e)

            self.name_message = "Name update failed."

    # ======================================================
    # BUTTON
    # ======================================================

    def draw_button(self, rect, text):

        pygame.draw.rect(
            self.screen,
            BUTTON_COLOR,
            rect,
            border_radius=10
        )

        pygame.draw.rect(
            self.screen,
            ACCENT_COLOR,
            rect,
            2,
            border_radius=10
        )

        button_text = self.font.render(text, True, TEXT_COLOR)

        self.screen.blit(
            button_text,
            (
                rect.x + (rect.width - button_text.get_width()) // 2,
                rect.y + (rect.height - button_text.get_height()) // 2
            )
        )

    # ======================================================
    # HEART ICON
    # ======================================================

    def draw_heart(self, x, y, size, color):

        radius = size // 4

        pygame.draw.circle(
            self.screen,
            color,
            (x + radius, y + radius),
            radius
        )

        pygame.draw.circle(
            self.screen,
            color,
            (x + size - radius, y + radius),
            radius
        )

        pygame.draw.polygon(
            self.screen,
            color,
            [
                (x, y + radius),
                (x + size, y + radius),
                (x + size // 2, y + size)
            ]
        )

    # ======================================================
    # LIVES (HEARTS)
    # ======================================================

    def draw_lives(self, x, y, max_lives=3, heart_size=28, spacing=10):

        for i in range(max_lives):

            heart_x = x + i * (heart_size + spacing)

            if i < self.lives:

                color = ERROR_COLOR

            else:

                color = (55, 55, 65)

            self.draw_heart(heart_x, y, heart_size, color)

    # ======================================================
    # COLLISIONS
    # ======================================================

    def check_collisions(self):

        player_rect = self.player.get_rect()

        # ==================================================
        # PLAYER vs ENEMY
        # ==================================================

        for enemy in self.enemies:

            if enemy.state == "offscreen":

                continue

            enemy_rect = enemy.get_rect()

            if player_rect.colliderect(enemy_rect):

                # Invulnerable right after shield breaks
                if self.invuln_timer > 0:

                    continue

                ex, ey = enemy_rect.center
                px, py = player_rect.center

                # SHIELD ABSORBS THE HIT
                if self.shield_timer > 0:

                    self.shield_timer = 0
                    self.invuln_timer = 60

                    self.explode(
                        px, py,
                        [(90, 170, 255), (200, 230, 255)],
                        count=30,
                        speed=6
                    )

                    self.play_sound("boss_hit")

                    self.add_shake(5, 10)

                    if not getattr(enemy, "is_boss", False):

                        enemy.state = "offscreen"

                        self.explode(
                            ex, ey,
                            [(255, 200, 80), (255, 120, 60)],
                            count=20,
                            speed=5
                        )

                        self.play_sound("explosion")

                    return

                # LOSE ONE LIFE
                self.lives -= 1

                enemy.state = "offscreen"

                self.game_state = "blinking"

                self.player.is_blinking = True

                self.state_timer = 0

                self.explode(
                    px, py,
                    [(255, 120, 130), (255, 255, 255), (80, 220, 235)],
                    count=45,
                    speed=7
                )

                self.explode(
                    ex, ey,
                    [(255, 200, 80), (255, 120, 60)],
                    count=25,
                    speed=5
                )

                self.play_sound("hit")

                self.add_shake(14, 28)

                return

        # ==================================================
        # BULLETS vs ENEMY
        # ==================================================

        for bullet in self.bullets[:]:

            bullet_rect = bullet.get_rect()

            for enemy in self.enemies:

                if enemy.state == "offscreen":

                    continue

                if bullet_rect.colliderect(enemy.get_rect()):

                    self.bullets.remove(bullet)

                    self.damage_enemy(enemy, bullet_rect.center)

                    break

    # ======================================================
    # LEADERBOARD
    # ======================================================

    def draw_leaderboard(self):

        self.draw_background()

        title = self.big_font.render(
            "LEADERBOARD",
            True,
            ACCENT_COLOR
        )

        self.screen.blit(
            title,
            (
                self.screen_width // 2
                - title.get_width() // 2,
                50
            )
        )

        scores = db.get_top_scores(10)

        if not scores:

            no_scores = self.font.render(
                "No scores available.",
                True,
                MUTED_COLOR
            )

            self.screen.blit(
                no_scores,
                (
                    self.screen_width // 2
                    - no_scores.get_width() // 2,
                    180
                )
            )

        else:

            y = 140

            for rank, row in enumerate(scores, start=1):

                username, score, played_at = row

                leaderboard_text = self.font.render(
                    f"{rank}. {username}   {score} pts",
                    True,
                    TEXT_COLOR
                )

                self.screen.blit(
                    leaderboard_text,
                    (
                        self.screen_width // 2
                        - leaderboard_text.get_width() // 2,
                        y
                    )
                )

                y += 45

        self.draw_button(self.back_button_rect, "BACK")
        self.draw_button(self.settings_button_rect, "SETTINGS")

    # ======================================================
    # SETTINGS SCREEN
    # ======================================================

    def toggle_mobile_button(self, setting_key):
        enabled = not settings.get(setting_key, False)
        settings.set(setting_key, enabled)
        settings.set(
            "mobile_controls",
            all(
                settings.get(key, False)
                for key in (
                    "left_button",
                    "right_button",
                    "fire_button"
                )
            )
        )

    def cycle_difficulty(self, direction):
        options = ("easy", "normal", "hard")
        current = settings.get("difficulty", "normal")
        if current not in options:
            current = "normal"
        index = (options.index(current) + direction) % len(options)
        settings.set("difficulty", options[index])

        # Update current run lives immediately, keeping the existing game state.
        lives_by_difficulty = {"easy": 5, "normal": 3, "hard": 2}
        self.lives = min(5, max(1, lives_by_difficulty[options[index]]))

    def change_player_speed(self, amount):
        current = int(settings.get("player_speed", 10))
        settings.set("player_speed", max(1, min(20, current + amount)))
        self.player.speed = settings.get("player_speed", 10)

    def cycle_enemy_difficulty(self, direction):
        options = ("easy", "normal", "hard")
        current = settings.get("enemy_difficulty", "normal")
        if current not in options:
            current = "normal"
        index = (options.index(current) + direction) % len(options)
        settings.set("enemy_difficulty", options[index])

        multiplier = {"easy": 0.75, "normal": 1.0, "hard": 1.35}[options[index]]
        self.boss_difficulty = multiplier
        for enemy in self.enemies:
            if getattr(enemy, "is_boss", False):
                enemy.boss_speed = max(1, int(enemy.base_speed * multiplier))

    def draw_game_over_settings(self):

        self.draw_background()

        title = self.big_font.render("GAMEPLAY SETTINGS", True, ACCENT_COLOR)
        self.screen.blit(
            title,
            (self.screen_width // 2 - title.get_width() // 2, 35)
        )

        # Difficulty
        self.screen.blit(
            self.font.render("DIFFICULTY", True, TEXT_COLOR),
            (self.screen_width // 2 - 125, 120)
        )
        difficulty = str(settings.get("difficulty", "normal")).upper()
        value = self.small_font.render(difficulty, True, ACCENT_COLOR)
        self.screen.blit(
            value,
            (self.screen_width // 2 - value.get_width() // 2, 173)
        )
        self.draw_button(self.difficulty_minus_rect, "<")
        self.draw_button(self.difficulty_plus_rect, ">")

        # Player speed
        self.screen.blit(
            self.font.render("PLAYER SPEED", True, TEXT_COLOR),
            (self.screen_width // 2 - 125, 220)
        )
        speed = int(settings.get("player_speed", 10))
        speed_text = self.small_font.render(f"{speed} / 20", True, ACCENT_COLOR)
        self.screen.blit(
            speed_text,
            (self.screen_width // 2 - speed_text.get_width() // 2, 273)
        )
        self.draw_button(self.player_speed_minus_rect, "-")
        self.draw_button(self.player_speed_plus_rect, "+")

        # Enemy difficulty
        self.screen.blit(
            self.font.render("ENEMY DIFFICULTY", True, TEXT_COLOR),
            (self.screen_width // 2 - 125, 320)
        )
        enemy_difficulty = str(settings.get("enemy_difficulty", "normal")).upper()
        enemy_text = self.small_font.render(enemy_difficulty, True, ACCENT_COLOR)
        self.screen.blit(
            enemy_text,
            (self.screen_width // 2 - enemy_text.get_width() // 2, 373)
        )
        self.draw_button(self.enemy_difficulty_minus_rect, "<")
        self.draw_button(self.enemy_difficulty_plus_rect, ">")

        # Music volume
        self.screen.blit(
            self.font.render("MUSIC VOLUME", True, TEXT_COLOR),
            (self.screen_width // 2 - 125, 395)
        )
        volume_text = self.small_font.render(
            f"{int(self.music_volume * 100)}%",
            True,
            ACCENT_COLOR
        )
        self.screen.blit(
            volume_text,
            (self.screen_width // 2 - volume_text.get_width() // 2, 443)
        )
        self.draw_button(self.gameplay_music_minus_rect, "-")
        self.draw_button(self.gameplay_music_plus_rect, "+")

        # Original ON/OFF switch retained for mobile controls.
        mobile_label = self.small_font.render(
            "MOBILE CONTROLS", True, TEXT_COLOR
        )
        self.screen.blit(
            mobile_label,
            (self.screen_width // 2 - mobile_label.get_width() // 2, 480)
        )
        mobile_state = "ON" if settings.get("mobile_controls", False) else "OFF"
        self.draw_button(self.gameplay_mobile_controls_rect, mobile_state)

        self.draw_button(self.settings_back_button_rect, "BACK")

    def draw_settings(self):

        self.draw_background()

        title = self.big_font.render(
            "SETTINGS",
            True,
            ACCENT_COLOR
        )

        self.screen.blit(
            title,
            (
                self.screen_width // 2
                - title.get_width() // 2,
                25
            )
        )

        profile_rect = pygame.Rect(
            self.screen_width // 2 - 250,
            100,
            500,
            170
        )

        pygame.draw.rect(
            self.screen,
            (8, 20, 38),
            profile_rect,
            border_radius=15
        )

        pygame.draw.rect(
            self.screen,
            ACCENT_COLOR,
            profile_rect,
            2,
            border_radius=15
        )

        profile_title = self.font.render(
            "PLAYER PROFILE",
            True,
            ACCENT_COLOR
        )

        self.screen.blit(
            profile_title,
            (
                self.screen_width // 2
                - profile_title.get_width() // 2,
                112
            )
        )

        player_name_text = self.small_font.render(
            f"PLAYER: {self.username}",
            True,
            TEXT_COLOR
        )

        self.screen.blit(
            player_name_text,
            (
                self.screen_width // 2
                - player_name_text.get_width() // 2,
                155
            )
        )

        final_score_text = self.font.render(
            f"FINAL SCORE: {self.score}",
            True,
            SUCCESS_COLOR
        )

        self.screen.blit(
            final_score_text,
            (
                self.screen_width // 2
                - final_score_text.get_width() // 2,
                190
            )
        )

        level_text = self.small_font.render(
            f"LEVEL REACHED: {self.level}",
            True,
            ACCENT_COLOR
        )

        self.screen.blit(
            level_text,
            (
                self.screen_width // 2
                - level_text.get_width() // 2,
                230
            )
        )

        music_text = self.small_font.render(
            "MUSIC",
            True,
            TEXT_COLOR
        )

        self.screen.blit(
            music_text,
            (
                self.screen_width // 2
                - music_text.get_width() // 2,
                290
            )
        )

        volume_percent = int(self.music_volume * 100)

        volume_text = self.small_font.render(
            f"{volume_percent}%",
            True,
            ACCENT_COLOR
        )

        self.screen.blit(
            volume_text,
            (
                self.screen_width // 2
                - volume_text.get_width() // 2,
                325
            )
        )

        self.draw_button(self.volume_minus_button_rect, "-")
        self.draw_button(self.volume_plus_button_rect, "+")

        name_label = self.small_font.render(
            "EDIT PLAYER NAME",
            True,
            TEXT_COLOR
        )

        self.screen.blit(
            name_label,
            (
                self.screen_width // 2
                - name_label.get_width() // 2,
                395
            )
        )

        pygame.draw.rect(
            self.screen,
            (10, 20, 38),
            self.name_input_rect,
            border_radius=10
        )

        pygame.draw.rect(
            self.screen,
            ACCENT_COLOR,
            self.name_input_rect,
            2,
            border_radius=10
        )

        name_text = self.small_font.render(
            self.name_input,
            True,
            TEXT_COLOR
        )

        self.screen.blit(
            name_text,
            (
                self.name_input_rect.x + 12,
                self.name_input_rect.y + 12
            )
        )

        self.draw_button(self.save_name_button_rect, "SAVE NAME")

        if self.name_message:

            if "successfully" in self.name_message:

                message_color = SUCCESS_COLOR

            else:

                message_color = ERROR_COLOR

            message_font = pygame.font.SysFont("Arial", 18)

            message_text = message_font.render(
                self.name_message,
                True,
                message_color
            )

            self.screen.blit(
                message_text,
                (
                    self.screen_width // 2
                    - message_text.get_width() // 2,
                    525
                )
            )

        mobile_controls_label = self.small_font.render(
            "MOBILE CONTROLS",
            True,
            TEXT_COLOR
        )

        self.screen.blit(
            mobile_controls_label,
            (
                self.screen_width // 2
                - mobile_controls_label.get_width()
                - 15,
                357
            )
        )

        mobile_controls_state = (
            "ON"
            if settings.get("mobile_controls", False)
            else "OFF"
        )

        self.draw_button(
            self.mobile_controls_button_rect,
            mobile_controls_state
        )

        self.draw_button(self.settings_back_button_rect, "BACK")