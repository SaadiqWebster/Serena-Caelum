import pygame, os, time, math, random
import player as _p

class SpecialTransition:
    def __init__(self, x_cor, CAMERA_SIZE):
        self.CAMERA_SIZE = CAMERA_SIZE
        self.x_cor = x_cor
        self.width = 1
        self.transition = True
    
    def update(self):
        self.width += 3

    def draw(self):
        surf = pygame.Surface(self.CAMERA_SIZE)
        surf.set_colorkey((0,0,0))
        rect = pygame.Rect(self.x_cor-(self.width/2),0,self.width,self.CAMERA_SIZE[1])
        pygame.draw.rect(surf,(255,255,255),rect)
        return surf   

class TrippyBackground:
    def __init__(self, tilesets_database, CAMERA_SIZE, CHUNK_SIZE, COLORSET, GREYSCALE):
        self.COLORSET = COLORSET
        self.GREYSCALE = GREYSCALE
        self.skybox_index = 0 
        self.greyscale_index_top = 0
        self.greyscale_index_bottom = 200
        self.tilesets_database = tilesets_database
        self.back_pos = [0,0]
        self.background = pygame.Surface(CAMERA_SIZE)
        self.CHUNK_SIZE = CHUNK_SIZE
        self.x_cor = 0
        self.y_cor = 0

    def palette_swap(self, img, old_color, new_color):
        img_copy = pygame.Surface(img.get_size())
        img_copy.fill(new_color)
        img.set_colorkey(old_color)
        img_copy.blit(img,(0,0))
        return img_copy

    def update(self):
        self.skybox_index += 1
        if self.skybox_index >= len(self.COLORSET):
            self.skybox_index = 0

        self.greyscale_index_top += 1
        if self.greyscale_index_top >= len(self.GREYSCALE):
            self.greyscale_index_top = 0

        self.greyscale_index_bottom += 1
        if self.greyscale_index_bottom >= len(self.GREYSCALE):
            self.greyscale_index_bottom = 0
            
        self.back_pos[0] += 1
        if self.back_pos[0] >= self.CHUNK_SIZE[0]:
            self.back_pos[0] -= self.CHUNK_SIZE[0]
        if self.back_pos[1] >= self.CHUNK_SIZE[1]:
            self.back_pos[1] -= self.CHUNK_SIZE[1] 
        
        self.x_cor = self.back_pos[0]
        self.y_cor = self.back_pos[1]-(math.sin(time.time()*0.4)*self.CHUNK_SIZE[1])

    def draw(self):
        top_layer = self.palette_swap(self.tilesets_database['backgrounds_list']['cracked_sky'], (255,255,255), self.GREYSCALE[self.greyscale_index_top])
        top_layer.set_colorkey((0,0,0))
        top_layer.set_alpha(50)
        bottom_layer = self.palette_swap(self.tilesets_database['backgrounds_list']['cracked_sky'], (255,255,255), self.GREYSCALE[self.greyscale_index_bottom])
        bottom_layer.set_colorkey((0,0,0))
            
        self.background.fill(self.COLORSET[self.skybox_index])
        for x in range(-1,2):
            for y in range(-1,2):
                self.background.blit(bottom_layer,(0,0))
                self.background.blit(top_layer,(self.x_cor+(self.CHUNK_SIZE[0]*x),self.y_cor+(self.CHUNK_SIZE[1]*y)))

        return self.background

class SkyBackground:
    def __init__(self, tilesets_database, CAMERA_SIZE, CHUNK_SIZE):
        self.tilesets_database = tilesets_database
        self.cor_top = [0,0]
        self.cor_bottom = [0,0]
        self.x_velocity_top = -0.3
        self.x_velocity_bottom = 0.2
        self.background = pygame.Surface(CAMERA_SIZE)
        self.CHUNK_SIZE = CHUNK_SIZE
        self.sky_color = (3, 169, 252)

    def update(self):
        self.cor_top[0] += self.x_velocity_top
        self.cor_bottom[0] += self.x_velocity_bottom

        if self.cor_top[0] < 0-self.CHUNK_SIZE[0]:
            self.cor_top[0] += self.CHUNK_SIZE[0]
        elif self.cor_bottom[0] > self.CHUNK_SIZE[0]:
            self.cor_bottom[0] -= self.CHUNK_SIZE[0]

    def draw(self):
        self.background.fill(self.sky_color)
        self.background.blit(self.tilesets_database['backgrounds_list']['sky_layer0'],(0,0))
        self.background.blit(self.tilesets_database['backgrounds_list']['sky_layer1'],(self.cor_bottom[0],self.cor_bottom[1]))
        self.background.blit(self.tilesets_database['backgrounds_list']['sky_layer1'],(self.cor_bottom[0]+self.CHUNK_SIZE[0],self.cor_bottom[1]))
        self.background.blit(self.tilesets_database['backgrounds_list']['sky_layer1'],(self.cor_bottom[0]-self.CHUNK_SIZE[0],self.cor_bottom[1]))
        self.background.blit(self.tilesets_database['backgrounds_list']['sky_layer2'],(self.cor_top[0],self.cor_top[1]))
        self.background.blit(self.tilesets_database['backgrounds_list']['sky_layer2'],(self.cor_top[0]+self.CHUNK_SIZE[0],self.cor_top[1]))
        self.background.blit(self.tilesets_database['backgrounds_list']['sky_layer2'],(self.cor_top[0]-self.CHUNK_SIZE[0],self.cor_top[1]))
        return self.background

