import pygame, sys, socket, threading, pickle, math, random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Online Tactical Shooter - Final Edition")
clock = pygame.time.Clock()

# --- 색상 및 설정 ---
WHITE, BLACK, GRAY, DARK_GRAY = (255, 255, 255), (20, 20, 22), (100, 100, 110), (50, 50, 60)
RED, BLUE, YELLOW, GREEN = (255, 70, 70), (70, 170, 255), (255, 220, 50), (70, 255, 70)
ORANGE, CYAN = (255, 150, 0), (0, 255, 255)
PORT = 5555

# --- 캐릭터 데이터 (라이플 무제한 장탄 적용) ---
CHAR_DATA = [
    {"name": "Rifle", "speed": 4.5, "shape": "square", "wp": {"n": "Assault Rifle", "cd": 8, "spd": 15, "dmg": 10, "mag": -1, "rl": 0, "type": "gun"}},
    {"name": "Sniper", "speed": 3.5, "shape": "sniper", "wp": {"n": "Sniper Rifle", "cd": 50, "spd": 25, "dmg": 50, "mag": 5, "rl": 100, "type": "gun"}},
    {"name": "Knife", "speed": 6.5, "shape": "circle", "wp": {"n": "Combat Knife", "cd": 15, "spd": 0, "dmg": 35, "mag": -1, "rl": 0, "type": "melee"}}
]

# --- 네트워크 데이터 패키지 ---
class GameState:
    def __init__(self):
        self.phase = "MENU" # MENU, HOSTING, JOINING, SELECT_MAP, CHAR_SELECT, PLAYING, GAME_OVER
        self.map_idx = 0
        self.p1 = {"x": 100, "y": 300, "hp": 100, "shield": 0, "c_idx": 0, "ready": False, "ammo": 0, "grenades": 0, "reload": 0, "use_g": False, "mx": 100, "my": 300, "dir": (1,0)}
        self.p2 = {"x": 650, "y": 300, "hp": 100, "shield": 0, "c_idx": 0, "ready": False, "ammo": 0, "grenades": 0, "reload": 0, "use_g": False, "mx": 650, "my": 300, "dir": (-1,0)}
        self.bullets = [] # [x, y, dx, dy, type, id]
        self.items = []   # [x, y, type]
        self.obs = []     # [x, y, w, h]
        self.m_obs = []   # [x, y, w, h]
        self.effects = [] # 이벤트 큐 ["shake", amount] or ["explode", x, y]

# 글로벌 변수
is_host = False
my_socket = None
g_data = GameState()
my_inputs = {'up':0, 'down':0, 'left':0, 'right':0, 'dash':0, 'shoot':0, 'reload':0, 'swap':0, 'mx':0, 'my':0}
p2_inputs = my_inputs.copy()
particles = []
screen_shake = 0

# --- 파티클 & 유틸 ---
class Particle:
    def __init__(self, x, y, color, speed, life):
        self.x, self.y, self.color, self.life = x, y, color, life
        ang = random.uniform(0, math.pi*2)
        self.dx, self.dy = math.cos(ang)*speed, math.sin(ang)*speed
        self.size = random.randint(2, 5)
    def update(self):
        self.x += self.dx; self.y += self.dy; self.life -= 1; self.size *= 0.95
    def draw(self, surf, ox, oy):
        if self.life>0: pygame.draw.circle(surf, self.color, (int(self.x+ox), int(self.y+oy)), int(self.size))

def add_shake(amt): global screen_shake; screen_shake = min(screen_shake+amt, 20)
def draw_txt(txt, size, col, x, y, center=True):
    surf = pygame.font.SysFont("impact", size).render(txt, True, col)
    rect = surf.get_rect(center=(x,y)) if center else surf.get_rect(topleft=(x,y))
    screen.blit(surf, rect)

# --- 네트워크 통신 ---
def host_server():
    global p2_inputs, g_data
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', PORT)); server.listen(1)
    conn, _ = server.accept()
    g_data.phase = "SELECT_MAP"
    while True:
        try:
            data = conn.recv(2048)
            if not data: break
            p2_inputs = pickle.loads(data)
            conn.sendall(pickle.dumps(g_data))
            g_data.effects.clear() # 보낸 이펙트는 소비됨
        except: break

