import pygame, math, os, time, json
import player as p
import objects as o

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(300)
pygame.display.set_caption('Serena Caelum')
pygame.display.set_icon(pygame.image.load('assets/tilesets/tiles/icon.png'))
pygame.joystick.init()
WINDOW_SIZE = (720,480)
CAMERA_SIZE = (240,160)
CHUNK_SIZE = CAMERA_SIZE
TILE_SIZE = (16,16)
FPS = 60
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
COLORSET = []
GREYSCALE = []

main_display = pygame.display.set_mode(WINDOW_SIZE, pygame.NOFRAME)
camera = pygame.Surface(CAMERA_SIZE)
true_camera_pos = [0,0]
clock = pygame.time.Clock()
last_time = time.time()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
joystick_buttonstate = [False]*16
settings = {'Window Size':3,'Window Border':1,'Full Screen':0,'Music Volume':3,'Sound Volume':3}
tilesets_database = {}
sounds_database = {}

tile_rect_list = {}
obj_list = {'gates':[], 'enemies':[], 'items':[], 'projectiles':[]}
level_config = {}
current_chunk = [0,0]

player = p.Player(16*7,16*7)


def fill_colorset():
    _range = 85
    incr = 3
    color = [255,0,0]
    for i in range(_range):
        color[1] += incr
        COLORSET.append((color[0],color[1],color[2]))
    for i in range(_range):
        color[0] -= incr
        COLORSET.append((color[0],color[1],color[2]))
    for i in range(_range):
        color[2] += incr
        COLORSET.append((color[0],color[1],color[2]))
    for i in range(_range):
        color[1] -= incr
        COLORSET.append((color[0],color[1],color[2]))
    for i in range(_range):
        color[0] += incr
        COLORSET.append((color[0],color[1],color[2]))
    for i in range(_range):
        color[2] -= incr
        COLORSET.append((color[0],color[1],color[2]))

    min_grey_brightness = 50
    max_grey_brightness = 150
    color = min_grey_brightness

    for i in range(510):
        GREYSCALE.append((color,color,color))

    for i in range(min_grey_brightness, max_grey_brightness):
        color += 1
        GREYSCALE.append((color,color,color))
        GREYSCALE.append((color,color,color))

    for i in range(min_grey_brightness, max_grey_brightness):
        GREYSCALE.append((color,color,color))
        GREYSCALE.append((color,color,color))
        color -= 1
fill_colorset()


def apply_settings(settings):
    global WINDOW_SIZE, main_display
    
    pygame.mixer.music.set_volume(settings['Music Volume']/10)
    WINDOW_SIZE = (CAMERA_SIZE[0]*settings['Window Size'], CAMERA_SIZE[1]*settings['Window Size'])
    window_mode = pygame.NOFRAME
    if settings['Full Screen'] == 1:
        window_mode = pygame.FULLSCREEN|pygame.SCALED
    elif settings['Window Border'] == 1:
        window_mode = pygame.RESIZABLE
    
    main_display = pygame.display.set_mode(WINDOW_SIZE, window_mode)
apply_settings(settings)


def fill_tilesets_database(path):
    _dir = os.listdir(path)
    for directory in _dir:
        tilesets_database[directory+'_list'] = {}
        _file = os.listdir(path+'/'+directory)
        for f in _file:
            tile = pygame.image.load(path+'/'+directory+'/'+f)
            tile.set_colorkey(BLACK)
            tile.convert_alpha()
            tilesets_database[directory+'_list'][f[:-4]] = tile
            if directory == 'tiles':
                tile_rect_list[f[:-4]] = []
fill_tilesets_database('assets/tilesets')


def fill_sounds_database(path):
    database = {}
    files = os.listdir(path)
    for f in files:
        database[f[:-4]] = pygame.mixer.Sound(path+'/'+f)
    return database
sounds_database = fill_sounds_database('assets/sounds/sfx/menu')
player.sounds_database = fill_sounds_database('assets/sounds/sfx/player')
o.enemy_sounds_database = fill_sounds_database('assets/sounds/sfx/objects')


