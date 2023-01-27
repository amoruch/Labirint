import os
import sys
import pygame
from pygame import mixer
from pygame.locals import *
import random

# перемещивает содержимое массива
def random_sort(M):
    M2 = M[::]
    res = []
    while M2 != []:
        a = len(M2)
        ind = random.randint(0, a - 1)
        res.append(M2[ind])
        M2.pop(ind)
    return res

# функция создания уровня
def creating_level():
    M = []
    n = 5
    var1 = [[0, 1], [0, -1], [1, 0], [-1, 0]]
    Board = [['0' for i in range(n * 2 + 1)] for j in range(n * 2 + 1)]
    x = random.randint(0, n) * 2
    y = random.randint(0, n) * 2
    M.append([x, y])

    # алгоритм генерации уровня очень сложная, поэтому я думаю комментарии излишни
    while M != []:
        var = random_sort(var1)
        a = random.randint(0, len(M) - 1)
        bol = True
        for i in var:
            x2, y2 = M[a][0] + i[0] * 2, M[a][1] + i[1] * 2
            if 0 <= x2 <= n * 2 and 0 <= y2 <= n * 2:
                if Board[x2][y2] == '0':
                    bol = False
                    Board[x2][y2] = '1'
                    x3, y3 = M[a][0] + i[0], M[a][1] + i[1]
                    Board[x3][y3] = '1'
                    M.append([x2, y2])
                    break
        if bol:
            M.pop(a)

    s = n * 2 + 1
    for i in range(s):
        for j in range(s):
            if Board[i][j] == "0" and random.randint(0, 10) == 0:
                Board[i][j] = "1"

    s += 2
    resB = [["0" for i in range(s)]]
    for i in range(s - 2):
        resB.append(["0"] + Board[i] + ["0"])
    resB.append(["0" for i in range(s)])

    var_obj = []
    for i in range(1, s):
        for j in range(1, s):
            if resB[i][j] == "1":
                c = int(resB[i - 1][j]) + int(resB[i + 1][j])
                c += int(resB[i][j - 1]) + int(resB[i][j + 1])
                if c == 1:
                    var_obj.append((i, j))
    # точка появления
    ind = random.randint(0, len(var_obj) - 1)
    xs, ys = var_obj[ind]
    var_obj.pop(ind)
    resB[xs][ys] = "2"

    # выход
    ind = random.randint(0, len(var_obj) - 1)
    xe, ye = var_obj[ind]
    var_obj.pop(ind)
    resB[xe][ye] = "3"

    # разбрасываем еду по уровню
    for i in var_obj:
        if random.randint(0, 1) == 0:
            xf, yf = i
            resB[xf][yf] = "4"
            
    S = {"x": ys * 100, "y": xs * 100, "hungry": 120, "level": 1,
         "board_size": n * 2 + 3, "board": [[1, 1], [1, 1]]}
    S["board"] = resB
    return S

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

# загружаем звуки и объявляем некоторые переменные
s_eating = pygame.mixer.Sound('sounds/eating.wav')
s_walking = pygame.mixer.Sound('sounds/walking.wav')
s_death = pygame.mixer.Sound('sounds/death.wav')
s_clicking = pygame.mixer.Sound('sounds/clicking.wav')
size = (800, 600)
fps = 120
cell_size = size[1] / 6
game_speed = 1

clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)

# чтобы было проще создавать текст
def text_gen(s, height, color):
    font = pygame.font.Font(None, height)
    text = font.render(str(s), True, color)
    return text

# вычисляем рассояние между двумя точками с помощью пифагора
def distance(p1, p2):
    return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

# загрузка уровня из текстового файлика
def load_level(name):
    S = {"x": 0, "y": 0, "hungry": 0, "level": 0, "board_size": 2,
         "board": [[1, 1], [1, 1]]}
    M = ["x", "y", "hungry", "level", "board_size", "board"]
    f = open(name, 'r')
    f2 = f.read()
    word = ""
    ss = []
    for i in f2:
        if i != '\n':
            word += i
        else:
            ss.append(word)
            word = ""
    ind = 0
    while M[ind] != "board":
        s = ss[ind]
        tt = s.index(':')
        a = s[tt + 1:]
        S[M[ind]] = int(a)
        ind += 1
    Board = []
    for i in range(ind + 1, len(ss)):
        Board.append(list(ss[i]))
    S["board"] = Board
    f.close()
    return S

