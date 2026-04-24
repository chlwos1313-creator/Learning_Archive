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
CYAN = (0, 255, 255)

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
            pygame.draw.circle(surf, self.color, (int(self.x + offset_x), int(self.y + offset_y)), int(self.size))

class MovingObstacle:
    def __init__(self, x, y, w, h, move_axis, move_range, speed):
        self.rect = pygame.Rect(x, y, w, h)
        self.start_x = x
        self.start_y = y
        self.move_axis = move_axis
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

class Item:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 12, y - 12, 24, 24)
        self.type = random.choice(["HEAL", "SHIELD", "GRENADE", "SPEED"])
        self.float_timer = 0
        
        if self.type == "HEAL": self.color = GREEN
        elif self.type == "SHIELD": self.color = CYAN
        elif self.type == "GRENADE": self.color = ORANGE
        elif self.type == "SPEED": self.color = YELLOW

    def draw(self, surf, offset_x, offset_y):
        self.float_timer += 0.1
        y_offset = math.sin(self.float_timer) * 5
        draw_rect = self.rect.copy()
        draw_rect.x += offset_x
        draw_rect.y += offset_y + y_offset
        
        pygame.draw.rect(surf, self.color, draw_rect, border_radius=4)
        pygame.draw.rect(surf, WHITE, draw_rect, 2, border_radius=4)
        
        # 아이콘 대체 (간단한 텍스트 기호)
        font = pygame.font.SysFont("arial", 16, bold=True)
        symbol = {"HEAL": "+", "SHIELD": "S", "GRENADE": "G", "SPEED": ">>"}[self.type]
        txt = font.render(symbol, True, BLACK)
        surf.blit(txt, (draw_rect.centerx - txt.get_width()//2, draw_rect.centery - txt.get_height()//2))

class Bullet:
    def __init__(self, x, y, dx, dy, speed, damage, owner, weapon_type="gun"):
        self.weapon_type = weapon_type # "gun", "grenade", "melee"
        self.size = 12 if weapon_type == "grenade" else (24 if weapon_type == "melee" else 6)
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.damage = damage
        self.owner = owner
        
        if weapon_type == "grenade": self.color = GREEN
        elif weapon_type == "melee": self.color = WHITE
        else: self.color = YELLOW
        
        self.life = 60 if weapon_type == "grenade" else (8 if weapon_type == "melee" else 150)
        self.active = True

        if weapon_type == "melee":
            # 근접 무기는 플레이어 바로 앞에 생성되고 멈춰있음
            self.rect.x += dx * 20
            self.rect.y += dy * 20

    def update(self):
        if self.weapon_type != "melee":
            self.rect.x += self.dx * self.speed
            self.rect.y += self.dy * self.speed
            # 꼬리 파티클
            if random.random() < 0.3 and self.weapon_type == "gun":
                particles.append(Particle(self.rect.centerx, self.rect.centery, YELLOW, 1, 10))
        
        self.life -= 1

    def explode(self, players):
        add_shake(10)
        for _ in range(30):
            particles.append(Particle(self.rect.centerx, self.rect.centery, ORANGE, 5, 30))
        explosion_radius = 80
        for p in players:
            dist = math.hypot(p.rect.centerx - self.rect.centerx, p.rect.centery - self.rect.centery)
            if dist < explosion_radius:
                p.take_damage(self.damage)

# --- 캐릭터 클래스 데이터 ---
CHAR_DATA = [
    {
        "name": "Rifle", 
        "base_speed": 4, 
        "shape": "square",
        "weapon": {"name": "Assault Rifle", "cd": 8, "spd": 15, "dmg": 10, "mag": 30, "reload": 60, "type": "gun"}
    },
    {
        "name": "Sniper", 
        "base_speed": 3.5, 
        "shape": "sniper",
        "weapon": {"name": "Sniper Rifle", "cd": 50, "spd": 25, "dmg": 50, "mag": 5, "reload": 100, "type": "gun"}
    },
    {
        "name": "Knife", 
        "base_speed": 6.5, 
        "shape": "circle",
        "weapon": {"name": "Combat Knife", "cd": 15, "spd": 0, "dmg": 35, "mag": -1, "reload": 0, "type": "melee"} # mag -1 은 무한
    }
]

class Player:
    def __init__(self, x, y, color, controls, name):
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(x, y, 32, 32)
        self.color = color
        self.controls = controls
        self.name = name
        self.char_idx = 0
        self.reset()

    def set_class(self, idx):
        self.char_idx = idx
        data = CHAR_DATA[idx]
        self.base_speed = data["base_speed"]
        self.shape = data["shape"]
        self.main_weapon = data["weapon"].copy()
        self.current_mag = self.main_weapon["mag"]
        self.grenades = 0 # 수류탄은 0개로 시작, 아이템으로 획득

    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.hp = 100
        self.max_hp = 100
        self.shield = 0
        
        if hasattr(self, 'main_weapon'):
            self.current_mag = self.main_weapon["mag"]
            
        self.timer = 0
        self.reload_timer = 0
        self.dash_timer = 0
        self.speed_buff_timer = 0
        self.dir = (0, -1)
        self.swap_pressed = False
        self.dash_pressed = False
        self.use_grenade = False

    def take_damage(self, amount):
        if self.shield > 0:
            if self.shield >= amount:
                self.shield -= amount
                amount = 0
            else:
                amount -= self.shield
                self.shield = 0
        self.hp -= amount

    def handle_input(self, keys, bullets, obstacles, moving_obstacles):
        old_pos = self.rect.topleft
        
        # 상태 업데이트
        if self.speed_buff_timer > 0: self.speed_buff_timer -= 1
        if self.timer > 0: self.timer -= 1
        
        # 장전 처리
        if self.reload_timer > 0:
            self.reload_timer -= 1
            if self.reload_timer <= 0:
                self.current_mag = self.main_weapon["mag"]
        
        # 대시 처리
        speed = self.base_speed
        if self.speed_buff_timer > 0:
            speed *= 1.5
            if random.random() < 0.2: particles.append(Particle(self.rect.centerx, self.rect.centery, self.color, 0.5, 10))

        if self.dash_timer > 0:
            speed = self.base_speed * 3
            self.dash_timer -= 1
            particles.append(Particle(self.rect.centerx, self.rect.centery, self.color, 0.5, 10))

        if keys[self.controls['dash']] and self.dash_timer <= -60 and not self.dash_pressed:
            self.dash_timer = 10 
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

        # 충돌 처리
        for obs in obstacles:
            if self.rect.colliderect(obs): self.rect.topleft = old_pos
        for mobs in moving_obstacles:
            if self.rect.colliderect(mobs.rect): self.rect.topleft = old_pos
        self.rect.clamp_ip(screen.get_rect())

        # 무기 스왑 (수류탄 모드 전환)
        if keys[self.controls['swap']]:
            if not self.swap_pressed:
                self.use_grenade = not self.use_grenade
                self.swap_pressed = True
        else:
            self.swap_pressed = False

        # 사격 처리
        if keys[self.controls['shoot']] and self.timer <= 0 and self.reload_timer <= 0:
            mag = math.hypot(self.dir[0], self.dir[1])
            ndx, ndy = self.dir[0]/mag, self.dir[1]/mag
            
            if self.use_grenade:
                if self.grenades > 0:
                    bullets.append(Bullet(self.rect.centerx, self.rect.centery, ndx, ndy, 8, 60, self, "grenade"))
                    self.timer = 40
                    self.grenades -= 1
                    self.use_grenade = False # 던지고 나면 주무기로 복귀
            else:
                w = self.main_weapon
                if self.current_mag > 0 or w["mag"] == -1:
                    bullets.append(Bullet(self.rect.centerx, self.rect.centery, ndx, ndy, w['spd'], w['dmg'], self, w['type']))
                    self.timer = w['cd']
                    if w['name'] == "Sniper Rifle": add_shake(5)
                    
                    if w["mag"] != -1:
                        self.current_mag -= 1
                        if self.current_mag <= 0:
                            self.reload_timer = w['reload']

    def draw(self, surf, offset_x, offset_y):
        draw_x, draw_y = self.rect.x + offset_x, self.rect.y + offset_y
        center = (draw_x + 16, draw_y + 16)
        
        # 외형 그리기
        if self.shape == "circle":
            pygame.draw.circle(surf, self.color, center, 16)
        else:
            pygame.draw.rect(surf, self.color, (draw_x, draw_y, 32, 32), border_radius=4)
        
        # 실드 효과
        if self.shield > 0:
            pygame.draw.circle(surf, CYAN, center, 22, 2)
            
        # 총구 그리기
        mag = math.hypot(self.dir[0], self.dir[1])
        ndx, ndy = self.dir[0]/mag, self.dir[1]/mag
        
        if self.use_grenade:
            pygame.draw.circle(surf, GREEN, (center[0] + ndx*15, center[1] + ndy*15), 5)
        elif self.shape == "sniper":
            gun_end = (center[0] + ndx*30, center[1] + ndy*30)
            pygame.draw.line(surf, WHITE, center, gun_end, 3)
            # 스코프
            pygame.draw.circle(surf, GRAY, (center[0] + ndx*10, center[1] + ndy*10), 4)
        elif self.shape == "square": # Rifle
            gun_end = (center[0] + ndx*20, center[1] + ndy*20)
            pygame.draw.line(surf, WHITE, center, gun_end, 4)
        elif self.shape == "circle": # Knife (들고있는 칼)
            gun_end = (center[0] + ndx*18, center[1] + ndy*18)
            pygame.draw.line(surf, WHITE, (center[0] + ndx*8, center[1] + ndy*8), gun_end, 5)

        # 체력바
        pygame.draw.rect(surf, GRAY, (draw_x, draw_y - 12, 32, 6))
        hp_ratio = max(0, self.hp / self.max_hp)
        hp_color = GREEN if hp_ratio > 0.5 else RED
        pygame.draw.rect(surf, hp_color, (draw_x, draw_y - 12, hp_ratio * 32, 6))

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
items = []
map_spawn_points = []

def load_map(map_idx):
    global obstacles, moving_obstacles, map_spawn_points, items
    obstacles.clear()
    moving_obstacles.clear()
    items.clear()
    p1.start_x, p1.start_y = 100, 300
    p2.start_x, p2.start_y = 650, 300
    
    if map_idx == 0: # Classic Map
        obstacles = [
            pygame.Rect(150, 100, 100, 150), pygame.Rect(550, 100, 100, 150),
            pygame.Rect(350, 250, 100, 100),
            pygame.Rect(150, 400, 100, 100), pygame.Rect(550, 400, 100, 100)
        ]
        map_spawn_points = [(400, 100), (400, 500)]
    elif map_idx == 1: # Factory Map
        obstacles = [
            pygame.Rect(380, 0, 40, 200), pygame.Rect(380, 400, 40, 200),
            pygame.Rect(150, 250, 50, 100), pygame.Rect(600, 250, 50, 100)
        ]
        moving_obstacles = [
            MovingObstacle(250, 100, 50, 100, 'y', 200, 2),
            MovingObstacle(500, 400, 50, 100, 'y', 200, 2)
        ]
        map_spawn_points = [(400, 300), (100, 100), (700, 500)]
        
    p1.reset()
    p2.reset()
    bullets.clear()
    particles.clear()

def draw_text(text, font_size, color, x, y, center=True):
    font = pygame.font.SysFont("impact", font_size)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center: rect.center = (x, y)
    else: rect.topleft = (x, y)
    screen.blit(surf, rect)

def draw_hud(player, is_left):
    x_base = 20 if is_left else WIDTH - 180
    y_base = HEIGHT - 60
    
    # 클래스 이름 및 체력/실드
    draw_text(f"{player.name} - {CHAR_DATA[player.char_idx]['name']}", 20, player.color, x_base, y_base, center=False)
    shield_txt = f" + {player.shield}S" if player.shield > 0 else ""
    draw_text(f"HP: {player.hp}{shield_txt}", 18, WHITE, x_base, y_base + 25, center=False)
    
    # 탄약 정보
    if player.use_grenade:
        ammo_txt = f"Grenades: {player.grenades}"
        color = ORANGE
    elif player.main_weapon["mag"] == -1:
        ammo_txt = "Ammo: Melee"
        color = GRAY
    elif player.reload_timer > 0:
        ammo_txt = "RELOADING..."
        color = RED
    else:
        ammo_txt = f"Ammo: {player.current_mag} / {player.main_weapon['mag']}"
        color = YELLOW
        
    draw_text(ammo_txt, 20, color, x_base + 150 if is_left else WIDTH - 20, y_base + 25, center=is_left==False)
    if not is_left: # P2 탄약 텍스트 정렬 보정
        rect = pygame.font.SysFont("impact", 20).render(ammo_txt, True, color).get_rect()
        rect.topright = (WIDTH - 20, y_base + 25)
        screen.blit(pygame.font.SysFont("impact", 20).render(ammo_txt, True, color), rect)

# --- 메인 루프 ---
map_selection = 0
maps = ["Classic Arena", "Moving Factory"]
p1_ready, p2_ready = False, False

item_spawn_timer = 0

while True:
    screen.fill(BLACK)
    
    offset_x = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
    offset_y = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
    if screen_shake > 0: screen_shake -= 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if state == "START":
                if event.key == pygame.K_SPACE: state = "SELECT"
            elif state == "SELECT":
                if event.key == pygame.K_LEFT: map_selection = (map_selection - 1) % len(maps)
                elif event.key == pygame.K_RIGHT: map_selection = (map_selection + 1) % len(maps)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    load_map(map_selection)
                    p1.char_idx, p2.char_idx = 0, 0
                    p1_ready, p2_ready = False, False
                    state = "CHAR_SELECT"
            elif state == "CHAR_SELECT":
                # P1 컨트롤
                if not p1_ready:
                    if event.key == pygame.K_a: p1.char_idx = (p1.char_idx - 1) % len(CHAR_DATA)
                    elif event.key == pygame.K_d: p1.char_idx = (p1.char_idx + 1) % len(CHAR_DATA)
                    elif event.key == pygame.K_w: p1_ready = True
                else:
                    if event.key == pygame.K_s: p1_ready = False
                # P2 컨트롤
                if not p2_ready:
                    if event.key == pygame.K_LEFT: p2.char_idx = (p2.char_idx - 1) % len(CHAR_DATA)
                    elif event.key == pygame.K_RIGHT: p2.char_idx = (p2.char_idx + 1) % len(CHAR_DATA)
                    elif event.key == pygame.K_UP: p2_ready = True
                else:
                    if event.key == pygame.K_DOWN: p2_ready = False
                
                if p1_ready and p2_ready:
                    p1.set_class(p1.char_idx)
                    p2.set_class(p2.char_idx)
                    p1.reset()
                    p2.reset()
                    state = "PLAYING"
            elif state == "GAME_OVER":
                if event.key == pygame.K_r: state = "SELECT"

    keys = pygame.key.get_pressed()

    if state == "START":
        draw_text("2D TACTICAL SHOOTER", 60, WHITE, WIDTH//2, HEIGHT//3)
        draw_text("PRESS SPACE TO START", 30, GRAY, WIDTH//2, HEIGHT//2 + 50)

    elif state == "SELECT":
        draw_text("SELECT MAP", 50, WHITE, WIDTH//2, HEIGHT//4)
        draw_text(f"<  {maps[map_selection]}  >", 40, YELLOW, WIDTH//2, HEIGHT//2)
        draw_text("Press ENTER to Select", 25, GRAY, WIDTH//2, HEIGHT - 100)

    elif state == "CHAR_SELECT":
        draw_text("SELECT CHARACTER", 50, WHITE, WIDTH//2, 50)
        pygame.draw.line(screen, DARK_GRAY, (WIDTH//2, 100), (WIDTH//2, HEIGHT-50), 2)
        
        # P1 Area
        draw_text("PLAYER 1", 30, RED, WIDTH//4, 120)
        draw_text(f"< {CHAR_DATA[p1.char_idx]['name']} >", 40, WHITE, WIDTH//4, 250)
        w1 = CHAR_DATA[p1.char_idx]['weapon']
        draw_text(f"Weapon: {w1['name']}", 20, GRAY, WIDTH//4, 320)
        if p1_ready: draw_text("READY", 40, GREEN, WIDTH//4, 450)
        else: draw_text("A/D to Change, W to Ready", 20, GRAY, WIDTH//4, 450)
        
        # P2 Area
        draw_text("PLAYER 2", 30, BLUE, WIDTH*3//4, 120)
        draw_text(f"< {CHAR_DATA[p2.char_idx]['name']} >", 40, WHITE, WIDTH*3//4, 250)
        w2 = CHAR_DATA[p2.char_idx]['weapon']
        draw_text(f"Weapon: {w2['name']}", 20, GRAY, WIDTH*3//4, 320)
        if p2_ready: draw_text("READY", 40, GREEN, WIDTH*3//4, 450)
        else: draw_text("L/R to Change, UP to Ready", 20, GRAY, WIDTH*3//4, 450)

    elif state == "PLAYING" or state == "GAME_OVER":
        if state == "PLAYING":
            # 아이템 스폰 로직
            item_spawn_timer += 1
            if item_spawn_timer > 300 and len(items) < 2: # 약 5초마다 스폰 시도
                item_spawn_timer = 0
                pt = random.choice(map_spawn_points)
                # 스폰 지점에 다른 아이템이 없을 때만 생성
                if not any(math.hypot(i.rect.centerx - pt[0], i.rect.centery - pt[1]) < 30 for i in items):
                    items.append(Item(pt[0], pt[1]))

            for mobs in moving_obstacles: mobs.update()

            if p1.hp > 0 and p2.hp > 0:
                p1.handle_input(keys, bullets, obstacles, moving_obstacles)
                p2.handle_input(keys, bullets, obstacles, moving_obstacles)
            else:
                state = "GAME_OVER"

            # 아이템 획득 처리
            for p in [p1, p2]:
                for item in items[:]:
                    if p.rect.colliderect(item.rect):
                        if item.type == "HEAL": p.hp = min(p.max_hp, p.hp + 30)
                        elif item.type == "SHIELD": p.shield = 50
                        elif item.type == "GRENADE": p.grenades += 1
                        elif item.type == "SPEED": p.speed_buff_timer = 600 # 10초
                        items.remove(item)
                        # 이펙트
                        for _ in range(10): particles.append(Particle(p.rect.centerx, p.rect.centery, item.color, 2, 20))

            # 총알 업데이트
            for b in bullets[:]:
                b.update()
                
                # 수명 / 화면 밖
                if not screen.get_rect().collidepoint(b.rect.center) or b.life <= 0:
                    if b.weapon_type == "grenade": b.explode([p1, p2])
                    if b in bullets: bullets.remove(b)
                    continue

                # 장애물 충돌 (근접무기는 벽 관통 안됨, 이펙트만 냄)
                hit_obs = False
                for obs in obstacles + [m.rect for m in moving_obstacles]:
                    if b.rect.colliderect(obs):
                        if b.weapon_type != "melee":
                            for _ in range(3): particles.append(Particle(b.rect.centerx, b.rect.centery, GRAY, 3, 10))
                            if b.weapon_type == "grenade": b.explode([p1, p2])
                            if b in bullets: bullets.remove(b)
                        hit_obs = True
                        break
                if hit_obs and b.weapon_type != "melee": continue

                # 플레이어 피격
                if b.owner != p2 and b.rect.colliderect(p2.rect):
                    if b.weapon_type == "grenade": b.explode([p1, p2])
                    else: 
                        p2.take_damage(b.damage)
                        for _ in range(5): particles.append(Particle(b.rect.centerx, b.rect.centery, BLUE, 4, 20))
                    if b in bullets: bullets.remove(b)
                elif b.owner != p1 and b.rect.colliderect(p1.rect):
                    if b.weapon_type == "grenade": b.explode([p1, p2])
                    else: 
                        p1.take_damage(b.damage)
                        for _ in range(5): particles.append(Particle(b.rect.centerx, b.rect.centery, RED, 4, 20))
                    if b in bullets: bullets.remove(b)

            for p in particles[:]:
                p.update()
                if p.life <= 0: particles.remove(p)

        # --- 그리기 (렌더링) ---
        for x in range(0, WIDTH, 50): pygame.draw.line(screen, DARK_GRAY, (x + offset_x, 0), (x + offset_x, HEIGHT))
        for y in range(0, HEIGHT, 50): pygame.draw.line(screen, DARK_GRAY, (0, y + offset_y), (WIDTH, y + offset_y))

        for obs in obstacles:
            draw_rect = obs.copy()
            draw_rect.x += offset_x; draw_rect.y += offset_y
            pygame.draw.rect(screen, GRAY, draw_rect)
            pygame.draw.rect(screen, WHITE, draw_rect, 2)
            
        for mobs in moving_obstacles: mobs.draw(screen, offset_x, offset_y)
        for item in items: item.draw(screen, offset_x, offset_y)
        for p in particles: p.draw(screen, offset_x, offset_y)

        if p1.hp > 0: p1.draw(screen, offset_x, offset_y)
        if p2.hp > 0: p2.draw(screen, offset_x, offset_y)
        
        for b in bullets:
            if b.weapon_type == "melee":
                # 근접공격 베는 이펙트 (반투명 호나 선으로 표현)
                pygame.draw.circle(screen, b.color, (int(b.rect.centerx + offset_x), int(b.rect.centery + offset_y)), b.size//2, 2)
            else:
                pygame.draw.circle(screen, b.color, (int(b.rect.centerx + offset_x), int(b.rect.centery + offset_y)), b.size//2)

        # UI 그리기
        draw_hud(p1, True)
        draw_hud(p2, False)

        if state == "GAME_OVER":
            winner = "PLAYER 2 WINS!" if p1.hp <= 0 else "PLAYER 1 WINS!"
            win_color = BLUE if p1.hp <= 0 else RED
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            screen.blit(overlay, (0,0))
            
            draw_text(winner, 70, win_color, WIDTH//2, HEIGHT//2 - 30)
            draw_text("Press 'R' to Return to Map Select", 35, WHITE, WIDTH//2, HEIGHT//2 + 50)

    pygame.display.flip()
    clock.tick(60)