def play_sound(sound):
    sounds_database[sound].set_volume(settings['Sound Volume']/10)
    sounds_database[sound].play()


def read_input_joystick(event):
    # 0=A,1=B,2=X,3=Y,4=L,5=R,6=SELECT,7=START,8=L3,9=R3,10-13=DPAD
    button_pressed = -1
    if event.type == pygame.JOYBUTTONDOWN:
        joystick_buttonstate[event.button] = True
        button_pressed = event.button
    if event.type == pygame.JOYBUTTONUP:
        joystick_buttonstate[event.button] = False  
    if event.type == pygame.JOYHATMOTION:
        if event.value[0] < 0:
            joystick_buttonstate[10] = True
            button_pressed = 10
        else:
            joystick_buttonstate[10] = False

        if event.value[0] > 0: 
            joystick_buttonstate[11] = True
            button_pressed = 11
        else:
            joystick_buttonstate[11] = False

        if event.value[1] > 0:
            joystick_buttonstate[12] = True
            button_pressed = 12
        else:
            joystick_buttonstate[12] = False

        if event.value[1] < 0:  
            joystick_buttonstate[13] = True
            button_pressed = 13
        else:
            joystick_buttonstate[13] = False

    return button_pressed


def load_level_config(level):
    f=open('config/level_'+level+'.json')
    return json.load(f)


def getFromLevelConfig(config):
    return level_config[config]


def change_level(gate):
    global level_config, current_chunk
        
    clear_rect_list(obj_list)
    level_config = load_level_config(gate.level)
    gates_mappings = getFromLevelConfig('gate_mappings')
    gate_cor = gates_mappings[gate.id]
                    
    current_chunk = gate_cor[0]
    
    player.rect.x = (current_chunk[0]*CHUNK_SIZE[0])+(gate_cor[1][0]*TILE_SIZE[0])
    player.rect.y = (current_chunk[1]*CHUNK_SIZE[1])+(gate_cor[1][1]*TILE_SIZE[1])
                    
    for x in range(-1,2):
        for y in range(-1,2):
            spawn_objects([current_chunk[0]+x, current_chunk[1]+y])


def initialize_chunk(chunk_loc, chunk_id):
    tile_mappings = getFromLevelConfig('tile_mappings')
    chunks_map = getFromLevelConfig('chunks_map')
    y = 0
    for row in chunks_map[chunk_id]:
        x = 0
        for tile in row:
            if tile != '0':
                tile_rect = pygame.Rect(x*TILE_SIZE[0] + chunk_loc[0]*CHUNK_SIZE[0], y*TILE_SIZE[1] + chunk_loc[1]*CHUNK_SIZE[1], TILE_SIZE[0], TILE_SIZE[1])
                if tile_mappings[tile] not in tile_rect_list:
                    tile_rect_list[tile_mappings[tile]] = []
                tile_rect_list[tile_mappings[tile]].append(tile_rect)
            x += 1
        y += 1


def set_chunks(current_chunk):
    chunks_map = getFromLevelConfig('chunks_map')
    for x in range(-1,2):
        for y in range(-1,2):
            chunk_loc = [current_chunk[0]+x, current_chunk[1]+y]
            chunk_id = str(chunk_loc[0]) + ',' + str(chunk_loc[1])
            if chunk_id in chunks_map:
                initialize_chunk(chunk_loc, chunk_id)


