import pygame
import pygame_widgets
import random
import os
from pygame.locals import FULLSCREEN
from pygame_widgets.slider import Slider
import csv


# TO DO
# add mist to level 2
# create paint gun
# create level 3...
# create ghost mob (floating eyes) that if you shoot, bullet goes through. You need to find a paint can and shoot paint at the ghost. Then you can shoot it
# create map
# create ghost walk (through 1 wall)
# create dynamite

# Set up game admin
DIRECTORY = 'MAZE/maze_blocks'
test_keys = 1                   # commands while I am testing the game
t1 = 0

def log_event(event = "", location = [0, 0]):
    log = "(" + str(int(pygame.time.get_ticks() / 100) / 10) + ") " + event + " at: " + " ".join(str(e) for e in location)  # LOG
    if event == "Game started":
        type = "w"
    else:
        type = "a"
    with open(DIRECTORY + "/log.csv", type, encoding='UTF8', newline="") as temp:
        writer = csv.writer(temp)
        writer.writerow([log])

log_event("Game started")

# Defines colors
BLACK = (0, 0, 0)
WHITE = (200, 200, 200)

# Defines maze variables
size_x, size_y = 50, 50         # Dimensions of levels
x1, y1 = 1, 1                   # Starting point
x2, y2 = 4, 4                   # End point
x, y = 0, 0                     # starting point
deep = 1                        # measures how it player is
cell_size = 250                 # Size of each cell in pixels 250
dist_x = 9.5                    # Visual distance from center in the x-direction            NEED TO FIGURE WHERE THIS IS STILL USED AND DELETE IT
dist_y = 5                      # visual distance from center in the y-direction            NEED TO FIGURE WHERE THIS IS STILL USED AND DELETE IT

#Define player variables
step = 15                       # size of a step
jump = 8                        # speed of a jump
collectibles_touched = []       # list of collectibles player touched
jet_counter = 10

# Defines light variables
depth_of_light = 10             # depth when it stats to get dark
darkness = 5                    # how strong is the darkness

# Defines mist variables
mist = 0                        # is there mist in the area?
mist_counter = 0                # counter for mist fade in / fade out
mist_1_x = 0                    # counter for mist 1 movement
mist_2_x = 0                    # counter for mist 2 movement

# Defines gun variables
gun_counter = 0

# Defines directory and file names for player animation
FILE_NAMES = ['user', 'blink', 'jet_', 'notorch', 'notorch', 'jetnotorch', 'jetonnotorch',
              'stick', 's_jet', 's_jet', 's_jet', 's_jet', 's_jet']

data = []

with open(DIRECTORY + "/items.csv", "r", encoding='UTF8', newline="") as file:
    reader = csv.reader(file)
    for row in reader:
        data.append(row)

def convert_value(value):
    try:
        return int(value)  # Convert to integer if possible
    except ValueError:
        try:
            return float(value)  # Convert to float if possible
        except ValueError:
            return value  # Return the value as-is if not numeric

def get_data(info, type_col):
    info_index = data[0].index(info)
    type_index = data[0].index("type")
    return [convert_value(line[info_index]) for line in data if line[type_index] == type_col]

COLLECTIBLES = get_data("name", "collectible")
minxs = get_data("minx", "collectible")
minys = get_data("miny", "collectible")
maxxs = get_data("maxx", "collectible")
maxys = get_data("maxy", "collectible")

mob_names = get_data("name", "mob")
mob_spawn_rate = get_data("spawn_rate", "mob")
mob_speed = get_data("speed", "mob")
mob_chase = get_data("chase", "mob")
mob_fly = get_data("fly", "mob")
mob_minxs = get_data("minx", "mob")
mob_minys = get_data("miny", "mob")
mob_maxxs = get_data("maxx", "mob")
mob_maxys = get_data("maxy", "mob")

