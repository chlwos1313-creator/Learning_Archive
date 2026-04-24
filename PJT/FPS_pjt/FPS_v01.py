import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Tactical Shooter - 2 Players")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GRAY = (100, 100, 100)
RED = (255, 50, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 0)
GREEN = (50, 255, 50)

obstacles = [
    pygame.Rect(150, 100, 100, 150),
    pygame.Rect(550, 100, 100, 150),
    pygame.Rect(350, 250, 100, 100),
    pygame.Rect(150, 400, 100, 100),
    pygame.Rect(550, 400, 100, 100)
]

class Bullet:
    def __init__(self, x, y, dx, dy, speed, damage, owner, is_grenade=False):
        self.size = 15 if is_grenade else 8
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.damage = damage
        self.owner = owner
        self.color = GREEN if is_grenade else YELLOW
        self.is_grenade = is_grenade
        self.life = 60 if is_grenade else 200

    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        self.life -= 1

class Player:
    def __init__(self, x, y, color, controls, name):
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(x, y, 32, 32)
        self.color = color
        self.controls = controls
        self.name = name
        self.speed = 4
        self.reset()

    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.hp = 100
        self.max_hp = 100
        self.weapons = [
            {"name": "Rifle", "cooldown": 12, "b_speed": 6, "dmg": 10, "ammo": float('inf'), "is_grenade": False},
            {"name": "Sniper", "cooldown": 60, "b_speed": 12, "dmg": 45, "ammo": 10, "is_grenade": False},
            {"name": "Grenade", "cooldown": 60, "b_speed": 8, "dmg": 100, "ammo": 1, "is_grenade": True}
        ]
        self.w_idx = 0
        self.timer = 0
        self.dir = (0, -1)
        self.swap_pressed = False

    def handle_input(self, keys, bullets):
        old_pos = self.rect.topleft
        
        if keys[self.controls['up']]:
            self.rect.y -= self.speed
            self.dir = (0, -1)
        elif keys[self.controls['down']]:
            self.rect.y += self.speed
            self.dir = (0, 1)
        
        if keys[self.controls['left']]:
            self.rect.x -= self.speed
            self.dir = (-1, 0)
        elif keys[self.controls['right']]:
            self.rect.x += self.speed
            self.dir = (1, 0)

        for obs in obstacles:
            if self.rect.colliderect(obs):
                self.rect.topleft = old_pos

        self.rect.clamp_ip(screen.get_rect())

        if self.timer > 0: self.timer -= 1
        
        if keys[self.controls['shoot']] and self.timer == 0:
            w = self.weapons[self.w_idx]
            if w['ammo'] > 0:
                bullets.append(Bullet(self.rect.centerx, self.rect.centery, 
                                      self.dir[0], self.dir[1], 
                                      w['b_speed'], w['dmg'], self, w['is_grenade']))
                self.timer = w['cooldown']
                if w['ammo'] != float('inf'):
                    w['ammo'] -= 1

        if keys[self.controls['swap']]:
            if not self.swap_pressed:
                self.w_idx = (self.w_idx + 1) % len(self.weapons)
                self.swap_pressed = True
        else:
            self.swap_pressed = False

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)
        gun_end = (self.rect.centerx + self.dir[0]*20, self.rect.centery + self.dir[1]*20)
        pygame.draw.line(surf, WHITE, self.rect.center, gun_end, 3)
        pygame.draw.rect(surf, GRAY, (self.rect.x, self.rect.y - 10, 32, 5))
        pygame.draw.rect(surf, RED, (self.rect.x, self.rect.y - 10, (self.hp/self.max_hp)*32, 5))
        font = pygame.font.SysFont(None, 20)
        w = self.weapons[self.w_idx]
        ammo_txt = str(w['ammo']) if w['ammo'] != float('inf') else "inf"
        txt = font.render(f"{w['name']} ({ammo_txt})", True, WHITE)
        surf.blit(txt, (self.rect.x - 10, self.rect.y + 35))

p1_keys = {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d, 'shoot': pygame.K_f, 'swap': pygame.K_q}
p2_keys = {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'shoot': pygame.K_SLASH, 'swap': pygame.K_PERIOD}

p1 = Player(100, 300, RED, p1_keys, "P1")
p2 = Player(650, 300, BLUE, p2_keys, "P2")
bullets = []

def reset_game():
    p1.reset()
    p2.reset()
    bullets.clear()

while True:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and (p1.hp <= 0 or p2.hp <= 0):
                reset_game()

    keys = pygame.key.get_pressed()
    
    if p1.hp > 0 and p2.hp > 0:
        p1.handle_input(keys, bullets)
        p2.handle_input(keys, bullets)

        for b in bullets[:]:
            b.update()
            
            if not screen.get_rect().collidepoint(b.rect.center) or b.life <= 0:
                if b in bullets: bullets.remove(b)
                continue

            hit_obs = False
            for obs in obstacles:
                if b.rect.colliderect(obs):
                    if b in bullets: bullets.remove(b)
                    hit_obs = True
                    break
            if hit_obs: continue

            if b.owner != p2 and b.rect.colliderect(p2.rect):
                p2.hp -= b.damage
                if b in bullets: bullets.remove(b)
            elif b.owner != p1 and b.rect.colliderect(p1.rect):
                p1.hp -= b.damage
                if b in bullets: bullets.remove(b)

    for obs in obstacles:
        pygame.draw.rect(screen, GRAY, obs)
    
    if p1.hp > 0: p1.draw(screen)
    if p2.hp > 0: p2.draw(screen)
    for b in bullets:
        pygame.draw.rect(screen, b.color, b.rect)

    if p1.hp <= 0 or p2.hp <= 0:
        winner = "P2 WIN!" if p1.hp <= 0 else "P1 WIN!"
        font = pygame.font.SysFont(None, 80)
        win_txt = font.render(winner, True, YELLOW)
        screen.blit(win_txt, (WIDTH//2 - 120, HEIGHT//2 - 40))
        
        font_small = pygame.font.SysFont(None, 40)
        restart_txt = font_small.render("Press 'R' to Restart", True, WHITE)
        screen.blit(restart_txt, (WIDTH//2 - 140, HEIGHT//2 + 40))

    pygame.display.flip()
    clock.tick(60)