def join_server(ip):
    global g_data, my_socket
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.connect((ip, PORT))
        while True:
            my_socket.sendall(pickle.dumps(my_inputs))
            data = my_socket.recv(16384)
            if not data: break
            g_data = pickle.loads(data)
            for e in g_data.effects:
                if e[0]=="shake": add_shake(e[1])
                elif e[0]=="explode": 
                    for _ in range(30): particles.append(Particle(e[1], e[2], ORANGE, 5, 30))
                elif e[0]=="hit":
                    for _ in range(5): particles.append(Particle(e[1], e[2], e[3], 4, 20))
    except: g_data.phase = "MENU"

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try: s.connect(('10.255.255.255', 1)); ip = s.getsockname()[0]
    except: ip = '127.0.0.1'
    finally: s.close()
    return ip

# --- 서버 물리 연산 (방장만 실행) ---
class SPlayer:
    def __init__(self, p_data):
        self.d = p_data
        self.timer, self.dash_cd, self.spd_buff = 0, 0, 0
        self.swap_p, self.dash_p = False, False
        
    def update(self, inp, bullets):
        w = CHAR_DATA[self.d['c_idx']]['wp']
        if self.timer > 0: self.timer -= 1
        if self.d['reload'] > 0:
            self.d['reload'] -= 1
            if self.d['reload'] == 0: self.d['ammo'] = w['mag']
        if self.dash_cd > 0: self.dash_cd -= 1
        elif self.dash_cd < 0: self.dash_cd += 1
        if self.spd_buff > 0: self.spd_buff -= 1

        self.d['mx'], self.d['my'] = inp['mx'], inp['my']
        
        # 방향 벡터 계산 (마우스 기준)
        dx_m, dy_m = inp['mx'] - self.d['x'], inp['my'] - self.d['y']
        mag_m = math.hypot(dx_m, dy_m) or 1
        self.d['dir'] = (dx_m/mag_m, dy_m/mag_m)

        if inp['swap'] and not self.swap_p:
            self.d['use_g'] = not self.d['use_g']
            self.swap_p = True
        elif not inp['swap']: self.swap_p = False

        spd = CHAR_DATA[self.d['c_idx']]['speed'] * (1.5 if self.spd_buff>0 else 1.0)
        if inp['dash'] and self.dash_cd == 0 and not self.dash_p:
            self.dash_cd = 10; self.dash_p = True
        elif not inp['dash']: self.dash_p = False
        
        if self.dash_cd > 0: spd *= 3
        if self.dash_cd == 1: self.dash_cd = -60

        ox, oy = self.d['x'], self.d['y']
        mx, my = 0, 0
        if inp['up']: my -= 1
        if inp['down']: my += 1
        if inp['left']: mx -= 1
        if inp['right']: mx += 1
        
        if mx!=0 or my!=0:
            mag = math.hypot(mx, my)
            self.d['x'] += (mx/mag)*spd
            self.d['y'] += (my/mag)*spd

        # 충돌
        rect = pygame.Rect(self.d['x']-16, self.d['y']-16, 32, 32)
        for ob in g_data.obs + g_data.m_obs:
            if rect.colliderect(pygame.Rect(ob)): self.d['x'], self.d['y'] = ox, oy
        self.d['x'] = max(16, min(WIDTH-16, self.d['x']))
        self.d['y'] = max(16, min(HEIGHT-16, self.d['y']))

        # 장전 & 사격
        if inp['reload'] and self.d['reload']==0 and w['mag']!=-1 and self.d['ammo']<w['mag']:
            self.d['reload'] = w['rl']; self.d['ammo'] = 0

        if inp['shoot'] and self.timer<=0 and self.d['reload']==0:
            if self.d['use_g'] and self.d['grenades']>0:
                bullets.append({"x":self.d['x'], "y":self.d['y'], "dx":self.d['dir'][0], "dy":self.d['dir'][1], "t":"grenade", "life":60, "own":id(self)})
                self.timer = 40; self.d['grenades'] -= 1; self.d['use_g'] = False
            elif not self.d['use_g'] and (self.d['ammo']>0 or w['mag']==-1):
                bullets.append({"x":self.d['x'], "y":self.d['y'], "dx":self.d['dir'][0], "dy":self.d['dir'][1], "t":w['type'], "life":8 if w['type']=="melee" else 100, "own":id(self), "dmg":w['dmg'], "spd":w['spd']})
                if w['type']=="melee":
                    bullets[-1]['x'] += self.d['dir'][0]*20; bullets[-1]['y'] += self.d['dir'][1]*20
                self.timer = w['cd']
                if w['n']=="Sniper Rifle": g_data.effects.append(["shake", 5])
                if w['mag']!=-1:
                    self.d['ammo'] -= 1
                    if self.d['ammo']<=0: self.d['reload'] = w['rl']

