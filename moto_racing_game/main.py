import os
import random

import pygame


WIDTH, HEIGHT = 500, 700
FPS = 60

ROAD_WIDTH = 300
ROAD_LEFT = (WIDTH - ROAD_WIDTH) // 2
ROAD_RIGHT = ROAD_LEFT + ROAD_WIDTH

BG_GREEN = (20, 120, 55)
ROAD_GRAY = (45, 45, 45)
WHITE = (245, 245, 245)
YELLOW = (255, 220, 80)
RED = (220, 50, 47)
ORANGE = (255, 145, 0)
BLACK = (15, 15, 15)


def asset_path(name):
    return os.path.join(os.path.dirname(__file__), "assets", name)


def load_scaled_image(path, size, alpha=True):
    if not os.path.exists(path):
        return None

    img = pygame.image.load(path)
    img = img.convert_alpha() if alpha else img.convert()
    return pygame.transform.smoothscale(img, size)


def tile_vertical(screen, image, offset_y):
    h = image.get_height()
    y = -h + (offset_y % h)

    while y < HEIGHT:
        screen.blit(image, (0, y))
        y += h


class PlayerBike:
    def __init__(self):
        self.speed = 6
        self.image = self._load_bike_image()
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 25))

    def _load_bike_image(self):
        img = load_scaled_image(asset_path("bike.png"), (56, 92), alpha=True)
        if img is not None:
            return img

        surf = pygame.Surface((56, 92), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (30, 30, 30), (6, 66, 18, 18))
        pygame.draw.ellipse(surf, (30, 30, 30), (32, 66, 18, 18))
        pygame.draw.rect(surf, (40, 130, 240), (16, 18, 24, 52), border_radius=6)
        pygame.draw.rect(surf, (180, 220, 255), (18, 24, 20, 14), border_radius=4)
        pygame.draw.rect(surf, (220, 20, 60), (20, 8, 16, 10), border_radius=4)
        return surf

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        if self.rect.left < ROAD_LEFT + 8:
            self.rect.left = ROAD_LEFT + 8
        if self.rect.right > ROAD_RIGHT - 8:
            self.rect.right = ROAD_RIGHT - 8

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class EnemyCar:
    def __init__(self, x, speed, image):
        self.width, self.height = 56, 94
        self.speed = speed
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, -self.height))

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Mini Moto Racing")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("Arial", 30, bold=True)
        self.big_font = pygame.font.SysFont("Arial", 56, bold=True)
        self.menu_font = pygame.font.SysFont("Arial", 40, bold=True)

        self.running = True
        self.state = "menu"
        self.game_over = False

        self.player = PlayerBike()
        self.enemies = []

        self.score = 0
        self.base_enemy_speed = 4
        self.spawn_timer = 0
        self.base_spawn_interval = 75
        self.lane_offset = 0
        self.bg_offset = 0

        self.road_texture = load_scaled_image(asset_path("road_texture.png"), (ROAD_WIDTH, HEIGHT), alpha=False)
        self.grass_texture = load_scaled_image(asset_path("grass_texture.png"), (WIDTH, HEIGHT), alpha=False)
        self.menu_bg = load_scaled_image(asset_path("menu_bg.png"), (WIDTH, HEIGHT), alpha=False)
        self.enemy_sprites = self._load_enemy_sprites()

        self.start_button = pygame.Rect(WIDTH // 2 - 90, HEIGHT // 2 + 40, 180, 52)
        self.quit_button = pygame.Rect(WIDTH // 2 - 90, HEIGHT // 2 + 108, 180, 52)

    def _load_enemy_sprites(self):
        images = []
        for i in range(1, 5):
            img = load_scaled_image(asset_path(f"enemy_{i}.png"), (56, 94), alpha=True)
            if img is not None:
                images.append(img)

        if images:
            return images

        fallback = pygame.Surface((56, 94), pygame.SRCALPHA)
        pygame.draw.rect(fallback, RED, (0, 0, 56, 94), border_radius=10)
        pygame.draw.rect(fallback, (170, 210, 255), (8, 12, 40, 22), border_radius=5)
        pygame.draw.circle(fallback, (20, 20, 20), (12, 86), 7)
        pygame.draw.circle(fallback, (20, 20, 20), (44, 86), 7)
        return [fallback]

    def spawn_enemy(self):
        x_min = ROAD_LEFT + 10
        x_max = ROAD_RIGHT - 10 - 56
        x = random.randint(x_min, x_max)
        speed = self.base_enemy_speed + self.score // 900
        sprite = random.choice(self.enemy_sprites)
        self.enemies.append(EnemyCar(x, speed, sprite))

    def update_lane_lines(self):
        lane_speed = self.base_enemy_speed + self.score // 1200
        self.lane_offset = (self.lane_offset + lane_speed) % 60

    def update(self):
        if self.state != "playing":
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys)

        self.spawn_timer += 1
        spawn_interval = max(30, self.base_spawn_interval - self.score // 600)
        if self.spawn_timer >= spawn_interval:
            self.spawn_enemy()
            self.spawn_timer = 0

        for enemy in self.enemies:
            enemy.update()

        self.enemies = [e for e in self.enemies if e.rect.top < HEIGHT + 20]

        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.game_over = True
                self.state = "game_over"
                break

        self.score += 1
        self.update_lane_lines()
        self.bg_offset += self.base_enemy_speed + self.score // 1200

    def draw_road(self):
        if self.grass_texture is not None:
            tile_vertical(self.screen, self.grass_texture, self.bg_offset)
        else:
            self.screen.fill(BG_GREEN)

        if self.road_texture is not None:
            road_segment = pygame.transform.smoothscale(self.road_texture, (ROAD_WIDTH, HEIGHT))
            self.screen.blit(road_segment, (ROAD_LEFT, 0))
        else:
            pygame.draw.rect(self.screen, ROAD_GRAY, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))
            pygame.draw.line(self.screen, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 4)
            pygame.draw.line(self.screen, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)

        y = -60 + self.lane_offset
        while y < HEIGHT:
            pygame.draw.rect(self.screen, YELLOW, (WIDTH // 2 - 4, y, 8, 36), border_radius=3)
            y += 60

    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (16, 14))

    def draw_menu(self):
        if self.menu_bg is not None:
            self.screen.blit(self.menu_bg, (0, 0))
        else:
            self.screen.fill(BLACK)

        title = self.big_font.render("MOTO RACING", True, ORANGE)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        self.screen.blit(title, title_rect)

        pygame.draw.rect(self.screen, ORANGE, self.start_button, border_radius=12)
        pygame.draw.rect(self.screen, ORANGE, self.quit_button, border_radius=12)

        start_label = self.menu_font.render("START", True, BLACK)
        quit_label = self.menu_font.render("QUIT", True, BLACK)
        self.screen.blit(start_label, start_label.get_rect(center=self.start_button.center))
        self.screen.blit(quit_label, quit_label.get_rect(center=self.quit_button.center))

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        go_text = self.big_font.render("GAME OVER", True, WHITE)
        go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        self.screen.blit(go_text, go_rect)

        final_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        final_rect = final_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        self.screen.blit(final_text, final_rect)

        hint_text = self.font.render("Press R to restart | ESC to quit", True, WHITE)
        hint_rect = hint_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70))
        self.screen.blit(hint_text, hint_rect)

    def restart(self):
        self.player = PlayerBike()
        self.enemies = []
        self.score = 0
        self.spawn_timer = 0
        self.game_over = False
        self.lane_offset = 0
        self.bg_offset = 0
        self.state = "playing"

    def handle_menu_click(self, pos):
        if self.start_button.collidepoint(pos):
            self.restart()
        elif self.quit_button.collidepoint(pos):
            self.running = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif self.state == "menu" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.restart()
                elif self.state == "game_over" and event.key == pygame.K_r:
                    self.restart()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == "menu":
                    self.handle_menu_click(event.pos)

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        else:
            self.draw_road()

            for enemy in self.enemies:
                enemy.draw(self.screen)

            self.player.draw(self.screen)
            self.draw_ui()

            if self.state == "game_over":
                self.draw_game_over()

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    Game().run()