# Function that returns paths to all images in directory, starting with file_name
def load_file_paths(directory, file_names):
    file_paths = []
    for file_number in range(len(file_names)):
        for filename in os.listdir(directory):
            if filename.startswith(file_names[file_number]):
                file_paths.append(os.path.join(directory, filename))
    return file_paths

# Lists file paths
image_path_player = load_file_paths(DIRECTORY, FILE_NAMES)
image_collectibles = load_file_paths(DIRECTORY, ['collectible'])
image_mobs = load_file_paths(DIRECTORY, ['creature'])
image_path_black = load_file_paths(DIRECTORY,['black'])

# Defines sprite classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.player_size = 100       #100
        self.animation_player_counter = 0
        self.player_frames = []
        for n in range(len(image_path_player)):
            player_img = pygame.image.load(image_path_player[n]).convert_alpha()
            player_img = pygame.transform.scale(player_img, (self.player_size, self.player_size))
            imm = [player_img]
            self.player_frames.append(imm)
        self.image = self.player_frames[self.animation_player_counter][0]
        self.rect = self.image.get_rect()
        self.rect.x = cell_size * 4.25
        self.rect.y = cell_size * 2.7
        self.can_jump = True
        self.vel = 0  # gravity
        self.gravity = .6
        self.propulsion = 2
        self.animation_player_facing = 1  # 1 = facing right, 0 = facing left
        self.jet_active = 0  # has the jet on its back
        self.jeton = 0  # jet is turned on
        self.boost = 0  # makes jump higher
        self.light = 1  # player has NO source of light?
        self.type_of_torch = 0
        self.rotation = 0
        self.collectibles_gathered = []
        self.position = [0, 0]
        self.correction = [0, 0]

    def animate(self):
        self.animation_player_counter += 0.1
        if self.jet_active == 0:
            if int(self.animation_player_counter * 10) == 50 and (random.randint(0, 20) != 0):
                self.animation_player_counter = 0
            if self.animation_player_counter >= 10:
                self.animation_player_counter = 0
        else:
            if self.animation_player_counter < 10:
                self.animation_player_counter = 10
            if int(self.animation_player_counter * 10) == 150:
                self.animation_player_counter = 10
        self.image = self.player_frames[int(self.animation_player_counter + 5* self.jeton + 20 * self.light + 40 * self.type_of_torch)][0]

    def rules(self):
        if self.type_of_torch == 0:
            self.rotation = 0

        if self.jeton and self.jet_active:
            self.vel = -1 * self.propulsion

        if self.jet_active != 1:
            self.jeton = 0

        self.vel += self.gravity

    def avoid_collisions(self):
        for other_sprite in wall_sprite_list:
            if other_sprite.rect.collidepoint(self.rect.midbottom) and other_sprite.rect.centery > self.rect.centery:  # Check bottom collision first
                all_sprites_list.update(move_x = 0, move_y = - (self.rect.bottom - other_sprite.rect.top) / step)
                self.vel = 0
                self.can_jump = True
            elif other_sprite.rect.collidepoint(self.rect.midtop) and other_sprite.rect.centery < self.rect.centery:  # Check top collision next
                all_sprites_list.update(move_x = 0, move_y = - (self.rect.top - other_sprite.rect.bottom) / step)
                self.vel = 0
            elif other_sprite.rect.collidepoint(self.rect.midright) and other_sprite.rect.centerx > self.rect.centerx:  # Check right collision next
                all_sprites_list.update(move_x = -(self.rect.right - other_sprite.rect.left) / step, move_y = 0)
            elif other_sprite.rect.collidepoint(self.rect.midleft) and other_sprite.rect.centerx < self.rect.centerx: # Check left collision last
                all_sprites_list.update(move_x = -(self.rect.left - other_sprite.rect.right) / step, move_y = 0)
            if int((other_sprite.rect.centerx - self.rect.centerx) / cell_size) == 0:
                self.position[0] = other_sprite.location[0]
                self.correction[0] = other_sprite.rect.centerx - self.rect.centerx
            if int((other_sprite.rect.centery - self.rect.centery) / cell_size) == 0:
                self.position[1] = other_sprite.location[1]
                self.correction[1] = other_sprite.rect.centery - self.rect.centery

    def update(self):
        self.animate()
        self.rules()
        self.avoid_collisions()

    def draw(self):
        if self.animation_player_facing == 0:
            img = pygame.transform.flip(self.image,True,False)
        else:
            img = self.image
        screen.blit(img, self.rect)