class BossBackground:
    def __init__(self, tilesets_database, CAMERA_SIZE, CHUNK_SIZE, COLORSET, GREYSCALE):
        self.CHUNK_SIZE = CHUNK_SIZE
        self.COLORSET = COLORSET
        self.GREYSCALE = GREYSCALE
        self.background = pygame.Surface(CAMERA_SIZE)
        self.skybox_index = 0 
        self.greyscale_index = [0,0,170,340]
        self.greyscale_velocity = [1,3,3,3]
        self.x_pos = [0,0,0]
        self.x_velocity = [-1,-2,-3]
        self.tilesets_database = tilesets_database
    
    def palette_swap(self, img, old_color, new_color):
        img_copy = pygame.Surface(img.get_size())
        img_copy.fill(new_color)
        img.set_colorkey(old_color)
        img_copy.blit(img,(0,0))
        return img_copy
    
    def update(self):
        self.skybox_index += 1
        if self.skybox_index >= len(self.COLORSET):
            self.skybox_index = 0

        for i in range(len(self.greyscale_index)):
            self.greyscale_index[i] += self.greyscale_velocity[i]
            if self.greyscale_index[i] >= len(self.GREYSCALE):
                self.greyscale_index[i]= 0

        for i in range(len(self.x_pos)):
            self.x_pos[i] += self.x_velocity[i]
            if self.x_pos[i] > self.CHUNK_SIZE[0]:
                self.x_pos[i] -= self.CHUNK_SIZE[0]
            elif self.x_pos[i] < 0-self.CHUNK_SIZE[0]:
                self.x_pos[i] += self.CHUNK_SIZE[0]


    def draw(self):
        crack_layer = self.palette_swap(self.tilesets_database['backgrounds_list']['cracked_sky'], (255,255,255), self.GREYSCALE[self.greyscale_index[0]])
        crack_layer = self.palette_swap(self.tilesets_database['backgrounds_list']['cracked_sky'], (255,255,255), self.COLORSET[self.skybox_index])
        crack_layer.set_colorkey((0,0,0))

        self.background.fill((1,0,0))
        #self.background.fill(self.COLORSET[self.skybox_index])
        #self.background.fill(self.GREYSCALE[self.greyscale_index[0]])
        self.background.blit(crack_layer, (0,0))

        self.background.blit(self.tilesets_database['backgrounds_list']['boss_layer1'], (0,0))
        
        for i in range(2, len(self.x_pos)+2):
            cloud_layer = self.palette_swap(self.tilesets_database['backgrounds_list']['boss_layer'+str(i)], (255,255,255), self.GREYSCALE[self.greyscale_index[i-1]])
            cloud_layer.set_colorkey((0,0,0))

            self.background.blit(cloud_layer, (self.x_pos[i-2],0))
            self.background.blit(cloud_layer, (self.x_pos[i-2]-self.CHUNK_SIZE[0],0))
            self.background.blit(cloud_layer, (self.x_pos[i-2]+self.CHUNK_SIZE[0],0))

        return self.background

class Gate:
    def __init__(self, level, id, rect):
        self.level = level
        self.id = id
        self.rect = rect

class Waterfall:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x,y,16,16)
        img_loc = 'assets/animations/objects/waterfall/'
        self.animation = []
        self.current_frame = 0
        for i in range(1,5):
            for j in range(6):
                self.animation.append(pygame.image.load(img_loc+'waterfall_'+str(i)+'.png'))

    def draw(self):
        self.current_frame += 1
        if self.current_frame >= len(self.animation):
            self.current_frame = 0
        return self.animation[self.current_frame]

class Item:
    def __init__(self, id, x, y):
        self.id = id
        self.rect = pygame.Rect(x, y, 16, 16)
        self.name = {
            0:"Strawberries",
            1:"Traveler's Kiss",
            2:"Rainbow Quartz",
            3:"Gift of The Sky",
            4:"Marigold Fairy"            
        }
        self.description = {
            0:"Restores half health",
            1:"Restores full health",
            2:"Restores half special",
            3:"Restores full special",
            4:"Doubles damage given"
        }
        self.item_img = pygame.image.load('assets/tilesets/tiles/'+self.name[self.id]+'.png').convert()
        self.item_img.set_colorkey((0,255,0))
        self.animation_frames_database = {}
        self.animation = self.load_animation('assets/animations/objects/item-bubble',[60]+[6]*5)
        self.current_frame = 0
        self.DESTROY = False
        
    def load_animation(self, path, frame_durations):
        animation_name = path.split('/')[-1]
        animation_frame_data = []

        i = 0
        for duration in frame_durations:
            animation_frame_id = animation_name + '_' + str(i+1)
            img_location = path + '/' + animation_frame_id + '.png'
            
            animation_img = pygame.image.load(img_location).convert()
            animation_img.set_colorkey((0,255,0))
            animation_img.convert_alpha() 
            self.animation_frames_database[animation_frame_id] = animation_img.copy()
            for j in range(duration):
                animation_frame_data.append(animation_frame_id)
            i += 1

        return animation_frame_data

    def draw(self):
        item_surf = pygame.Surface((16,16))
        item_surf.fill((0,255,0))
        item_surf.set_colorkey((0,255,0))
        item_surf.blit(self.item_img, (4,4))
        item_surf.blit(self.animation_frames_database[self.animation[self.current_frame]], (0,0))
        return item_surf

    def update(self):
        self.current_frame += 1 
        if self.current_frame >= len(self.animation):
            self.current_frame = 0

    def destroy(self):
        self.DESTROY = True