sp1 = SPlayer(g_data.p1)
sp2 = SPlayer(g_data.p2)
item_timer = 0
map_pts = []
m_obs_data = []

def srv_load_map(idx):
    global map_pts, m_obs_data
    g_data.bullets.clear(); g_data.items.clear()
    g_data.p1.update({"x":100, "y":300, "hp":100, "shield":0})
    g_data.p2.update({"x":700, "y":300, "hp":100, "shield":0})
    
    if idx == 0: # Classic
        g_data.obs = [[150,100,100,150], [550,100,100,150], [350,250,100,100], [150,400,100,100], [550,400,100,100]]
        g_data.m_obs = []; m_obs_data = []; map_pts = [(400,100), (400,500)]
    elif idx == 1: # Factory
        g_data.obs = [[380,0,40,200], [380,400,40,200], [150,250,50,100], [600,250,50,100]]
        g_data.m_obs = [[250,100,50,100], [500,400,50,100]]
        m_obs_data = [{"idx":0, "sy":100, "dir":1}, {"idx":1, "sy":400, "dir":1}]
        map_pts = [(400,300), (100,100), (700,500)]
    elif idx == 2: # Crossfire (New Map)
        g_data.obs = [[200,150,100,100], [500,150,100,100], [200,350,100,100], [500,350,100,100], [350,250,100,100]]
        g_data.m_obs = []; m_obs_data = []; map_pts = [(400,100), (400,500), (100,300), (700,300)]

