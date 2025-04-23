import pygame
import random
import sys

# Constants for board size and cell size
BOARD_SIZE = 25
CELL_SIZE = 25  
WIDTH, HEIGHT = BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE
FPS = 10

# Define Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)  # Active fireball (fatal) color
BLACK = (0, 0, 0)

class Board:
    def __init__(self, surface):
        self.surface = surface

    def draw_grid(self):
        self.surface.fill(WHITE)
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.surface, GRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.surface, GRAY, (0, y), (WIDTH, y))

class Player:
    def __init__(self, position=(0, 0)):
        self.position = position

    def move(self, dx, dy):
        x, y = self.position
        new_x = x + dx
        new_y = y + dy
        if 0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE:
            self.position = (new_x, new_y)

    def draw(self, surface):
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, BLUE, rect)

class Dragon:
    def __init__(self, position=(BOARD_SIZE-1, BOARD_SIZE-1), hp=10):
        self.position = position
        self.hp = hp
        self.fireball_cooldown = 0  # Delay timer for shooting

    def take_damage(self):
        self.hp -= 1
        print(f"Dragon takes damage! HP is now {self.hp}")

    def randomize_position(self):
        self.position = (random.randint(0, BOARD_SIZE - 1),
                         random.randint(0, BOARD_SIZE - 1))
        print("Dragon teleports to a new position!")

    def shoot_fireballs(self):
        """Shoots straight-line fireballs but has a cooldown."""
        if 5 <= self.hp < 8:
            if self.fireball_cooldown == 0:
                self.fireball_cooldown = 5  # Set delay before next shot
                return [Fireball(self.position, direction) for direction in ["up", "down", "left", "right"]]
        return []

    def spawn_fireballs(self):
        """Spawns random fireballs when HP < 5."""
        if self.hp < 5:
            return [FireballRandom() for _ in range(6 - self.hp)]
        return []

    def update_cooldown(self):
        if self.fireball_cooldown > 0:
            self.fireball_cooldown -= 1

    def draw(self, surface, font):
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, ORANGE, rect)
        hp_text = font.render(str(self.hp), True, WHITE)
        text_rect = hp_text.get_rect(center=rect.center)
        surface.blit(hp_text, text_rect)

class Fireball:
    """Moving fireball (straight-line)."""
    def __init__(self, position, direction):
        self.position = position
        self.direction = direction

    def move(self):
        x, y = self.position
        if self.direction == "up":
            y -= 1
        elif self.direction == "down":
            y += 1
        elif self.direction == "left":
            x -= 1
        elif self.direction == "right":
            x += 1

        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            self.position = (x, y)
            return True
        return False

    def draw(self, surface):
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, ORANGE, rect)

class FireballRandom:
    """Randomly appearing fireball."""
    def __init__(self):
        self.position = (random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1))

    def draw(self, surface):
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, ORANGE, rect)

class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Dragon Game - Fireball Delay")
        self.clock = pygame.time.Clock()
        self.board = Board(self.surface)
        self.font = pygame.font.SysFont(None, 30)
        self.player = Player(position=(0, 0))
        self.dragon = Dragon(position=(random.randint(0, BOARD_SIZE - 1),
                                        random.randint(0, BOARD_SIZE - 1)))
        self.fireballs = []
        self.fireball_randoms = []
        self.game_over = False
        self.win = False

    def handle_events(self):
        dx, dy = 0, 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                elif event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1
        if dx or dy:
            self.player.move(dx, dy)

    def update_fireballs(self):
        new_fireballs = []
        for fireball in self.fireballs:
            if fireball.move():
                new_fireballs.append(fireball)

            if fireball.position == self.player.position:
                self.game_over = True
                self.win = False
                print("Player hit by fireball!")

        self.fireballs = new_fireballs

        for fireball in self.fireball_randoms:
            if fireball.position == self.player.position:
                self.game_over = True
                self.win = False
                print("Player hit by random fireball!")

    def update_game(self):
        if self.player.position == self.dragon.position:
            self.dragon.take_damage()
            self.dragon.randomize_position()
            if self.dragon.hp <= 0:
                self.game_over = True
                self.win = True

        self.dragon.update_cooldown()

        self.fireballs += self.dragon.shoot_fireballs()
        self.fireball_randoms += self.dragon.spawn_fireballs()

        self.update_fireballs()

    def draw_game(self):
        self.board.draw_grid()
        self.player.draw(self.surface)
        if self.dragon.hp > 0:
            self.dragon.draw(self.surface, self.font)
        for fireball in self.fireballs:
            fireball.draw(self.surface)
        for fireball in self.fireball_randoms:
            fireball.draw(self.surface)
        pygame.display.flip()

    def display_message(self, message):
        text = self.font.render(message, True, BLACK)
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.surface.blit(text, rect)
        pygame.display.flip()
        pygame.time.wait(2000)

    def run(self):
        while True:
            self.clock.tick(FPS)
            if not self.game_over:
                self.handle_events()
                self.update_game()
                self.draw_game()
            else:
                if self.win:
                    self.display_message("You Win!")
                else:
                    self.display_message("Game Over!")
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    Game().run()