class WallSprite(pygame.sprite.Sprite):
    def __init__(self, filename, cell_size, sprite_x, sprite_y, row, col):
        super().__init__()
        self.image = pygame.image.load(filename).convert_alpha()
        self.image = pygame.transform.scale(self.image, (cell_size, cell_size))
        self.rect = self.image.get_rect()
        self.rect.x = sprite_x
        self.rect.y = sprite_y
        self.name = filename
        self.location = [col, row]

    def move(self, move_x, move_y):
        global x, y
        self.rect.x -= move_x * step
        self.rect.y -= move_y * step
        x += move_x / 10000
        y += move_y / 10000

    def update(self, move_x, move_y):
        self.move(move_x, move_y)

class Collectibles(pygame.sprite.Sprite):
    def __init__(self, image_number):
        super().__init__()
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(image_collectibles[image_number]).convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(cell_size / 2), int(cell_size / 2)))
        self.rect = self.image.get_rect(midbottom = (0, 0))            # FIX FIX FIX
        self.number = image_number
        self.name = COLLECTIBLES[image_number]

    def touched_by_player(self):
        collectibles_touched = pygame.sprite.spritecollide(player.sprite, pygame.sprite.Group(self), True)
        for collided_sprites in collectibles_touched:
            n = collided_sprites.number
            player.sprite.collectibles_gathered.append(n)
            log_event("Collectible gathered: " + str(COLLECTIBLES[n]), player.sprite.position)
        player.sprite.collectibles_gathered = list(filter(lambda item: item != [], player.sprite.collectibles_gathered))

    def move(self, move_x, move_y):
        self.rect.x -= move_x * step
        self.rect.y -= move_y * step

    def update(self, move_x, move_y):
        self.move(move_x, move_y)
        self.touched_by_player()