# загружаем изображения из datы
def load_image(name):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    
    image = image.convert_alpha()
    return image

# класс игрока(сразу скажу в нем очень много странных функций)
class Player(pygame.sprite.Sprite):
    image = load_image("player.png")
    image = pygame.transform.scale(image, (cell_size * 0.7, cell_size * 0.7))
    side = cell_size * 0.7
    def __init__(self, group, pos):
        super().__init__(group)
        self.start_image = Player.image
        self.player_size = Player.side
        self.death_play = False
        self.image = Player.image
        self.start_pos = [pos[0] - Player.side / 2, pos[1] - Player.side / 2]
        self.rect = [pos[0] - Player.side / 2, pos[1] - Player.side / 2]
        coliziya = load_image("coliziya.png")
        coliziya = pygame.transform.scale(coliziya, (cell_size * 0.7, cell_size * 0.7))
        self.mask = pygame.mask.from_surface(coliziya)
        self.cadr = 0
        self.player_walk = load_image("player_animation.png")
        self.cadr2 = 0
        self.player_death = load_image("death_animation.png")

    def walk_anim(self, rotate, a):
        image = self.player_walk
        frame_location = (48 * int(self.cadr), 0)
        self.cadr += a / 10
        if self.cadr >= 8:
            self.cadr = 0
            s_walking.play()
        image = image.subsurface(pygame.Rect(frame_location, (48, 48)))
        image = pygame.transform.scale(image, (cell_size * 0.7, cell_size * 0.7))
        image = pygame.transform.rotate(image, rotate)
        self.image = image

    def player_stop(self, rotate):
        self.image = self.start_image
        self.image = pygame.transform.rotate(self.image, rotate)
        
    def can_move(self, walls):
        return not pygame.sprite.collide_mask(self, walls)

    def move(self, camera):
        self.rect[0] = self.start_pos[0] - camera[0]
        self.rect[1] = self.start_pos[1] - camera[1]

    def death_anim(self, rotate, a):
        self.death_play = True
        image = self.player_death
        frame_location = (48 * int(self.cadr2), 0)
        self.cadr2 += a / 10
        image = image.subsurface(pygame.Rect(frame_location, (48, 48)))
        image = pygame.transform.scale(image, (cell_size * 0.7, cell_size * 0.7))
        self.start_image = image
        image = pygame.transform.rotate(image, rotate)
        self.image = image
        if self.cadr2 >= 8:
            self.cadr2 = 0
            self.death_play = False
    
    def dead_play(self):
        return self.death_play
    
# класс выходь
class Out(pygame.sprite.Sprite):
    image = load_image("out.png")
    image = pygame.transform.scale(image, (cell_size, cell_size))

    def __init__(self, group, coord, board_coord):
        super().__init__(group)
        self.image = Out.image
        self.start_pos = [coord[0], coord[1]]
        self.rect = [coord[0], coord[1]]
        self.board_coord = board_coord
        
    def update(self, camera_rp):
        self.rect[0] = self.start_pos[0] - camera_rp[0]
        self.rect[1] = self.start_pos[1] - camera_rp[1]

    def get_board_coord(self):
        return self.board_coord

# стена
class Wall(pygame.sprite.Sprite):
    def __init__(self, group, coord, board):
        super().__init__(group)
        cs = cell_size
        image = load_image("walls.png")
        image = pygame.transform.scale(image, (cs * 3, cs))
        frame_location = (cs * random.randint(0, 2), 0)
        self.image = image.subsurface(pygame.Rect(frame_location, (cs, cs)))
        self.start_pos = [coord[0], coord[1]]
        self.rect = [coord[0], coord[1]]
        self.mask = pygame.mask.from_surface(self.image)
        self.board = board
        
    def update(self, camera_rp):
        self.rect[0] = self.start_pos[0] - camera_rp[0]
        self.rect[1] = self.start_pos[1] - camera_rp[1]

# класс пола нужен чтобы у него была текстура
class Floor(pygame.sprite.Sprite):
    image = load_image("floor.png")
    image = pygame.transform.scale(image, (cell_size, cell_size))

    def __init__(self, group, coord):
        super().__init__(group)
        self.image = Floor.image
        self.start_pos = [coord[0], coord[1]]
        self.rect = [coord[0], coord[1]]
        
    def update(self, camera_rp):
        self.rect[0] = self.start_pos[0] - camera_rp[0]
        self.rect[1] = self.start_pos[1] - camera_rp[1]

