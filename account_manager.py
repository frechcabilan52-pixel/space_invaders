
import pygame
import os
import random
import math

from db_connection import db


GOLD = (255, 207, 92)
GOLD_LIGHT = (255, 235, 170)
WHITE = (245, 248, 255)
MUTED = (145, 165, 190)
CYAN = (90, 220, 255)
DARK = (5, 8, 19)


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp_rect(a, b, p):
    return pygame.Rect(
        *[
            int(a[i] + (b[i] - a[i]) * p)
            for i in range(4)
        ]
    )


class AccountManager:

    def __init__(
        self,
        screen,
        screen_width,
        screen_height,
        font,
        big_font
    ):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.font = font
        self.big_font = big_font

        self.title_font = pygame.font.SysFont(
            "segoeui", 43, bold=True
        )
        self.heading_font = pygame.font.SysFont(
            "segoeui", 31, bold=True
        )
        self.small_font = pygame.font.SysFont(
            "segoeui", 17
        )
        self.label_font = pygame.font.SysFont(
            "segoeui", 14, bold=True
        )
        self.button_font = pygame.font.SysFont(
            "segoeui", 19, bold=True
        )

        self.username = ""
        self.player_id = "N/A"
        self.username_input = ""
        self.password_input = ""
        self.message = ""
        self.active_input = "username"
        self.state = "account_menu"

        cx = screen_width // 2

        self.register_button_rect = pygame.Rect(
            cx - 205, 420, 190, 55
        )
        self.login_button_rect = pygame.Rect(
            cx + 15, 420, 190, 55
        )
        self.start_game_button_rect = pygame.Rect(
            cx - 130, 405, 260, 62
        )

        self.card_full = pygame.Rect(
            cx - 235, 145, 470, 375
        )
        self.card_small = pygame.Rect(
            0, 0, 100, 100
        )
        self.card_small.center = self.card_full.center

        self.username_rect = pygame.Rect(
            cx - 175, 265, 350, 48
        )
        self.password_rect = pygame.Rect(
            cx - 175, 355, 350, 48
        )
        self.action_button_rect = pygame.Rect(
            cx - 175, 425, 350, 50
        )
        self.switch_rect = pygame.Rect(
            cx - 180, 485, 360, 25
        )
        self.back_button_rect = pygame.Rect(
            28, screen_height - 62, 120, 40
        )

        self.transition = None
        self.T_SHRINK = 350
        self.T_HOLD = 450
        self.T_EXPAND = 400

        self.stars = []
        for _ in range(200):
            self.stars.append({
                "x": random.uniform(0, screen_width),
                "y": random.uniform(0, screen_height),
                "speed": random.uniform(8, 48),
                "size": random.choice([1, 1, 1, 2, 2, 3]),
                "phase": random.uniform(0, math.tau)
            })

        self.dust = []
        for _ in range(65):
            self.dust.append({
                "x": random.randrange(screen_width),
                "y": random.randrange(screen_height),
                "speed": random.uniform(5, 18),
                "phase": random.uniform(0, math.tau)
            })

        self.background_surface = pygame.Surface(
            (screen_width, screen_height)
        )

        self.vignette = pygame.Surface(
            (screen_width, screen_height),
            pygame.SRCALPHA
        )
        for i in range(12):
            inset = i * 12
            alpha = int(3 + i * 1.5)
            pygame.draw.rect(
                self.vignette,
                (0, 0, 8, alpha),
                (inset, inset,
                 screen_width - inset * 2,
                 screen_height - inset * 2),
                width=12
            )

        self.music_started = False

    # ==================================================
    # ANIMATED BACKGROUND
    # ==================================================

    def draw_background(self):
        screen = self.screen
        w = self.screen_width
        h = self.screen_height
        t = pygame.time.get_ticks() / 1000

        # Deep cinematic gradient
        top = (5, 8, 22)
        bottom = (18, 12, 29)

        for y in range(h):
            p = y / max(1, h - 1)
            color = tuple(
                int(top[i] + (bottom[i] - top[i]) * p)
                for i in range(3)
            )
            pygame.draw.line(screen, color, (0, y), (w, y))

        # Atmospheric blue and gold nebula
        glow = pygame.Surface((w, h), pygame.SRCALPHA)

        nebulae = [
            (
                int(w * 0.16 + math.sin(t * 0.19) * 32),
                int(h * 0.31 + math.cos(t * 0.17) * 24),
                220, (24, 67, 160)
            ),
            (
                int(w * 0.87 + math.cos(t * 0.15) * 25),
                int(h * 0.25 + math.sin(t * 0.13) * 24),
                200, (108, 46, 111)
            ),
            (
                int(w * 0.56 + math.sin(t * 0.12) * 35),
                int(h * 0.91),
                200, (104, 66, 24)
            )
        ]

        for x, y, radius, color in nebulae:
            for r in range(radius, 15, -15):
                strength = 1 - r / radius
                alpha = int(1 + strength * 5)
                pygame.draw.circle(
                    glow,
                    (*color, alpha),
                    (x, y),
                    r
                )

        screen.blit(glow, (0, 0))

        # Subtle orbital lines
        orbit = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, h // 2

        for i in range(4):
            rw = 220 + i * 46
            rh = 70 + i * 15
            alpha = int(8 + (math.sin(t + i) + 1) * 5)

            pygame.draw.ellipse(
                orbit,
                (GOLD[0], GOLD[1], GOLD[2], alpha),
                (cx - rw, cy - rh, rw * 2, rh * 2),
                1
            )

        screen.blit(orbit, (0, 0))

        # Moving stars
        for star in self.stars:
            star["y"] += star["speed"] * 0.016

            if star["y"] > h:
                star["y"] = -3
                star["x"] = random.randrange(w)

            pulse = (
                math.sin(t * 2.0 + star["phase"]) + 1
            ) / 2

            brightness = int(105 + pulse * 150)
            color = (
                brightness,
                min(255, brightness + 8),
                min(255, brightness + 24)
            )

            pygame.draw.circle(
                screen,
                color,
                (int(star["x"]), int(star["y"])),
                star["size"]
            )

        # Tiny golden particles
        for particle in self.dust:
            particle["y"] -= particle["speed"] * 0.016

            if particle["y"] < 0:
                particle["y"] = h
                particle["x"] = random.randrange(w)

            pulse = (
                math.sin(t * 1.8 + particle["phase"]) + 1
            ) / 2

            color = (
                int(115 + pulse * 100),
                int(95 + pulse * 100),
                int(48 + pulse * 45)
            )

            pygame.draw.circle(
                screen,
                color,
                (int(particle["x"]), int(particle["y"])),
                1
            )

        # Cinematic edge shading
        screen.blit(self.vignette, (0, 0))

    # ==================================================
    # MUSIC
    # ==================================================

    def start_music(self):
        if self.music_started:
            return

        try:
            root = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
            music_path = os.path.join(
                root, "space_music.mp3"
            )

            if os.path.exists(music_path):
                if not pygame.mixer.get_init():
                    pygame.mixer.init()

                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                self.music_started = True
                print("[Music] Space music started.")

        except (pygame.error, OSError) as e:
            print(f"[Music] {e}")

    # ==================================================
    # ACCOUNT ACTIONS
    # ==================================================

    def register_player(self):
        username = self.username_input.strip()
        password = self.password_input

        if not username:
            self.message = "Please enter your username."
            return False

        if not password:
            self.message = "Please enter your password."
            return False

        if len(username) < 3:
            self.message = "Username needs at least 3 characters."
            return False

        if len(password) < 4:
            self.message = "Password needs at least 4 characters."
            return False

        try:
            player_id = db.register_player(username, password)

            if player_id is not None:
                self.player_id = player_id
                self.username = username
                self.username_input = ""
                self.password_input = ""
                self.message = ""
                self.state = "welcome"
                self.start_music()

                print(
                    f"[AccountManager] Registered: {username}"
                )
                return True

        except Exception as e:
            print(f"[AccountManager] Registration error: {e}")

        self.message = (
            "Username already exists or registration failed."
        )
        return False

    def login_player(self):
        username = self.username_input.strip()
        password = self.password_input

        if not username:
            self.message = "Please enter your username."
            return False

        if not password:
            self.message = "Please enter your password."
            return False

        try:
            player = db.get_player(username, password)

            if player:
                self.player_id = player[0]
                self.username = player[1]
                self.username_input = ""
                self.password_input = ""
                self.message = ""
                self.state = "welcome"

                print(
                    f"[AccountManager] Login successful: "
                    f"{self.username}"
                )
                return True

        except Exception as e:
            print(f"[AccountManager] Login error: {e}")

        self.message = "Invalid username or password."
        return False

    # ==================================================
    # TRANSITION
    # ==================================================

    def start_switch(self, target, from_menu=False):
        now = pygame.time.get_ticks()

        self.transition = {
            "target": target,
            "start": now - (
                self.T_SHRINK if from_menu else 0
            ),
            "switched": False
        }

        self.message = ""
        self.active_input = "username"

    def update_transition(self):
        tr = self.transition
        elapsed = pygame.time.get_ticks() - tr["start"]

        total = (
            self.T_SHRINK + self.T_HOLD + self.T_EXPAND
        )

        if elapsed >= total:
            self.state = tr["target"]
            self.transition = None
            self.draw_account_screen()
            return

        self.draw_background()
        self.draw_title()

        if elapsed < self.T_SHRINK:
            p = ease(elapsed / self.T_SHRINK)
            rect = lerp_rect(self.card_full, self.card_small, p)
            content_alpha = int(255 * (1 - p))
            spinner_alpha = int(255 * max(0, (p - 0.5) * 2))

        elif elapsed < self.T_SHRINK + self.T_HOLD:
            rect = self.card_small
            content_alpha = 0
            spinner_alpha = 255

        else:
            if not tr["switched"]:
                self.state = tr["target"]
                self.username_input = ""
                self.password_input = ""
                self.message = ""
                tr["switched"] = True

            p = ease(
                (elapsed - self.T_SHRINK - self.T_HOLD)
                / self.T_EXPAND
            )
            rect = lerp_rect(self.card_small, self.card_full, p)
            content_alpha = int(255 * p)
            spinner_alpha = int(255 * (1 - p))

        self.draw_card(rect)

        if spinner_alpha > 0:
            self.draw_spinner(
                rect.centerx, rect.centery, spinner_alpha
            )

        if content_alpha > 0 and self.state in ("login", "register"):
            self.draw_form_faded(content_alpha)

        if elapsed > self.T_SHRINK + self.T_HOLD:
            self.draw_button(
                self.back_button_rect, "←  BACK",
                (27, 30, 45)
            )

    # ==================================================
    # INPUT / STATE UPDATE
    # ==================================================

    def update(self, events):
        if self.transition:
            self.update_transition()
            return None

        if self.state == "account_menu":
            for event in events:
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    if self.register_button_rect.collidepoint(event.pos):
                        self.username_input = ""
                        self.password_input = ""
                        self.start_switch("register", True)
                        return None

                    if self.login_button_rect.collidepoint(event.pos):
                        self.username_input = ""
                        self.password_input = ""
                        self.start_switch("login", True)
                        return None

            self.draw_account_menu()
            return None

        if self.state in ("login", "register"):
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        if self.active_input == "username":
                            self.username_input = self.username_input[:-1]
                        else:
                            self.password_input = self.password_input[:-1]

                    elif event.key == pygame.K_TAB:
                        self.active_input = (
                            "password" if self.active_input == "username"
                            else "username"
                        )

                    elif event.key == pygame.K_RETURN:
                        if self.state == "register":
                            self.register_player()
                        else:
                            self.login_player()
                        return None

                    elif event.unicode.isprintable():
                        if self.active_input == "username":
                            if (
                                len(self.username_input) < 20
                                and event.unicode not in "\r\n\t"
                            ):
                                self.username_input += event.unicode
                        elif len(self.password_input) < 30:
                            if event.unicode not in "\r\n\t":
                                self.password_input += event.unicode

                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    if self.username_rect.collidepoint(event.pos):
                        self.active_input = "username"

                    elif self.password_rect.collidepoint(event.pos):
                        self.active_input = "password"

                    elif self.action_button_rect.collidepoint(event.pos):
                        if self.state == "register":
                            self.register_player()
                        else:
                            self.login_player()
                        return None

                    elif self.switch_rect.collidepoint(event.pos):
                        target = (
                            "register" if self.state == "login"
                            else "login"
                        )
                        self.start_switch(target)
                        return None

                    elif self.back_button_rect.collidepoint(event.pos):
                        self.username_input = ""
                        self.password_input = ""
                        self.message = ""
                        self.state = "account_menu"
                        return None

            self.draw_account_screen()
            return None

        if self.state == "welcome":
            for event in events:
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and self.start_game_button_rect.collidepoint(event.pos)
                ):
                    return "start_game"

                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_RETURN
                ):
                    return "start_game"

            self.draw_welcome_screen()
            return None

        return None

    # ==================================================
    # TEXT / HEADER
    # ==================================================

    def draw_center_text(
        self, text, font, color, center, shadow=True
    ):
        if shadow:
            shadow_text = font.render(text, True, (0, 0, 0))
            shadow_rect = shadow_text.get_rect(
                center=(center[0] + 2, center[1] + 3)
            )
            self.screen.blit(shadow_text, shadow_rect)

        rendered = font.render(text, True, color)
        rect = rendered.get_rect(center=center)
        self.screen.blit(rendered, rect)
        return rect

    def draw_title(self):
        t = pygame.time.get_ticks() / 1000
        cx = self.screen_width // 2

        # Gold accent line
        line_width = 130 + int((math.sin(t * 1.4) + 1) * 22)
        pygame.draw.line(
            self.screen,
            (95, 70, 35),
            (cx - 120, 42),
            (cx + 120, 42),
            1
        )
        pygame.draw.line(
            self.screen,
            GOLD,
            (cx - line_width // 2, 42),
            (cx + line_width // 2, 42),
            2
        )

        self.draw_center_text(
            "CABILAN",
            self.title_font,
            GOLD_LIGHT,
            (cx, 76)
        )

        self.draw_center_text(
            "SPACE COMMAND  •  GALACTIC DEFENSE",
            self.small_font,
            MUTED,
            (cx, 111),
            False
        )

    # ==================================================
    # GLASS CARD
    # ==================================================

    def draw_card(self, rect):
        if rect.width < 4 or rect.height < 4:
            return

        surface = pygame.Surface(rect.size, pygame.SRCALPHA)

        pygame.draw.rect(
            surface,
            (12, 17, 31, 238),
            surface.get_rect(),
            border_radius=20
        )

        pygame.draw.rect(
            surface,
            (255, 255, 255, 12),
            (2, 2, max(1, rect.width - 4), 55),
            border_radius=18
        )

        pygame.draw.rect(
            surface,
            (255, 255, 255, 32),
            surface.get_rect(),
            1,
            border_radius=20
        )

        self.screen.blit(surface, rect.topleft)

        # Animated gold frame
        t = pygame.time.get_ticks() / 1000
        glow = int(155 + (math.sin(t * 2) + 1) * 45)
        gold = (glow, int(glow * 0.78), 60)

        L = min(32, rect.width // 4, rect.height // 4)
        pad = 9

        x1, y1 = rect.left + pad, rect.top + pad
        x2, y2 = rect.right - pad, rect.bottom - pad

        pygame.draw.lines(
            self.screen, gold, False,
            [(x1, y1 + L), (x1, y1), (x1 + L, y1)], 2
        )
        pygame.draw.lines(
            self.screen, gold, False,
            [(x2 - L, y2), (x2, y2), (x2, y2 - L)], 2
        )

    def draw_spinner(self, cx, cy, alpha=255):
        t = pygame.time.get_ticks() / 1000

        for i in range(12):
            angle = t * 5 + i * math.tau / 12
            x = int(cx + math.cos(angle) * 23)
            y = int(cy + math.sin(angle) * 23)

            k = (i + 1) / 12 * (alpha / 255)
            color = (
                int(GOLD[0] * k),
                int(GOLD[1] * k),
                int(GOLD[2] * k)
            )

            pygame.draw.circle(
                self.screen, color, (x, y),
                2 + (i % 3 == 0)
            )

    # ==================================================
    # ACCOUNT MENU
    # ==================================================

    def draw_account_menu(self):
        self.draw_background()
        self.draw_title()

        self.draw_center_text(
            "COMMANDER ACCESS",
            self.heading_font,
            WHITE,
            (self.screen_width // 2, 205)
        )

        self.draw_center_text(
            "Identify yourself to enter the galaxy.",
            self.small_font,
            MUTED,
            (self.screen_width // 2, 244),
            False
        )

        self.draw_avatar(
            self.screen_width // 2, 323, 39
        )

        self.draw_button(
            self.register_button_rect,
            "CREATE ACCOUNT",
            GOLD
        )
        self.draw_button(
            self.login_button_rect,
            "SIGN IN",
            (37, 52, 79)
        )

        self.draw_center_text(
            "SECURE ACCESS  •  GALACTIC COMMAND",
            self.small_font,
            (120, 133, 153),
            (self.screen_width // 2, 510),
            False
        )

    def draw_avatar(self, cx, cy, radius):
        pygame.draw.circle(
            self.screen, (18, 25, 43),
            (cx, cy), radius + 5
        )
        pygame.draw.circle(
            self.screen, GOLD,
            (cx, cy), radius + 5, 1
        )
        pygame.draw.circle(
            self.screen, (95, 108, 127),
            (cx, cy - 10), 11
        )
        pygame.draw.ellipse(
            self.screen, (95, 108, 127),
            (cx - 20, cy + 5, 40, 27)
        )
        pygame.draw.arc(
            self.screen, GOLD_LIGHT,
            (cx - 18, cy - 29, 36, 58),
            0.3, math.pi - 0.3, 1
        )

    # ==================================================
    # LOGIN / REGISTER FORM
    # ==================================================

    def draw_account_screen(self):
        self.draw_background()
        self.draw_title()
        self.draw_card(self.card_full)
        self.draw_form_content()
        self.draw_button(
            self.back_button_rect, "←  BACK",
            (27, 30, 45)
        )

    def draw_form_content(self):
        is_login = self.state == "login"
        cx = self.screen_width // 2
        top = self.card_full.top

        heading = "WELCOME BACK" if is_login else "JOIN THE COMMAND"
        subtitle = (
            "Sign in to continue your mission."
            if is_login
            else "Create your commander account."
        )

        self.draw_center_text(
            heading, self.heading_font, GOLD_LIGHT,
            (cx, top + 43)
        )
        self.draw_center_text(
            subtitle, self.small_font, MUTED,
            (cx, top + 72), False
        )

        self.draw_input(
            self.username_rect,
            "USERNAME",
            self.username_input,
            self.active_input == "username",
            "user"
        )

        self.draw_input(
            self.password_rect,
            "PASSWORD",
            "*" * len(self.password_input),
            self.active_input == "password",
            "lock"
        )

        self.draw_button(
            self.action_button_rect,
            "SIGN IN  →" if is_login else "CREATE ACCOUNT  →",
            GOLD
        )

        if self.message:
            msg = self.small_font.render(
                self.message, True, (255, 115, 125)
            )
            max_width = self.screen_width - 30

            if msg.get_width() > max_width:
                msg = pygame.transform.smoothscale(
                    msg,
                    (max_width, msg.get_height())
                )

            self.screen.blit(
                msg,
                (
                    cx - msg.get_width() // 2,
                    top + 345
                )
            )

        question = (
            "New commander?  Create account"
            if is_login
            else "Already registered?  Sign in"
        )
        link = self.small_font.render(
            question, True, WHITE
        )
        self.screen.blit(
            link,
            (
                cx - link.get_width() // 2,
                self.switch_rect.y
            )
        )

        # Gold underline indicates the clickable switch link
        pygame.draw.line(
            self.screen, GOLD,
            (cx - 75, self.switch_rect.bottom + 1),
            (cx + 75, self.switch_rect.bottom + 1),
            1
        )

    def draw_form_faded(self, alpha):
        real_screen = self.screen
        layer = pygame.Surface(
            real_screen.get_size(), pygame.SRCALPHA
        )

        self.screen = layer
        self.draw_form_content()
        self.screen = real_screen

        layer.set_alpha(max(0, min(255, alpha)))
        real_screen.blit(layer, (0, 0))

    def draw_input(self, rect, label, value, active, icon_name):
        t = pygame.time.get_ticks() / 1000

        label_text = self.label_font.render(
            label, True, GOLD_LIGHT if active else MUTED
        )
        self.screen.blit(
            label_text, (rect.x + 2, rect.y - 23)
        )

        bg = (17, 24, 41) if active else (11, 17, 30)
        pygame.draw.rect(
            self.screen, bg, rect, border_radius=10
        )

        if active:
            pulse = int(165 + (math.sin(t * 3) + 1) * 35)
            border = (pulse, int(pulse * 0.75), 65)
        else:
            border = (57, 68, 88)

        pygame.draw.rect(
            self.screen, border, rect, 1, border_radius=10
        )

        # Simple user / lock symbol
        ix = rect.x + 19
        iy = rect.centery

        if icon_name == "user":
            pygame.draw.circle(
                self.screen, GOLD, (ix, iy - 5), 4, 1
            )
            pygame.draw.arc(
                self.screen, GOLD,
                (ix - 7, iy, 14, 12),
                0, math.pi, 1
            )
        else:
            pygame.draw.arc(
                self.screen, GOLD,
                (ix - 5, iy - 10, 10, 13),
                0, math.pi, 2
            )
            pygame.draw.rect(
                self.screen, GOLD,
                (ix - 7, iy - 2, 14, 11),
                1, border_radius=2
            )

        text = self.font.render(value, True, WHITE)
        clip = pygame.Rect(
            rect.x + 43, rect.y + 2,
            rect.width - 52, rect.height - 4
        )

        old_clip = self.screen.get_clip()
        self.screen.set_clip(clip)

        self.screen.blit(
            text,
            (
                rect.x + 43,
                rect.y + (rect.height - text.get_height()) // 2
            )
        )

        # Blinking text cursor
        if active and int(t * 2) % 2 == 0:
            cursor_x = rect.x + 44 + text.get_width() + 1
            if cursor_x < rect.right - 9:
                pygame.draw.line(
                    self.screen, GOLD,
                    (cursor_x, rect.y + 13),
                    (cursor_x, rect.bottom - 13), 2
                )

        self.screen.set_clip(old_clip)

    # ==================================================
    # BUTTONS
    # ==================================================

    def draw_button(self, rect, text, color):
        mouse = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse)

        if color == GOLD:
            fill = GOLD_LIGHT if hovered else GOLD
            text_color = (27, 22, 13)
        else:
            fill = (
                (45, 61, 88) if hovered
                else color
            )
            text_color = WHITE

        # Soft shadow
        shadow = pygame.Rect(
            rect.x, rect.y + 4,
            rect.width, rect.height
        )
        pygame.draw.rect(
            self.screen, (0, 0, 0, 100),
            shadow, border_radius=11
        )

        pygame.draw.rect(
            self.screen, fill, rect, border_radius=11
        )

        border = GOLD_LIGHT if hovered else (
            (105, 91, 62) if color == GOLD
            else (75, 95, 125)
        )

        pygame.draw.rect(
            self.screen, border, rect, 1,
            border_radius=11
        )

        label = self.button_font.render(
            text, True, text_color
        )
        self.screen.blit(
            label,
            (
                rect.centerx - label.get_width() // 2,
                rect.centery - label.get_height() // 2
            )
        )

    # ==================================================
    # WELCOME SCREEN
    # ==================================================

    def draw_welcome_screen(self):
        self.draw_background()
        self.draw_title()

        cx = self.screen_width // 2

        self.draw_card(
            pygame.Rect(cx - 235, 165, 470, 300)
        )

        self.draw_avatar(cx, 235, 29)

        self.draw_center_text(
            "ACCESS GRANTED",
            self.heading_font,
            GOLD_LIGHT,
            (cx, 300)
        )

        self.draw_center_text(
            f"Welcome, {self.username}!",
            self.font,
            WHITE,
            (cx, 342)
        )

        self.draw_center_text(
            "Your next mission is waiting, Commander.",
            self.small_font,
            MUTED,
            (cx, 375),
            False
        )

        self.draw_button(
            self.start_game_button_rect,
            "LAUNCH MISSION  →",
            GOLD
        )

        self.draw_center_text(
            "PRESS ENTER TO START",
            self.small_font,
            (120, 133, 153),
            (cx, 492),
            False
        )
