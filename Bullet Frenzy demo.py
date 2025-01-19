import pygame
import random
import math

# 定数定義
WIDTH = 600
HEIGHT = 800
WHITE = (255, 255, 255)
LIGHT_GRAY = (240, 240, 240)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
P1_COLOR1 = (0, 200, 200)
P1_COLOR2 = (0, 100, 255)
P2_COLOR1 = (200, 200, 0)
P2_COLOR2 = (200, 100, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
FPS = 60
PLAYER_SPEED = 5
PLAYER_BULLET_SPEED = 18
ENEMY_BULLET_SPEED = 5
INVULNERABLE_TIME = 120
MAX_LIVES = 8
ENEMY_MAX_HP = 1000
ENEMY_SPAWN_Y = 200
NUM_BULLET_PATTERNS = 3
NUM_PHASES = 2
SLOWDOWN_DISTANCE = 150
RED_BULLET_SPEED_FACTOR = 0.7
MIN_FIRE_INTERVAL = 3
MAX_FIRE_INTERVAL = 16
GRAVITY = 0.008
PLAYER_MAX_HP = 100
NUM_POLYGONS = 50
POLYGON_SIZE = 20
POLYGON_SPEED_BASE = 0.2
POLYGON_SPEED_RANDOM = 0.1
AREA_BORDER = 100
NUM_LAYERS = 3

def create_polygon_layers(width, height):
    layers = []
    for _ in range(NUM_LAYERS):
        polygons = []
        for _ in range(NUM_POLYGONS):
            num_sides = random.randint(3, 6)
            x = random.randint(-AREA_BORDER, width + AREA_BORDER)
            y = random.randint(-AREA_BORDER, height + AREA_BORDER)
            speed_x = 0
            speed_y = random.uniform(POLYGON_SPEED_BASE, POLYGON_SPEED_BASE + POLYGON_SPEED_RANDOM)
            color = (
                random.randint(200, 255),
                random.randint(200, 255),
                random.randint(200, 255)
            )
            polygons.append({
                "x": x,
                "y": y,
                "num_sides": num_sides,
                "color": color,
                "speed_x": speed_x,
                "speed_y": speed_y
            })
        layers.append(polygons)
    return layers

# ゲームオブジェクトのインターフェース
class GameObject:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, screen):
        raise NotImplementedError

    def update(self):
        pass

    def move(self):
        pass

# Ballクラス
class Ball(GameObject):
    def __init__(self, x, y, radius, color, speed_x, speed_y, ball_type, start_angle=0, rotation_speed=0.05, speed_y_modifier=0):
        super().__init__(x, y, 2 * radius, 2 * radius, color)
        self.radius = radius
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.ball_type = ball_type
        self.angle = start_angle
        self.rotation_speed = rotation_speed
        self.initial_x = x
        self.initial_y = y
        self.speed_y_modifier = speed_y_modifier
        if ball_type == 5:
            self.radius = 40

    def move(self, target_x=None):
        if self.ball_type != 4:
            self.speed_y += self.speed_y_modifier
        if self.ball_type == 1 or self.ball_type == 3:
            if target_x is not None:
                if target_x > self.x:
                    self.speed_x = PLAYER_BULLET_SPEED / 3 if self.speed_x < PLAYER_BULLET_SPEED / 3 else self.speed_x
                elif target_x < self.x:
                    self.speed_x = -PLAYER_BULLET_SPEED / 3 if self.speed_x > -PLAYER_BULLET_SPEED / 3 else self.speed_x

        self.x += self.speed_x
        self.y += self.speed_y

    def draw(self, screen):
        if self.ball_type == 1:
            inner_color = tuple(min(255, c + 80) for c in self.color)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, inner_color, (int(self.x), int(self.y)), int(self.radius * 0.4))
        elif self.ball_type == 2:
            inner_color = tuple(min(255, c + 80) for c in self.color)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, inner_color, (int(self.x), int(self.y)), int(self.radius * 0.4))
        elif self.ball_type == 3:
            inner_color = tuple(min(255, c + 80) for c in self.color)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, inner_color, (int(self.x), int(self.y)), int(self.radius * 0.4))
        elif self.ball_type == 4:
            inner_color = tuple(min(255, c + 80) for c in self.color)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, inner_color, (int(self.x), int(self.y)), int(self.radius * 0.4))
        elif self.ball_type == 5:
            inner_color = tuple(min(255, c + 80) for c in self.color)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, inner_color, (int(self.x), int(self.y)), int(self.radius * 0.4))

    def distance_to(self, x, y, width, height):
        rect_center_x = x + width / 2
        rect_center_y = y + height / 2
        distance = math.sqrt((self.x - rect_center_x) ** 2 + (self.y - rect_center_y) ** 2)
        return distance

