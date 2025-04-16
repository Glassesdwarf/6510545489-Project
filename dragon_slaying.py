"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
from gamelib import Game, GameElement
import random
import math

class DragonElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "KillTheDragon"):
        super().__init__(game)
        self.__game: "KillTheDragon" = game

    @property
    def game(self) -> "KillTheDragon":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(DragonElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "KillTheDragon"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Dragon(DragonElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "KillTheDragon", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(DragonElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "KillTheDragon",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("triangle")
        
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(DragonElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "KillTheDragon",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 < self.game.player.x < self.x + self.size/2)
            and
            (self.y - self.size/2 < self.game.player.y < self.y + self.size/2)
        )




class DemoEnemy(Enemy):
    """
    Demo enemy
    """

    def __init__(self,
                 game: "KillTheDragon",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        
    def create(self) -> None:
        
        
        
        pass

    def update(self) -> None:
        
        
        pass

    def render(self) -> None:
        
        pass

    def delete(self) -> None:
        pass

class RandomWalkEnemy(Enemy):
    def __init__(self, game: "KillTheDragon", size: int, color: str):
        super().__init__(game, size, color)
        self.__id = None
        self.__dx = random.choice([-1, 1]) * random.uniform(1, 3)
        self.__dy = random.choice([-1, 1]) * random.uniform(1, 3)
        self.x = random.randint(50, game.screen_width - 50)
        self.y = random.randint(50, game.screen_height - 50)

    def create(self):
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self):
        self.x += self.__dx
        self.y += self.__dy

        # Bounce off walls
        if self.x < 0 or self.x > self.game.screen_width:
            self.__dx *= -1
        if self.y < 0 or self.y > self.game.screen_height:
            self.__dy *= -1

        # Occasionally change direction
        if random.random() < 0.02:
            self.__dx = random.choice([-1, 1]) * random.uniform(1, 3)
            self.__dy = random.choice([-1, 1]) * random.uniform(1, 3)

        if self.hits_player():
            self.game.game_over_lose()

    def render(self):
        half = self.size / 2
        self.canvas.coords(self.__id, self.x - half, self.y - half, self.x + half, self.y + half)

    def delete(self):
        self.canvas.delete(self.__id)
class ChasingEnemy(Enemy):
    def __init__(self, game: "KillTheDragon", size: int, color: str, speed: float = 2):
        super().__init__(game, size, color)
        self.__id = None
        self.__speed = speed
        self.x = random.randint(50, game.screen_width - 50)
        self.y = random.randint(50, game.screen_height - 50)

    def create(self):
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self):
        player = self.game.player
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist > 0:
            self.x += self.__speed * dx / dist
            self.y += self.__speed * dy / dist

        if self.hits_player():
            self.game.game_over_lose()

    def render(self):
        half = self.size / 2
        self.canvas.coords(self.__id, self.x - half, self.y - half, self.x + half, self.y + half)

    def delete(self):
        self.canvas.delete(self.__id)

class FencingEnemy(Enemy):
    def __init__(self, game: "KillTheDragon", size: int, color: str, speed: float = 2):
        super().__init__(game, size, color)
        self.__id = None
        self.__speed = speed
        self.__path = self.__generate_path_around_home()
        self.__target_index = 0
        self.x, self.y = self.__path[0]
        print("FencingEnemy Path:", self.__path)

    def __generate_path_around_home(self):
        home = self.game.home
        half = home.size / 2 + 30
        cx, cy = home.x, home.y
        return [
            (cx - half, cy - half),
            (cx + half, cy - half),
            (cx + half, cy + half),
            (cx - half, cy + half)
        ]

    def create(self):
        print("FencingEnemy created")
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self):
        target = self.__path[self.__target_index]
        dx = target[0] - self.x
        dy = target[1] - self.y
        dist = math.hypot(dx, dy)

        if dist < self.__speed:
            self.x, self.y = target
            self.__target_index = (self.__target_index + 1) % len(self.__path)
        else:
            self.x += self.__speed * dx / dist
            self.y += self.__speed * dy / dist

        

        if self.hits_player():
            self.game.game_over_lose()

    def render(self):
        half = self.size / 2
        self.canvas.coords(self.__id, self.x - half, self.y - half, self.x + half, self.y + half)

    def delete(self):
        self.canvas.delete(self.__id)

