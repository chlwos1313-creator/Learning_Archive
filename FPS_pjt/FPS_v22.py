import pygame, sys, socket, threading, pickle, math, random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Online Tactical Shooter - Chat Lag Fixed")
clock = pygame.time.Clock()

# --- 색상 및 설정 ---
WHITE, BLACK, GRAY, DARK_GRAY = (255, 255, 255), (20, 20, 22), (100, 100, 110), (50, 50, 60)
RED, BLUE, YELLOW, GREEN = (255, 70, 70), (70, 170, 255), (255, 220, 50), (70, 255, 70)
ORANGE, CYAN = (255, 150, 0), (0, 255, 255)
PORT = 5555

# --- 캐릭터 데이터 ---
CHAR_DATA = [
    {"name": "Rifle", "speed": 4.5, "shape": "square", "wp": {"n": "Assault Rifle", "cd": 8, "spd": 15, "dmg": 10, "mag": -1, "rl": 0, "type": "gun"}},
    {"name": "Sniper", "speed": 3.5, "shape": "sniper", "wp": {"n": "Sniper Rifle", "cd": 50, "spd": 25, "dmg": 50, "mag": 5, "rl": 100, "type": "gun"}},
    {"name": "Knife", "speed": 6.5, "shape": "circle", "wp": {"n": "Combat Knife", "cd": 15, "spd": 0, "dmg": 35, "mag": -1, "rl": 0, "type": "melee"}},
    {"name": "Random (?)", "speed": 4.0, "shape": "circle", "wp": {"n": "???", "cd": 0, "spd": 0, "dmg": 0, "mag": 0, "rl": 0, "type": "none"}},
    {"name": "Bazooka (Hidden)", "speed": 3.0, "shape": "square", "wp": {"n": "Rocket Launcher", "cd": 80, "spd": 12, "dmg": 80, "mag": 3, "rl": 120, "type": "bazooka"}}
]

def create_player(team):
    return {'team': team, 'c_idx': 0, 'ready': False, 'hp': 100, 'shield': 0, 'x': -100, 'y': -100,
            'ammo': 0, 'grenades': 0, 'reload': 0, 'use_g': False, 'mx': 0, 'my': 0, 'dir': (1,0),
            'timer': 0, 'dash_cd': 0, 'spd_buff': 0, 'swap_p': False, 'dash_p': False,
            'last_t': 0, 'last_a': 0, 'last_d': 0, 'last_rdy': 0}

class GameState:
    def __init__(self):
        self.phase = "MENU"
        self.map_idx = 0
        self.round_num = 1
        self.red_score = 0
        self.blue_score = 0
        self.players = {}
        self.bullets = []
        self.items = []
        self.obs = []
        self.m_obs = []
        self.effects = []
        self.chat = []
        self.msg = ""
        self.timer = 0

is_host = False
my_id = -1
my_socket = None
g_data = GameState()
pickled_g_data = None
server_inputs = {} 
my_inputs = {'up':0, 'down':0, 'left':0, 'right':0, 'dash':0, 'shoot':0, 'reload':0, 'swap':0, 'mx':0, 'my':0, 
             'chat':None, 'a_t':0, 'a_a':0, 'a_d':0, 'a_rdy':0}

particles = []
screen_shake = 0
eff_counter = 0
processed_effs = set()
is_typing = False
chat_txt = ""
pending_chat = None # 1회성 채팅 전송을 위한 변수

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
def draw_txt(txt, size, col, x, y, center=True, font_name="malgungothic, arial"):
    font = pygame.font.SysFont(font_name, size, bold=True)
    surf = font.render(txt, True, col)
    rect = surf.get_rect(center=(x,y)) if center else surf.get_rect(topleft=(x,y))
    screen.blit(surf, rect)

def trigger_effect(eff):
    global eff_counter
    eff_counter += 1
    g_data.effects.append((eff_counter, eff))
    if len(g_data.effects) > 50: g_data.effects.pop(0)

def accept_clients():
    global pickled_g_data
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try: server.bind(('', PORT))
    except: g_data.phase = "MENU"; return
    server.listen(6)
    next_id = 1
    
    while g_data.phase != "MENU":
        try:
            conn, addr = server.accept()
            conn.sendall(pickle.dumps(next_id))
            g_data.players[next_id] = create_player(team=next_id % 2)
            threading.Thread(target=handle_client, args=(conn, next_id), daemon=True).start()
            next_id += 1
        except: break