def spawn_objects(chunk):
    objects_map = getFromLevelConfig('objects_map')
    chunk_id = str(chunk[0]) + ',' + str(chunk[1])
    y = 0
    if chunk_id in objects_map:
        for row in objects_map[chunk_id]:
            x = 0
            for object in row:
                if object[0] == 'G':
                    obj = o.Gate(object[2:-1],object[-1],pygame.Rect(x*TILE_SIZE[0] + chunk[0]*CHUNK_SIZE[0], y*TILE_SIZE[1] + chunk[1]*CHUNK_SIZE[1], TILE_SIZE[0], TILE_SIZE[1]))
                    obj_list['gates'].append(obj)
                if object[0] == 'I':
                    obj = o.Item(int(object[-1]), x*TILE_SIZE[0] + chunk[0]*CHUNK_SIZE[0], y*TILE_SIZE[1] + chunk[1]*CHUNK_SIZE[1])
                    obj_list['items'].append(obj)
                if object[0] == 'E':
                    if object[2:] == 'Frog':
                        obj = o.Frog(x*TILE_SIZE[0] + chunk[0]*CHUNK_SIZE[0] +1, y*TILE_SIZE[1] + chunk[1]*CHUNK_SIZE[1] +8)
                        obj_list['enemies'].append(obj)
                    elif object[2:] == 'Bat':
                        obj = o.Bat(x*TILE_SIZE[0] + chunk[0]*CHUNK_SIZE[0] +2, y*TILE_SIZE[1] + chunk[1]*CHUNK_SIZE[1])
                        obj_list['enemies'].append(obj)
                    elif object[2:] == 'Wolf':
                        obj = o.Wolf(x*TILE_SIZE[0] + chunk[0]*CHUNK_SIZE[0], y*TILE_SIZE[1] + chunk[1]*CHUNK_SIZE[1])
                        obj_list['enemies'].append(obj)
                    elif object[2:] == 'Bird':
                        obj = o.Bird(x*TILE_SIZE[0] + chunk[0]*CHUNK_SIZE[0], y*TILE_SIZE[1] + chunk[1]*CHUNK_SIZE[1])
                        obj_list['enemies'].append(obj)
                    elif object[2:] == 'Ghost':
                        obj = o.Ghost(x*TILE_SIZE[0] + chunk[0]*CHUNK_SIZE[0], y*TILE_SIZE[1] + chunk[1]*CHUNK_SIZE[1])
                        obj_list['enemies'].append(obj)
                    elif object[2:] == 'Boss':
                        obj = o.Boss()
                        obj_list['enemies'].append(obj)
                x += 1
            y += 1


def despawn_objects(chunk):
    for _list in obj_list:
        removed = 0
        for i in range(len(obj_list[_list])):
            rect = obj_list[_list][i-removed].rect
            if rect.x > chunk[0]*CHUNK_SIZE[0] and rect.x < (chunk[0]+1)*CHUNK_SIZE[0] and rect.y > chunk[1]*CHUNK_SIZE[1] and rect.y < (chunk[1]+1)*CHUNK_SIZE[1]:
                obj_list[_list].pop(i-removed)
                removed += 1


def set_objects(prev_chunk, next_chunk):
    spawn_offset = 1
    despawn_offset = 2
    if next_chunk[0] != prev_chunk[0] and next_chunk[1] != prev_chunk[1]:
        pass # this condition is if the next chunk is diagonal 
    else:
        if next_chunk[0] != prev_chunk[0]:
            if next_chunk[0] < prev_chunk[0]:
                spawn_offset *= -1
            else:
                despawn_offset *= -1

            despawn_objects([next_chunk[0]+despawn_offset, next_chunk[1]])
            despawn_objects([next_chunk[0]+despawn_offset, next_chunk[1]+1])
            despawn_objects([next_chunk[0]+despawn_offset, next_chunk[1]-1])
            
            spawn_objects([next_chunk[0]+spawn_offset, next_chunk[1]])
            spawn_objects([next_chunk[0]+spawn_offset, next_chunk[1]+1])
            spawn_objects([next_chunk[0]+spawn_offset, next_chunk[1]-1])
            
        elif next_chunk[1] != prev_chunk[1]:
            if next_chunk[1] < prev_chunk[1]:
                spawn_offset *= -1
            else:
                despawn_offset *= -1

            despawn_objects([next_chunk[0], next_chunk[1]+despawn_offset])
            despawn_objects([next_chunk[0]+1, next_chunk[1]+despawn_offset])
            despawn_objects([next_chunk[0]-1, next_chunk[1]+despawn_offset])

            spawn_objects([next_chunk[0], next_chunk[1]+spawn_offset])
            spawn_objects([next_chunk[0]+1, next_chunk[1]+spawn_offset])
            spawn_objects([next_chunk[0]-1, next_chunk[1]+spawn_offset])