class CamouflageEnemy(Enemy):
    def __init__(self, game: "KillTheDragon", size: int, color: str, speed: float = 1.5):
        super().__init__(game, size, color)
        self.__id = None
        self.__dx = random.choice([-1, 1]) * speed
        self.__dy = random.choice([-1, 1]) * speed
        self.__visible = True
        self.__tick = 0
        self.x = random.randint(50, game.screen_width - 50)
        self.y = random.randint(50, game.screen_height - 50)

    def create(self):
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self):
        # Move like a slow random walker
        self.x += self.__dx
        self.y += self.__dy

        if self.x < 0 or self.x > self.game.screen_width:
            self.__dx *= -1
        if self.y < 0 or self.y > self.game.screen_height:
            self.__dy *= -1

        # Blink every 60 frames (~2 seconds at 30fps)
        self.__tick += 1
        if self.__tick % 60 == 0:
            self.__visible = not self.__visible

        if self.hits_player():
            self.game.game_over_lose()

    def render(self):
        half = self.size / 2
        self.canvas.coords(self.__id, self.x - half, self.y - half, self.x + half, self.y + half)
        state = "normal" if self.__visible else "hidden"
        self.canvas.itemconfigure(self.__id, state=state)

    def delete(self):
        self.canvas.delete(self.__id)
class Fireball(DragonElement):
    def __init__(self, game: "KillTheDragon", x: float, y: float, dx: float, dy: float, speed: float = 10):
        super().__init__(game)
        self.__id = None
        self.x = x
        self.y = y
        self.__dx = dx
        self.__dy = dy
        self.__speed = speed

    def create(self):
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill="red")

    def update(self):
        self.x += self.__dx * self.__speed
        self.y += self.__dy * self.__speed

        # Off screen? remove it
        if (self.x < 0 or self.x > self.game.screen_width or
            self.y < 0 or self.y > self.game.screen_height):
            self.game.delete_element(self)
            return

        # Hit the player?
        player = self.game.player
        if abs(self.x - player.x) < 10 and abs(self.y - player.y) < 10:
            self.game.game_over_lose()

    def render(self):
        self.canvas.coords(self.__id, self.x - 5, self.y - 5, self.x + 5, self.y + 5)

    def delete(self):
        self.canvas.delete(self.__id)
class ShooterEnemy(Enemy):
    def __init__(self, game: "KillTheDragon", size: int, color: str, fire_delay: int = 90):
        super().__init__(game, size, color)
        self.__id = None
        self.x = random.randint(100, game.screen_width - 100)
        self.y = random.randint(100, game.screen_height - 100)
        self.__tick = 0
        self.__fire_delay = fire_delay
        

    def create(self):
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self):
        self.__tick += 1
        if self.__tick % self.__fire_delay == 0:
            self.fire()

        if self.hits_player():
            self.canvas.delete(self.__id)
            self.game.enemy_generator.create_enemy()
            self.game.enemy_generator.dragon_hp -= 1

    def fire(self):
        player = self.game.player
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0: return

        # Normalize direction
        dir_x = dx / dist
        dir_y = dy / dist

        fireball = Fireball(self.game, self.x, self.y, dir_x, dir_y)
        self.game.add_element(fireball)

    def render(self):
        half = self.size / 2
        self.canvas.coords(self.__id, self.x - half, self.y - half, self.x + half, self.y + half)

    def delete(self):
        self.canvas.delete(self.__id)


class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "KillTheDragon", level: int):
        self.__game: KillTheDragon= game
        self.__level: int = level
        self.dragon_hp = 10
        # example
        self.__game.after(100, self.create_enemy)

    @property
    def game(self) -> "KillTheDragon":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def create_enemy(self) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        
       
        
        if self.dragon_hp > 5:
            shoot_enemy = ShooterEnemy(self.__game, 20, "orange")
            shoot_enemy.x = random.randint(1,600)
            shoot_enemy.y = random.randint(1,600)
            self.game.add_element(shoot_enemy)
            
        elif self.dragon_hp > 0:
            shoot_enemy = ShooterEnemy(self.__game, 20, "orange")
            shoot_enemy.x = 300
            shoot_enemy.y = 300
            self.game.add_element(shoot_enemy)
        


class KillTheDragon(Game): # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Dragon(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height//2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")
