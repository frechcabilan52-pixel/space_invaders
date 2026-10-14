import pygame


class MobileButtons:

    def __init__(self):

        # MOVEMENT BUTTONS
        self.left = pygame.Rect(20, 520, 70, 55)
        self.right = pygame.Rect(100, 520, 70, 55)
        self.up = pygame.Rect(60, 450, 70, 55)
        self.down = pygame.Rect(60, 585, 70, 55)

        # FIRE BUTTON
        self.fire = pygame.Rect(680, 520, 100, 60)

        # FONTS
        self.arrow_font = pygame.font.SysFont(
            "Arial", 38, bold=True
        )
        self.fire_font = pygame.font.SysFont(
            "Arial", 26, bold=True
        )

    def draw(
        self,
        screen,
        left_enabled=True,
        right_enabled=True,
        fire_enabled=True,
        up_enabled=True,
        down_enabled=True
    ):

        buttons = [
            (self.left, "←", left_enabled, (20, 55, 85), (80, 220, 235)),
            (self.right, "→", right_enabled, (20, 55, 85), (80, 220, 235)),
            (self.up, "↑", up_enabled, (20, 55, 85), (80, 220, 235)),
            (self.down, "↓", down_enabled, (20, 55, 85), (80, 220, 235)),
            (self.fire, "FIRE", fire_enabled, (150, 35, 55), (255, 110, 120)),
        ]

        for rect, label, enabled, bg_color, border_color in buttons:

            if not enabled:
                continue

            pygame.draw.rect(
                screen, bg_color, rect, border_radius=12
            )
            pygame.draw.rect(
                screen, border_color, rect, 2, border_radius=12
            )

            font = (
                self.fire_font
                if label == "FIRE"
                else self.arrow_font
            )

            color = (
                (255, 240, 240)
                if label == "FIRE"
                else (220, 240, 250)
            )

            text = font.render(label, True, color)

            screen.blit(
                text,
                (
                    rect.centerx - text.get_width() // 2,
                    rect.centery - text.get_height() // 2
                )
            )

    def handle_mouse(
        self,
        player,
        events,
        left_enabled=True,
        right_enabled=True,
        fire_enabled=True,
        up_enabled=True,
        down_enabled=True
    ):

        mouse_pressed = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        if mouse_pressed[0]:

            if left_enabled and self.left.collidepoint(mouse_pos):
                player.move_left()

            if right_enabled and self.right.collidepoint(mouse_pos):
                player.move_right()

            if up_enabled and self.up.collidepoint(mouse_pos):
                if hasattr(player, "move_up"):
                    player.move_up()

            if down_enabled and self.down.collidepoint(mouse_pos):
                if hasattr(player, "move_down"):
                    player.move_down()

        for event in events:

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                if fire_enabled and self.fire.collidepoint(event.pos):
                    return True

        return False