def set_camera_pos(current_chunk, actor):
    chunks_map = getFromLevelConfig('chunks_map')
    new_pos = [0,0]
    new_pos[0] = actor.rect.x - (CAMERA_SIZE[0] / 2) + (actor.rect.width / 2)
    new_pos[1] = actor.rect.y - CAMERA_SIZE[1] + player.rect.height + (TILE_SIZE[1]*2)
    
    if new_pos[0] > current_chunk[0] * CHUNK_SIZE[0]:
        if str(current_chunk[0]+1) + ',' + str(current_chunk[1]) in chunks_map:
            true_camera_pos[0] = new_pos[0]
        else:
            true_camera_pos[0] = current_chunk[0] * CHUNK_SIZE[0]

    elif new_pos[0] <= current_chunk[0] * CHUNK_SIZE[0]: 
        if str(current_chunk[0]-1) + ',' + str(current_chunk[1]) in chunks_map:
            true_camera_pos[0] = new_pos[0]
        else:
            true_camera_pos[0] = current_chunk[0] * CHUNK_SIZE[0]
    
    if new_pos[1] >= current_chunk[1] * CHUNK_SIZE[1]:
        if str(current_chunk[0]) + ',' + str(current_chunk[1]+1) in chunks_map:
            true_camera_pos[1] = new_pos[1]
        else:
            true_camera_pos[1] = current_chunk[1] * CHUNK_SIZE[1]

    elif new_pos[1] <= current_chunk[1] * CHUNK_SIZE[1]:
        if str(current_chunk[0]) + ',' + str(current_chunk[1]-1) in chunks_map:
            true_camera_pos[1] = new_pos[1]
        else:
            true_camera_pos[1] = current_chunk[1] * CHUNK_SIZE[1]

    camera_pos = true_camera_pos.copy()
    camera_pos[0] = int(camera_pos[0])
    camera_pos[1] = int(camera_pos[1])
    return camera_pos


def clear_rect_list(tile_rect_list):
    for _list in tile_rect_list:
        tile_rect_list[_list].clear()


def collision_floor_test(rect, tiles_list):
    collision_list = {'tile':[],'slope':{'up':[],'down':[]}}
    for _list in tiles_list:
        for tile in tiles_list[_list]:
            if pygame.Rect.colliderect(rect, tile):
                if _list == 'slope-up':
                    collision_list['slope']['up'].append(tile)
                elif _list == 'slope-down':
                    collision_list['slope']['down'].append(tile)
                else:
                    collision_list['tile'].append(tile)
    return collision_list


def collision_obj_test(rect, obj_list):
    collision_list = {}
    for _list in obj_list:
        collision_list[_list] = []
        for tile in obj_list[_list]:
            if pygame.Rect.colliderect(rect, tile.rect):
                collision_list[_list].append(tile)
                break
                    
    return collision_list              


