import pygame
import sys
import random
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Tactical Shooter - Pro Edition")
clock = pygame.time.Clock()

# --- 색상 정의 ---
WHITE = (255, 255, 255)
BLACK = (20, 20, 22)
GRAY = (100, 100, 110)
DARK_GRAY = (50, 50, 60)
RED = (255, 70, 70)
BLUE = (70, 170, 255)
YELLOW = (255, 220, 50)
GREEN = (70, 255, 70)
ORANGE = (255, 150, 0)

# --- 글로벌 이펙트 ---
screen_shake = 0
particles = []

def add_shake(amount):
    global screen_shake
    screen_shake = min(screen_shake + amount, 20)

class Particle:
    def __init__(self, x, y, color, speed, life):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, math.pi * 2)
        self.dx = math.cos(angle) * speed * random.uniform(0.5, 1.5)
        self.dy = math.sin(angle) * speed * random.uniform(0.5, 1.5)
        self.life = life
        self.max_life = life
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        self.size = max(0, self.size * 0.95)

    def draw(self, surf, offset_x, offset_y):
        if self.life > 0:
            alpha = int((self.life / self.max_life) * 255)
            pygame.draw.circle(surf, self.color, (int(self.x + offset_x), int(self.y + offset_y)), int(self.size))

class MovingObstacle:
    def __init__(self, x, y, w, h, move_axis, move_range, speed):
        self.rect = pygame.Rect(x, y, w, h)
        self.start_x = x
        self.start_y = y
        self.move_axis = move_axis # 'x' or 'y'
        self.move_range = move_range
        self.speed = speed
        self.direction = 1

    def update(self):
        if self.move_axis == 'y':
            self.rect.y += self.speed * self.direction
            if abs(self.rect.y - self.start_y) > self.move_range:
                self.direction *= -1
        else:
            self.rect.x += self.speed * self.direction
            if abs(self.rect.x - self.start_x) > self.move_range:
                self.direction *= -1

    def draw(self, surf, offset_x, offset_y):
        draw_rect = self.rect.copy()
        draw_rect.x += offset_x
        draw_rect.y += offset_y
        pygame.draw.rect(surf, ORANGE, draw_rect)
        pygame.draw.rect(surf, WHITE, draw_rect, 2)

class Bullet:
    def __init__(self, x, y, dx, dy, speed, damage, owner, is_grenade=False):
        self.size = 12 if is_grenade else 6
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.damage = damage
        self.owner = owner
        self.color = GREEN if is_grenade else YELLOW
        self.is_grenade = is_grenade
        self.life = 60 if is_grenade else 150
        self.active = True

    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        self.life -= 1
        
        # 꼬리 파티클 생성
        if random.random() < 0.3 and not self.is_grenade:
            particles.append(Particle(self.rect.centerx, self.rect.centery, YELLOW, 1, 10))

    def explode(self, players):
        add_shake(10)
        for _ in range(30):
            particles.append(Particle(self.rect.centerx, self.rect.centery, ORANGE, 5, 30))
        # 광역 데미지
        explosion_radius = 80
        for p in players:
            dist = math.hypot(p.rect.centerx - self.rect.centerx, p.rect.centery - self.rect.centery)
            if dist < explosion_radius:
                p.hp -= self.damage