# -- ENEMIES ---
enemy_sounds_database = {}
enemy_animation_database = {}
def fill_enemy_animation_database(path):
    dir_parent = os.listdir(path)
    for directory in dir_parent:
        enemy_animation_database[directory] = {}
        dir_child = os.listdir(path+'/'+directory)
        for _dir in dir_child:
            enemy_animation_database[directory][_dir] = []
            animation = os.listdir(path+'/'+directory+'/'+_dir)
            for i in range(len(animation)):
                frame = pygame.image.load(path+'/'+directory+'/'+_dir+'/'+_dir+'_'+str(i+1)+'.png')
                frame.set_colorkey((0,255,0))
                repeat_frame = 6 
                if _dir == 'beam':
                    repeat_frame = 3
                elif _dir == 'explosion':
                    repeat_frame = 5
                enemy_animation_database[directory][_dir] += [frame] * repeat_frame
fill_enemy_animation_database("assets/animations/enemies")


class Enemy:
    def __init__(self, x, y):
        self.id = 'Enemy'
        self.max_health = 3
        self.damage = 1
        self.rect = pygame.Rect(x, y, 16, 16)
        self.health = self.max_health
        self.velocity = [0,0]
        self.gravity = 0
        self.state = 'IDLE'
        self.item_drop = None
        self.projectile_q = []
        self.DESTROY = False

        self.animation_database = {}
        self.sound_volume = 0
        self.animation_play = 'LOOP'
        self.current_animation = 'idle'
        self.current_frame = 0
        self.flip = False
        self.alpha = 255
        self.white_shading = 0
        self.white_shade_timer = 0

        self.iframes = False
        self.iframes_timer = 0

    def set_animation(self, animation, frame, play_type):
        self.current_frame = frame
        self.animation_play = play_type
        self.current_animation = animation

    def play_sound(self, sound):
        enemy_sounds_database[sound].set_volume(self.sound_volume)
        enemy_sounds_database[sound].play()

    def draw(self):
        frame = pygame.transform.flip(self.animation_database[self.current_animation][self.current_frame], self.flip, False)
        mask = pygame.mask.from_surface(frame)
        mask_surf = mask.to_surface()
        mask_surf.set_colorkey((0,0,0))
        mask_surf.set_alpha(self.white_shading)
        frame.blit(mask_surf,(0,0))
        frame.set_alpha(self.alpha)
        return frame

    def update_timer_events(self):
        if self.animation_play != 'STOP':
            self.current_frame += 1
            if self.current_frame >= len(self.animation_database[self.current_animation]):
                if self.animation_play == 'ONCE':
                    self.current_frame -= 1
                    self.animation_play = 'STOP'
                elif self.animation_play == 'LOOP':
                    self.current_frame = 0

        if self.iframes:
            self.iframes_timer -= 1
            if self.iframes_timer <= 0:
                self.iframes_timer = 0
                self.iframes = False

            self.white_shade_timer -= 1
            if self.white_shade_timer <= 0 and self.state != 'DESTROY':
                self.white_shade_timer = 0
                self.white_shading = 0

    def update(self, floor_collisions, object_collisions, player):
        if self.state == 'DESTROY':
            self.destroy()
        else:
            self.update_timer_events()

            self.velocity[1] = self.gravity
            self.gravity += 0.2
            if self.gravity > 10:
                self.gravity = 10

            if object_collisions['hitboxes'] and object_collisions['hitboxes'][0].id != 'guardbox' and not self.iframes:
                self.hit(object_collisions['hitboxes'][0].damage, player.flip)

            if self.state == 'IDLE':
                self.velocity[0] = 0
            
            if self.id != 'Bean' and self.rect.x < player.rect.x-480 or self.rect.x > player.rect.x+480 or self.rect.y < player.rect.y-320 or self.rect.y > player.rect.y+320:
                self.DESTROY = True

    def hit(self, damage, player_direction):
        if not self.iframes:
            self.health -= damage

            self.white_shading = 255
            self.white_shade_timer = 10

            self.iframes = True
            self.iframes_timer = 45

            if self.health <= 0:
                self.alpha = 255
                self.state = 'DESTROY'
                self.play_sound('enemy_hitkill')   
                self.play_sound('enemy_down')
            else:
                self.play_sound('enemy_hit'+str(random.randint(1,3)))
        
    def destroy(self):
        self.velocity = [0,0]
        self.alpha -= 5
        if self.alpha < 0:
            self.DESTROY = True
            # 20% chance an item drop
            if random.random() < 0.25:
                x = self.rect.x + (self.rect.width / 2) - 8
                y = self.rect.y - 8 #+ (self.rect.height / 2) - 8
                n = random.randint(0,4)
                self.item_drop = Item(n,x,y)