# класс облака(чистый декор, чтобы небо вокруг не казалось пустым)
class Clouds(pygame.sprite.Sprite):
    def __init__(self, group, coord, speed):
        super().__init__(group)
        image = load_image("облака.png")
        frame_location = (300 * random.randint(0, 1), 150 * random.randint(0, 2))
        self.image = image.subsurface(pygame.Rect(frame_location, (300, 150)))
        self.start_pos = [coord[0], coord[1]]
        self.rect = [coord[0], coord[1]]
        self.speed = speed
        
    def update(self, camera_rp):
        self.rect[0] = self.start_pos[0] - camera_rp[0]
        self.rect[1] = self.start_pos[1] - camera_rp[1]
        self.start_pos[0] += self.speed
        # если выходит за границы экрана, появляется на другом его конце
        if self.rect[0] > size[0]:
            self.start_pos[0] -= size[0] + 200
            if self.rect[1] > size[1]:
                self.start_pos[1] -= size[1]
            if self.rect[1] < 0:
                self.start_pos[1] += size[1]

# класс света(бывает двух типов: градиент и в виде круга)
class Light():
    image_1 = load_image("light_1.png")
    image_2 = load_image("light_2.png")

    def __init__(self, pos, form, side, rotate):
        if form == 1:
            self.image = Light.image_1
        elif form == 2:
            self.image = Light.image_2
        self.image = pygame.transform.scale(self.image, (side, side))
        self.image = pygame.transform.rotate(self.image, rotate)
        self.side = side
        self.form = form
        self.start_pos = [pos[0], pos[1]]
        self.rect = [pos[0], pos[1]]

    def update(self, camera):
        self.rect[0] = self.start_pos[0] + camera[0]
        self.rect[1] = self.start_pos[1] + camera[1]

    def rimage(self):
        return self.image

    def coord(self):
        return self.rect

# необходимый класс, хранит в себе голод персонажа
class Hungry():
    image_hungry = load_image("bar_of_hungry.png")

    def __init__(self, value):
        self.image = Hungry.image_hungry
        self.image = pygame.transform.scale(self.image, (240, 240))
        self.pos = (size[0] - 180, 50)
        self.start_hungry = 120
        self.hungry = value
        self.speed = 1

    def change_hungry(self, value):
        self.hungry += value
        
    def update(self, screen):
        if self.hungry <= 0:
            self.speed = 0
        x, y = self.pos
        a = int(196 * (self.hungry / self.start_hungry))
        hun = pygame.Rect(x + 102, y + 22 + (196 - a), 36, a)
        screen.fill((255, 0, 0), hun)
        screen.blit(self.image, self.pos)
        
        b = int(120 * (self.hungry / self.start_hungry) + 0.9)
        s = str(b) + "/120"
        text = text_gen(s, 20, (255, 255, 255))
        text_x = x + 90
        text_y = y + 230
        screen.blit(text, (text_x, text_y))

    def get_hungry(self):
        return self.hungry

    def player_eated(self):
        self.hungry += self.start_hungry * 0.2
        self.hungry = min(self.hungry, self.start_hungry)
    