def move_and_test(rect, velocity, floor_tiles, obj_list, ignore_wall=False):
    collision_direction = {'top': False, 'bottom': False, 'right': False, 'left': False}
    collision_objects = {}

    rect.x += float(velocity[0])
    collision_list = collision_floor_test(rect, floor_tiles)
    if not ignore_wall:
        for tile in collision_list['tile']:
            if velocity[0] > 0:
                rect.right = tile.left
                collision_direction['right'] = True
            elif velocity[0] < 0:
                rect.left = tile.right
                collision_direction['left'] = True
        for type in collision_list['slope']:
            for slope in collision_list['slope'][type]:
                x_pos = rect.x - slope.x
                height_pos = 0
                if type == 'up':
                    height_pos = max(min(x_pos+rect.width, TILE_SIZE[1]), 0)
                else:
                    height_pos = max(min(TILE_SIZE[1]-x_pos, TILE_SIZE[1]), 0)
                target_y = slope.y + TILE_SIZE[1] - height_pos
                if rect.bottom > target_y:
                    rect.bottom = target_y
                    collision_direction['bottom'] = True
    collision_objects = collision_obj_test(rect, obj_list)

    rect.y += float(velocity[1])
    collision_list = collision_floor_test(rect, floor_tiles)
    if not ignore_wall:
        for tile in collision_list['tile']:
            if velocity[1] > 0:
                rect.bottom = tile.top
                collision_direction['bottom'] = True
            elif velocity[1] < 0:
                rect.top = tile.bottom
                collision_direction['top'] = True
        for type in collision_list['slope']:
            for slope in collision_list['slope'][type]:
                x_pos = rect.x - slope.x
                height_pos = 0
                if type == 'up':
                    height_pos = max(min(x_pos+rect.width, TILE_SIZE[0]), 0)
                else:
                    height_pos = max(min(TILE_SIZE[0]-x_pos, TILE_SIZE[0]), 0)
                target_y = slope.y + TILE_SIZE[0] - height_pos
                if rect.bottom > target_y:
                    rect.bottom = target_y
                    collision_direction['bottom'] = True
    collision_list = collision_obj_test(rect, obj_list)
    for _list in collision_list:
        if _list not in collision_objects:
            collision_objects[_list] = collision_list[_list]

    return collision_direction, collision_objects


def draw_chunk_map(camera_pos, chunk_loc, chunk_id, map):
    tile_mappings = getFromLevelConfig('tile_mappings')
    offset = 0
    y = 0
    for row in map[chunk_id]:
        x = 0
        for tile in row:
            if tile != '0':
                if tile_mappings[tile] == 'grass':
                    offset = 2
                elif tile_mappings[tile] == 'tall_grass':
                    offset = 5
                else:
                    offset = 0

                if tile_mappings[tile] != 'slope-up' and tile_mappings[tile] != 'slope-down': 
                    camera.blit(tilesets_database['tiles_list'][tile_mappings[tile]], ((x*TILE_SIZE[0] + chunk_loc[0]*CHUNK_SIZE[0])-camera_pos[0], (y*TILE_SIZE[1] + chunk_loc[1]*CHUNK_SIZE[1])-camera_pos[1]-offset))
            x += 1
        y += 1


def draw_chunks(camera_pos, current_chunk):
    background_map = getFromLevelConfig('background_map')
    chunks_map = getFromLevelConfig('chunks_map')

    for x in range(-1,2):
        for y in range(-1,2):
            chunk_loc = [current_chunk[0]+x, current_chunk[1]+y]
            chunk_id = str(chunk_loc[0]) + ',' + str(chunk_loc[1])

            if chunk_id in background_map:
                draw_chunk_map(camera_pos, chunk_loc, chunk_id, background_map)
            if chunk_id in chunks_map:
                draw_chunk_map(camera_pos, chunk_loc, chunk_id, chunks_map)


