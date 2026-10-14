import pygame


class Player:

    def __init__(self, screen_width, screen_height):

        self.width = 200
        self.height = 100
        self.speed = 10

        self.image = pygame.image.load(
            "assets/images/jet.png"
        ).convert_alpha()

        self.image = pygame.transform.scale(
            self.image,
            (self.width, self.height)
        )

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height - self.height - 20

        self.is_blinking = False
        self.blink_timer = 0
        self.visible = True

    # MOVE LEFT
    def move_left(self):
        if not self.is_blinking:
            self.x -= self.speed
            self.keep_inside_screen()

    # MOVE RIGHT
    def move_right(self):
        if not self.is_blinking:
            self.x += self.speed
            self.keep_inside_screen()

    # MOVE UP
    def move_up(self):
        if not self.is_blinking:
            self.y -= self.speed
            self.keep_inside_screen()

    # MOVE DOWN
    def move_down(self):
        if not self.is_blinking:
            self.y += self.speed
            self.keep_inside_screen()

    # KEEP PLAYER INSIDE SCREEN
    def keep_inside_screen(self):

        self.x = max(
            0,
            min(self.x, self.screen_width - self.width)
        )

        self.y = max(
            0,
            min(self.y, self.screen_height - self.height)
        )

    # PLAYER COLLISION RECTANGLE
    def get_rect(self):
        return pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )

    # BLINK EFFECT
    def update_blink(self):

        if self.is_blinking:
            self.blink_timer += 1

            if self.blink_timer % 10 == 0:
                self.visible = not self.visible
        else:
            self.visible = True

    # DRAW PLAYER
    def draw(self, screen):

        if self.visible:
            screen.blit(
                self.image,
                (self.x, self.y)
            )