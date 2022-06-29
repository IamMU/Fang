import time

import pygame
import random
import threading


class Player(pygame.sprite.Sprite):
    def __init__(self, role, start_pos, color, window_dimensions, username, is_player):
        super().__init__()

        self.username = username

        self.role = role
        self.color = color

        self.is_player = is_player

        self.width = 20
        self.height = 20

        self.allow_dash = True
        self.dash_renew_timer = 1

        self.font_smol = pygame.font.SysFont("monospace", 16)
        self.font_normal = pygame.font.SysFont("monospace", 26)
        self.font_big = pygame.font.SysFont("monospace", 32)

        if self.is_player:
            self.username_text = self.font_smol.render("You", 1, "black")
        elif not self.is_player and not self.role.lower() == "catcher":
            self.username_text = self.font_smol.render(username, 1, "black")
        elif not self.is_player and self.role.lower() == "catcher":
            self.username_text = self.font_smol.render("Catcher", 1, "black")

        if is_player:
            self.dash_available_text = self.font_big.render("DASH!", 1, (0, 0, 255))

        if is_player:
            if self.role.lower() == "catcher":
                self.role_text = self.font_normal.render("Catcher", 1, (255, 0, 0))
            elif self.role.lower() == "runner":
                self.role_text = self.font_normal.render("Runner", 1, (0, 255, 0))

        self.caught = False

        self.window_dimensions = window_dimensions

        self.x = start_pos[0]
        self.y = start_pos[1]

        self.x_dir = 0
        self.y_dir = 0

        self.dash_distance = 140

        # Setting surface and rect
        if role.lower() == "catcher":
            self.speed = 4
            # Make catcher square

            self.surface = pygame.Surface((self.width, self.height))
            self.surface.fill(self.color)

            self.rect = self.surface.get_rect(topleft=(self.x, self.y))
        elif role.lower() == "runner":
            self.speed = 8
            # TODO: Make runner circle

            self.surface = pygame.Surface((self.width, self.height))
            self.surface.fill(self.color)

            self.rect = self.surface.get_rect(topleft=(self.x, self.y))

    def draw(self, surface):
        if self.caught:
            self.surface.fill((255, 0, 0))

        surface.blit(self.surface, self.rect)

    def update(self, surface):
        if self.is_player:
            if self.allow_dash and self.role.lower() == "runner":
                surface.blit(self.dash_available_text, (self.window_dimensions[0]/2 - self.dash_available_text.get_width()/2, 0))

            surface.blit(self.role_text, (10, 10))

        surface.blit(self.username_text, (self.rect.topleft[0] - self.username_text.get_width()/6, self.rect.topleft[1] - self.username_text.get_height()))

        if not self.caught:
            self.movement()

        self.draw(surface)

    def renew_dash(self, t):
        time.sleep(t)

        self.allow_dash = True

    def get_pos(self):
        return self.rect.topleft

    def dash(self):
        if self.window_dimensions[0] * 0.1 <= self.rect.x <= self.window_dimensions[0] * (1 - 0.1) and self.window_dimensions[1] * 0.1 <= self.rect.y <= self.window_dimensions[1] * (1 - 0.1):
            # print("Dash")

            # up_down = random.randint(0, 100)
            #
            # if up_down % 2 == 0:
            random_pos = (random.randint(self.rect.x + 30, self.rect.x + self.dash_distance + 30), random.randint(self.rect.y, self.rect.y + self.dash_distance))

            self.rect.x = random_pos[0]
            self.rect.y = random_pos[1]

            # print(f"Dashed to {random_pos}")
        else:
            # print("Dash not allowed!")
            pass

    def handle_catcher_collisions(self, catcher):
        # if self.role.lower() == "runner":
        if self.rect.colliderect(catcher.rect):
            # print("You collided with the catcher!")
            self.caught = True

        return self.caught

    def movement(self):
        if self.is_player:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_w]:
                # print("Up")
                self.y_dir = -1
                print(self.rect.y)
            elif keys[pygame.K_s]:
                # print("Down")
                self.y_dir = 1
                print(self.rect.y)
            else:
                self.y_dir = 0

            if keys[pygame.K_a]:
                # print("Left")
                self.x_dir = -1
            elif keys[pygame.K_d]:
                # print("Right")
                self.x_dir = 1
            else:
                self.x_dir = 0

            if self.role.lower() == "runner":
                if keys[pygame.K_SPACE]:
                    if self.allow_dash:
                        self.dash()
                        self.allow_dash = False

                        renew_dash_thread = threading.Thread(target=self.renew_dash, args=(self.dash_renew_timer, ))
                        renew_dash_thread.start()

            # Moving the player
            if self.x_dir > 0:
                if not self.rect.x + self.x_dir * self.speed + self.surface.get_width() >= self.window_dimensions[0]:
                    # print("Allow right")
                    self.rect.x += self.x_dir * self.speed
            elif self.x_dir < 0:
                if self.rect.x - self.x_dir * self.speed > 0:
                    # print("Allow left")
                    self.rect.x += self.x_dir * self.speed

            if self.y_dir > 0:
                if not self.rect.y + self.y_dir * self.speed + self.surface.get_width() >= self.window_dimensions[1]:
                    # print("Allow right")
                    self.rect.y += self.y_dir * self.speed
            elif self.y_dir < 0:
                if self.rect.y - self.y_dir * self.speed > 0:
                    # print("Allow left")
                    self.rect.y += self.y_dir * self.speed


if __name__ == "__main__":
    pygame.init()

    window = pygame.display.set_mode((600, 600))

    player = Player("catcher", (100, 200), "#00FF00", (600, 600), "MU", True)

    catcher = Player("runner", (400, 40), "#000000", (600, 600), "Dude", False)

    runners = [
        Player("runner", (150, 200), "#FFFF00", (600, 600), "TU", False),
        Player("runner", (100, 100), "#00FFFF", (600, 600), "DU", False),
        Player("runner", (100, 400), "#0A0DDD", (600, 600), "ZU", False)
    ]

    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        window.fill((255, 255, 255))

        player.update(window)
        # player.handle_catcher_collisions(catcher)
        # print(f"POSITION: {player.get_pos()}")

        for runner in runners:
            runner.update(window)
            runner.handle_catcher_collisions(player)

        pygame.display.update()

    pygame.quit()