def handle_client(conn, pid):
    conn_file = conn.makefile('rb')
    while g_data.phase != "MENU":
        try:
            server_inputs[pid] = pickle.load(conn_file)
            if pickled_g_data: conn.sendall(pickled_g_data)
        except: break
    if pid in g_data.players: del g_data.players[pid]
    conn.close()

def join_server(ip):
    global g_data, my_socket, my_id
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.connect((ip, PORT))
        my_id = pickle.loads(my_socket.recv(1024))
        sock_file = my_socket.makefile('rb')
        while g_data.phase != "MENU":
            my_socket.sendall(pickle.dumps(my_inputs))
            g_data = pickle.load(sock_file)
            
            for eid, e in g_data.effects:
                if eid not in processed_effs:
                    processed_effs.add(eid)
                    if e[0]=="shake": add_shake(e[1])
                    elif e[0]=="explode": 
                        for _ in range(30): particles.append(Particle(e[1], e[2], ORANGE, 5, 30))
                    elif e[0]=="hit":
                        for _ in range(5): particles.append(Particle(e[1], e[2], e[3], 4, 20))
    except: pass
    finally:
        if my_socket: my_socket.close()
        g_data.phase = "MENU"

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try: s.connect(('10.255.255.255', 1)); ip = s.getsockname()[0]
    except: ip = '127.0.0.1'
    finally: s.close()
    return ip

LOCAL_IP = get_ip()

map_pts, m_obs_data = [], []
def srv_load_map(idx):
    global map_pts, m_obs_data
    idx = idx % 5
    g_data.bullets.clear(); g_data.items.clear()
    
    if idx == 0:
        g_data.obs = [[150,100,100,150], [550,100,100,150], [350,250,100,100], [150,400,100,100], [550,400,100,100]]
        g_data.m_obs = []; m_obs_data = []; map_pts = [(400,100), (400,500)]
    elif idx == 1:
        g_data.obs = [[380,0,40,200], [380,400,40,200], [150,250,50,100], [600,250,50,100]]
        g_data.m_obs = [[250,100,50,100], [500,400,50,100]]
        m_obs_data = [{"idx":0, "sy":100, "dir":1}, {"idx":1, "sy":400, "dir":1}]
        map_pts = [(400,300), (100,100), (700,500)]
    elif idx == 2:
        g_data.obs = [[200,150,100,100], [500,150,100,100], [200,350,100,100], [500,350,100,100], [350,250,100,100]]
        g_data.m_obs = []; m_obs_data = []; map_pts = [(400,100), (400,500), (100,300), (700,300)]
    elif idx == 3: 
        g_data.obs = [[150,150,200,50], [450,150,200,50], [150,400,200,50], [450,400,200,50], [380,250,40,100]]
        g_data.m_obs = []; m_obs_data = []; map_pts = [(400,200), (400,400)]
    elif idx == 4: 
        g_data.obs = [[200, 200, 400, 200]] 
        g_data.m_obs = []; m_obs_data = []; map_pts = [(400,100), (400,500)]

    red_spawns = [(100, 150), (100, 300), (100, 450), (50, 150), (50, 300), (50, 450)]
    blue_spawns = [(700, 150), (700, 300), (700, 450), (750, 150), (750, 300), (750, 450)]
    r_idx, b_idx = 0, 0
    
    for pid, p in g_data.players.items():
        p['hp'], p['shield'] = 100, 0
        if p['c_idx'] == 3: p['c_idx'] = 4 if random.random() < 0.1 else random.randint(0, 2)
        p['ammo'] = CHAR_DATA[p['c_idx']]['wp']['mag']
        
        if p['team'] == 0:
            p['x'], p['y'] = red_spawns[r_idx % len(red_spawns)]; r_idx += 1; p['dir'] = (1,0)
        else:
            p['x'], p['y'] = blue_spawns[b_idx % len(blue_spawns)]; b_idx += 1; p['dir'] = (-1,0)

ip_inp = ""
item_timer = 0