# --- 루프 ---
ip_inp = ""
while True:
    screen.fill(BLACK)
    ox = random.randint(-screen_shake, screen_shake) if screen_shake>0 else 0
    oy = random.randint(-screen_shake, screen_shake) if screen_shake>0 else 0
    if screen_shake>0: screen_shake-=1

    keys = pygame.key.get_pressed()
    m_btns = pygame.mouse.get_pressed()
    mx, my = pygame.mouse.get_pos()
    
    my_inputs = {'up':keys[pygame.K_w], 'down':keys[pygame.K_s], 'left':keys[pygame.K_a], 'right':keys[pygame.K_d], 
                 'dash':keys[pygame.K_SPACE], 'swap':keys[pygame.K_q], 'shoot':m_btns[0], 'reload':m_btns[2], 'mx':mx, 'my':my}

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            if my_socket: my_socket.close()
            pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN:
            if g_data.phase == "MENU":
                if e.key == pygame.K_1: is_host = True; threading.Thread(target=host_server, daemon=True).start(); g_data.phase = "HOSTING"
                elif e.key == pygame.K_2: g_data.phase = "JOINING"
            elif g_data.phase == "JOINING":
                if e.key == pygame.K_RETURN: threading.Thread(target=join_server, args=(ip_inp,), daemon=True).start()
                elif e.key == pygame.K_BACKSPACE: ip_inp = ip_inp[:-1]
                elif e.unicode.isnumeric() or e.unicode=='.': ip_inp += e.unicode
            elif g_data.phase == "SELECT_MAP" and is_host:
                if e.key == pygame.K_LEFT: g_data.map_idx = (g_data.map_idx - 1) % 3
                elif e.key == pygame.K_RIGHT: g_data.map_idx = (g_data.map_idx + 1) % 3
                elif e.key == pygame.K_RETURN: srv_load_map(g_data.map_idx); g_data.phase = "CHAR_SELECT"
            elif g_data.phase == "CHAR_SELECT":
                p = g_data.p1 if is_host else g_data.p2
                if not p['ready']:
                    if e.key == pygame.K_a: p['c_idx'] = (p['c_idx'] - 1) % 3
                    elif e.key == pygame.K_d: p['c_idx'] = (p['c_idx'] + 1) % 3
                    elif e.key == pygame.K_RETURN: p['ready'] = True
                elif e.key == pygame.K_BACKSPACE: p['ready'] = False
            elif g_data.phase == "GAME_OVER" and is_host and e.key == pygame.K_r:
                g_data.p1['ready'] = False; g_data.p2['ready'] = False; g_data.phase = "SELECT_MAP"

    # --- 서버 로직 (방장만 연산) ---
    if is_host and g_data.phase == "PLAYING":
        sp1.update(my_inputs, g_data.bullets)
        sp2.update(p2_inputs, g_data.bullets)

        # 동적 장애물
        for mo in m_obs_data:
            rect = g_data.m_obs[mo['idx']]
            rect[1] += 2 * mo['dir']
            if abs(rect[1] - mo['sy']) > 150: mo['dir'] *= -1

        # 아이템 스폰
        item_timer += 1
        if item_timer > 300 and len(g_data.items) < 2:
            item_timer = 0; pt = random.choice(map_pts)
            if not any(math.hypot(i[0]-pt[0], i[1]-pt[1])<30 for i in g_data.items):
                g_data.items.append([pt[0], pt[1], random.choice(["HEAL", "SHIELD", "GRENADE", "SPEED"])])

        # 아이템 획득
        for p, sp in [(g_data.p1, sp1), (g_data.p2, sp2)]:
            pr = pygame.Rect(p['x']-16, p['y']-16, 32, 32)
            for it in g_data.items[:]:
                if pr.colliderect(pygame.Rect(it[0]-12, it[1]-12, 24, 24)):
                    if it[2] == "HEAL": p['hp'] = min(100, p['hp']+30)
                    elif it[2] == "SHIELD": p['shield'] = 50
                    elif it[2] == "GRENADE": p['grenades'] += 1
                    elif it[2] == "SPEED": sp.spd_buff = 600
                    g_data.items.remove(it)

        # 총알 업데이트 & 충돌
        p1r = pygame.Rect(g_data.p1['x']-16, g_data.p1['y']-16, 32, 32)
        p2r = pygame.Rect(g_data.p2['x']-16, g_data.p2['y']-16, 32, 32)
        
        for b in g_data.bullets[:]:
            if b['t'] != "melee": b['x'] += b['dx']*b['spd']; b['y'] += b['dy']*b['spd']
            b['life'] -= 1
            sz = 12 if b['t']=="grenade" else (24 if b['t']=="melee" else 6)
            br = pygame.Rect(b['x']-sz//2, b['y']-sz//2, sz, sz)
            
            # 수명 다함
            if b['life'] <= 0 or b['x']<0 or b['x']>WIDTH or b['y']<0 or b['y']>HEIGHT:
                if b['t']=="grenade":
                    g_data.effects.extend([["explode", b['x'], b['y']], ["shake", 10]])
                    for p, pr in [(g_data.p1, p1r), (g_data.p2, p2r)]:
                        if math.hypot(p['x']-b['x'], p['y']-b['y']) < 80: p['hp'] -= 60
                if b in g_data.bullets: g_data.bullets.remove(b)
                continue
                
            # 장애물 충돌
            hit_obs = False
            for ob in g_data.obs + g_data.m_obs:
                if br.colliderect(pygame.Rect(ob)):
                    if b['t'] != "melee":
                        if b['t']=="grenade":
                            g_data.effects.extend([["explode", b['x'], b['y']], ["shake", 10]])
                            for p, pr in [(g_data.p1, p1r), (g_data.p2, p2r)]:
                                if math.hypot(p['x']-b['x'], p['y']-b['y']) < 80: p['hp'] -= 60
                        if b in g_data.bullets: g_data.bullets.remove(b)
                        hit_obs = True; break
            if hit_obs: continue

            # 플레이어 피격
            for p, pr, col in [(g_data.p1, p1r, RED), (g_data.p2, p2r, BLUE)]:
                if b['own'] != id(sp1) if p==g_data.p1 else id(sp2):
                    if br.colliderect(pr):
                        if b['t']=="grenade":
                            g_data.effects.extend([["explode", b['x'], b['y']], ["shake", 10]])
                            for pp in [g_data.p1, g_data.p2]:
                                if math.hypot(pp['x']-b['x'], pp['y']-b['y']) < 80: pp['hp'] -= 60
                        else:
                            dmg = b['dmg']
                            if p['shield'] >= dmg: p['shield'] -= dmg
                            else: dmg -= p['shield']; p['shield'] = 0; p['hp'] -= dmg
                            g_data.effects.append(["hit", b['x'], b['y'], col])
                        if b in g_data.bullets: g_data.bullets.remove(b)

        if g_data.p1['hp'] <= 0 or g_data.p2['hp'] <= 0: g_data.phase = "GAME_OVER"

    # --- 방장 상태 전환 ---
    if is_host and g_data.phase == "CHAR_SELECT" and g_data.p1['ready'] and g_data.p2['ready']:
        g_data.p1['ammo'] = CHAR_DATA[g_data.p1['c_idx']]['wp']['mag']
        g_data.p2['ammo'] = CHAR_DATA[g_data.p2['c_idx']]['wp']['mag']
        g_data.phase = "PLAYING"

    # --- 렌더링 (클라이언트/서버 공통) ---
    if g_data.phase == "MENU":
        draw_txt("ONLINE MULTIPLAYER: FINAL", 50, WHITE, WIDTH//2, HEIGHT//3)
        draw_txt("1. Create Room (Host)", 30, RED, WIDTH//2, HEIGHT//2)
        draw_txt("2. Join Room (Client)", 30, BLUE, WIDTH//2, HEIGHT//2+50)
        draw_txt(f"Your IP: {get_ip()}", 20, GRAY, WIDTH//2, HEIGHT-50)
    elif g_data.phase == "HOSTING": draw_txt(f"Waiting for player... Tell IP: {get_ip()}", 30, YELLOW, WIDTH//2, HEIGHT//2)
    elif g_data.phase == "JOINING":
        draw_txt("ENTER HOST IP", 40, WHITE, WIDTH//2, HEIGHT//3)
        draw_txt(ip_inp + "_", 30, YELLOW, WIDTH//2, HEIGHT//2)
        draw_txt("Press ENTER to Connect", 20, GRAY, WIDTH//2, HEIGHT//2+50)
    elif g_data.phase == "SELECT_MAP":
        maps = ["Classic Arena", "Moving Factory", "Crossfire (New!)"]
        draw_txt("SELECT MAP (Host Only)", 50, WHITE, WIDTH//2, HEIGHT//4)
        draw_txt(f"< {maps[g_data.map_idx]} >", 40, YELLOW, WIDTH//2, HEIGHT//2)
    elif g_data.phase == "CHAR_SELECT":
        draw_txt("SELECT CHARACTER", 50, WHITE, WIDTH//2, 50)
        for i, (p, col, x, role) in enumerate([(g_data.p1, RED, WIDTH//4, "P1"), (g_data.p2, BLUE, WIDTH*3//4, "P2")]):
            draw_txt(role, 30, col, x, 150)
            draw_txt(f"< {CHAR_DATA[p['c_idx']]['name']} >", 40, WHITE, x, 250)
            draw_txt(f"Weapon: {CHAR_DATA[p['c_idx']]['wp']['n']}", 20, GRAY, x, 300)
            if p['ready']: draw_txt("READY!", 40, GREEN, x, 400)
            else: draw_txt("A/D to Change, ENTER to Ready", 15, GRAY, x, 400)
    elif g_data.phase in ["PLAYING", "GAME_OVER"]:
        # 배경 & 장애물
        for x in range(0, WIDTH, 50): pygame.draw.line(screen, DARK_GRAY, (x+ox, 0), (x+ox, HEIGHT))
        for y in range(0, HEIGHT, 50): pygame.draw.line(screen, DARK_GRAY, (0, y+oy), (WIDTH, y+oy))
        for ob in g_data.obs + g_data.m_obs:
            pygame.draw.rect(screen, GRAY, (ob[0]+ox, ob[1]+oy, ob[2], ob[3]))
            pygame.draw.rect(screen, WHITE, (ob[0]+ox, ob[1]+oy, ob[2], ob[3]), 2)
            
        # 아이템
        cols = {"HEAL":GREEN, "SHIELD":CYAN, "GRENADE":ORANGE, "SPEED":YELLOW}
        syms = {"HEAL":"+", "SHIELD":"S", "GRENADE":"G", "SPEED":">>"}
        for it in g_data.items:
            rect = pygame.Rect(it[0]-12+ox, it[1]-12+oy, 24, 24)
            pygame.draw.rect(screen, cols[it[2]], rect, border_radius=4)
            draw_txt(syms[it[2]], 16, BLACK, it[0]+ox, it[1]+oy)

        # 파티클 업데이트
        for pt in particles[:]: pt.update(); pt.draw(screen, ox, oy); (particles.remove(pt) if pt.life<=0 else None)

        # 총알
        for b in g_data.bullets:
            sz, col = (12, GREEN) if b['t']=="grenade" else ((24, WHITE) if b['t']=="melee" else (6, YELLOW))
            if b['t']=="melee": pygame.draw.circle(screen, col, (int(b['x']+ox), int(b['y']+oy)), sz//2, 2)
            else: pygame.draw.circle(screen, col, (int(b['x']+ox), int(b['y']+oy)), sz//2)

        # 플레이어 렌더링
        for p, col in [(g_data.p1, RED), (g_data.p2, BLUE)]:
            px, py = p['x']+ox, p['y']+oy
            shape = CHAR_DATA[p['c_idx']]['shape']
            if shape=="circle": pygame.draw.circle(screen, col, (int(px), int(py)), 16)
            else: pygame.draw.rect(screen, col, (px-16, py-16, 32, 32), border_radius=4)
            if p['shield']>0: pygame.draw.circle(screen, CYAN, (int(px), int(py)), 22, 2)
            
            # 총구 방향 (마우스 방향)
            ex, ey = px + p['dir'][0]*20, py + p['dir'][1]*20
            if p['use_g']: pygame.draw.circle(screen, GREEN, (int(px+p['dir'][0]*15), int(py+p['dir'][1]*15)), 5)
            elif shape=="sniper": 
                pygame.draw.line(screen, WHITE, (px, py), (px+p['dir'][0]*30, py+p['dir'][1]*30), 3)
                pygame.draw.circle(screen, GRAY, (int(px+p['dir'][0]*10), int(py+p['dir'][1]*10)), 4)
            else: pygame.draw.line(screen, WHITE, (px, py), (ex, ey), 4 if shape=="square" else 2)

            # 체력바
            pygame.draw.rect(screen, GRAY, (px-16, py-24, 32, 6))
            pygame.draw.rect(screen, GREEN if p['hp']>50 else RED, (px-16, py-24, max(0, p['hp']/100)*32, 6))

        # UI (탄약 등)
        for is_l, p, role in [(True, g_data.p1, "P1"), (False, g_data.p2, "P2")]:
            bx = 20 if is_l else WIDTH-180
            draw_txt(f"{role} HP: {int(p['hp'])}", 20, WHITE, bx, HEIGHT-60, False)
            if p['use_g']: a_txt = f"GRENADES: {p['grenades']}"; ac = ORANGE
            elif CHAR_DATA[p['c_idx']]['wp']['mag']==-1: a_txt = "AMMO: INF"; ac = YELLOW
            elif p['reload']>0: a_txt = "RELOADING..."; ac = RED
            else: a_txt = f"AMMO: {p['ammo']} / {CHAR_DATA[p['c_idx']]['wp']['mag']}"; ac = YELLOW
            draw_txt(a_txt, 20, ac, bx, HEIGHT-30, False)

        if g_data.phase == "GAME_OVER":
            over = pygame.Surface((WIDTH, HEIGHT)); over.set_alpha(150); screen.blit(over, (0,0))
            draw_txt("P2 WINS!" if g_data.p1['hp']<=0 else "P1 WINS!", 70, BLUE if g_data.p1['hp']<=0 else RED, WIDTH//2, HEIGHT//2)
            if is_host: draw_txt("Press 'R' to return to Map Select", 30, WHITE, WIDTH//2, HEIGHT//2+60)

    pygame.display.flip(); clock.tick(60)