class Player:
    def __init__(self, x, y, color, controls, name):
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(x, y, 32, 32)
        self.color = color
        self.controls = controls
        self.name = name
        self.base_speed = 4
        self.reset()

    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.hp = 100
        self.max_hp = 100
        self.weapons = [
            {"name": "Rifle", "cooldown": 8, "b_speed": 10, "dmg": 8, "ammo": float('inf'), "is_grenade": False},
            {"name": "Sniper", "cooldown": 50, "b_speed": 18, "dmg": 50, "ammo": 5, "is_grenade": False},
            {"name": "Grenade", "cooldown": 40, "b_speed": 8, "dmg": 60, "ammo": 2, "is_grenade": True}
        ]
        self.w_idx = 0
        self.timer = 0
        self.dash_timer = 0
        self.dir = (0, -1)
        self.swap_pressed = False
        self.dash_pressed = False

    def handle_input(self, keys, bullets, obstacles, moving_obstacles):
        old_pos = self.rect.topleft
        
        # 대시 처리
        speed = self.base_speed
        if self.dash_timer > 0:
            speed = self.base_speed * 3
            self.dash_timer -= 1
            particles.append(Particle(self.rect.centerx, self.rect.centery, self.color, 0.5, 10))

        if keys[self.controls['dash']] and self.dash_timer <= -60 and not self.dash_pressed:
            self.dash_timer = 10 # 대시 지속시간
            self.dash_pressed = True
        elif not keys[self.controls['dash']]:
            self.dash_pressed = False
            if self.dash_timer <= 0:
                self.dash_timer -= 1

        # 이동 처리
        dx, dy = 0, 0
        if keys[self.controls['up']]: dy = -1
        elif keys[self.controls['down']]: dy = 1
        if keys[self.controls['left']]: dx = -1
        elif keys[self.controls['right']]: dx = 1

        if dx != 0 or dy != 0:
            self.dir = (dx, dy)
            self.rect.x += dx * speed
            self.rect.y += dy * speed

        # 충돌 처리 (정적 장애물)
        for obs in obstacles:
            if self.rect.colliderect(obs):
                self.rect.topleft = old_pos
        
        # 충돌 처리 (동적 장애물)
        for mobs in moving_obstacles:
            if self.rect.colliderect(mobs.rect):
                self.rect.topleft = old_pos

        self.rect.clamp_ip(screen.get_rect())

        # 사격 처리
        if self.timer > 0: self.timer -= 1
        if keys[self.controls['shoot']] and self.timer <= 0:
            w = self.weapons[self.w_idx]
            if w['ammo'] > 0:
                # 대각선 조준 보정
                mag = math.hypot(self.dir[0], self.dir[1])
                ndx, ndy = self.dir[0]/mag, self.dir[1]/mag
                bullets.append(Bullet(self.rect.centerx, self.rect.centery, ndx, ndy, w['b_speed'], w['dmg'], self, w['is_grenade']))
                self.timer = w['cooldown']
                if w['name'] == "Sniper": add_shake(5)
                if w['ammo'] != float('inf'): w['ammo'] -= 1

        # 무기 교체
        if keys[self.controls['swap']]:
            if not self.swap_pressed:
                self.w_idx = (self.w_idx + 1) % len(self.weapons)
                self.swap_pressed = True
        else:
            self.swap_pressed = False

    def draw(self, surf, offset_x, offset_y):
        draw_x, draw_y = self.rect.x + offset_x, self.rect.y + offset_y
        
        # 플레이어 본체
        pygame.draw.rect(surf, self.color, (draw_x, draw_y, 32, 32), border_radius=5)
        
        # 총구
        mag = math.hypot(self.dir[0], self.dir[1])
        ndx, ndy = self.dir[0]/mag, self.dir[1]/mag
        gun_end = (draw_x + 16 + ndx*25, draw_y + 16 + ndy*25)
        pygame.draw.line(surf, WHITE, (draw_x + 16, draw_y + 16), gun_end, 4)
        
        # 체력바
        pygame.draw.rect(surf, GRAY, (draw_x, draw_y - 12, 32, 6))
        hp_ratio = max(0, self.hp / self.max_hp)
        hp_color = GREEN if hp_ratio > 0.5 else RED
        pygame.draw.rect(surf, hp_color, (draw_x, draw_y - 12, hp_ratio * 32, 6))
        
        # 무기 정보
        font = pygame.font.SysFont(None, 22)
        w = self.weapons[self.w_idx]
        ammo_txt = str(w['ammo']) if w['ammo'] != float('inf') else "∞"
        txt = font.render(f"{w['name']} ({ammo_txt})", True, WHITE)
        surf.blit(txt, (draw_x - 10, draw_y + 35))


# --- 컨트롤 설정 ---
p1_keys = {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d, 'shoot': pygame.K_f, 'swap': pygame.K_q, 'dash': pygame.K_LSHIFT}
p2_keys = {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'shoot': pygame.K_SLASH, 'swap': pygame.K_PERIOD, 'dash': pygame.K_RSHIFT}

p1 = Player(100, 300, RED, p1_keys, "P1")
p2 = Player(650, 300, BLUE, p2_keys, "P2")

# --- 게임 상태 및 데이터 ---
state = "START"
bullets = []
obstacles = []
moving_obstacles = []

def load_map(map_idx):
    global obstacles, moving_obstacles
    obstacles.clear()
    moving_obstacles.clear()
    p1.start_x, p1.start_y = 100, 300
    p2.start_x, p2.start_y = 650, 300
    
    if map_idx == 0: # Classic Map
        obstacles = [
            pygame.Rect(150, 100, 100, 150),
            pygame.Rect(550, 100, 100, 150),
            pygame.Rect(350, 250, 100, 100),
            pygame.Rect(150, 400, 100, 100),
            pygame.Rect(550, 400, 100, 100)
        ]
    elif map_idx == 1: # Factory Map (Moving)
        obstacles = [
            pygame.Rect(380, 0, 40, 200),
            pygame.Rect(380, 400, 40, 200),
            pygame.Rect(150, 250, 50, 100),
            pygame.Rect(600, 250, 50, 100)
        ]
        moving_obstacles = [
            MovingObstacle(250, 100, 50, 100, 'y', 200, 2),
            MovingObstacle(500, 400, 50, 100, 'y', 200, 2)
        ]
    p1.reset()
    p2.reset()
    bullets.clear()
    particles.clear()

def draw_text(text, font_size, color, x, y, center=True):
    font = pygame.font.SysFont("impact", font_size)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)

# --- 메인 루프 ---
map_selection = 0
maps = ["Classic Arena", "Moving Factory"]