class Blast(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("MAZE/maze_blocks/blast01.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.facing = (player.sprite.animation_player_facing - .5) * 2
        self.rect = self.image.get_rect(center = (cell_size * 4.5 + self.facing * 15, cell_size * 3))

    def move(self, move_x, move_y):
        self.rect.x += self.facing * 20 - move_x * step
        self.rect.y -= move_y * step

    def collide(self):
        for other_sprite in mob_sprite_list:
            if self.rect.colliderect(other_sprite.rect):
                other_sprite.kill()
                self.kill()
                log_event("Mob killed", player.sprite.position)
        for other_sprite in wall_sprite_list:
            if self.rect.colliderect(other_sprite.rect):
                self.kill()

    def update(self, move_x, move_y):
        self.move(move_x, move_y)
        self.collide()

class Mob(pygame.sprite.Sprite):
    def __init__(self, image_number):
        super().__init__()
        self.number = image_number
        self.image = pygame.image.load(image_mobs[image_number]).convert_alpha()
        self.img = pygame.transform.scale(self.image, (200, 200))
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.facing = [1, 0]
        self.mob_length = 80                                    # Adjust the desired mob path length
        self.speed = mob_speed[image_number]
        self.chase = mob_chase[image_number]
        self.fly = mob_fly[image_number]
        self.blob = 1
        self.blob_message_counter = 0
        self.on_screen = 0

    def spawn(self, player_x, player_y):
        temp5 = []
        for temp in range(1, size_x - 1):
            for temp2 in range(1, size_y - 1):
                if (maze[temp2][temp] == " " and self.fly == 1) or (maze[temp2][temp] == " " and maze[temp2 + 1][temp] == maze[temp2 + 1][temp - 1] ==maze [temp2 + 1][temp + 1] != " "):
                    temp5.append([[temp, temp2]])

        random.shuffle(temp5)
        log_event("Mob spawn", temp5[0][0])
        self.spawn_location = temp5[0][0]
        self.rect = self.image.get_rect(center=(cell_size * (self.spawn_location[0] + 4.5 - player_x) + player.sprite.correction[0], cell_size * (self.spawn_location[1] + 3 - player_y) + player.sprite.correction[1]))

    def create_path(self):
        self.path = [[0 ,0]]
        self.pathend = [[0, 0]]
        self.position = [0, 0]
        self.position [0] = self.spawn_location [0]
        self.position [1] = self.spawn_location [1]
        if self.fly:
            directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        else:
            directions = [[1, 0], [-1, 0]]
        for _ in range(self.mob_length):
            random.shuffle(directions)
            temp = self.position[0] + directions[0][0]      # 0 is X
            temp2 = self.position[1] + directions[0][1]     # 1 is Y
            if (maze[temp2][temp] == " " and self.fly == 1) or (maze[temp2][temp] == " " and maze[temp2 + 1][temp] != " "):
                self.path.append(directions[0])
                self.pathend.append([-x for x in directions[0]])
                self.position[0] += directions[0][0]
                self.position[1] += directions[0][1]
        for n in range(len(self.pathend), 0, -1):
            self.path.append(self.pathend[n - 1])
        self.step_counter = 0

    def move(self, move_x, move_y):
        if self.rect.x > - cell_size and self.rect.x < 1920 + cell_size and self.rect.y > - cell_size and self.rect.y < 1080 + cell_size:
            self.on_screen = 1
            self.rect.x -= (move_x - self.path[0][0] * self.speed) * step
            self.rect.y -= (move_y - self.path[0][1] * self.speed) * step
            self.facing = self.path[0]
            if self.step_counter < cell_size / (step * self.speed):
                self.step_counter += 1
            else:
                self.path = self.path[1:]
                self.path.append(self.facing)
                self.step_counter = 0
            if self.fly != 1:
                self.rect.y += 5
                for other_sprite in wall_sprite_list:
                    if other_sprite.rect.collidepoint(self.rect.midbottom) and other_sprite.rect.centery > self.rect.centery:  # Check bottom collision first
                        self.rect.bottom = other_sprite.rect.top - 1
        else:
            self.on_screen = 0
            self.rect.x -= (move_x) * step
            self.rect.y -= (move_y) * step

    def face(self):
        if self.facing[0] == -1:
            self.image = pygame.transform.flip(self.img, True, False)
        else:
            self.image = self.img

    def collide(self):
        if self.number <= 1 and self.on_screen == 1:
            for other_sprite in mob_sprite_list:
                if other_sprite.on_screen == 1 and other_sprite.number <= 1:
                    if (self.rect.colliderect(other_sprite.rect) and other_sprite != self): # or (self.on_screen == other_sprite.on_screen == 0 and random.randint(0,100000) < 1):
                        self.blob += other_sprite.blob
                        other_sprite.kill()
                        if self.blob == 2:
                            self.create_amalgamation()
                        if self.blob >= 3:
                            self.create_blob()
                        log_event("Blob at " + str(self.blob))

    def create_amalgamation(self):
        log_event("Amalgamation was born")
        self.number = 1
        self.image = pygame.image.load(image_mobs[1]).convert_alpha()
        self.img = pygame.transform.scale(self.image, (200, 200))
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.speed = mob_speed[1]
        self.chase = mob_chase[1]
        self.fly = mob_fly[1]
        self.blob_message_counter = 100

    def create_blob(self):
        log_event("Blob was born")
        self.number = 2
        self.image = pygame.image.load(image_mobs[2]).convert_alpha()
        self.img = pygame.transform.scale(self.image, (200, 200))
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.speed = mob_speed[2]
        self.chase = mob_chase[2]
        self.fly = mob_fly[2]
        self.blob_message_counter = 100

    def announce_blob(self):
        self.blob_message_counter -= 1
        blob_message = font.render("REFUGEES BLOBBED", True, font_color)
        screen.blit(blob_message, (1000, 200))

    def update(self, move_x, move_y):
        self.move(move_x, move_y)
        self.face()
        self.collide()
        if self.blob_message_counter > 0:
            self.announce_blob()

# Function that loads the wall block sprites
def load_wall_sprites(directory, cell_size):
    wall_sprites_list = {}
    sprite_configs = ["0000", "1000", "0100", "0010", "0001", "1100", "0110", "0011",
                      "1001", "1010", "0101", "1110", "0111", "1101", "1011", "1111"]
    for num in range(len(sprite_configs)):
        filename = os.path.join(directory, sprite_configs[num] + "d.png")
        wall_sprites_list[sprite_configs[num]] = WallSprite(filename, cell_size, 0, 0, 0, 0)
    return wall_sprites_list

# Function that generates the maze
def generate_maze(x1, y1, x2, y2, size_x, size_y, h_c = 5, v_c = 0, h = 0, v = 0):
    wall_char = '\u2588'  # Unicode character U+2588 (Full Block)
    maze = [[wall_char for _ in range(size_x)] for _ in range(size_y)]
    maze[x1][y1] = 'S'
    maze[x2][y2] = 'E'

    # Recursive function to create paths in the maze
    def create_path(x, y, level = 1, h_c = 0, v_c = 0, h = 0, v = 0):
        # if level == 2 and random.randint(0,10) <= 6:                #increases the likelihood fof vertical paths after 50 in depth
        #     directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 0)]
        # else:
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(directions)
        if random.randint(0, 100) <= h_c:
            temp2 = directions.index((0, 1))
            temp = directions[:temp2]
            temp.append((0, 1))
            temp.extend([(0, 1)] * 2)
            temp.extend(directions[temp2 + 1:])
            directions = temp

        if random.randint(0, 100) <= v_c:
            temp2 = directions.index((1, 0))
            temp = directions[:temp2]
            temp.append((1, 0))
            temp.extend([(1, 0)] * 2)
            temp.extend(directions[temp2 + 1:])
            directions = temp

        size_x = len(maze[0])  # Get the size of the maze in the x-direction
        size_y = len(maze)  # Get the size of the maze in the y-direction

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            adjacent_path_count = 0

            for ddx, ddy in directions:
                adj_x, adj_y = new_x + ddx, new_y + ddy
                if (
                    0 <= adj_x < size_x
                    and 0 <= adj_y < size_y
                    and maze[adj_y][adj_x] == ' '
                ):
                    adjacent_path_count += 1

            if (
                1 <= new_x < size_x - 1
                and 1 <= new_y < size_y - 1
                and maze[new_y][new_x] == wall_char
                and adjacent_path_count < 2
            ):
                maze[new_y][new_x] = ' '
                create_path(new_x, new_y, level, h_c = h_c, v_c = v_c)

    create_path(x1, y1, level = 1, h_c = h_c, v_c = v_c)

    # create level 2
    old_len = len(maze) - 2
    next_level = [[wall_char for _ in range(size_x)] for _ in range(size_y)]
    maze.extend(next_level)
    create_path(2, old_len, level = 2, h_c = 0, v_c = 50)

    # space to create other levels

    return maze

# Creates the maze
maze = generate_maze(x1, y1, x2, y2, size_x, size_y, h_c = 50)

# Initializes Pygame
pygame.init()
pygame.key.set_repeat(40, 5)
size = (dist_x * cell_size, dist_y * cell_size)
screen = pygame.display.set_mode((1920, 1080), FULLSCREEN) #size
pygame.display.set_caption("Maze Game")
font = pygame.font.SysFont(None, 24)
font_color = (WHITE)

# Loads images
image_background = pygame.image.load(DIRECTORY +'/background.png').convert_alpha()

def load_mist(name = "mist.png"):
    image_mist = pygame.image.load(DIRECTORY + '/' + name).convert_alpha()
    image_mist.set_alpha(0)
    return(image_mist)

def draw_mist(mist_counter, image_mist, mist_x, off_set, mist_move):
    mist_counter += (255 * mist - mist_counter) // 100
    alpha_value = int(mist_counter)
    if alpha_value < 240 and alpha_value % 20 == 0:
        image_mist.set_alpha(alpha_value)
    mist_x_offset = int(off_set + mist_x)
    for temp3 in mist_h_range:
        for temp4 in mist_w_range:
            screen.blit(image_mist, (
            mist_x_offset - temp4 * mist_w - (x * 40) % mist_w, - (deep * cell_size) % mist_h + temp3 * mist_h))
            mist_x += mist_move
            mist_x = mist_x * (abs(mist_x) < mist_w)  # resets mist 1 loop
    return(mist_counter, mist_x)

image_mist = load_mist("mist.png")
image_mist_2 = load_mist("mist2.png")
mist_h = image_mist.get_height()
mist_w = image_mist.get_width()
mist_h_range = range(-2, int(1080 // mist_h + 2))
mist_w_range = range(-2, int(1920 // mist_w + 3))

image_dark_light = []
for temp in range(len(image_path_black)):
    temp2 = pygame.image.load(image_path_black[temp]).convert_alpha()
    temp2 = pygame.transform.scale(temp2, size)
    image_dark_light.append(temp2)

# slider = Slider(screen, 100, 100, 800, 40, min=100, max=500, step=10)
# factor = 0

# Creates lists of sprites
collectibles_list = pygame.sprite.Group()
all_sprites_list = pygame.sprite.Group()
wall_sprite_list = pygame.sprite.Group()
mob_sprite_list = pygame.sprite.Group()
blast_list = pygame.sprite.Group()



coll_icon = ["", "", "", "", "", "", "", "", "", "", ""]
for i_i in range(len(COLLECTIBLES)):
    coll_icon[i_i] = pygame.image.load(image_collectibles[i_i]).convert_alpha()
    coll_icon[i_i] = pygame.transform.scale(coll_icon[i_i], (40, 40))

# Creates the maze walls
maze_width = len(maze[0])
maze_height = len(maze)
wall_sprites = load_wall_sprites(DIRECTORY, cell_size)
for row in range(maze_height):
    for col in range(maze_width):
        if maze[row][col] == '\u2588':
            adjacent_blocks = "/"
            sprite_x = col * cell_size
            sprite_y = row * cell_size
            if row > 0 and maze[row - 1][col] == ' ':
                adjacent_blocks += "1"
            else:
                adjacent_blocks += "0"
            if col < maze_width - 1 and maze[row][col + 1] == ' ':
                adjacent_blocks += "1"
            else:
                adjacent_blocks += "0"
            if row < maze_height - 1 and maze[row + 1][col] == ' ':
                adjacent_blocks += "1"
            else:
                adjacent_blocks += "0"
            if col > 0 and maze[row][col - 1] == ' ':
                adjacent_blocks += "1d.png"
            else:
                adjacent_blocks += "0d.png"
            sprite_file = DIRECTORY+adjacent_blocks
            sprite = WallSprite(sprite_file, cell_size, sprite_x, sprite_y, row, col)
            all_sprites_list.add(sprite)
            wall_sprite_list.add(sprite)

# Creates the map
tile_size = 10
map_width = len(maze[0]) * tile_size
map_height = len(maze) * tile_size
map_margin = int((1080 - map_height)/2)
map_surface = pygame.Surface((map_width, map_height))
for y, row in enumerate(maze):
    temp3 = ""
    for x, char in enumerate(row):
        temp3 += char
        if char == '\u2588':
            tile_color = BLACK
        else:
            tile_color = WHITE
        pygame.draw.rect(map_surface, tile_color, (x * tile_size, y * tile_size, tile_size, tile_size))
    with open(DIRECTORY + "/log.csv", "a", encoding='UTF8', newline="") as temp:
        writer = csv.writer(temp)
        writer.writerow([temp3])

# # prints map of maze
# for temp in range(len(maze)):
#     temp3 = ""
#     for temp2 in range (len(maze[0])):
#         temp3 += maze[temp][temp2]
#     log = f'{temp:03d} {temp3}'  # LOG
#     with open(DIRECTORY + "/log.csv", "a", encoding='UTF8', newline="") as temp:
#         writer = csv.writer(temp)
#         writer.writerow([log])

# Creates the collectibles and places them in the maze
for temp in range(len(COLLECTIBLES)):
    temp2 = Collectibles (temp)
    collectibles_list.add(temp2)
    all_sprites_list.add(temp2)
for temp, temp2 in enumerate(collectibles_list.sprites()):
    actx, acty = 0, 0
    while maze[acty][actx] == '\u2588':
        actx = random.randint(minxs[temp], maxxs[temp])
        acty = random.randint(minys[temp], maxys[temp])
    maze[acty][actx] = "C"
    log_event("Collectible spawn: " + str(COLLECTIBLES[temp2.number]), [actx, acty])
    temp2.rect.center = (cell_size * (actx + .5), cell_size * (acty + .5))

# Create the player
player = pygame.sprite.GroupSingle()
player.add(Player())
player.sprite.update()
pygame.sprite.spritecollide(player.sprite, wall_sprite_list, True)

# Creates the mobs and places them in the maze
for mob_n in range(len(mob_spawn_rate)):
    for mob_nn in range(mob_spawn_rate[mob_n]): #if random.randint(0, 10000) <= mob_spawn_rate[mob_n]:
        mob = Mob(mob_n)
        mob.spawn(player_x = player.sprite.position[0], player_y = player.sprite.position[1])
        mob.create_path()
        all_sprites_list.add(mob)
        mob_sprite_list.add(mob)

# Game loop
done = False
clock = pygame.time.Clock()

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # Clears the screen, draws background, finds depth
    screen.fill(WHITE)
    screen.blit(image_background, (- x * 10, - y * 10))                       #FIX FIX FIX
    deep = player.sprite.position[1]

    # Draws the player, mobs and collectibles
    player.sprite.draw()
    collectibles_list.draw(screen)
    mob_sprite_list.draw(screen)
    blast_list.draw(screen)

    # Draws mist
    if mist or mist_counter > 30:
        mist_counter, mist_1_x = draw_mist(mist_counter, image_mist, mist_1_x, 0, -.05)
        temp, mist_2_x = draw_mist(mist_counter, image_mist_2, mist_2_x, 1920, 0.07)

    # Draws wall sprites
    wall_sprite_list.draw(screen)

    # Updates
    all_sprites_list.update(move_x = 0, move_y = player.sprite.vel)
    player.sprite.update()

    # Draws darkness and light
    if deep > depth_of_light:
        if player.sprite.light == 1:
            shade = pygame.Surface(size)
            shade.set_alpha(min(int(deep - depth_of_light) * darkness, 255))
            screen.blit(shade, (0, 0))
        else:
            ime = image_dark_light[player.sprite.type_of_torch + player.sprite.rotation]
            ime.set_alpha(min(int(deep - depth_of_light) * darkness, 255))
            if player.sprite.animation_player_facing == 0:
                ime = pygame.transform.flip(ime, True, False)
            screen.blit(ime, (- cell_size * .4, 0))

    # Displays depth
    depth = font.render("Depth: " + str(int(deep)), True, font_color)
    screen.blit(depth, (200, 200))

    # Displays boost
    if player.sprite.boost:
        boost_on = font.render("BOOST", True, font_color)
        screen.blit(boost_on, (200, 230))

    # Displays the images of sprites of collectibles_gathered
    ico_number = 0
    for i_i in player.sprite.collectibles_gathered:
        ico_number = max(ico_number, i_i + 1)
        screen.blit(coll_icon[i_i], (200, 320 + 40 * i_i))

    # Displays frame for pannel
    pygame.draw.rect(screen, (200, 200, 200), (180, 180, 200, 60 + ico_number * 40 + 80 * (ico_number > 0)), 1)

    # # Displays sliders
    # pygame_widgets.update(pygame.event.get())
    # factor = slider.value
    # print("factor = " + str(factor))

#    pygame.display.update()

    # Handles player events
    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE]:
        done = True

    if keys[pygame.K_UP] and player.sprite.can_jump == True:
        player.sprite.vel = -jump - player.sprite.boost
        player.sprite.can_jump = False
    if keys[pygame.K_RIGHT]:
        all_sprites_list.update(move_x=1, move_y=0)
        player.sprite.animation_player_facing = 1
    if keys[pygame.K_LEFT]:
        all_sprites_list.update(move_x=-1, move_y=0)
        player.sprite.animation_player_facing = 0

    if keys[pygame.K_j]:  # and 0 in collectibles_gathered:
        player.sprite.jet_active = 1
    if keys[pygame.K_k]:  # and 0 in collectibles_gathered:
        player.sprite.jet_active = 0
    if keys[pygame.K_RETURN] and player.sprite.jet_active and jet_counter == 10:
        player.sprite.jeton = 1 - player.sprite.jeton
        jet_counter -= 1
    if jet_counter < 10:
        jet_counter -= 1
        if jet_counter == 0:
            jet_counter = 10

    if keys[pygame.K_l] and 2 in player.sprite.collectibles_gathered or keys[pygame.K_l] and 1 in player.sprite.collectibles_gathered:
        player.sprite.light = 0
        player.sprite.type_of_torch = 1 - player.sprite.type_of_torch
    if keys[pygame.K_SEMICOLON]:
        player.sprite.light = 1
        player.sprite.type_of_torch = 0
    if player.sprite.type_of_torch == 1:
        if keys[pygame.K_1]:
            player.sprite.rotation = 0
        elif keys[pygame.K_2]:
            player.sprite.rotation = 1
        elif keys[pygame.K_3]:
            player.sprite.rotation = 2

    if keys[pygame.K_SPACE] and gun_counter == 0 and 4 in player.sprite.collectibles_gathered:
        blast = Blast()
        all_sprites_list.add(blast)
        blast_list.add(blast)
        gun_counter += 1
    if gun_counter > 0:
        gun_counter += 1
        gun_counter = int(gun_counter % 10)

    if keys[pygame.K_F1]:
        test_keys = 1
    elif keys[pygame.K_F2]:
        test_keys = 0
    if test_keys == 1:
        if keys[pygame.K_m]:
            mist = 1
        if keys[pygame.K_n]:
            mist = 0

    if keys[pygame.K_g] and 5 in player.sprite.collectibles_gathered:
        if player.sprite.animation_player_facing == 1:
            screen.blit(map_surface, (map_margin, map_margin))
        else:
            screen.blit(map_surface, (1920 - map_width - map_margin, map_margin))

    if keys[pygame.K_b] and 3 in player.sprite.collectibles_gathered:
        player.sprite.boost = 1
    if keys[pygame.K_v]:
        player.sprite.boost = 0

    pygame.display.update()

    # Update the screen
    pygame.display.flip()

    # Limit frames per second
    clock.tick(60)
#    print(clock.get_time())

# Quit the game
pygame.quit()