# затемнение(в ранних версиях использовался при переходах между уровнями)
class Fogging():
    def __init__(self, dark):
        self.dark = dark
        self.speed = 1
        
    def update(self, screen, form):
        dark_filter = pygame.surface.Surface(size)
        dark_filter.fill((self.dark, self.dark, self.dark))
        screen.blit(dark_filter, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        if form == 1:
            if 0 <= self.dark < 255:
                self.dark += self.speed
        else:
            if 0 < self.dark <= 255:
                self.dark -= self.speed

    def get_dark(self):
        return self.dark

    def set_dark(self, a):
        self.dark = a

# еда(просто еда, восполняет голод)
class Food(pygame.sprite.Sprite):
    image_1 = load_image("food_1.png")
    image_2 = load_image("food_2.png")
    image_3 = load_image("food_3.png")

    def __init__(self, group, coord, board_coord):
        super().__init__(group)
        M = [Food.image_1, Food.image_2, Food.image_3]
        self.image = M[random.randint(0, 2)]
        self.image = pygame.transform.scale(self.image, (cell_size, cell_size))
        self.start_pos = [coord[0], coord[1]]
        self.rect = [coord[0], coord[1]]
        self.board_coord = board_coord
        
    def update(self, camera_rp):
        self.rect[0] = self.start_pos[0] - camera_rp[0]
        self.rect[1] = self.start_pos[1] - camera_rp[1]

    def get_board_coord(self):
        return self.board_coord

# кнопки, существуют чтобы на них тыкали, а они жаловались что на них тыкнули
class Button():
    def __init__(self, coord, size, text):
        self.text = text
        self.button_text = text_gen(text, 40, (73, 73, 73))
        self.image_1 = load_image("button_1.png")
        self.image_2 = load_image("button_2.png")
        self.image_3 = load_image("button_3.png")
        self.image = self.image_1
        self.coord = coord[::]
        self.text_coord = [coord[0] + 100 - (8 * len(text) + 2), coord[1] + 22]
        self.start_coord = coord[::]
        self.size = size
        self.image = pygame.transform.scale(self.image, size)

    def move(self, vec):
        self.coord[0] = self.start_coord[0] + vec[0]
        self.coord[1] = self.start_coord[1] + vec[1]
        self.text_coord = [self.coord[0] + 100 - (8 * len(self.text) + 2), self.coord[1] + 22]

    def update(self, screen):
        screen.blit(self.image, self.coord)
        screen.blit(self.button_text, self.text_coord)

    def click_button(self, x, y):
        if x >= self.coord[0] and x <= self.coord[0] + self.size[0]:
            if y >= self.coord[1] and y <= self.coord[1] + self.size[1]:
                return True
        return False

    def animation(self, mpos, can_press):
        if Button.click_button(self, mpos[0], mpos[1]) and can_press:
            self.image = self.image_2
        else:
            self.image = self.image_1
        

    def change_image(self, n):
        if n == 1:
            self.image = self.image_1
        if n == 2:
            self.image = self.image_2
        if n == 3:
            self.image =  self.image_3

fogging = Fogging(0)

def game_screen(food, number_level, board, player_pos):
    start_time = pygame.time.get_ticks()
    count_cell = 13
    all_sprites = pygame.sprite.Group()
    Board = board
    camera_rp = [0, 0]
    camera_np = [0, 0]
    a = (size[0] - size[1]) / 2
    xp, yp = player_pos

    for i in range(-10, 10):
        for j in range(-10, 10):
            if random.randint(0, 20) == 0:
                xo, yo = i * size[0] / 10, j * size[1] / 10
                speed = random.randint(1, 3) / 5
                clouds = Clouds(all_sprites, [xo, yo], speed)

    lights = []
    foods = []
    walls = []
    
    for i in range(count_cell):
        for j in range(count_cell):
            xo = a + cell_size * i + 300 - xp - cell_size / 2
            yo = cell_size * j + 300 - yp - cell_size / 2
            if int(Board[j][i]) == 0:
                wall = Wall(all_sprites, [xo, yo], [i, j])
                walls.append(wall)
                if i == 0:
                    lights.append(Light((cell_size * i, cell_size * j), 2, cell_size, 0))
                if j == 0:
                    lights.append(Light((cell_size * i, cell_size * j), 2, cell_size, 270))
                if i == count_cell - 1:
                    lights.append(Light((cell_size * i, cell_size * j), 2, cell_size, 180))
                if j == count_cell - 1:
                    lights.append(Light((cell_size * i, cell_size * j), 2, cell_size, 90))
            else:
                floor = Floor(all_sprites, [xo, yo])
            if int(Board[j][i]) == 3:
                out = Out(all_sprites, [xo, yo], (i, j))
            if int(Board[j][i]) == 4:
                foods.append(Food(all_sprites, [xo, yo], (i, j)))

    save_but = Button([300, 305], [200, 75], "Сохранить")
    back_menu_but = Button([300, 405], [200, 75], "Главное меню")
    buttons = [save_but, back_menu_but]

    xcor = a + 300 - xp
    ycor = 300 - yp
    player_walk_anim = load_image
    player = Player(all_sprites, [size[0] / 2, size[1] / 2])
    x2 = camera_np[0] + cell_size / 2
    y2 = camera_np[1] + cell_size / 2
    abc = cell_size * 2
    player_light = Light((xp + x2 - abc, yp + y2 - abc), 1, abc * 2, 0)
    hungry = Hungry(food)
    death = False
    next_level = False
    can_press = True
    back_anim = False
    boool = False
    back_menu_anim = False
    save_anim = False
    death_sound = True
    pause = 0
    time = pygame.time.get_ticks()
    t1 = (pygame.time.get_ticks() - start_time) // 1000
    rot = 0
    while True:
        can_eat = 0
        can_escape = False
        x = (size[0] - size[1]) / 2
        y = size[1]
        xb, yb = (xp + cell_size // 2) // cell_size, (yp + cell_size // 2) // cell_size
        for i in range(len(foods)):
            if foods[i].get_board_coord() == (xb, yb):
                can_eat = i + 1
                break

        if out.get_board_coord() == (xb, yb):
            can_escape = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return (1, 0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    a, b = event.pos
                    if save_but.click_button(a, b) and can_press:
                        save_anim = True
                    if back_menu_but.click_button(a, b) and can_press:
                        back_menu_anim = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    a, b = event.pos
                    if save_but.click_button(a, b) and save_anim:
                        s_clicking.play()
                        save_anim = False
                        f = open('level.txt', 'w')
                        f.write("x:" + str(int(xp)) + "\n")
                        f.write("y:" + str(int(yp)) + "\n")
                        f.write("hungry:" + str(int(hungry.get_hungry())) + "\n")
                        f.write("level:" + str(number_level) + "\n")
                        f.write("board_size:" + str(count_cell) + "\n")
                        f.write("board:\n")
                        for i in range(len(Board)):
                            for j in range(len(Board[i])):
                                f.write(str(Board[i][j]))
                            f.write("\n")
                        f.close()
                    elif save_anim:
                        save_anim = False
                        
                    if back_menu_but.click_button(a, b) and can_press and back_menu_anim:
                        s_clicking.play()
                        back_menu_anim = False
                        return (4, 0)
                    elif back_menu_anim:
                        back_menu_anim = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if can_eat:
                        print(1)
                        s_eating.play()
                        foods[can_eat - 1].kill()
                        foods.pop(can_eat - 1)
                        hungry.player_eated()
                        Board[int(xb)][int(yb)] = 1
                    elif can_escape and not next_level and not death:
                        print(2)
                        next_level = True
                if event.key == pygame.K_ESCAPE:
                    pause = 1 - pause
                    time = pygame.time.get_ticks()
                    dark_f = pygame.surface.Surface(size)
                    drak = (120, 120, 120)
                    dark_f.fill(drak)
                    screen.blit(dark_f, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
                    text = text_gen("Pause", 40, (255, 255, 255))
                    pygame.display.flip()

        if not pause:
            # если игра не на паузе
            screen.fill((0, 191, 255))
            keys = pygame.key.get_pressed()
            vec = [0, 0]
            if not (hungry.get_hungry() == 0):
                if not (death):
                    if keys[K_w]:
                        vec[1] += -1
                    if keys[K_s]:
                        vec[1] += 1
                    if keys[K_d]:
                        vec[0] += 1
                    if keys[K_a]:
                        vec[0] += -1

                if abs(vec[0] * vec[1]):
                    vec[0] /= 2 ** 0.5 
                    vec[1] /= 2 ** 0.5

            # зависимость от времени позволит перемещаться игроку
            # более равномерно, не завися от fps
            ticks = (pygame.time.get_ticks() - time) / 10
            time = pygame.time.get_ticks()
            
            camera_np[0] += vec[0] * game_speed * ticks
            xp += vec[0] * game_speed * ticks

            d = distance(camera_np, camera_rp)
            vec2 = [camera_np[0] - camera_rp[0], camera_np[1] - camera_rp[1]]
            # / задаем резкость камеры
            camera_rp[0] = (camera_rp[0] + vec2[0] / 30 * ticks)
            player.move([camera_rp[0] - camera_np[0], camera_rp[1] - camera_np[1]])
            player.update(camera_rp)

            # обработка столкновений
            player_collision = False
            wall_ind = -1
            for ind in range(len(walls)):
                _wall_ = walls[ind]
                if not player.can_move(_wall_):
                    wall_ind = ind
                    player_collision = True
                    break
            if player_collision:
                v0 = vec[0] * game_speed * ticks
                camera_np[0] += v0 * -1
                xp += v0 * -1
                
                d = distance(camera_np, camera_rp)
                vec2 = [camera_np[0] - camera_rp[0], camera_np[1] - camera_rp[1]]
                camera_rp[0] = (camera_rp[0] + vec2[0] / 30 * ticks)
                player.move([camera_rp[0] - camera_np[0], camera_rp[1] - camera_np[1]])
                player.update(camera_rp)


            camera_np[1] += vec[1] * game_speed * ticks
            yp += vec[1] * game_speed * ticks

            d = distance(camera_np, camera_rp)
            vec2 = [camera_np[0] - camera_rp[0], camera_np[1] - camera_rp[1]]
            # / задаем резкость камеры
            camera_rp[1] = (camera_rp[1] + vec2[1] / 30 * ticks)
            player.move([camera_rp[0] - camera_np[0], camera_rp[1] - camera_np[1]])

            player.update(camera_rp)

            # обработка столкновений
            player_collision = False
            wall_ind = -1
            for ind in range(len(walls)):
                _wall_ = walls[ind]
                if not player.can_move(_wall_):
                    wall_ind = ind
                    player_collision = True
                    break
            if player_collision:
                v1 = vec[1] * game_speed * ticks
                camera_np[1] += v1 * -1
                yp += v1 * -1
                
                d = distance(camera_np, camera_rp)
                vec2 = [camera_np[0] - camera_rp[0], camera_np[1] - camera_rp[1]]
                camera_rp[1] = (camera_rp[1] + vec2[1] / 30 * ticks)
                player.move([camera_rp[0] - camera_np[0], camera_rp[1] - camera_np[1]])
                player.update(camera_rp)
                

            # анимация движения игрока
            if vec[0] < 0:
                rot = 90
            elif vec[0] > 0:
                rot = 270
            elif vec[1] < 0:
                rot = 0
            elif vec[1] > 0:
                rot = 180
            if not (vec[0] == 0 and vec[1] == 0):
                player.walk_anim(rot, ticks)
            else:
                player.player_stop(rot)

            # анимация смерти
            if hungry.get_hungry() == 0 and not death:
                player.death_anim(rot, ticks / 3)
                if death_sound:
                    s_death.play()
                    death_sound = False
                if not player.dead_play():
                    death = True

            all_sprites.update(camera_rp)
            all_sprites.draw(screen)

            # работа с освещением
            light_filter = pygame.surface.Surface((count_cell * cell_size, count_cell * cell_size))
            light_filter.fill(pygame.color.Color('white'))
            x1 = camera_rp[0] + cell_size / 2
            y1 = camera_rp[1] + cell_size / 2
            player_light.update(camera_np)
            for light in lights:
                light_filter.blit(light.rimage(), light.coord())
            light_filter.blit(player_light.rimage(), player_light.coord())
            screen.blit(light_filter, (xcor - x1, ycor - y1), special_flags=pygame.BLEND_RGBA_SUB)

            # работа с затемнением
            if death or next_level:
                fogging.update(screen, 1)

            if fogging.get_dark() == 255 and death:
                fogging.set_dark(0)
                return (0, 0)

            if next_level:
                for objekt in all_sprites:
                    objekt.kill()
                return (2, hungry.get_hungry())

            # рисует черные поля по краям
            screen.fill((0, 0, 0), pygame.Rect(size[0] - x, 0, x, y))
            screen.fill((0, 0, 0), pygame.Rect(0, 0, x, y))
            pygame.draw.line(screen, (255, 255, 255), (x, 0), (x, y), 2)
            pygame.draw.line(screen, (255, 255, 255), (size[0] - x, 0), (size[0] - x, y), 2)

            # номер уровня слева сверху
            s = "Уровень: " + str(number_level)
            text = text_gen(s, 25, (255, 255, 255))
            text_x = 5
            text_y = 50
            screen.blit(text, (text_x, text_y))

            # полоска голода
            hungry.update(screen)
            t2 = (pygame.time.get_ticks() - start_time) // 1000
            if not (hungry.get_hungry() == 0) and not next_level:
                if t2 > t1:
                    hungry.change_hungry(-1)
                    t1 = t2
            
            pygame.display.flip()
            clock.tick(fps)
        else:
            # если сейчас пауза
            mouse_pos = pygame.mouse.get_pos()
            for i in range(len(buttons)):
                button = buttons[i]
                button.animation(mouse_pos, can_press)

            if save_anim and not hungry.get_hungry() == 0:
                save_but.change_image(3)

            if back_menu_anim:
                back_menu_but.change_image(3)
            
            screen.blit(text, (size[0] // 2 - 40, size[1] // 2 - 100))
            for button in buttons:
                button.update(screen)
            if back_anim:
                fogging.update(screen, 1)
                if fogging.get_dark() == 255:
                    start_anim = False
                    can_press = True
                    for objekt in all_sprites:
                        objekt.kill()
                    start_menu()
            pygame.display.flip()
            clock.tick(fps)
        
def start_game(Level):
    number_level = Level["level"]
    food = Level["hungry"]
    play = 2
    while play == 2:
        player_pos = (Level["x"], Level["y"])
        play, food = game_screen(food, number_level, Level["board"], player_pos)
        number_level += 1
        Level = creating_level()
    if play == 1:
        # закрытие игры
        pygame.quit()

def start_menu(): # очень много кнопок
    can_press = True
    to_opt_anim = False
    to_menu_anim = False
    time = 0
    start_game_anim = False
    option_anim = False
    back_anim = False
    start_anim = False
    continue_anim = False
    exit_anim = False
    moving = [0, 0]
    fon = pygame.transform.scale(load_image("fon_2.png"), size)
    fon_2 = pygame.transform.scale(load_image("fon.png"), size)
    start_but = Button([300, 105], [200, 75], "Начать")
    continue_but = Button([300, 205], [200, 75], "Продолжить")
    option_but = Button([300, 305], [200, 75], "Помощь")
    exit_but = Button([300, 405], [200, 75], "Выход")
    back_but = Button([300, 650], [200, 75], "Назад")
    buttons = [start_but, continue_but, option_but, exit_but, back_but]
    while True:
        screen.blit(fon, (0, 0 + moving[1]))
        screen.blit(fon_2, (0, 600 + moving[1]))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return  
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and can_press:
                    a, b = event.pos
                    if start_but.click_button(a, b):
                        start_anim = True
                    if continue_but.click_button(a, b):
                        continue_anim = True
                    if option_but.click_button(a, b):
                        option_anim = True
                    if exit_but.click_button(a, b):
                        exit_anim = True
                    if back_but.click_button(a, b):
                        back_anim = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and can_press:
                    a, b = event.pos
                    if start_but.click_button(a, b) and start_anim:
                        s_clicking.play()
                        start_game(creating_level())
                        start_anim = False
                    elif start_anim:
                        start_anim = False
                    
                    if continue_but.click_button(a, b) and continue_anim:
                        s_clicking.play()
                        try:
                            start_game(load_level("level.txt"))
                        except:
                            print("сохранение отсутствует")
                        continue_anim = False
                    elif continue_anim:
                        continue_anim = False
                    
                    if option_but.click_button(a, b) and option_anim:
                        s_clicking.play()
                        option_anim = False
                        to_opt_anim = True
                        can_press = False
                    elif option_anim:
                        option_anim = False
                    
                    if exit_but.click_button(a, b) and exit_anim:
                        s_clicking.play()
                        exit_anim = False
                        return  
                    elif exit_anim:
                        exit_anim = False
                    
                    if back_but.click_button(a, b) and back_anim:
                        s_clicking.play()
                        can_press = False
                        to_menu_anim = True
                        back_anim = False
                    elif back_anim:
                        back_anim = False
        mouse_pos = pygame.mouse.get_pos()
        for i in range(len(buttons)):
            button = buttons[i]
            button.animation(mouse_pos, can_press)
            
        if start_anim:
            start_but.change_image(3)

        if continue_anim:
            continue_but.change_image(3)

        if option_anim:
            option_but.change_image(3)

        if exit_anim:
            exit_but.change_image(3)

        if back_anim:
            back_but.change_image(3)
                    
        ticks = (pygame.time.get_ticks() - time) / 10
        time = pygame.time.get_ticks()
        
        for i in range(len(buttons)):
            button = buttons[i]
            button.update(screen)
            button.move(moving)
            
        if to_opt_anim:
            moving[1] -= ticks * 4
            if moving[1] < -600:
                moving[1] = -600
                to_opt_anim = False
                can_press = True

        if to_menu_anim:
            moving[1] += ticks * 4
            if moving[1] > 0:
                moving[1] = 0
                to_menu_anim = False
                can_press = True
        pygame.display.flip()
        clock.tick(fps)

try:
    start_menu()
except:
    pass
pygame.quit()
