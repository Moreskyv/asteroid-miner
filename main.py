import pygame
import random
import math

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Астероидный рудокоп")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)


class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.speed = 0
        self.max_speed = 5
        self.acceleration = 0.2
        self.friction = 0.98
        self.radius = 15
        self.health = 100
        self.max_health = 100
        self.minerals = 0
        self.mining_cooldown = 0
        self.mining_range = 50
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_timer = 0

    def update(self):
        # Управление
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += 5
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - self.acceleration, -self.max_speed / 2)
        else:
            self.speed *= self.friction

        # Движение
        angle_rad = math.radians(self.angle)
        self.x += math.cos(angle_rad) * self.speed
        self.y -= math.sin(angle_rad) * self.speed

        # Границы экрана
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

        # Добыча
        if self.mining_cooldown > 0:
            self.mining_cooldown -= 1

        # Неуязвимость
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False

    def mine(self, asteroids):
        if self.mining_cooldown == 0:
            for asteroid in asteroids[:]:
                distance = math.sqrt((self.x - asteroid.x) ** 2 + (self.y - asteroid.y) ** 2)
                if distance < self.mining_range + asteroid.radius:
                    if asteroid.mine():
                        self.minerals += asteroid.value
                        self.mining_cooldown = 30
                        return True
        return False

    def take_damage(self, damage):
        if not self.invulnerable:
            self.health -= damage
            if self.health <= 0:
                self.lives -= 1
                self.health = self.max_health
                self.invulnerable = True
                self.invulnerable_timer = 120
                return self.lives <= 0
        return False

    def draw(self, screen):
        # Рисуем корабль
        points = []
        angle_rad = math.radians(self.angle)
        for offset_angle in [0, 140, 220]:
            offset_rad = math.radians(offset_angle)
            x = self.x + math.cos(angle_rad + offset_rad) * self.radius
            y = self.y - math.sin(angle_rad + offset_rad) * self.radius
            points.append((x, y))

        color = WHITE if not self.invulnerable or pygame.time.get_ticks() % 200 < 100 else GRAY
        pygame.draw.polygon(screen, color, points, 2)

        # Рисуем радиус добычи
        if self.mining_cooldown == 0:
            pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)),
                               self.mining_range + self.radius, 1)

        # Индикатор здоровья
        health_percent = self.health / self.max_health
        health_color = GREEN if health_percent > 0.5 else YELLOW if health_percent > 0.25 else RED
        pygame.draw.rect(screen, health_color,
                         (self.x - self.radius, self.y - self.radius - 10,
                          self.radius * 2 * health_percent, 5))


class Asteroid:
    def __init__(self, x, y, size_type):
        self.x = x
        self.y = y
        self.size_type = size_type  # 'small', 'medium', 'large'

        if size_type == 'small':
            self.radius = random.randint(10, 20)
            self.health = 1
            self.value = random.randint(1, 3)
            self.speed_x = random.uniform(-1, 1)
            self.speed_y = random.uniform(-1, 1)
        elif size_type == 'medium':
            self.radius = random.randint(20, 35)
            self.health = 2
            self.value = random.randint(3, 7)
            self.speed_x = random.uniform(-0.5, 0.5)
            self.speed_y = random.uniform(-0.5, 0.5)
        else:  # large
            self.radius = random.randint(35, 50)
            self.health = 3
            self.value = random.randint(7, 15)
            self.speed_x = random.uniform(-0.3, 0.3)
            self.speed_y = random.uniform(-0.3, 0.3)

        self.max_health = self.health
        self.color = GRAY

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

        # Границы экрана
        if self.x < -self.radius:
            self.x = WIDTH + self.radius
        elif self.x > WIDTH + self.radius:
            self.x = -self.radius
        if self.y < -self.radius:
            self.y = HEIGHT + self.radius
        elif self.y > HEIGHT + self.radius:
            self.y = -self.radius

    def mine(self):
        self.health -= 1
        health_percent = self.health / self.max_health
        self.color = (int(255 * health_percent), int(255 * health_percent), int(255 * health_percent))
        return self.health <= 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius, 2)
        # Рисуем кратеры
        for _ in range(3):
            angle = random.uniform(0, 2 * math.pi)
            crater_x = self.x + math.cos(angle) * self.radius * 0.5
            crater_y = self.y + math.sin(angle) * self.radius * 0.5
            crater_radius = self.radius * random.uniform(0.1, 0.3)
            pygame.draw.circle(screen, self.color, (int(crater_x), int(crater_y)), int(crater_radius), 1)