# Playerクラス（基本クラス）
class Player(GameObject):
    def __init__(self, x, y, width, height, color1, color2, speed):
        super().__init__(x, y, width, height, color1)
        self.color1 = color1
        self.color2 = color2
        self.speed = speed
        self.balls = []
        self.frame_count = 0
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.bullet_timer = 0
        self.left_key = None
        self.right_key = None
        self.up_key = None
        self.down_key = None
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.trail = []

    def move(self, keys):
        speed_modifier = 0.5 if (pygame.key.get_mods() & pygame.KMOD_SHIFT) else 1
        if keys[self.left_key]:
            self.x = max(0, self.x - self.speed * speed_modifier)
        if keys[self.right_key]:
            self.x = min(WIDTH - self.width, self.x + self.speed * speed_modifier)
        if keys[self.up_key]:
            self.y = max(0, self.y - self.speed * speed_modifier)
        if keys[self.down_key]:
            self.y = min(HEIGHT - self.height, self.y + self.speed * speed_modifier)

    def fire_ball(self, ball_type):
        ball_x = self.x + self.width // 2
        ball_y = self.y
        speed_x = 0
        speed_y = -PLAYER_BULLET_SPEED
        ball = Ball(ball_x, ball_y, 10, self.color2, speed_x, speed_y, ball_type)
        self.balls.append(ball)

    def update_balls(self, other_player):
        self.balls = [ball for ball in self.balls if ball.y > 0]
        for ball in self.balls:
            ball.move()

        self.frame_count += 1

        fire_interval = self.calculate_fire_interval(other_player)
        self.bullet_timer += 1
        if self.bullet_timer % int(fire_interval) == 0:
            self.fire_ball(1)
            self.bullet_timer = 0

    def draw(self, screen):
        for x, y, frame in self.trail:
            alpha = max(0, 255 - frame * 20)
            trail_color = list(self.color1)
            trail_color.append(alpha)
            pygame.draw.circle(screen, trail_color, (int(x) + self.width // 2, int(y) + self.height // 2), 10)

        if self.invulnerable and self.invulnerable_timer % 20 < 10:
            pass
        else:
            pygame.draw.circle(screen, self.color1, (int(self.x) + self.width // 2, int(self.y) + self.height // 2), 20)
            pygame.draw.polygon(screen, (0, 0, 0), [
                (int(self.x + self.width / 4), int(self.y + self.height / 2)),
                (int(self.x + self.width / 2), int(self.y + self.height / 4)),
                (int(self.x + self.width * 3 / 4), int(self.y + self.height / 2))
            ])
        for ball in self.balls:
            ball.draw(screen)

        bar_width = self.width * (self.hp / self.max_hp)
        bar_height = 5
        pygame.draw.rect(screen, GREEN, (int(self.x), int(self.y - 10), int(bar_width), bar_height))

        self.trail.append((self.x, self.y, 0))
        self.trail = [(x, y, frame + 1) for x, y, frame in self.trail]
        self.trail = [item for item in self.trail if item[2] < 10]

    def hit(self):
        if not self.invulnerable:
            self.invulnerable = True
            self.invulnerable_timer = INVULNERABLE_TIME
            self.hp -= 10

    def update_invulnerable(self):
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False

    def distance_to_other(self, other_player):
        dx = self.x - other_player.x
        dy = self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def calculate_fire_interval(self, other_player):
        distance = self.distance_to_other(other_player)
        if distance > 150:
            return MIN_FIRE_INTERVAL
        else:
            return min(MAX_FIRE_INTERVAL, MIN_FIRE_INTERVAL + (MAX_FIRE_INTERVAL - MIN_FIRE_INTERVAL) * (200 - distance) / 200)

# Player1クラス（Playerクラスを継承）
class Player1(Player):
    def __init__(self, x, y, width, height, color1, color2, speed):
        super().__init__(x, y, width, height, color1, color2, speed)
        self.left_key = pygame.K_a
        self.right_key = pygame.K_d
        self.up_key = pygame.K_w
        self.down_key = pygame.K_s

# Player2クラス（Playerクラスを継承）
class Player2(Player):
    def __init__(self, x, y, width, height, color1, color2, speed):
        super().__init__(x, y, width, height, color1, color2, speed)
        self.left_key = pygame.K_k
        self.right_key = pygame.K_SEMICOLON
        self.up_key = pygame.K_o
        self.down_key = pygame.K_l

# BulletManager クラス (弾の管理と当たり判定)
class BulletManager:
    def __init__(self):
        self.balls = []

    def create_ball(self, x, y, color, speed_x, speed_y, ball_type, start_angle=0, rotation_speed=0, speed_factor=1, speed_y_modifier=0):
        ball = Ball(x, y, 10, color, speed_x * speed_factor, speed_y * speed_factor, ball_type, start_angle, rotation_speed, speed_y_modifier)
        self.balls.append(ball)

    def update_balls(self, player1, player2):
        balls_to_remove = []
        hit_player1 = False
        hit_player2 = False
        for ball in self.balls:
            if ball.ball_type == 2:
                distance = math.sqrt((ball.x - ball.initial_x) ** 2 + (ball.y - ball.initial_y) ** 2)
                if distance > SLOWDOWN_DISTANCE:
                    ball.rotation_speed *= 0.9
                ball.angle += ball.rotation_speed
                ball.speed_x = ENEMY_BULLET_SPEED * math.cos(ball.angle)
                ball.speed_y = ENEMY_BULLET_SPEED * math.sin(ball.angle)
            elif ball.ball_type == 4:
                ball.move()
            elif ball.ball_type == 5:
                ball.move()
            elif ball.ball_type != 3:
                distance = math.sqrt((ball.x - ball.initial_x) ** 2 + (ball.y - ball.initial_y) ** 2)
                if distance > SLOWDOWN_DISTANCE:
                    ball.rotation_speed *= 0.9
                ball.angle += ball.rotation_speed
                ball.speed_x = ENEMY_BULLET_SPEED * math.cos(ball.angle)
                ball.speed_y = ENEMY_BULLET_SPEED * math.sin(ball.angle)
            ball.move()

            if ball.ball_type == 1 and ball.distance_to(player1.x, player1.y, player1.width, player1.height) < 14:
                hit_player1 = True
                balls_to_remove.append(ball)
            elif ball.ball_type == 2 and ball.distance_to(player2.x, player2.y, player2.width, player2.height) < 7:
                hit_player2 = True
                balls_to_remove.append(ball)
            elif ball.ball_type == 3 and (ball.distance_to(player1.x, player1.y, player1.width, player1.height) < 7 or ball.distance_to(player2.x, player2.y, player2.width, player2.height) < 7):
                hit_player1 = True
                hit_player2 = True
                balls_to_remove.append(ball)
            elif ball.ball_type == 4 and ball.distance_to(player2.x, player2.y, player2.width, player2.height) < 7:
                hit_player2 = True
                balls_to_remove.append(ball)
            elif ball.ball_type == 5 and ball.distance_to(player1.x, player1.y, player1.width, player1.height) < 35:
                hit_player1 = True
                balls_to_remove.append(ball)
            if ball.x < -ball.radius * 9 or ball.x > WIDTH + ball.radius * 9 or ball.y < -ball.radius * 9 or ball.y > HEIGHT + ball.radius * 9:
                balls_to_remove.append(ball)

        for ball in balls_to_remove:
            if ball in self.balls:
                self.balls.remove(ball)

        return hit_player1, hit_player2

    def draw(self, screen):
        for ball in self.balls:
            ball.draw(screen)

class Enemy(GameObject):
    def __init__(self, x, y, width, height, color, speed, initial_hp=ENEMY_MAX_HP):
        super().__init__(x, y, width, height, color)
        self.speed = speed
        self.direction = 1
        self.bullet_manager = BulletManager()
        self.frame_count = 0
        self.FIRE_RATE = 20
        self.bullet_pattern = 1
        self.fire_timer = 0
        self.custom_pattern_index = 0
        self.hp = initial_hp * 1.5
        self.max_hp = initial_hp * 1.5
        self.pattern_counter = 0
        self.defeated = False
        self.phase = 0
        self.phase_data = self.create_phase_data()
        self.special_fire_count = 0
        self.move_pattern = 0
        self.move_timer = 0
        self.move_duration = 40
        self.move_wait = 0
        self.move_stage = 0
        self.target_x = x
        self.target_y = y
        self.blue_angle_offset = 0
        self.fire_angle = 0
        self.fire_interval_counter = 0
        self.blue_ball2_num = 8
        self.blue_ball2_angle_offset = 20
        self.blue_ball2_speed_factor = 0.3
        self.move_positions = []
        self.current_move_index = 0
        self.orange_ball2_num = 8
        self.is_recovering = False
        self.recovery_timer = 0
        self.recovery_duration = 120
        self.orange_fire_timer = 0
        self.animation_frame = 0

    def create_phase_data(self):
        phase_data = []
        phase_data.append({
            'bullet_pattern': [1, 2],
            'pattern_duration': 180,
            'fire_rate': 20,
            'move_pattern': [0, 1, 2, 3],
            'move_duration': 40,
            'move_wait': 60
        })
        phase_data.append({
            'bullet_pattern': [4, 5],
            'pattern_duration': 180,
            'fire_rate': 2,
            'move_pattern': [5],
            'move_duration': 60,
            'move_wait': 90
        })
        return phase_data

    def move(self):
        if not self.defeated and not self.is_recovering:
            if self.move_stage == 1:
                if self.move_pattern == 5:
                    dx = self.target_x - self.x
                    dy = self.target_y - self.y
                    distance = math.sqrt(dx ** 2 + dy ** 2)
                    if distance > self.speed:
                        self.x += dx / distance * self.speed
                        self.y += dy / distance * self.speed
                    else:
                        self.x = self.target_x
                        self.y = self.target_y

    def draw(self, screen):
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        radius = 30
            
        points = [
                (int(center_x), int(center_y + radius)),
                (int(center_x - radius * 0.95), int(center_y + radius * 0.30)),
                (int(center_x - radius * 0.6), int(center_y - radius * 0.65)),
                (int(center_x + radius * 0.6), int(center_y - radius * 0.65)),
                (int(center_x + radius * 0.95), int(center_y + radius * 0.30)),
            ]
        pygame.draw.polygon(screen, self.color, points)

        triangle_points = [
                (center_x, int(center_y + radius * 0.7)),
                (int(center_x - radius * 0.5), int(center_y)),
                (int(center_x + radius * 0.5), int(center_y))
                ]
        pygame.draw.polygon(screen, (0,0,0), triangle_points)

        if not self.defeated:
            bar_width = self.width * (self.hp / self.max_hp)
            bar_height = 5
            pygame.draw.rect(screen, GREEN, (int(self.x), int(self.y - 10), int(bar_width), bar_height))
        self.bullet_manager.draw(screen)

    def fire_ball(self, speed_factor=1):
        ball_x = self.x + self.width // 2
        ball_y = self.y + self.height // 2

        rotation_speed = random.choice([-0.05, 0.05])
        if self.phase == 0:
            if self.bullet_pattern == 1:
                num_balls = 30
                start_angle = random.uniform(0, 2 * math.pi)
                for i in range(num_balls):
                    angle = start_angle + (2 * math.pi * i / num_balls)
                    speed = ENEMY_BULLET_SPEED
                    speed_x = speed * math.cos(angle)
                    speed_y = speed * math.sin(angle)
                    self.bullet_manager.create_ball(ball_x, ball_y, P2_COLOR2, speed_x, speed_y, 1, angle, rotation_speed, speed_factor)
            elif self.bullet_pattern == 2:
                num_balls = 30
                start_angle = random.uniform(0, 2 * math.pi)
                for i in range(num_balls):
                    angle = start_angle + (2 * math.pi * i / num_balls)
                    speed = ENEMY_BULLET_SPEED
                    speed_x = speed * math.cos(angle)
                    speed_y = speed * math.sin(angle)
                    self.bullet_manager.create_ball(ball_x, ball_y, P1_COLOR2, speed_x, speed_y, 2, angle, rotation_speed, speed_factor)
        elif self.phase == 1:
            if self.bullet_pattern == 4:
                num_balls = self.blue_ball2_num
                for i in range(num_balls):
                    angle = self.fire_angle + (math.pi / 4 * i)
                    speed = ENEMY_BULLET_SPEED * self.blue_ball2_speed_factor
                    speed_x = speed * math.cos(angle)
                    speed_y = speed * math.sin(angle)
                    self.bullet_manager.create_ball(ball_x, ball_y, P1_COLOR2, speed_x, speed_y, 4, angle, 0, speed_factor)
                self.fire_angle += math.radians(self.blue_ball2_angle_offset)
            elif self.bullet_pattern == 5:
                num_balls = self.orange_ball2_num
                for i in range(num_balls):
                    base_angle = (math.pi / 4 * i)
                    angle_offset = random.uniform(-math.pi / 18, math.pi / 18)
                    angle = base_angle + angle_offset
                    speed = ENEMY_BULLET_SPEED * 0.3
                    speed_x = speed * math.cos(angle)
                    speed_y = speed * math.sin(angle)
                    self.bullet_manager.create_ball(ball_x, ball_y, P2_COLOR2, speed_x, speed_y, 5, angle, 0, speed_factor, GRAVITY)

    def update(self, player1, player2, player1_balls, player2_balls):
        if self.defeated:
            return False, False

        if self.is_recovering:
            self.recovery_timer += 1
            if self.recovery_timer < self.recovery_duration:
                self.hp = min(self.max_hp, self.hp + (self.max_hp / self.recovery_duration))
                return False, False
            else:
                self.is_recovering = False
                self.recovery_timer = 0
                return False, False

        self.fire_timer += 1
        self.move_timer += 1
        self.orange_fire_timer += 1
        self.animation_frame += 1

        if self.phase < len(self.phase_data):
            current_phase = self.phase_data[self.phase]
            fire_rate = current_phase['fire_rate']

            if self.move_stage == 0 and self.move_timer > self.move_wait:
                self.move_pattern = random.choice(current_phase['move_pattern'])
                self.move_duration = current_phase['move_duration']
                self.move_wait = current_phase['move_wait']
                self.move_stage = 1
                self.move_timer = 0

                if self.move_pattern == 5:
                    if not self.move_positions:
                        self.move_positions = [
                            (WIDTH // 4, ENEMY_SPAWN_Y),
                            (WIDTH // 2, ENEMY_SPAWN_Y),
                            (WIDTH * 3 // 4, ENEMY_SPAWN_Y)
                        ]
                    self.current_move_index = random.randint(0, len(self.move_positions) - 1)
                    self.target_x = self.move_positions[self.current_move_index][0]
                    self.target_y = self.move_positions[self.current_move_index][1]
            elif self.move_stage == 1 and self.move_timer > self.move_duration:
                self.move_stage = 2
                self.move_timer = 0
            elif self.move_stage == 2:
                self.move_stage = 0

        if self.move_stage == 0:
            if self.phase == 0:
                self.fire_interval_counter += 1
                if self.fire_interval_counter % int(fire_rate) == 0:
                    self.special_fire_count += 1
                    self.bullet_pattern = random.choice([1, 2])
                    self.fire_ball()
                    self.fire_interval_counter = 0
            elif self.phase == 1:
                self.bullet_pattern = 4
                self.fire_ball()
                if self.orange_fire_timer >= 60:
                    self.bullet_pattern = 5
                    self.fire_ball()
                    self.orange_fire_timer = 0

        if self.phase == 0 and self.hp <= 0:
            self.phase = 1
            self.is_recovering = True
            self.frame_count = 0
            self.bullet_manager.balls = []
            self.fire_interval_counter = 0

        hit_player1, hit_player2 = self.bullet_manager.update_balls(player1, player2)

        if not self.is_recovering:
            player1_balls_to_remove = []
            for ball in player1_balls:
                if ball.distance_to(self.x, self.y, self.width, self.height) < 20:
                    self.hp -= 10
                    player1_balls_to_remove.append(ball)
            for ball in player1_balls_to_remove:
                if ball in player1_balls:
                    player1_balls.remove(ball)

            player2_balls_to_remove = []
            for ball in player2_balls:
                if ball.distance_to(self.x, self.y, self.width, self.height) < 20:
                    self.hp -= 10
                    player2_balls_to_remove.append(ball)
            for ball in player2_balls_to_remove:
                if ball in player2_balls:
                    player2_balls.remove(ball)

        self.frame_count += 1

        if self.hp <= 0:
            if self.phase < len(self.phase_data) - 1:
                self.phase += 1
                self.is_recovering = True
                self.frame_count = 0
                self.bullet_manager.balls = []
            else:
                self.defeated = True
                self.bullet_manager.balls = []
                return False, False

        return hit_player1, hit_player2

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bullet Frenzy demo")

bg_layers = create_polygon_layers(WIDTH, HEIGHT)

font = pygame.font.Font(None, 30)

enemy = Enemy(WIDTH // 2 - 50, ENEMY_SPAWN_Y, 50, 50, RED, 3)

balls = []
FIRE_RATE = 3

player1 = Player1(WIDTH // 2 - 75, HEIGHT - 100, 50, 50, P1_COLOR1, P1_COLOR2, PLAYER_SPEED)
player2 = Player2(WIDTH // 2 + 25, HEIGHT - 100, 50, 50, P2_COLOR1, P2_COLOR2, PLAYER_SPEED)

lives = MAX_LIVES

frame_count = 0
running = True
clock = pygame.time.Clock()
game_over = False
game_clear = False
game_state = "start"

def reset_game():
    global lives, enemy, game_over, game_clear, bg_layers, game_state
    lives = MAX_LIVES
    enemy = Enemy(WIDTH // 2 - 50, ENEMY_SPAWN_Y, 50, 50, RED, 3)

    player1.x = WIDTH // 2 - 75
    player1.y = HEIGHT - 100
    player1.balls = []
    player2.x = WIDTH // 2 + 25
    player2.y = HEIGHT - 100
    player2.balls = []
    bg_layers = create_polygon_layers(WIDTH, HEIGHT)
    game_over = False
    game_clear = False
    game_state = "start"

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state == "start":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_state = "game"
        elif event.type == pygame.KEYDOWN and (game_over or game_clear):
            if event.key == pygame.K_r:
                reset_game()

    if game_state == "start":
        screen.fill(LIGHT_GRAY)
        title_text = font.render("Bullet Frenzy demo", True, BLACK)
        text_rect = title_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 100))
        screen.blit(title_text, text_rect)

        start_text = font.render("Press SPACE to Start", True, BLACK)
        start_rect = start_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))

        if pygame.time.get_ticks() % 1000 < 500:
            screen.blit(start_text, start_rect)

        controls_text = font.render("Player1: A/D/W/S & SPACE", True, BLACK)
        controls_text2 = font.render("Player2: K/;/O/L & ENTER", True, BLACK)
        controls_rect = controls_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 150))
        controls_rect2 = controls_text2.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 180))
        screen.blit(controls_text, controls_rect)
        screen.blit(controls_text2, controls_rect2)

        description_text = font.render("Avoid the balls of different colors.", True, BLACK)
        description_rect = description_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 220))
        screen.blit(description_text, description_rect)
        description_text = font.render("Getting too close reduces your power.", True, BLACK)
        description_rect = description_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 260))
        screen.blit(description_text, description_rect)

        angle = pygame.time.get_ticks() / 1000 * 3
        radius = 40
        for i in range(6):
            x = int(WIDTH / 2 + math.cos(angle + 2 * math.pi * i / 6) * radius)
            y = int(HEIGHT / 2 - 100 + math.sin(angle + 2 * math.pi * i / 6) * radius)
            pygame.draw.circle(screen, BLACK, (x, y), 5)

        for i in range(4):
            x = int(WIDTH / 2 + math.cos(angle - 2 * math.pi * i / 4) * radius * 0.5)
            y = int(HEIGHT / 2 + 50 + math.sin(angle - 2 * math.pi * i / 4) * radius * 0.5)
            pygame.draw.polygon(screen, (50, 50, 50), [(x, y - 5), (x - 5, y + 5), (x + 5, y + 5)])

    elif game_state == "game" and not game_over and not game_clear:
        screen.fill(LIGHT_GRAY)
        for layer in bg_layers:
            for polygon in layer:
                points = []
                num_sides = polygon["num_sides"]
                for i in range(num_sides):
                    angle = 2 * math.pi * i / num_sides
                    x = int(polygon["x"] + math.cos(angle) * POLYGON_SIZE)
                    y = int(polygon["y"] + math.sin(angle) * POLYGON_SIZE)
                    points.append((x, y))
                pygame.draw.polygon(screen, polygon["color"], points)
                polygon["x"] += polygon["speed_x"]
                polygon["y"] += polygon["speed_y"]

                if polygon["y"] > HEIGHT + AREA_BORDER * 1.5:
                    polygon["y"] = -AREA_BORDER * 1.5
                    polygon["x"] = random.randint(-AREA_BORDER, WIDTH + AREA_BORDER)
                    polygon["speed_y"] = random.uniform(POLYGON_SPEED_BASE, POLYGON_SPEED_BASE + POLYGON_SPEED_RANDOM)

        enemy.move()
        hit_player1, hit_player2 = enemy.update(player1, player2, player1.balls, player2.balls)
        if hit_player1:
            if not player1.invulnerable:
                lives -= 1
                player1.hit()
        if hit_player2:
            if not player2.invulnerable:
                lives -= 1
                player2.hit()
        enemy.draw(screen)

        if enemy.defeated:
            game_clear = True

        keys = pygame.key.get_pressed()
        player1.move(keys)
        player1.update_balls(player2)
        player1.update_invulnerable()
        player1.draw(screen)

        player2.move(keys)
        player2.update_balls(player1)
        player2.update_invulnerable()
        player2.draw(screen)

        distance = player1.distance_to_other(player2)
        distance_text = font.render(f"Distance: {distance:.2f}", True, (0, 0, 0))

        lives_text = font.render(f"Lives: {lives}", True, (0, 0, 0))
        screen.blit(lives_text, (10, 70))

        if lives <= 0:
            game_over = True

        fps = clock.get_fps()
        fps_text = font.render(f"FPS: {fps:.2f}", True, (0, 0, 0))

        frame_count += 1
        frame_text = font.render(f"Frames: {frame_count}", True, (0, 0, 0))

    elif game_over:
        screen.fill(RED)
        game_over_text = font.render("Game Over", True, (255, 255, 255))
        text_rect = game_over_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 50))
        screen.blit(game_over_text, text_rect)

        shake_offset = random.randint(-2, 2)
        restart_text = font.render("Press R to restart", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
        screen.blit(restart_text, restart_rect)

        for i in range(0):
            x1 = random.randint(0, WIDTH)
            y1 = random.randint(0, HEIGHT)
            x2 = random.randint(0, WIDTH)
            y2 = random.randint(0, HEIGHT)
            line_color = (random.randint(100, 200), 0, 0)
            pygame.draw.line(screen, line_color, (x1, y1), (x2, y2), 2)

    elif game_clear:
        screen.fill(GREEN)
        game_clear_text = font.render("Game Clear!", True, (255, 255, 255))
        text_rect = game_clear_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 50))
        screen.blit(game_clear_text, text_rect)

        restart_text = font.render("Press R to restart", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
        screen.blit(restart_text, restart_rect)

        for _ in range(30):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            size = random.randint(5, 10)
            star_color = (random.randint(100, 255), random.randint(100, 255), 0)

            points = []
            for i in range(5):
                angle = 2 * math.pi * i / 5 + (pygame.time.get_ticks() / 1000 * 3)
                offset_x = math.cos(angle) * size * 2
                offset_y = math.sin(angle) * size * 2
                points.append((x + int(offset_x), y + int(offset_y)))

            pygame.draw.polygon(screen, star_color, points)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