while True:
    screen.fill(BLACK)
    
    # 스크린 쉐이크 계산
    offset_x = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
    offset_y = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
    if screen_shake > 0: screen_shake -= 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if state == "START":
                if event.key == pygame.K_SPACE:
                    state = "SELECT"
            elif state == "SELECT":
                if event.key == pygame.K_LEFT:
                    map_selection = (map_selection - 1) % len(maps)
                elif event.key == pygame.K_RIGHT:
                    map_selection = (map_selection + 1) % len(maps)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    load_map(map_selection)
                    state = "PLAYING"
            elif state == "GAME_OVER":
                if event.key == pygame.K_r:
                    state = "SELECT"

    keys = pygame.key.get_pressed()

    if state == "START":
        draw_text("2D TACTICAL SHOOTER", 60, WHITE, WIDTH//2, HEIGHT//3)
        draw_text("PRESS SPACE TO START", 30, GRAY, WIDTH//2, HEIGHT//2 + 50)

    elif state == "SELECT":
        draw_text("SELECT MAP", 50, WHITE, WIDTH//2, HEIGHT//4)
        draw_text(f"<  {maps[map_selection]}  >", 40, YELLOW, WIDTH//2, HEIGHT//2)
        draw_text("Press ENTER to Begin", 25, GRAY, WIDTH//2, HEIGHT - 100)

    elif state == "PLAYING" or state == "GAME_OVER":
        # 동적 장애물 업데이트
        if state == "PLAYING":
            for mobs in moving_obstacles:
                mobs.update()

            # 플레이어 입력 처리
            if p1.hp > 0 and p2.hp > 0:
                p1.handle_input(keys, bullets, obstacles, moving_obstacles)
                p2.handle_input(keys, bullets, obstacles, moving_obstacles)
            else:
                state = "GAME_OVER"

            # 총알 업데이트 및 충돌
            for b in bullets[:]:
                b.update()
                
                # 수명 다함 / 화면 밖
                if not screen.get_rect().collidepoint(b.rect.center) or b.life <= 0:
                    if b.is_grenade: b.explode([p1, p2])
                    if b in bullets: bullets.remove(b)
                    continue

                # 장애물 충돌
                hit_obs = False
                for obs in obstacles + [m.rect for m in moving_obstacles]:
                    if b.rect.colliderect(obs):
                        for _ in range(5): particles.append(Particle(b.rect.centerx, b.rect.centery, GRAY, 3, 15))
                        if b.is_grenade: b.explode([p1, p2])
                        if b in bullets: bullets.remove(b)
                        hit_obs = True
                        break
                if hit_obs: continue

                # 플레이어 피격
                if b.owner != p2 and b.rect.colliderect(p2.rect):
                    if b.is_grenade: b.explode([p1, p2])
                    else: 
                        p2.hp -= b.damage
                        for _ in range(5): particles.append(Particle(b.rect.centerx, b.rect.centery, BLUE, 4, 20))
                    if b in bullets: bullets.remove(b)
                elif b.owner != p1 and b.rect.colliderect(p1.rect):
                    if b.is_grenade: b.explode([p1, p2])
                    else: 
                        p1.hp -= b.damage
                        for _ in range(5): particles.append(Particle(b.rect.centerx, b.rect.centery, RED, 4, 20))
                    if b in bullets: bullets.remove(b)

            # 파티클 업데이트
            for p in particles[:]:
                p.update()
                if p.life <= 0: particles.remove(p)

        # --- 그리기 (렌더링) ---
        # 바닥 그리드 효과 (옵션)
        for x in range(0, WIDTH, 50): pygame.draw.line(screen, DARK_GRAY, (x + offset_x, 0), (x + offset_x, HEIGHT))
        for y in range(0, HEIGHT, 50): pygame.draw.line(screen, DARK_GRAY, (0, y + offset_y), (WIDTH, y + offset_y))

        for obs in obstacles:
            draw_rect = obs.copy()
            draw_rect.x += offset_x
            draw_rect.y += offset_y
            pygame.draw.rect(screen, GRAY, draw_rect)
            pygame.draw.rect(screen, WHITE, draw_rect, 2)
            
        for mobs in moving_obstacles:
            mobs.draw(screen, offset_x, offset_y)

        for p in particles:
            p.draw(screen, offset_x, offset_y)

        if p1.hp > 0: p1.draw(screen, offset_x, offset_y)
        if p2.hp > 0: p2.draw(screen, offset_x, offset_y)
        
        for b in bullets:
            pygame.draw.circle(screen, b.color, (b.rect.centerx + offset_x, b.rect.centery + offset_y), b.size//2)

        if state == "GAME_OVER":
            winner = "PLAYER 2 WINS!" if p1.hp <= 0 else "PLAYER 1 WINS!"
            win_color = BLUE if p1.hp <= 0 else RED
            # 반투명 오버레이
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            screen.blit(overlay, (0,0))
            
            draw_text(winner, 70, win_color, WIDTH//2, HEIGHT//2 - 30)
            draw_text("Press 'R' to Return to Map Select", 35, WHITE, WIDTH//2, HEIGHT//2 + 50)

    pygame.display.flip()
    clock.tick(60)