def draw_background_parallax(camera_pos):
    background_layers = getFromLevelConfig('background_layers')
    if background_layers:
        for i in range (1,len(background_layers)+1):
            x_pos = 0-camera_pos[0]*background_layers['layer_'+str(i)][1]
            x_pos -= (x_pos // CHUNK_SIZE[0]) * CHUNK_SIZE[0]

            camera.blit(tilesets_database['backgrounds_list'][background_layers['layer_'+str(i)][0]], (x_pos, 0))
            camera.blit(tilesets_database['backgrounds_list'][background_layers['layer_'+str(i)][0]], (x_pos+CHUNK_SIZE[0], 0))
            camera.blit(tilesets_database['backgrounds_list'][background_layers['layer_'+str(i)][0]], (x_pos-CHUNK_SIZE[0], 0))


def draw_foreground_parallax(camera_pos):
    foreground_layers = getFromLevelConfig('foreground_layers')
    if foreground_layers:
        for i in range (1,len(foreground_layers)+1):
            x_pos = 0-camera_pos[0]*foreground_layers['layer_'+str(i)][1]
            x_pos -= (x_pos // CHUNK_SIZE[0]) * CHUNK_SIZE[0]

            camera.blit(tilesets_database['backgrounds_list'][foreground_layers['layer_'+str(i)][0]], (x_pos, 0))
            camera.blit(tilesets_database['backgrounds_list'][foreground_layers['layer_'+str(i)][0]], (x_pos+CHUNK_SIZE[0], 0))
            camera.blit(tilesets_database['backgrounds_list'][foreground_layers['layer_'+str(i)][0]], (x_pos-CHUNK_SIZE[0], 0))


class Hud:
    def __init__(self):
        self.text = Font('assets/fonts/plain.png')
        self.target = None
        self.timer = 0

    def draw_player_hud(self, player):
        pygame.draw.rect(camera, (0,0,0), pygame.Rect(0,0,CAMERA_SIZE[0], 23))
        camera.blit(tilesets_database['hud_list']['player_window'], (0, 0))
        
        for i in range(math.ceil(player.health / (player.max_health/10) )):
            camera.blit(tilesets_database['hud_list']['health_bar'], (2+(i*6), 2))

        #color_offset = math.floor(len(COLORSET) / 56)
        color = (85*3) if player.special >= 20 else 85*4
        for i in range(math.floor(player.special / 0.35)):
            pygame.draw.rect(camera, COLORSET[color], pygame.Rect(3+(i*1),16,1,3))

    def draw_enemy_hud(self, enemy):
        if enemy is not None:
            self.target = enemy
            self.timer = 90

        if self.target is not None:
            camera.blit(tilesets_database['hud_list']['enemy_window'], (CAMERA_SIZE[0]-tilesets_database['hud_list']['enemy_window'].get_width(), 0))
        
            for i in range(math.ceil((self.target.health / self.target.max_health) * 10)):
                camera.blit(tilesets_database['hud_list']['health_bar'], (CAMERA_SIZE[0]-7-(i*6), 2))

            camera.blit(self.text.draw(self.target.id,WHITE), (CAMERA_SIZE[0] - self.text.get_width(self.target.id) - 1, 15))

            self.timer -= 1
            if self.timer <= 0:
                self.timer = 0
                self.target = None

    def draw_inventory(self, inv_select):
        x_offset = 0
        for item in player.inventory:
            camera.blit(item.item_img, (tilesets_database['hud_list']['player_window'].get_width()+2+x_offset,2))
            x_offset += 10

        if inv_select != -1:
            camera.blit(tilesets_database['hud_list']['arrow'], (tilesets_database['hud_list']['player_window'].get_width()+2+(inv_select*10), 13))
            camera.blit(self.text.draw(player.inventory[inv_select].name[player.inventory[inv_select].id],(255,242,0)), (tilesets_database['hud_list']['player_window'].get_width()+36, 4))
            camera.blit(self.text.draw(player.inventory[inv_select].description[player.inventory[inv_select].id],(255,255,255)), (tilesets_database['hud_list']['player_window'].get_width()+36, 15))


class Font:
    def __init__(self, path_to_img, hor_spacing=1):
        self.character_order = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9','.',',','"','\'','?','!','_','#','%','&','(',')','+','-','/',':','<','>']
        self.characters = {}
        self.spacing = hor_spacing
        self.space_width = 3

        font_img = pygame.image.load(path_to_img)
        char_width = 0
        char_count = 0
        for i in range(font_img.get_width()):
            color = font_img.get_at((i,0))
            if color == (255,0,0):
                char_img = self.cut_image(font_img, i - char_width, 0, char_width, font_img.get_height())
                self.characters[self.character_order[char_count]] = char_img
                char_count += 1
                char_width = 0
            else:
                char_width += 1

        self.height = self.characters['A'].get_height()

    def cut_image(self,surf,x,y,width,height):
        surf_copy = surf.copy()
        clip = pygame.Rect(x,y,width,height)
        surf_copy.set_clip(clip)
        cut = surf.subsurface(surf_copy.get_clip())
        return cut.copy()

    def palette_swap(self, img, old_color, new_color):
        img_copy = pygame.Surface(img.get_size())
        img_copy.fill(new_color)
        img.set_colorkey(old_color)
        img_copy.blit(img,(0,0))
        return img_copy

    def get_width(self, text):
        width = 0
        for char in text:
            if char == ' ':
                width += self.space_width
            elif char != '|':
                width += self.characters[char].get_width()
            width += self.spacing
        return width

    def draw(self, text, color=(1,0,0), alpha=255):
        offset = 0
        text_surf = pygame.Surface((self.get_width(text), self.height))
        for char in text:
            if char not in self.characters:
                offset += self.space_width + self.spacing
            else:
                img = self.characters[char]
                img = self.palette_swap(img,(255,255,255),color)
                text_surf.blit(img, (offset, 0))
                text_surf.set_colorkey((0,0,0))
                text_surf.set_alpha(alpha)
                offset += self.characters[char].get_width() + self.spacing
        return text_surf      


class TextScroller:
    def __init__(self, text, font, color, width, height, delay, startoffset=0):
        self.font = font
        self.width = width
        self.height = height
        self.delay = delay
        self.text = text  # list of strings
        self.color = color
        self.startoffset = startoffset
        self.pointer_visible = False

        self.text_ptr = 0
        self.timer = 0
        self.end = False
        self.next = True if len(self.text) > 1 else False

    def update(self):
        self.timer += 1
        
        if self.end and self.timer > 30:
            self.timer = 0
            self.pointer_visible = not self.pointer_visible

        elif not self.end and self.timer >= self.delay:
            self.timer = 0
            if self.text_ptr + 1 >= len(self.text[0]):
                self.end = True
            else:
                self.text_ptr += 1
                if self.text[0][self.text_ptr] != ' ':
                    play_sound('text')
        

    def next_line(self):
        if not self.end:
            self.text_ptr = len(self.text[0])-1
            self.end =  True
        elif self.next:
            self.text.pop(0)
            self.text_ptr = 0
            self.end = False
            self.next = True if len(self.text) > 1 else False
 
    def draw(self):
        text_surf = pygame.Surface((self.width, self.height))
        text_surf.set_colorkey((0,0,0))
        x_offset = self.startoffset
        y_offset = 0
        for i in range(self.text_ptr+1):
            char_width = self.font.get_width(self.text[0][i])
            if x_offset + char_width > self.width or self.text[0][i] == '|':
                x_offset = 0
                y_offset += self.font.height + 2
                if y_offset > self.height:
                    self.end = True
            
            text_surf.blit(self.font.draw(self.text[0][i],color=self.color), (x_offset, y_offset))
            x_offset += char_width + self.font.spacing
        
        if self.end and self.pointer_visible:
            text_surf.blit(tilesets_database['tiles_list']['pointer'], (x_offset+2, y_offset+self.font.height-6) )
        
        return text_surf


class DialogBox:
    def __init__(self, text, font, delay):
        self.width = CAMERA_SIZE[0]
        self.height = 38
        self.font = font
        self.textscroller = TextScroller(text,font,(255,255,255),self.width-12,200,delay)
        self.speaker = self.get_speaker()
        self.textscroller.text[0] = self.textscroller.text[0][2:]
        self.textscroller.startoffset = self.font.get_width(self.speaker)
        self.end = False

    def next_line(self):
        if not self.textscroller.end:
            self.textscroller.next_line()
        elif self.textscroller.next:
            self.textscroller.next_line()
            self.speaker = self.get_speaker()
            self.textscroller.text[0] = self.textscroller.text[0][2:]
            self.textscroller.startoffset = self.font.get_width(self.speaker)
        else:
            self.end = True

    def get_speaker(self):
        if self.textscroller.text[0][0] == 'C':
            return 'Caelum '
        elif self.textscroller.text[0][0] == 'S':
            return 'Soleanna '
        else:
            return ''

    def draw(self):
        text_surf = pygame.Surface((self.width, self.height))
        if not self.end:
            text_surf.fill((0,0,0))
            
            speakercolor = (80,185,235) if self.speaker == 'Caelum ' else (255,232,0)
            text_surf.blit(self.font.draw(self.speaker, speakercolor), (4,4))
            text_surf.blit(self.textscroller.draw(), (4,4))  
        else:
            text_surf.set_colorkey((0,0,0))

        return text_surf

    def update(self):
        self.textscroller.update()

        


class Transition:
    def __init__(self, type, color, alpha, speed, size, next_level=None):
        self.transition_type = type
        self.transition_color = color
        self.transition_alpha = alpha
        self.size = size
        self.transition_speed = speed
        if self.transition_type == 'FADE-OUT':
            self.transition_speed *= -1

        self.end = False
        self.next_level = next_level
        self.hold_timer = 0

    def draw(self):
        box = pygame.Surface(self.size)
        box.fill(self.transition_color)
        box.set_alpha(self.transition_alpha)
        self.transition_alpha += self.transition_speed

        if (self.transition_type == 'FADE-IN' and self.transition_alpha >= 255) or (self.transition_type == 'FADE-OUT' and self.transition_alpha <= 0):
                self.execute_end()

        return box

    def execute_end(self):
        if self.next_level is not None:
            change_level(self.next_level)
        
        self.end = True


class TitleCard:
        def __init__(self, text):
            self.fancy_font = Font('assets/fonts/fancy.png',0)
            self.alpha = 0
            self.text = text
            self.text_width = self.fancy_font.get_width(self.text)
            self.text_offset = self.text_width * -1
            self.timer = 0
            self.timer_duration = 90
            self.end = False

        def draw(self):
            # update
            if self.text_offset < int((CAMERA_SIZE[0]/2)-(self.text_width/2))+1:
                self.text_offset += 1.5
                if self.text_offset > int((CAMERA_SIZE[0]/2)-(self.text_width/2))+1:
                    self.text_offset = int((CAMERA_SIZE[0]/2)-(self.text_width/2))+1
            elif self.timer >= self.timer_duration:
                self.text_offset += 4
                if self.text_offset >= CAMERA_SIZE[0]:
                    self.end = True
            else:
                self.timer += 1

            # draw   
            rect_surf = pygame.Surface((CAMERA_SIZE[0],self.fancy_font.height+4))
            rect_surf.fill((50,50,50))
            rect_surf.set_alpha(self.alpha)
            
            card_surf = pygame.Surface((CAMERA_SIZE[0],self.fancy_font.height+4))
            card_surf.set_colorkey((0,0,0))
            # outline
            card_surf.blit(self.fancy_font.draw(self.text),(self.text_offset-1, 1))
            card_surf.blit(self.fancy_font.draw(self.text),(self.text_offset+1, 1))
            card_surf.blit(self.fancy_font.draw(self.text),(self.text_offset-1, 3))
            card_surf.blit(self.fancy_font.draw(self.text),(self.text_offset+1, 3))
            card_surf.blit(self.fancy_font.draw(self.text),(self.text_offset, 1))
            card_surf.blit(self.fancy_font.draw(self.text),(self.text_offset, 3))
            card_surf.blit(self.fancy_font.draw(self.text),(self.text_offset-1, 2))
            card_surf.blit(self.fancy_font.draw(self.text),(self.text_offset+2, 2))
            card_surf.blit(self.fancy_font.draw(self.text),(self.text_offset+2, 3))
            # shadow and text
            card_surf.blit(self.fancy_font.draw(self.text,(100,0,0)),(self.text_offset+1, 2))
            card_surf.blit(self.fancy_font.draw(self.text,(255,255,0)),(self.text_offset, 2))
            
            return card_surf