while True:
    screen.fill(BLACK)
    ox = random.randint(-screen_shake, screen_shake) if screen_shake>0 else 0
    oy = random.randint(-screen_shake, screen_shake) if screen_shake>0 else 0
    if screen_shake>0: screen_shake-=1

    keys = pygame.key.get_pressed()
    m_btns = pygame.mouse.get_pressed()
    mx, my = pygame.mouse.get_pos()
    
    # [핵심 픽스] pending_chat을 넣어주고, 즉시 변수를 비워 1회만 전송되게 합니다.
    my_inputs.update({
        'up': keys[pygame.K_w] and not is_typing, 'down': keys[pygame.K_s] and not is_typing, 
        'left': keys[pygame.K_a] and not is_typing, 'right': keys[pygame.K_d] and not is_typing, 
        'dash': keys[pygame.K_SPACE] and not is_typing, 'swap': keys[pygame.K_q] and not is_typing, 
        'shoot': m_btns[0] and not is_typing, 'reload': (m_btns[2] or keys[pygame.K_r]) and not is_typing, 
        'mx': mx, 'my': my, 'chat': pending_chat
    })
    pending_chat = None 

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            g_data.phase = "MENU"
            if my_socket: my_socket.close()
            pygame.quit(); sys.exit()
            
        if e.type == pygame.KEYDOWN:
            # 채팅 입력 로직 (모든 페이즈에서 작동)
            if g_data.phase in ["LOBBY", "PLAYING", "ROUND_OVER", "MATCH_OVER"]:
                if e.key == pygame.K_RETURN:
                    if is_typing:
                        if chat_txt.strip(): pending_chat = chat_txt
                        is_typing = False; chat_txt = ""
                    else: is_typing = True
                elif is_typing:
                    if e.key == pygame.K_ESCAPE: is_typing = False; chat_txt = ""
                    elif e.key == pygame.K_BACKSPACE: chat_txt = chat_txt[:-1]
                    else: chat_txt += e.unicode

            # 게임 & 로비 조작 로직 (채팅 중이 아닐 때만)
            if not is_typing:
                if e.key == pygame.K_t: my_inputs['a_t'] += 1
                if e.key == pygame.K_a: my_inputs['a_a'] += 1
                if e.key == pygame.K_d: my_inputs['a_d'] += 1
                if e.key == pygame.K_SPACE: my_inputs['a_rdy'] += 1 # [핵심 픽스] 레디 키를 SPACE로 분리!
                
                if e.key == pygame.K_ESCAPE and g_data.phase in ["LOBBY", "JOINING"]:
                    g_data.phase = "MENU"; ip_inp = ""
                    if is_host: is_host = False
                if g_data.phase == "JOINING" and e.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    try: pygame.scrap.init(); txt = pygame.scrap.get(pygame.SCRAP_TEXT)
                    except: txt = None
                    if txt: ip_inp += txt.decode('utf-8').replace('\0', '')

                if g_data.phase == "MENU":
                    if e.key == pygame.K_1: 
                        is_host = True; my_id = 0
                        g_data.players.clear()
                        g_data.players[0] = create_player(0)
                        threading.Thread(target=accept_clients, daemon=True).start()
                        g_data.phase = "LOBBY"
                    elif e.key == pygame.K_2: g_data.phase = "JOINING"
                elif g_data.phase == "JOINING":
                    if e.key == pygame.K_RETURN: threading.Thread(target=join_server, args=(ip_inp,), daemon=True).start()
                    elif e.key == pygame.K_BACKSPACE: ip_inp = ip_inp[:-1]
                    elif e.unicode.isnumeric() or e.unicode=='.': ip_inp += e.unicode

    # --- 서버 코어 로직 (방장 전용) ---
    if is_host:
        server_inputs[0] = my_inputs.copy() 
        
        for pid, inp in server_inputs.items():
            if inp.get('chat'):
                g_data.chat.append({"txt": f"Player {pid}: {inp['chat']}", "life": 300})
                inp['chat'] = None # 서버에서도 1회 적용 후 비움
                
        for c in g_data.chat[:]:
            c['life'] -= 1
            if c['life'] <= 0: g_data.chat.remove(c)

        if g_data.phase == "LOBBY":
            all_ready = len(g_data.players) > 0
            for pid, p in g_data.players.items():
                inp = server_inputs.get(pid, {})
                if inp.get('a_t', 0) > p['last_t']: p['team'] = 1 - p['team']; p['last_t'] = inp['a_t']
                if inp.get('a_a', 0) > p['last_a']: p['c_idx'] = (p['c_idx'] - 1) % 4; p['last_a'] = inp['a_a']
                if inp.get('a_d', 0) > p['last_d']: p['c_idx'] = (p['c_idx'] + 1) % 4; p['last_d'] = inp['a_d']
                if inp.get('a_rdy', 0) > p['last_rdy']: p['ready'] = not p['ready']; p['last_rdy'] = inp['a_rdy']
                if not p['ready']: all_ready = False
                
            if all_ready:
                g_data.red_score, g_data.blue_score, g_data.round_num = 0, 0, 1
                g_data.map_idx = 0
                srv_load_map(g_data.map_idx)
                g_data.msg = "ROUND 1 START!"
                g_data.phase = "PLAYING"

        elif g_data.phase == "PLAYING":
            for pid, p in g_data.players.items():
                if p['hp'] <= 0: continue
                inp = server_inputs.get(pid, {})
                w = CHAR_DATA[p['c_idx']]['wp']
                
                if p['timer'] > 0: p['timer'] -= 1
                if p['reload'] > 0:
                    p['reload'] -= 1
                    if p['reload'] == 0: p['ammo'] = w['mag']
                if p['dash_cd'] > 0: p['dash_cd'] -= 1
                elif p['dash_cd'] < 0: p['dash_cd'] += 1
                if p['spd_buff'] > 0: p['spd_buff'] -= 1

                p['mx'], p['my'] = inp.get('mx', p['x']), inp.get('my', p['y'])
                dx_m, dy_m = p['mx'] - p['x'], p['my'] - p['y']
                mag_m = math.hypot(dx_m, dy_m) or 1
                p['dir'] = (dx_m/mag_m, dy_m/mag_m)

                if inp.get('swap') and not p['swap_p']: p['use_g'] = not p['use_g']; p['swap_p'] = True
                elif not inp.get('swap'): p['swap_p'] = False

                spd = CHAR_DATA[p['c_idx']]['speed'] * (1.5 if p['spd_buff']>0 else 1.0)
                if inp.get('dash') and p['dash_cd'] == 0 and not p['dash_p']: p['dash_cd'] = 10; p['dash_p'] = True
                elif not inp.get('dash'): p['dash_p'] = False
                
                if p['dash_cd'] > 0: spd *= 3
                if p['dash_cd'] == 1: p['dash_cd'] = -60

                old_px, old_py = p['x'], p['y']
                move_x, move_y = 0, 0
                if inp.get('up'): move_y -= 1
                if inp.get('down'): move_y += 1
                if inp.get('left'): move_x -= 1
                if inp.get('right'): move_x += 1
                
                if move_x!=0 or move_y!=0:
                    mag = math.hypot(move_x, move_y)
                    p['x'] += (move_x/mag)*spd; p['y'] += (move_y/mag)*spd

                rect = pygame.Rect(p['x']-16, p['y']-16, 32, 32)
                for ob in g_data.obs + g_data.m_obs:
                    if rect.colliderect(pygame.Rect(ob)): p['x'], p['y'] = old_px, old_py
                p['x'] = max(16, min(WIDTH-16, p['x']))
                p['y'] = max(16, min(HEIGHT-16, p['y']))

                if inp.get('reload') and p['reload']==0 and w['mag']!=-1 and p['ammo']<w['mag']:
                    p['reload'] = w['rl']; p['ammo'] = 0

                if inp.get('shoot') and p['timer']<=0 and p['reload']==0:
                    if p['use_g'] and p['grenades']>0:
                        g_data.bullets.append({"x":p['x'], "y":p['y'], "dx":p['dir'][0], "dy":p['dir'][1], "t":"grenade", "life":60, "own":pid, "team":p['team'], "spd":8})
                        p['timer'] = 40; p['grenades'] -= 1; p['use_g'] = False
                    elif not p['use_g'] and (p['ammo']>0 or w['mag']==-1):
                        life_time = 8 if w['type']=="melee" else (60 if w['type']=="bazooka" else 100)
                        g_data.bullets.append({"x":p['x'], "y":p['y'], "dx":p['dir'][0], "dy":p['dir'][1], "t":w['type'], "life":life_time, "own":pid, "team":p['team'], "dmg":w['dmg'], "spd":w['spd']})
                        if w['type']=="melee":
                            g_data.bullets[-1]['x'] += p['dir'][0]*20; g_data.bullets[-1]['y'] += p['dir'][1]*20
                        p['timer'] = w['cd']
                        if w['n'] in ["Sniper Rifle", "Rocket Launcher"]: trigger_effect(["shake", 5])
                        if w['mag']!=-1:
                            p['ammo'] -= 1
                            if p['ammo']<=0: p['reload'] = w['rl']

            for mo in m_obs_data:
                rect = g_data.m_obs[mo['idx']]
                rect[1] += 2 * mo['dir']
                if abs(rect[1] - mo['sy']) > 150: mo['dir'] *= -1

            item_timer += 1
            if item_timer > 300 and len(g_data.items) < 3:
                item_timer = 0; pt = random.choice(map_pts)
                if not any(math.hypot(i[0]-pt[0], i[1]-pt[1])<30 for i in g_data.items):
                    g_data.items.append([pt[0], pt[1], random.choice(["HEAL", "SHIELD", "GRENADE", "SPEED"])])

            for pid, p in g_data.players.items():
                if p['hp'] <= 0: continue
                pr = pygame.Rect(p['x']-16, p['y']-16, 32, 32)
                for it in g_data.items[:]:
                    if pr.colliderect(pygame.Rect(it[0]-12, it[1]-12, 24, 24)):
                        if it[2] == "HEAL": p['hp'] = min(100, p['hp']+30)
                        elif it[2] == "SHIELD": p['shield'] = 50
                        elif it[2] == "GRENADE": p['grenades'] += 1
                        elif it[2] == "SPEED": p['spd_buff'] = 600
                        g_data.items.remove(it)

            for b in g_data.bullets[:]:
                if b['t'] != "melee": b['x'] += b['dx']*b['spd']; b['y'] += b['dy']*b['spd']
                b['life'] -= 1
                sz = 16 if b['t']=="bazooka" else (12 if b['t']=="grenade" else (24 if b['t']=="melee" else 6))
                br = pygame.Rect(b['x']-sz//2, b['y']-sz//2, sz, sz)
                
                should_explode = False
                if b['life'] <= 0 or b['x']<0 or b['x']>WIDTH or b['y']<0 or b['y']>HEIGHT: should_explode = True
                
                if not should_explode:
                    for ob in g_data.obs + g_data.m_obs:
                        if br.colliderect(pygame.Rect(ob)) and b['t'] != "melee":
                            should_explode = True; break

                if not should_explode:
                    for pid, p in g_data.players.items():
                        if p['hp']>0 and b['team'] != p['team'] and br.colliderect(pygame.Rect(p['x']-16, p['y']-16, 32, 32)):
                            if b['t'] not in ["grenade", "bazooka"]:
                                dmg = b['dmg']
                                if p['shield'] >= dmg: p['shield'] -= dmg
                                else: dmg -= p['shield']; p['shield'] = 0; p['hp'] -= dmg
                                trigger_effect(["hit", b['x'], b['y'], RED if p['team']==0 else BLUE])
                            should_explode = True; break

                if should_explode:
                    if b['t'] in ["grenade", "bazooka"]:
                        trigger_effect(["explode", b['x'], b['y']])
                        trigger_effect(["shake", 15 if b['t']=="bazooka" else 10])
                        for ptid, pt in g_data.players.items():
                            if pt['hp'] > 0 and pt['team'] != b['team']:
                                if math.hypot(pt['x']-b['x'], pt['y']-b['y']) < 80: pt['hp'] -= (80 if b['t']=="bazooka" else 60)
                    if b in g_data.bullets: g_data.bullets.remove(b)

            red_alive = sum(1 for p in g_data.players.values() if p['team']==0 and p['hp']>0)
            blue_alive = sum(1 for p in g_data.players.values() if p['team']==1 and p['hp']>0)
            
            if red_alive == 0 or blue_alive == 0:
                if red_alive == 0: g_data.blue_score += 1; g_data.msg = "BLUE WINS ROUND!"
                if blue_alive == 0: g_data.red_score += 1; g_data.msg = "RED WINS ROUND!"
                
                if g_data.red_score >= 3 or g_data.blue_score >= 3:
                    g_data.phase = "MATCH_OVER"
                    g_data.msg = "RED WINS MATCH!" if g_data.red_score >= 3 else "BLUE WINS MATCH!"
                else: g_data.phase = "ROUND_OVER"
                g_data.timer = 180 

        elif g_data.phase in ["ROUND_OVER", "MATCH_OVER"]:
            g_data.timer -= 1
            if g_data.timer <= 0:
                if g_data.phase == "MATCH_OVER":
                    g_data.phase = "LOBBY"
                    for p in g_data.players.values(): p['ready'] = False
                else:
                    g_data.round_num += 1
                    g_data.map_idx = g_data.round_num - 1
                    srv_load_map(g_data.map_idx)
                    g_data.msg = f"ROUND {g_data.round_num} START!"
                    g_data.phase = "PLAYING"

        pickled_g_data = pickle.dumps(g_data) 

    # --- 렌더링 ---
    if g_data.phase == "MENU":
        draw_txt("ONLINE MULTIPLAYER: 3v3 TEAM FPS", 45, WHITE, WIDTH//2, HEIGHT//3)
        draw_txt("1. Create Server (Host)", 30, RED, WIDTH//2, HEIGHT//2)
        draw_txt("2. Join Server (Client)", 30, BLUE, WIDTH//2, HEIGHT//2+50)
        draw_txt(f"Your IP: {LOCAL_IP}", 20, GRAY, WIDTH//2, HEIGHT-50)
        
    elif g_data.phase == "JOINING":
        draw_txt("ENTER HOST IP", 40, WHITE, WIDTH//2, HEIGHT//3)
        draw_txt(ip_inp + "_", 30, YELLOW, WIDTH//2, HEIGHT//2)
        draw_txt("Press ENTER to Connect / ESC to Cancel (Ctrl+V Paste)", 20, GRAY, WIDTH//2, HEIGHT//2+50)
    
    elif g_data.phase == "LOBBY":
        draw_txt("TEAM LOBBY (Max 6 Players)", 50, WHITE, WIDTH//2, 40)
        draw_txt(f"Host IP to Join: {LOCAL_IP}", 25, GREEN, WIDTH//2, 80)
        pygame.draw.line(screen, DARK_GRAY, (WIDTH//2, 100), (WIDTH//2, 500), 2)
        draw_txt("RED TEAM", 30, RED, WIDTH//4, 130)
        draw_txt("BLUE TEAM", 30, BLUE, WIDTH*3//4, 130)
        
        ry, by = 180, 180
        for pid, p in g_data.players.items():
            cx, cy = (WIDTH//4, ry) if p['team']==0 else (WIDTH*3//4, by)
            if p['team']==0: ry += 60
            else: by += 60
            
            p_txt = f"Player {pid}" + (" (YOU)" if pid == my_id else "")
            draw_txt(p_txt, 20, WHITE, cx, cy)
            draw_txt(f"[{CHAR_DATA[p['c_idx']]['name']}]", 16, GRAY, cx, cy+25)
            if p['ready']: draw_txt("READY", 20, GREEN, cx+100, cy)
            
        # [수정] 안내 문구 변경
        draw_txt("T: Team Swap | A/D: Change Char | SPACE: Ready | ENTER: Chat", 20, YELLOW, WIDTH//2, 550)

    elif g_data.phase in ["PLAYING", "ROUND_OVER", "MATCH_OVER"]:
        for x in range(0, WIDTH, 50): pygame.draw.line(screen, DARK_GRAY, (x+ox, 0), (x+ox, HEIGHT))
        for y in range(0, HEIGHT, 50): pygame.draw.line(screen, DARK_GRAY, (0, y+oy), (WIDTH, y+oy))
        for ob in g_data.obs + g_data.m_obs:
            pygame.draw.rect(screen, GRAY, (ob[0]+ox, ob[1]+oy, ob[2], ob[3]))
            pygame.draw.rect(screen, WHITE, (ob[0]+ox, ob[1]+oy, ob[2], ob[3]), 2)
            
        cols = {"HEAL":GREEN, "SHIELD":CYAN, "GRENADE":ORANGE, "SPEED":YELLOW}
        syms = {"HEAL":"+", "SHIELD":"S", "GRENADE":"G", "SPEED":">>"}
        for it in g_data.items:
            rect = pygame.Rect(it[0]-12+ox, it[1]-12+oy, 24, 24)
            pygame.draw.rect(screen, cols[it[2]], rect, border_radius=4)
            draw_txt(syms[it[2]], 16, BLACK, it[0]+ox, it[1]+oy)

        for pt in particles[:]: pt.update(); pt.draw(screen, ox, oy); (particles.remove(pt) if pt.life<=0 else None)

        for b in g_data.bullets:
            sz = 16 if b['t']=="bazooka" else (12 if b['t']=="grenade" else (24 if b['t']=="melee" else 6))
            col = ORANGE if b['t']=="bazooka" else (GREEN if b['t']=="grenade" else (WHITE if b['t']=="melee" else YELLOW))
            if b['t']=="melee": pygame.draw.circle(screen, col, (int(b['x']+ox), int(b['y']+oy)), sz//2, 2)
            else: pygame.draw.circle(screen, col, (int(b['x']+ox), int(b['y']+oy)), sz//2)

        for pid, p in g_data.players.items():
            if p['hp'] <= 0: continue
            col = RED if p['team']==0 else BLUE
            px, py = p['x']+ox, p['y']+oy
            shape = CHAR_DATA[p['c_idx']]['shape']
            
            if shape=="circle": pygame.draw.circle(screen, col, (int(px), int(py)), 16)
            else: pygame.draw.rect(screen, col, (px-16, py-16, 32, 32), border_radius=4)
            if pid == my_id: pygame.draw.rect(screen, YELLOW, (px-18, py-18, 36, 36), 2) 
            if p['shield']>0: pygame.draw.circle(screen, CYAN, (int(px), int(py)), 22, 2)
            
            ex, ey = px + p['dir'][0]*20, py + p['dir'][1]*20
            if p['use_g']: pygame.draw.circle(screen, GREEN, (int(px+p['dir'][0]*15), int(py+p['dir'][1]*15)), 5)
            elif shape=="sniper": 
                pygame.draw.line(screen, WHITE, (px, py), (px+p['dir'][0]*30, py+p['dir'][1]*30), 3)
                pygame.draw.circle(screen, GRAY, (int(px+p['dir'][0]*10), int(py+p['dir'][1]*10)), 4)
            else: pygame.draw.line(screen, WHITE, (px, py), (ex, ey), 4 if shape=="square" else 2)

            pygame.draw.rect(screen, GRAY, (px-16, py-24, 32, 6))
            pygame.draw.rect(screen, GREEN if p['hp']>50 else RED, (px-16, py-24, max(0, p['hp']/100)*32, 6))

        draw_txt(f"ROUND {g_data.round_num}", 20, GRAY, WIDTH//2, 15)
        draw_txt(f"RED {g_data.red_score} : {g_data.blue_score} BLUE", 40, WHITE, WIDTH//2, 45)
        
        if my_id in g_data.players:
            my_p = g_data.players[my_id]
            draw_txt(f"HP: {int(my_p['hp'])}", 20, WHITE, 20, HEIGHT-30, False)
            if my_p['use_g']: a_txt = f"GRENADES: {my_p['grenades']}"; ac = ORANGE
            elif CHAR_DATA[my_p['c_idx']]['wp']['mag']==-1: a_txt = "AMMO: INF"; ac = YELLOW
            elif my_p['reload']>0: a_txt = "RELOADING..."; ac = RED
            else: a_txt = f"AMMO: {my_p['ammo']} / {CHAR_DATA[my_p['c_idx']]['wp']['mag']}"; ac = YELLOW
            draw_txt(a_txt, 20, ac, WIDTH-150, HEIGHT-30, False)

        chat_y = HEIGHT - 130 - (len(g_data.chat) * 20)
        for c in g_data.chat:
            draw_txt(c['txt'], 16, WHITE, 20, chat_y, False)
            chat_y += 20
            
        if is_typing:
            pygame.draw.rect(screen, (50, 50, 50), (20, HEIGHT - 110, 300, 25))
            pygame.draw.rect(screen, WHITE, (20, HEIGHT - 110, 300, 25), 1)
            draw_txt("Say: " + chat_txt + "_", 16, YELLOW, 25, HEIGHT - 105, False)

        if g_data.phase in ["ROUND_OVER", "MATCH_OVER"]:
            over = pygame.Surface((WIDTH, HEIGHT)); over.set_alpha(100); screen.blit(over, (0,0))
            draw_txt(g_data.msg, 60, YELLOW, WIDTH//2, HEIGHT//2)

    pygame.display.flip(); clock.tick(60)