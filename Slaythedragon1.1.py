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
RED = (255,0,0)

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

    def draw(self, surface, color=BLUE):
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, color, rect)

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
        pygame.draw.rect(surface, RED, rect)
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
    """Randomly appearing fireball with a limited lifetime."""
    def __init__(self):
        self.position = (random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1))
        self.lifetime = random.randint(10, 30)  # Fireball lasts 10-30 frames

    def update(self):
        self.lifetime -= 1
        return self.lifetime > 0  # Returns True if still alive

    def draw(self, surface):
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, ORANGE, rect)
class PowerUp:
    def __init__(self):
        self.position = (random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1))

    def draw(self, surface):
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, (0, 255, 0), rect)  # Green color




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
        self.final_time = []
        self.fireballs = []
        self.fireball_randoms = []
        self.game_over = False
        self.win = False
        self.start_time = pygame.time.get_ticks()  # record the starting time

        self.timer_running = True  # Timer is running at the start
        self.move_count = 0
        self.powerups_collected = 0

  
     
       
        self.powerup = None
        self.invincible = False
        self.invincible_timer = 0
        self.normal_fps = FPS
        self.fast_fps = 20
        self.score = 5000
        self.powerup_spawn_time = pygame.time.get_ticks()  # track last spawn time

        self.show_intro = True
    
    def introduction_screen(self):
        self.surface.fill(WHITE)
        title_text = self.font.render("Slay the Dragon!", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
        self.surface.blit(title_text, title_rect)

        instructions = [
            "Oh No! The dragon have been escaping from the zoo!",
            "Help the knight punish that bad bad dragon!",
            "Use Arrow Keys to move the Knight (blue square).",
            "Touch the dragon (Red square) to deal damage.",
            "Avoid fireballs (orange squares) — instant death.",
            "Collect plant power-ups (green squares) for 5 seconds of invincibility.",
            "During invincibility, Knight will going full rainbow.",
            "Win by reducing dragon's HP to 0!",
            "Slay the Dragon!",
            "",
            "Click 'Start Game' to begin."
        ]

        for i, line in enumerate(instructions):
            line_text = self.font.render(line, True, BLACK)
            line_rect = line_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100 + i * 30))
            self.surface.blit(line_text, line_rect)

        # Draw Start Button
        self.start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 220, 200, 50)
        pygame.draw.rect(self.surface, (0, 200, 0), self.start_button)
        start_text = self.font.render("Start Game", True, WHITE)
        start_rect = start_text.get_rect(center=self.start_button.center)
        self.surface.blit(start_text, start_rect)

        pygame.display.flip()

    
    def update_fireballs(self):
        new_fireballs = []
        for fireball in self.fireballs:
            if fireball.move():
                new_fireballs.append(fireball)
            if fireball.position == self.player.position and not self.invincible:
                self.game_over = True
                self.win = False
                print("Player hit by fireball!")

        self.fireballs = new_fireballs

        # Update random fireballs
        new_randoms = []
        for fireball in self.fireball_randoms:
            if fireball.position == self.player.position and not self.invincible:
                self.game_over = True
                self.win = False
                print("Player hit by random fireball!")
            elif fireball.update():
                new_randoms.append(fireball)

        self.fireball_randoms = new_randoms



    def handle_events(self):
        dx, dy = 0, 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if self.game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if (WIDTH // 2 - 100 <= mouse_x <= WIDTH // 2 + 100 and
                        HEIGHT // 2 + 80 <= mouse_y <= HEIGHT // 2 + 130):
                        self.restart_game()
                        self.game_over = False  # <-- ADD THIS LINE
                        self.final_time.clear() # <-- CLEAR previous final_time
                        return  # Exit early to avoid extra input handling

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    dy = -1
                    self.move_count += 1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                    self.move_count += 1
                elif event.key == pygame.K_LEFT:
                    dx = -1
                    self.move_count += 1
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                    self.move_count += 1

        if dx or dy:
            self.player.move(dx, dy)
    
    def handle_gameover_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if (WIDTH // 2 - 100 <= mouse_x <= WIDTH // 2 + 100 and
                    HEIGHT // 2 + 80 <= mouse_y <= HEIGHT // 2 + 130):
                    self.restart_game()



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

        # Check power-up pickup
        if self.powerup and self.player.position == self.powerup.position:
            print("Power-up collected!")
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()  # current time in ms
            self.clock.tick(self.fast_fps)  # temporarily faster FPS
            self.score = max(0, self.score - 500)
            self.powerup = None
            self.powerups_collected += 1
        # Handle invincibility duration
        if self.invincible:
            if pygame.time.get_ticks() - self.invincible_timer >= 5000:
                self.invincible = False
                print("Invincibility ended.")
                self.clock.tick(self.normal_fps)

        # Randomly spawn a powerup (1 in 300 chance per tick)
        if not self.powerup and random.randint(1, 300) == 1:
            self.powerup = PowerUp()

        self.score -= 1  # Increase score per tick

        # Spawn a power-up every 20 seconds
        current_time = pygame.time.get_ticks()
        if not self.powerup and current_time - self.powerup_spawn_time >= 20000:
            self.powerup = PowerUp()
            self.powerup_spawn_time = current_time
            print("Power-up spawned!")



    def draw_game(self):
        self.board.draw_grid()

        # Player color logic
        if self.invincible:
            player_color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
        else:
            player_color = BLUE

        self.player.draw(self.surface, player_color)

        if self.dragon.hp > 0:
            self.dragon.draw(self.surface, self.font)
        for fireball in self.fireballs:
            fireball.draw(self.surface)
        for fireball in self.fireball_randoms:
            fireball.draw(self.surface)

        # Draw power-up if exists
        if self.powerup:
            self.powerup.draw(self.surface)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.surface.blit(score_text, (5, 5))

        # Show Invincible status
        if self.invincible:
            inv_text = self.font.render("INVINCIBLE!", True, (255, 0, 0))
            self.surface.blit(inv_text, (5, 35))

        pygame.display.flip()
        # Draw timer
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000  # in seconds
        timer_text = self.font.render(f"Time: {elapsed_time}s", True, BLACK)
        self.surface.blit(timer_text, (5, 65))



    def display_message(self, message, elapsed_time=None, score=None , powerup = None , movecount = None):
        self.surface.fill(WHITE)
        text = self.font.render(message, True, BLACK)
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
        self.surface.blit(text, rect)

        if elapsed_time is not None:
            time_text = self.font.render(f"Time Used: {elapsed_time}s", True, BLACK)
            time_rect = time_text.get_rect(center=(WIDTH // 2, HEIGHT // 2-80))
            self.surface.blit(time_text, time_rect)
        
        if powerup is not None:
            powerup_text = self.font.render(f"Power-up collected: {powerup} each", True, BLACK)
            powerup_rect = powerup_text.get_rect(center=(WIDTH // 2, HEIGHT // 2-40))
            self.surface.blit(powerup_text, powerup_rect)
        
        if score is not None:
            score_text = self.font.render(f"Score: {score}", True, BLACK)
            score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 ))
            self.surface.blit(score_text, score_rect)
        if movecount is not None:
            move_text = self.font.render(f"You moved: {movecount} time", True, BLACK)
            move_rect = move_text.get_rect(center=(WIDTH // 2, HEIGHT // 2+40))
            self.surface.blit(move_text, move_rect)

        # Draw Try Again button
        try_again_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50)
        pygame.draw.rect(self.surface, (0, 255, 0), try_again_button)
        try_again_text = self.font.render("Try Again", True, BLACK)
        self.surface.blit(try_again_text, try_again_button.move(90, 10))
        

        pygame.display.flip()




    def restart_game(self):
        self.player = Player(position=(0, 0))
        self.dragon = Dragon(position=(random.randint(0, BOARD_SIZE - 1),
                                        random.randint(0, BOARD_SIZE - 1)))
        self.fireballs = []
        self.fireball_randoms = []
        self.final_time = []
        self.start_time = pygame.time.get_ticks()
        self.game_over = False
        self.win = False
        self.powerups_collected = 0
        self.score = 5000
        self.move_count = 0
        self.show_intro = False
       
    def handle_intro_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.start_button.collidepoint(event.pos):
                    self.show_intro = False
                    #self.start_time = pygame.time.get_ticks()  # Start game timer


    def run(self):
        while True:
            self.clock.tick(FPS)
           
            if self.show_intro:
                self.handle_intro_events()
                self.introduction_screen()
            elif not self.game_over:
                self.handle_events()
                self.update_game()
                self.draw_game()
            
            else:                                
                
                y = pygame.time.get_ticks()
                self.final_time.append(y)
                
                

                final_time = (self.final_time[0] - self.start_time) // 1000
                if self.win:
                    self.display_message("You Win! The Dragon have been slained!", final_time, self.score+3000, self.powerups_collected, self.move_count)
                else:
                    self.display_message("Game Over! You let the Dragon escape", final_time, self.score, self.powerups_collected, self.move_count)

                self.handle_gameover_events()


                  
               
                    

                    # Wait for the user to click Try Again button
                   # self.game_over = True  # Stop game loop when it's over

    

if __name__ == "__main__":
    Game().run()