class Enemy:
    def __init__(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.x = random.randint(0, WIDTH)
            self.y = -20
        elif side == 'bottom':
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + 20
        elif side == 'left':
            self.x = -20
            self.y = random.randint(0, HEIGHT)
        else:
            self.x = WIDTH + 20
            self.y = random.randint(0, HEIGHT)

        self.speed = random.uniform(1, 3)
        self.radius = 12
        angle_to_player = math.atan2(HEIGHT // 2 - self.y, WIDTH // 2 - self.x)
        self.speed_x = math.cos(angle_to_player) * self.speed
        self.speed_y = math.sin(angle_to_player) * self.speed
        self.damage = 10

    def update(self, player):
        # Преследование игрока
        angle = math.atan2(player.y - self.y, player.x - self.x)
        self.speed_x = math.cos(angle) * self.speed
        self.speed_y = math.sin(angle) * self.speed

        self.x += self.speed_x
        self.y += self.speed_y

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)
        # Глаза
        eye_offset = self.radius * 0.4
        pygame.draw.circle(screen, YELLOW, (int(self.x - eye_offset), int(self.y - eye_offset)), 3)
        pygame.draw.circle(screen, YELLOW, (int(self.x + eye_offset), int(self.y - eye_offset)), 3)


class Game:
    def __init__(self):
        self.player = Player()
        self.asteroids = []
        self.enemies = []
        self.score = 0
        self.wave = 1
        self.game_over = False
        self.paused = False
        self.spawn_asteroids(10)

    def spawn_asteroids(self, count):
        for _ in range(count):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            size_type = random.choice(['small', 'medium', 'large'])
            self.asteroids.append(Asteroid(x, y, size_type))

    def spawn_enemy(self):
        self.enemies.append(Enemy())

    def update(self):
        if self.game_over or self.paused:
            return

        self.player.update()

        # Добыча
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if self.player.mine(self.asteroids):
                self.score += 10

        # Обновление астероидов
        for asteroid in self.asteroids[:]:
            asteroid.update()

        # Обновление врагов
        for enemy in self.enemies[:]:
            enemy.update(self.player)
            # Проверка столкновений с игроком
            distance = math.sqrt((self.player.x - enemy.x) ** 2 + (self.player.y - enemy.y) ** 2)
            if distance < self.player.radius + enemy.radius:
                if self.player.take_damage(enemy.damage):
                    self.game_over = True
                self.enemies.remove(enemy)
            # Удаление врагов за экраном
            elif (enemy.x < -50 or enemy.x > WIDTH + 50 or
                  enemy.y < -50 or enemy.y > HEIGHT + 50):
                self.enemies.remove(enemy)

        # Спавн врагов
        if random.random() < 0.02 * self.wave and len(self.enemies) < 5:
            self.spawn_enemy()

        # Проверка на новую волну
        if len(self.asteroids) < 5:
            self.wave += 1
            self.spawn_asteroids(5 + self.wave * 2)
            self.player.minerals += 10  # Бонус за волну

    def draw(self, screen):
        screen.fill(BLACK)

        # Рисуем звезды
        for _ in range(50):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            pygame.draw.circle(screen, WHITE, (x, y), 1)

        # Рисуем объекты
        for asteroid in self.asteroids:
            asteroid.draw(screen)

        for enemy in self.enemies:
            enemy.draw(screen)

        self.player.draw(screen)

        # UI
        score_text = font.render(f"Счёт: {self.score}", True, WHITE)
        minerals_text = font.render(f"Минералы: {self.player.minerals}", True, GREEN)
        lives_text = font.render(f"Жизни: {self.player.lives}", True, RED if self.player.lives <= 1 else WHITE)
        wave_text = font.render(f"Волна: {self.wave}", True, YELLOW)
        health_text = font.render(f"HP: {self.player.health}/{self.player.max_health}", True, WHITE)

        screen.blit(score_text, (10, 10))
        screen.blit(minerals_text, (10, 50))
        screen.blit(lives_text, (10, 90))
        screen.blit(wave_text, (WIDTH - 150, 10))
        screen.blit(health_text, (WIDTH - 200, 50))

        # Подсказки
        controls_text = small_font.render("WASD/Стрелки - движение | SPACE - добыча | P - пауза | R - рестарт", True,
                                          WHITE)
        screen.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, HEIGHT - 30))

        if self.game_over:
            game_over_text = font.render("ИГРА ОКОНЧЕНА!", True, RED)
            restart_text = font.render("Нажмите R для перезапуска", True, WHITE)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))

        if self.paused:
            pause_text = font.render("ПАУЗА", True, YELLOW)
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))

    def restart(self):
        self.__init__()


def main():
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game.paused = not game.paused
                elif event.key == pygame.K_r:
                    game.restart()
                elif event.key == pygame.K_ESCAPE:
                    running = False

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()