class Frog(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.id = 'Squish'
        self.max_health = 2
        self.rect = pygame.Rect(x, y, 14, 8)
        self.health = self.max_health
        global enemy_animation_database
        self.animation_database = enemy_animation_database[self.id]
        
        self.hop_timer = 60
        self.hop_forward = True

    def update(self, floor_collisions, object_collisions, player):
        super().update(floor_collisions, object_collisions, player)
        if self.state != 'DESTROY':
            if floor_collisions['bottom']:
                if self.state == 'JUMP':
                    self.state = 'IDLE'
                    self.set_animation('idle',0,'LOOP')
                    self.hop_timer = 60
                    self.hop_forward = not self.hop_forward

            if self.state == 'IDLE' and not self.iframes:
                self.hop_timer -= 1
                if self.hop_timer < 0:
                    if random.randint(0,1) == 0:
                        self.state = 'JUMP'
                        self.set_animation('jump',0,'ONCE')
                        self.play_sound('hop')
                        self.gravity = -4
                        self.velocity[1] = self.gravity
                    else:
                        self.hop_timer = 60

            if self.state == 'JUMP':
                if self.hop_forward:
                    self.velocity[0] = 1 
                    self.flip = False 
                else: 
                    self.velocity[0] = -1
                    self.flip = True
    
    def hit(self, damage, player_direction):
        super().hit(damage, player_direction)
        if self.state != 'JUMP':
            self.flip = not player_direction
            self.hop_forward = not self.flip
      
class Bat(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.id = 'Freez'
        self.max_health = 2
        self.rect = pygame.Rect(x, y, 12, 16)
        self.health = self.max_health
        global enemy_animation_database
        self.animation_database = enemy_animation_database[self.id]
        
        self.timer = 0

    def update_timer_events(self):
        if self.state == 'WAKE UP' or self.state == 'STUN':
            self.current_frame += 1

        super().update_timer_events()

        if self.current_animation == 'fly' and self.current_frame == 0:
            self.play_sound('wing_flap')

    def update(self, floor_collisions, object_collisions, player):
        super().update(floor_collisions, object_collisions, player)
        if self.state != 'DESTROY':
            self.gravity = 0

            if self.state == 'IDLE':
                if player.rect.x < self.rect.x:
                    self.flip = True
                else:
                    self.flip = False
            
                if player.rect.y > self.rect.y and player.rect.y < self.rect.y+128 and player.rect.x > self.rect.x-48 and player.rect.x < self.rect.x+48:
                    self.set_animation('fly',0,'LOOP')
                    self.play_sound('wing_flap')
                    self.state = 'WAKE UP'

            if self.state == 'WAKE UP' or self.state == 'STUN':
                if self.state == 'WAKE UP':
                    self.velocity[0] = 1 if self.flip else -1
                else:
                    self.velocity = [0,0]

                self.timer += 1
                if (self.state == 'WAKE UP' and self.timer > 45) or (self.state == 'STUN' and self.timer > 60):
                    self.state = 'FOLLOW'

            if self.state == 'FOLLOW':
                if player.rect.x+8 > self.rect.x:
                    self.velocity[0] = 1
                    self.flip = False
                elif player.rect.x+8 < self.rect.x:
                    self.velocity[0] = -1
                    self.flip = True
                else:
                    self.velocity[0] = 0

                if player.rect.y+4 > self.rect.y:
                    self.velocity[1] = 1
                elif player.rect.y+4 < self.rect.y:
                    self.velocity[1] = -1
                else:
                    self.velocity[1] = 0

                if object_collisions['player'] and not player.iframes:
                    self.timer = 0
                    self.state = 'STUN'
                
                if object_collisions['hitboxes'] and object_collisions['hitboxes'][0].id == 'guardbox' and not self.iframes:
                    self.timer = 0
                    self.state = 'STUN'
                    if self.current_animation != 'fly':
                        self.set_animation('fly',0,'LOOP')

    def hit(self, damage, player_direction):
        super().hit(damage, player_direction)
        if self.state != 'DESTROY' and self.state != 'IDLE':
            self.timer = 0
            self.state = 'STUN'
            if self.current_animation != 'fly':
                self.set_animation('fly',0,'LOOP')

class Ghost(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.id = 'Joak'
        self.max_health = 3
        self.rect = pygame.Rect(x, y, 16, 16)
        self.health = self.max_health
        global enemy_animation_database
        self.animation_database = enemy_animation_database[self.id]

        self.timer = 0
        self.alpha_speed = 15

    def draw(self):
        a = self.alpha
        if self.white_shading > 0 and self.state != 'DESTROY':
            self.alpha = 255 
        frame = super().draw()
        self.alpha = a
        return frame

    def update_timer_events(self):
        if self.state == 'LAUGH':
            self.current_frame += 2
        super().update_timer_events()

    def update(self, floor_collisions, object_collisions, player):
        super().update(floor_collisions, object_collisions, player)
        if self.state != 'DESTROY':
            self.gravity = 0

            if self.state == 'IDLE' and player.rect.x > self.rect.x-120 and player.rect.x < self.rect.x+120:
                self.state = 'FOLLOW'

            if self.state == 'FOLLOW':
                self.alpha += self.alpha_speed
                if self.alpha > 255:
                    self.alpha = 255

                if player.rect.x+8 > self.rect.x:
                    self.velocity[0] = 1
                    self.flip = False
                elif player.rect.x+8 < self.rect.x:
                    self.velocity[0] = -1
                    self.flip = True
                else:
                    self.velocity[0] = 0

                if player.rect.y+2 > self.rect.y:
                    self.velocity[1] = 1
                elif player.rect.y+2 < self.rect.y:
                    self.velocity[1] = -1
                else:
                    self.velocity[1] = 0
                
                if self.flip != player.flip:
                    self.set_animation('spook',0,'LOOP')
                    self.state = 'SPOOK'
            
            if self.state == 'RUN':
                self.alpha -= self.alpha_speed
                if self.alpha < 0:
                    self.alpha = 0

                if self.timer == 0:
                    self.velocity[0] = 1 if not player.flip else -1
                    self.flip = False if self.velocity[0] > 0 else True
                
                self.velocity[1] = -1
                self.timer += 1
                if self.timer > 45:
                    self.set_animation('idle',0,'LOOP')
                    self.state = 'FOLLOW'
            
            if self.state == 'SPOOK':
                self.alpha -= self.alpha_speed
                if self.alpha < 0:
                    self.alpha = 0                
                self.velocity = [0,0]

                if self.flip == player.flip or (self.flip and player.rect.x > self.rect.x+32) or (not self.flip and player.rect.x < self.rect.x-16):
                    self.set_animation('idle',0,'LOOP')
                    self.play_sound('laugh')
                    self.state = 'FOLLOW'

            if self.state == 'LAUGH':
                self.alpha += self.alpha_speed
                if self.alpha > 255:
                    self.alpha = 255

                self.velocity = [0,0]
                self.timer += 1
                if self.timer > 45:
                    self.state = 'FOLLOW'

            if object_collisions['player'] and not player.iframes and player.x_state != 'TRANSITION_IN' and player.x_state != 'TRANSITION_OUT' and self.state != 'LAUGH':
                self.timer = 0
                self.set_animation('idle',0,'LOOP')
                self.play_sound('laugh')
                self.state = 'LAUGH'
            
            if object_collisions['hitboxes'] and object_collisions['hitboxes'][0].id == 'guardbox' and not self.iframes:
                self.set_animation('spook',0,'LOOP')
                self.alpha = 255
                self.timer = 0
                self.state = 'RUN'
            
    
    def hit(self, damage, player_direction):
        super().hit(damage, player_direction)
        if self.state != 'DESTROY':
            self.set_animation('spook',0,'LOOP')
            self.alpha = 255
            self.timer = 0
            self.state = 'RUN'

class Bird(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.id = 'Bean'
        self.max_health = 1
        self.rect = pygame.Rect(x, y, 16, 16)
        self.health = self.max_health
        global enemy_animation_database
        self.animation_database = enemy_animation_database[self.id]

        self.ypos = self.rect.y
        self.ytarget = self.ypos + 40
        self.timer = 0

    def update_timer_events(self):
        if self.state == 'DOWN':
            self.current_frame = 24
        if self.state == 'UP':
            self.current_frame += 2
        super().update_timer_events()

    def update(self, floor_collisions, object_collisions, player):

        super().update(floor_collisions, object_collisions, player)
        if self.state != 'DESTROY':
            self.gravity = 0

            self.timer -= 1
            if self.timer < 0:
                self.timer = 0
            
            if self.state == 'IDLE' and player.rect.x > self.rect.x-136 and player.rect.x < self.rect.x+136:
                self.state = 'FLY'
                self.flip = True if player.rect.x < self.rect.x else False

            if self.state != 'IDLE':
                self.velocity[0] = 1 if not self.flip else -1
                self.velocity[1] = 0

                if self.flip and self.rect.x < player.rect.x-180:
                        self.rect.x += 400
                if not self.flip and self.rect.x > player.rect.x+180:
                        self.rect.x -= 400
                    
                if self.state == 'FLY' and self.timer <= 0 and ((player.rect.x > self.rect.x-48 and player.rect.x < self.rect.x and self.flip) or (player.rect.x < self.rect.x+48 and player.rect.x > self.rect.x+16 and not self.flip)):
                    self.state = 'DOWN'
                    
                elif self.state == 'DOWN':
                    self.velocity[1] = 1
                    if self.rect.y > self.ytarget:
                        self.state = 'UP'
                    
                elif self.state == 'UP':
                    self.velocity[1] = -1
                    if self.rect.y < self.ypos:
                        self.rect.y = self.ypos
                        self.state = 'FLY'
                        self.timer = 60
                    
class Wolf(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.id = 'Roa'
        self.max_health = 3
        self.damage = 2
        self.rect = pygame.Rect(x, y, 32, 16)
        self.health = self.max_health
        
        global enemy_animation_database
        self.animation_database = enemy_animation_database[self.id]
        self.timer = 0
        self.timer_cap = 30
        self.wait_duration = 55
        self.idle_duration = 60
        self.cooldown_duration = 90
        self.leftbound = 0
        self.rightbound = 4
        self.distance = 0

    def update(self, floor_collisions, object_collisions, player):
        super().update(floor_collisions, object_collisions, player)
        if self.state != 'DESTROY':
            if floor_collisions['bottom']:
                    if self.state == 'JUMP' and self.timer > self.timer_cap:
                        self.state = 'WAIT'
                        self.set_animation('idle',42,'LOOP')
                        self.timer = 0
                        self.timer_cap = self.cooldown_duration

            if self.state == 'WAIT':
                self.velocity[0] = 0
                self.timer += 1
                if self.timer >= self.timer_cap:
                    self.timer = 0
                    self.timer_cap = self.wait_duration
                    self.flip = False if player.rect.x > self.rect.x else True
                    if player.rect.x > self.rect.x-32 and player.rect.x < self.rect.x+48:
                        self.state = 'JUMP'
                        self.play_sound('growl')
                        self.set_animation('ready',0,'LOOP')
                    elif player.rect.x > self.rect.x-64 and player.rect.x < self.rect.x+80:
                        self.state = 'CHASE'
                        self.set_animation('run',0,'LOOP')
                    else:
                        self.state = 'IDLE'
                        self.timer = 0
                        self.timer_cap = self.idle_duration
                        self.set_animation('idle',0,'LOOP')

            if self.state == 'IDLE':
                if player.rect.x > self.rect.x-64 and player.rect.x < self.rect.x+80:
                    self.state = 'CHASE'
                    self.set_animation('run',0,'LOOP')
                else:
                    self.timer += 1  
                    if self.timer >= self.timer_cap:
                        if self.rightbound == 0:
                            self.flip = True
                        elif self.leftbound == 0:
                            self.flip = False
                        elif random.randint(0,1) == 0:
                            self.flip = not self.flip
                        self.distance = random.randint(0,4)
                        if self.distance > 0:
                            self.state = 'WALK'
                            self.timer = 0
                            self.set_animation('walk',0,'LOOP')
                        else:
                            self.timer = 0
                            self.timer_cap = self.idle_duration

            if self.state == 'CHASE':
                if player.rect.x > self.rect.x-32 and player.rect.x < self.rect.x+48:
                    self.timer = 0
                    self.timer_cap = self.wait_duration
                    self.state = 'JUMP'
                    self.play_sound('growl')
                    self.set_animation('ready',0,'LOOP')
                self.velocity[0] = 2 if player.rect.x > self.rect.x else -2
                self.flip = False if player.rect.x > self.rect.x else True
            
            if self.state == 'JUMP':
                self.timer += 1
                self.velocity[0] = 0
                if self.timer == self.timer_cap:
                    self.gravity = -3
                    self.play_sound('roar')
                    self.set_animation('jump',0,'ONCE')
                if self.timer >= self.timer_cap:
                    self.velocity[0] = 3 if not self.flip else -3

            if self.state == 'WALK':
                if player.rect.x > self.rect.x-64 and player.rect.x < self.rect.x+80:
                    self.distance = 0
                    self.state = 'CHASE'
                    self.set_animation('run',0,'LOOP')
                elif self.distance > 0:
                    self.velocity[0] = 1 if not self.flip else -1
                    self.timer += 1
                    if self.timer >= 15:
                        self.timer = 0
                        self.distance -= 1
                        self.leftbound += 1 if not self.flip else -1
                        self.rightbound += -1 if not self.flip else 1
                        if self.rightbound == 0 or self.leftbound == 0:
                            self.flip = not self.flip
                else:
                    self.state = 'IDLE'
                    self.set_animation('idle',0,'LOOP')
                    self.timer = 0
                    self.timer_cap = self.idle_duration


# -- PROJECTILES ---
class Projectile:
    def __init__(self, x, y, width, height, damage, duration, anim = None):
        self.rect = pygame.Rect(x,y,width,height)
        self.duration = duration
        self.timer = 0
        self.velocity = [0,0]
        self.damage = damage
        self.particle_q = []
        self.particle_timer = 0
        self.DESTROY = False

        global enemy_animation_database
        if anim is not None and anim != '':
            self.animation = enemy_animation_database['projectiles'][anim]
        else:
            frame = pygame.Surface((width, height))
            frame.fill((0,255,0))
            frame.set_colorkey((0,255,0))
            self.animation = [frame]
        self.current_frame = 0

    def spawn_particle(self,duration=24):
        self.particle_q.append(_p.Particle(self.rect.x+random.randrange(0,12),self.rect.y+random.randrange(0,12),duration))

    def draw(self):
        return self.animation[self.current_frame]

    def update(self):
        self.current_frame += 1
        if self.current_frame >= len(self.animation):
            self.current_frame = 0
            
        self.timer += 1
        if self.timer >= self.duration:
            self.DESTROY = True

        for particle in self.particle_q:
            particle.update()
            if particle.destroy:
                self.particle_q.remove(particle)

class ShootProjectile(Projectile):
    def __init__(self, x, y, width, height, damage, duration, velocity):
        super().__init__(x, y, width, height, damage, duration, 'moon')
        self.velocity = velocity

    def update(self):
        self.particle_timer += 1
        if self.particle_timer > 6:
            self.particle_timer = 0
            self.spawn_particle()

        super().update()

class JumpProjectile(Projectile):
    def __init__(self, x, y, width, height, damage, duration, hor_velocity):
        super().__init__(x, y, width, height, damage, duration, 'moon')
        self.velocity[0] = hor_velocity
        self.velocity[1] = -5

    def update(self):
        self.particle_timer += 1
        if self.particle_timer > 6:
            self.particle_timer = 0
            self.spawn_particle()

        super().update()

        self.velocity[1] = min(10, self.velocity[1] + 0.2)

# -- BOSS ---
class Boss(Enemy):
    def __init__(self):
        x, y = 96, 47

        super().__init__(x, y)
        self.id = 'Lux Furem'
        self.max_health = 30
        self.rect = pygame.Rect(x, y, 48, 48)
        self.health = self.max_health
        global enemy_animation_database
        self.animation_database = enemy_animation_database[self.id]

        self.cor = [x,y]
        self.phase = -1
        self.prev_phase = -1
        self.phase_duration = 330
        self.phase_time = self.phase_duration
        self.shoot_speed = 3.5
        self.spit_amount = 1
        self.spit_movement_speed = 0.015
        self.idle_movement_speed = 0.015
        self.movement_timer = 0
    
    def change_phase(self):
        if self.phase != 0: # WAIT PERIOD
            self.set_animation('idle',0,'LOOP')
            self.rect.x = 300
            self.rect.y = 80
            self.prev_phase = self.phase
            self.phase = 0
            if self.prev_phase == 2 or self.prev_phase == 4:
                self.phase_duration = 30
            elif self.health > self.max_health / 2:
                self.phase_duration = 180
            else: 
                self.phase_duration = random.randint(30,120)

            self.phase_time = self.phase_duration

        else:
            #self.prev_phase = -1 # this line is needed when testing individual phases
            r = 0
            if self.prev_phase == 4:
                r = 5 
            elif self.prev_phase == 5:
                r = random.randint(1,3)
            else:
                r = random.randint(1,5)
            if r != self.prev_phase or r == 2:
                self.phase = r
                self.movement_timer = 0

                if r == 1: # RAIN
                    self.cor = [120-(self.rect.width/2),32]
                    self.phase_duration = random.randint(300,600) + 96
                    self.set_animation('eyetomouth',0,'ONCE')
                    self.spit_amount = 1 if self.health > self.max_health / 2 else 2

                elif r == 2: # SHOOT 
                    self.cor[0] = 8 if random.randint(0,1) == 0 else 184
                    self.cor[1] = random.randint(28,88)
                    animation = 'pointright' if self.cor[0] < 120 else 'pointleft'
                    self.set_animation(animation,0,'ONCE')
                    self.phase_duration = 132

                elif r == 3: # LIGHTNING
                    self.cor = [120-(self.rect.width/2), 26]
                    self.phase_duration = 243
                    self.set_animation('lightning',0,'ONCE')

                elif r == 4: # BEAM
                    self.cor = [300,80]
                    self.phase_duration = 465

                else: # FREE HIT
                    self.cor = [120-(self.rect.width/2),70-(self.rect.height/2)]
                    if random.random() < 0.15:
                        self.phase_duration = 138 
                    elif self.health > self.max_health / 2:
                        self.phase_duration = 218
                    else:
                        self.phase_duration = random.randint(138, 218)
                    self.set_animation('warp_in',0,'ONCE')
                
                self.phase_time = self.phase_duration
                self.rect.x = self.cor[0]
                self.rect.y = self.cor[1]
                if self.phase != 4:
                    self.play_sound('warp')

    def update(self, floor_collisions, object_collisions, player):
        super().update(floor_collisions, object_collisions, player)
        if self.state != 'DESTROY':
            #print('current:',self.phase,'prev:',self.prev_phase,self.phase_time,self.cor)
            self.gravity = 0
            
            self.phase_time = max(0, self.phase_time-1)
            if self.phase_time <= 0:
                    self.change_phase()

            # RAIN
            if self.phase == 1:
                if self.current_animation == 'eyetomouth' and self.animation_play == 'STOP':
                    self.set_animation('spit',0,'LOOP')
                
                if self.current_animation == 'spit':
                    self.movement_timer += self.spit_movement_speed
                    self.rect.x = self.cor[0] - math.sin(self.movement_timer) * 88
                    self.rect.y = self.cor[1] + (2/math.pi)*math.asin(math.sin(self.movement_timer * math.pi*2)) * 4
                    if self.current_frame == 18 and self.spit_amount == 1:
                        self.projectile_q.append(JumpProjectile(self.rect.x+16, self.rect.y+16, 16, 16, 1, 300, 0))
                        self.play_sound('spit')
                    
                    if self.current_frame == 18 and self.spit_amount == 2:
                        self.projectile_q.append(JumpProjectile(self.rect.x+16, self.rect.y+16, 16, 16, 1, 300, -1))
                        self.play_sound('spit')
                    
                    if self.current_frame == 30 and self.spit_amount == 2:
                        self.projectile_q.append(JumpProjectile(self.rect.x+16, self.rect.y+16, 16, 16, 1, 300, 1))
                        self.play_sound('spit')

                if self.phase_time == self.phase_duration - 18:
                    self.play_sound('eyetomouth')

                if self.phase_time == 48:
                    self.set_animation('mouthtoeye',0,'ONCE')
                    self.play_sound('mouthtoeye')

                if self.phase_time == 24:
                    self.play_sound('warp')
            
            # SHOOT
            elif self.phase == 2:
                if self.phase_time == 102 or self.phase_time == 36:
                    x_vel = player.rect.x+8 - self.rect.x+24
                    y_vel = player.rect.y+16 - self.rect.y+24
                    magnitude = float(math.sqrt(x_vel**2 + y_vel**2))
                    x_vel = float((x_vel / magnitude) * self.shoot_speed)
                    y_vel = float((y_vel / magnitude) * self.shoot_speed)
                    self.projectile_q.append(ShootProjectile(self.rect.x+16, self.rect.y+16, 16, 16, 1, 300, [x_vel, y_vel]))
                    self.play_sound('shoot')

                if self.phase_time == 66:
                    self.rect.x += 176 if self.cor[0] < 120 else -176
                    self.rect.y = random.randint(28,88)
                    animation = 'pointright' if self.rect.x < 120 else 'pointleft'
                    self.set_animation(animation,0,'ONCE')
                    self.play_sound('warp')

                if self.phase_time == 84 or self.phase_time == 18:
                    self.play_sound('warp')
                    

            # LIGHTNING
            elif self.phase == 3:
                self.movement_timer += self.idle_movement_speed
                self.rect.y = self.cor[1] + (2/math.pi)*math.asin(math.sin(self.movement_timer*math.pi*1)) * 2
                
                if self.phase_time == 171:
                    self.play_sound('spark')

                if self.phase_time == 122:
                    self.projectile_q.append(Projectile(8, 0, 48, 144, 1, 18, 'lightning'))
                    self.projectile_q.append(Projectile(184, 0, 48, 144, 1, 18, 'lightning'))
                    self.play_sound('lightning')

                if self.phase_time == 100:
                    self.projectile_q.append(Projectile(self.rect.x-64, 0, 48, 144, 1, 18, 'lightning'))
                    self.projectile_q.append(Projectile(self.rect.x+64, 0, 48, 144, 1, 18, 'lightning'))
                    self.play_sound('lightning')

                if self.phase_time == 60:
                    self.projectile_q.append(Projectile(self.rect.x,0, 48, 144, 1, 18, 'lightning'))
                    self.play_sound('lightning')

            # BEAM
            elif self.phase == 4:
                if self.phase_time == 450:
                    self.projectile_q.append(Projectile(0, 32, 0, 0, 0, 363, 'beam'))
                    self.play_sound('small_lazer')
                if self.phase_time == 363:
                    self.projectile_q.append(Projectile(0, 92, 0, 0, 0, 363, 'beam'))
                    self.play_sound('small_lazer')
                if self.phase_time == 291:
                    self.projectile_q.append(Projectile(0, 32, 240, 32, 2, 156, None))
                    self.play_sound('big_lazer')
                if self.phase_time == 204:
                    self.projectile_q.append(Projectile(0, 92, 240, 32, 2, 156, None))
                    self.play_sound('big_lazer')
            
            # OTHER / FREE HIT
            else:
                if self.current_animation != 'warp_in':
                    self.movement_timer += self.idle_movement_speed
                    self.rect.y = self.cor[1] + (2/math.pi)*math.asin(math.sin(self.movement_timer*math.pi*1)) * 2
                
                elif self.animation_play == 'STOP':
                    if self.phase_duration == 138:
                        self.set_animation('thefinger',0,'ONCE')
                    elif self.health <= self.max_health * 0.2:
                        self.set_animation('dizzy',0,'LOOP')
                    else:
                        self.set_animation('tease',0,'ONCE')

                if self.phase_time == 18 and self.phase != 0 and self.current_animation != 'thefinger':
                    self.set_animation('warp_out',0,'ONCE')
                
                if  self.phase != 0 and ((self.current_animation == 'thefinger' and self.phase_time == 36) or (self.current_animation != 'thefinger' and self.phase_time == 18)):
                    self.play_sound('warp')

