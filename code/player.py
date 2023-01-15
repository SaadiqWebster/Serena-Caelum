import pygame, math, random, time, copy


class Fairy:
    def __init__(self,x,y):
        self.cor = [x,y]
        img_loc = 'code/assets/animations/objects/fairy/'
        self.animation = [pygame.image.load(img_loc+'fairy_1.png')]*20 + [pygame.image.load(img_loc+'fairy_2.png')]*20
        self.current_frame = 0
        self.visible = False
        self.alpha = 255
        self.flip = False
        self.particle_q = []
        self.particle_timer = 0
    
    def update(self, player_cor, player_alpha, player_flip):
        self.alpha = player_alpha
        
        self.current_frame += 1
        if self.current_frame >= len(self.animation):
            self.current_frame = 0

        if self.visible and self.alpha >= 255:
            self.particle_timer += 1
            if self.particle_timer > 15:
                self.particle_timer = 0
                self.spawn_particle()

        y_offset = math.sin(time.time()*2)*4    
        new_cor = [((player_cor[0]-12) - self.cor[0]) / 10, ((player_cor[1]+4+y_offset) - self.cor[1]) / 10]
        self.cor[0] += new_cor[0]
        self.cor[1] += new_cor[1]
        if new_cor[0] < -0.07:
            self.flip = True
        elif new_cor[0] > 0.07:
            self.flip = False
        else:
            self.flip = player_flip
        
        for particle in self.particle_q:
            particle.update()
            if particle.destroy:
                self.particle_q.remove(particle)

    def draw(self):
        frame = pygame.Surface((self.animation[0].get_width(),self.animation[0].get_height()))
        frame.fill((0,255,0))
        frame.blit(pygame.transform.flip(self.animation[self.current_frame], self.flip, False),(0,0))
        frame.set_colorkey((0,255,0))
        if self.visible:
            frame.set_alpha(self.alpha)
        else:
            frame.set_alpha(0)
        return frame
    
    def spawn_particle(self):
        self.particle_q.append(self.Particle(self.cor[0]+random.randrange(0,12),self.cor[1]+random.randrange(0,12)))

    class Particle:
        def __init__(self,x,y):
            self.cor = [x,y]
            self.image = pygame.image.load('code/assets/tilesets/tiles/dust.png')
            self.image.set_colorkey((0,255,0))
            self.timer = 0
            self.destroy = False
        
        def update(self):
            self.timer += 1
            if self.timer % 6 == 0:
                self.cor[1] += 1
            if self.timer > 24:
                self.destroy = True
        
        def draw(self):
            return self.image


class AfterImage_Q:
    def __init__(self):
        self.q = []
        self.gradient = [(250,255,255),(176,255,241),(120,215,255),(96,165,255),(120,215,255),(176,255,241)]
        self.gradient_ptr = 0

    def add(self,x,y,player_frame):
        image_surf = pygame.Surface((player_frame.get_width(), player_frame.get_height()))
        mask = pygame.mask.from_surface(player_frame)
        image_surf.blit(mask.to_surface(unsetcolor=(0,0,0),setcolor=self.gradient[self.gradient_ptr]),(0,0))
        image_surf.set_colorkey((0,0,0))
        self.q.append(self.AfterImage(x,y,image_surf))
        
        self.gradient_ptr += 1
        if self.gradient_ptr >= len(self.gradient):
            self.gradient_ptr = 0

    def update(self):
        for image in self.q:
            image.alpha -= 10
            if image.alpha <= 0:
                self.q.remove(image)
    
    class AfterImage:
        def __init__(self, x, y, image):
            self.x = x
            self.y = y
            self.image = image
            self.alpha = 300
        
        def draw(self):
            self.image.set_alpha(self.alpha)
            return self.image         


class Hitbox:
        def __init__(self, id, damage, start, end, rect):
            self.id = id
            self.damage = damage
            self.rect = rect
            self.start_frame = start
            self.end_frame = end

        def copy(self):
            return [self.id, self.damage, self.start_frame, self.end_frame, self.rect]


class Player:
    def __init__(self, x, y):
        # hurtbox, states, velocities
        self.health = 100
        self.special = 0
        self.inventory = []
        self.inventory_size = 3
        self.velocity = [0,0]
        self.rect = pygame.Rect(x, y, 15, 32)
        self.gravity = 0.5
        self.x_state = 'IDLE'
        self.y_state = 'IDLE'
        
        # animation and animation database
        self.sounds_database = {}
        self.sound_volume = 0
        self.animation_frames_database = {}
        self.animation_database = {}
        self.animation_play = 'LOOP'
        self.current_animation = 'idle'
        self.current_frame = 0
        self.flip = False
        self.alpha = 255
        self.white_shading = 0
        self.fill_animation_database('code/assets/animations/player/')
        
        # hitboxes (x,y is offset from hurtbox), other objects
        self.hitbox = {
            'idle-attack': Hitbox('idle-attack',1,0,3*6,pygame.Rect(self.rect.width-8,10,24,13)),
            'dash-attack': Hitbox('dash-attack',1.5,3*6,8*6,pygame.Rect(self.rect.width-8,14,24,12)),
            'jump-attack': Hitbox('jump-attack',1,1,3*6,pygame.Rect(self.rect.width-8,8,23,11)),
            'down-attack': Hitbox('down-attack',1,1,2*6,pygame.Rect(self.rect.width-8,10,20,6)),
               'guardbox': Hitbox('guardbox',0,3,20,pygame.Rect(self.rect.width-8,-5,11,self.rect.height+3))
        }
        self.hitbox_q = []
        self.active_hitbox = []
        self.fairy = Fairy(self.rect.x-12, self.rect.y+8)
        self.afterimage_q = AfterImage_Q()
        
        # timers and triggers
        self.iframes = False
        self.iframes_timer = 0
        self.input_buffer = False
        self.input_buffer_timer = 0
        self.dtap_timer = 0
        self.ease_x = False
        self.ease_x_timer = 0
        self.item_timer = 0
        self.afterimage = False
        self.afterimage_timer = 0
        self.white_shade_timer = 0
        self.gate_collision = False
        self.key = pygame.key.get_pressed()
        self.prev_key = pygame.key.get_pressed()
        self.button = [False]*14
        self.prev_button = [False]*14
    
    def restart(self):
        self.health = 100
        self.special = 0
        self.inventory = []
        self.velocity = [0,0]
        self.rect.x = 16*7
        self.rect.y = 16*7
        self.gravity = 0.5
        self.x_state = 'IDLE'
        self.y_state = 'IDLE'
        self.animation_play = 'LOOP'
        self.current_animation = 'idle'
        self.current_frame = 0
        self.flip = False
        self.alpha = 255
        self.white_shading = 0
        self.hitbox_q = []
        self.active_hitbox = []
        self.fairy = Fairy(self.rect.x-12, self.rect.y+8)
        self.afterimage_q = AfterImage_Q()
        self.iframes = False
        self.iframes_timer = 0
        self.input_buffer = False
        self.input_buffer_timer = 0
        self.dtap_timer = 0
        self.ease_x = False
        self.ease_x_timer = 0
        self.item_timer = 0
        self.afterimage = False
        self.afterimage_timer = 0
        self.white_shade_timer = 0
        self.gate_collision = False
        self.key = pygame.key.get_pressed()
        self.prev_key = pygame.key.get_pressed()
        self.button = [False]*14
        self.prev_button = [False]*14

    def fill_animation_database(self, path):
        self.animation_database['idle'] = self.load_animation(path+'idle',[6]*14)
        self.animation_database['walk'] = self.load_animation(path+'walk',[6]*17)
        self.animation_database['walk-in'] = self.load_animation(path+'walkin',[6]*8)
        self.animation_database['walk-out'] = self.load_animation(path+'walkout',[6]*8)
        self.animation_database['run'] = self.load_animation(path+'run',[4]*8)
        self.animation_database['jump'] = self.load_animation(path+'jump',[3]*2+[6]+[3]*3)
        self.animation_database['duck'] = self.load_animation(path+'duck',[6]*1)
        self.animation_database['guard'] = self.load_animation(path+'guard',[30]*1)
        self.animation_database['slide'] = self.load_animation(path+'slide',[6]*1)
        self.animation_database['special'] = self.load_animation(path+'special',[6]*1)
        self.animation_database['idle-attack'] = self.load_animation(path+'idle-attack',[6]*4)
        self.animation_database['down-attack'] = self.load_animation(path+'down-attack',[6]+[3]+[6]*2)
        self.animation_database['jump-attack'] = self.load_animation(path+'jump-attack',[6]*4)
        self.animation_database['dash-attack'] = self.load_animation(path+'dash-attack',[6]+[12]+[6]*3+[12]+[6]*4)

    def load_animation(self, path, frame_durations):
        animation_name = path.split('/')[-1]
        animation_frame_data = []

        i = 1
        for duration in frame_durations:
            animation_frame_id = animation_name + '_' + str(i)
            img_location = path + '/' + animation_frame_id + '.png'
            
            animation_img = pygame.image.load(img_location).convert()
            animation_img.set_colorkey((0,255,0))
            animation_img.convert_alpha() 
            self.animation_frames_database[animation_frame_id] = animation_img.copy()
            for j in range(duration):
                animation_frame_data.append(animation_frame_id)
            i += 1

        return animation_frame_data

    def set_animation(self, animation, frame, play_type):
        self.current_frame = frame - 1
        self.animation_play = play_type
        self.current_animation = animation

    def play_sound(self, sound):
        self.sounds_database[sound].set_volume(self.sound_volume)
        self.sounds_database[sound].play()

    def draw(self):
        frame = pygame.transform.flip(self.animation_frames_database[self.animation_database[self.current_animation][self.current_frame]], self.flip, False)
        mask = pygame.mask.from_surface(frame)
        mask_surf = pygame.Surface((frame.get_width(), frame.get_height()))
        mask_surf.blit(mask.to_surface(),(0,0))
        mask_surf.set_colorkey((0,0,0))
        mask_surf.set_alpha(self.white_shading)
        frame.blit(mask_surf,(0,0))
        frame.set_alpha(self.alpha)
        return frame

    def read_input(self, key, button):
        self.prev_key = self.key
        self.prev_button = self.button.copy()
        self.key = key
        self.button = button.copy()

    def guard(self):
        self.play_sound('parry')
        self.white_shading = 255
        self.iframes = True
        self.iframes_timer = 60
        self.input_buffer_timer = 0
        self.input_buffer = False
        self.hitbox_q = []

    def use_item(self, id):
        if id == 0:
            self.health += 50
        if id == 1:
            self.health += 100
        if id == 2:
            self.increase_special(10)
        if id == 3:
            self.increase_special(20)
        if id == 4:
            self.item_timer = 60*30
            self.fairy.visible = True
            self.play_sound('fairy')
            
        if self.health > 100:
            self.health = 100

    def increase_special(self, amount):
        if self.special != 20 and self.special + amount >= 20:
            self.play_sound('special_ready')
        self.special = min(self.special+amount, 20)

    def set_velocity(self):
        if self.key[pygame.K_LEFT] or self.key[pygame.K_a] or self.button[10]:
            if self.x_state == 'WALK':
                if self.flip:
                    self.velocity[0] = -1
                elif not self.key[pygame.K_RIGHT] and not self.key[pygame.K_d] and not self.button[11]:
                    self.velocity[0] = -1
            elif self.x_state == 'RUN':
                if self.flip or (not self.key[pygame.K_RIGHT] and not self.key[pygame.K_d] and not self.button[11]):
                    self.velocity[0] = -2

        if self.key[pygame.K_RIGHT] or self.key[pygame.K_d] or self.button[11]:
            if self.x_state == 'WALK':
                if not self.flip:
                    self.velocity[0] = 1
                elif not self.key[pygame.K_LEFT] and not self.key[pygame.K_a] and not self.button[10]:
                    self.velocity[0] = 1
            elif self.x_state == 'RUN': 
                if not self.flip or (not self.key[pygame.K_LEFT] and not self.key[pygame.K_a] and not self.button[10]):
                    self.velocity[0] = 2

        self.velocity[1] += self.gravity
    
    def update_timer_events(self):
        if self.animation_play != 'STOP':
            self.current_frame += 1
            if self.current_frame >= len(self.animation_database[self.current_animation]):
                if self.animation_play == 'ONCE':
                    self.current_frame -= 1
                    self.animation_play = 'STOP'
                elif self.animation_play == 'LOOP':
                    self.current_frame = 0
            
            if self.alpha > 0 and (self.current_animation == 'walk-in' or self.current_animation == 'walk-out') and (self.current_frame == 1 or self.current_frame == 24):
                self.play_sound('walk')
            #elif self.current_animation == 'run' 

        if self.iframes:
            self.iframes_timer -= 1
            if self.iframes_timer <= 0:
                self.iframes_timer = 0
                self.iframes = False
                if self.current_animation == 'guard':
                    self.set_animation('idle',0,'LOOP')

            if self.white_shading > 0:
                self.white_shading -= 5
                if self.white_shading < 0:
                    self.white_shading = 0
        else:
            self.white_shade_timer -= 1
            if self.white_shade_timer <= 0:
                self.white_shade_timer = 0
                self.white_shading = 0

        if self.input_buffer:
            self.input_buffer_timer -= 1
            if self.input_buffer_timer <= 0:
                self.input_buffer_timer = 0
                self.input_buffer = False
                self.hitbox_q = []

                if self.x_state == 'IDLE' and self.y_state == 'IDLE':
                    self.set_animation('idle',0,'LOOP')
                    self.ease_x = False
                    self.ease_x_timer = 0
                    self.after_image = False

                if self.x_state == 'DUCK':
                    self.x_state = 'IDLE'
                    self.set_animation('idle',0,'LOOP')
                    self.rect = pygame.Rect(self.rect.x, self.rect.y - self.rect.height, self.rect.width, self.rect.height * 2)

        self.dtap_timer -= 1
        if self.dtap_timer < 0:
            self.dtap_timer = 0
        
        if self.afterimage:
            self.afterimage_timer += 1
            if self.afterimage_timer > 6:
                self.afterimage_q.add(self.rect.x-16, self.rect.y-16, self.draw())
                self.afterimage_timer = 0
        else:
            self.afterimage_timer = 0
            self.afterimage_q.gradient_ptr = 0

        self.item_timer -= 1
        if self.item_timer < 0:
            self.item_timer = 0
            if self.fairy.visible:
                self.play_sound('fairy')
                self.fairy.visible = False
                for i in range(7):
                    self.fairy.spawn_particle()
        
        if self.ease_x:
            self.ease_x_timer -= 1

            if self.ease_x_timer <= 0:
                self.ease_x_timer = 0
                self.velocity[0] = self.velocity[0] / 2
                if self.velocity[0] < 0.005 and self.velocity[0] > -0.005:
                    self.velocity[0] = 0
                    self.ease_x = False
                    self.afterimage = False
        elif self.x_state != 'DAMAGE':
            self.velocity[0] = 0
        
    def update_hitbox_q(self):
        for h in self.hitbox_q:
            if self.current_frame > h.end_frame:
                self.hitbox_q.remove(h)
            elif self.current_frame >= h.start_frame:
                h_copy = copy.deepcopy(h.copy())
                hitbox = Hitbox(h_copy[0], h_copy[1], h_copy[2], h_copy[3], h_copy[4])

                if self.flip:
                    hitbox.rect.x -= hitbox.rect.width
                if self.item_timer > 0:
                    hitbox.damage *= 2

                hitbox.rect.x += self.rect.x
                hitbox.rect.y += self.rect.y

                if hitbox not in self.active_hitbox:
                    self.active_hitbox.append(hitbox)

    def update(self, floor_collisions, object_collisions):
        #print('input_buffer', self.input_buffer, '\ttimer:', self.input_buffer_timer, self.active_hitbox)
        #print('x_state:', self.x_state, '\ty_state:', self.y_state, '\tflip:', self.flip, '\tleft:', self.key[pygame.K_LEFT], '\tright:', self.key[pygame.K_RIGHT], '\tattack:', self.key[pygame.K_z], '\tcurrent frame:', self.current_frame)
        #print('velocity:',self.velocity[0])
        
        self.update_timer_events()
        self.update_hitbox_q()

        self.velocity[1] = 0
        self.gravity += 0.275
        if self.gravity > 10:
            self.gravity = 10
        
        player_cor = [self.rect.x,self.rect.y]
        if self.flip:
            player_cor[0] += self.rect.width + 13
        self.fairy.update(player_cor, self.alpha, self.flip)
        self.afterimage_q.update()

        self.gate_collision = object_collisions['gates']

        if object_collisions['items'] and len(self.inventory) < self.inventory_size:
            self.inventory.append(object_collisions['items'][0])
            self.play_sound('item_get')

        if object_collisions['enemies'] and object_collisions['enemies'][0].state != 'DESTROY' and self.x_state != 'DAMAGE' and self.x_state != 'TRANSITION_IN' and self.x_state != 'TRANSITION_OUT' and not self.iframes:
            self.play_sound('damage')
            self.health -= object_collisions['enemies'][0].damage
            self.increase_special(object_collisions['enemies'][0].damage)

            if self.x_state == 'DUCK':
                self.rect = pygame.Rect(self.rect.x, self.rect.y - self.rect.height, self.rect.width, self.rect.height * 2)
            
            self.x_state = 'DAMAGE'
            self.y_state = 'JUMP 2'
            self.gravity = -2
            self.set_animation('slide',0,'ONCE')
            self.white_shading = 255
            self.white_shade_timer = 10

            self.ease_x = False
            self.ease_x_timer = 0
            self.input_buffer_timer = 0
            self.input_buffer = False
            self.after_image = False
            self.hitbox_q = []
            floor_collisions['bottom'] = False

            if self.velocity[0] == 0:
                self.velocity[0] = 1
            else:
                self.velocity[0] = abs(self.velocity[0])

            if not self.flip:
                self.velocity[0] *= -1

        if self.x_state == 'SPECIAL':
            self.set_animation('special',0,'ONCE')
            self.input_buffer = True
            self.afterimage_q.q.clear()

        if self.x_state == 'TRANSITION_IN':
            self.velocity = [0,0]
            self.input_buffer = True
            self.alpha -= 7
            if self.alpha < 0:
                self.alpha = 0

        if self.x_state == 'TRANSITION_OUT':
            self.velocity = [0,0]
            self.alpha += 7
            
            self.fairy.cor = [self.rect.x-13,self.rect.y+4]
            if self.flip:
                self.fairy.cor[0] += self.rect.width+14

            if self.alpha > 255 and not self.input_buffer:
                self.alpha = 255
                self.x_state = 'IDLE'
                self.set_animation('idle',0, 'LOOP')
            else:
                self.input_buffer = True
        

        if not self.input_buffer: 
            if self.key[pygame.K_LEFT] or self.key[pygame.K_a] or self.button[10]:
                if self.x_state == 'IDLE':
                    if self.dtap_timer > 0 and self.flip == True and self.y_state == 'IDLE':
                        self.x_state = 'RUN'
                        self.set_animation('run',0, 'LOOP')
                        self.ease_x = True
                        self.afterimage = True
                        self.dtap_timer = 0
                    else:
                        self.x_state = 'WALK'
                        if self.current_animation != 'walk' and self.y_state == 'IDLE':
                            self.set_animation('walk',0, 'LOOP')
                        if self.y_state == 'IDLE':
                            self.flip = True
                elif self.x_state == 'RUN':
                    self.ease_x_timer = 20
            
            elif self.prev_key[pygame.K_LEFT] or self.prev_key[pygame.K_a] or self.prev_button[10]:
                if (self.x_state == 'WALK' or self.x_state == 'RUN') and self.flip == True:
                    self.dtap_timer = 10
                    if self.x_state == 'RUN':
                        if self.ease_x:
                            self.ease_x_timer = 20
                            self.input_buffer = True
                            self.input_buffer_timer = 30
                            self.set_animation('slide',0, 'ONCE')
                    self.x_state = 'IDLE'
                    if self.y_state == 'IDLE' and not self.ease_x:
                        self.set_animation('idle',0, 'LOOP')

            if self.key[pygame.K_RIGHT] or self.key[pygame.K_d] or self.button[11]:
                if self.x_state == 'IDLE':
                    if self.dtap_timer > 0 and self.flip == False and self.y_state == 'IDLE':
                        self.x_state = 'RUN'
                        self.set_animation('run',0, 'LOOP')
                        self.ease_x = True
                        self.afterimage = True
                        self.dtap_timer = 0
                    else:
                        self.x_state = 'WALK'
                        if self.current_animation != 'walk' and self.y_state == 'IDLE':
                            self.set_animation('walk',0, 'LOOP')
                        if self.y_state == 'IDLE':
                            self.flip = False
                elif self.x_state == 'RUN':
                    self.ease_x_timer = 20

            elif self.prev_key[pygame.K_RIGHT] or self.prev_key[pygame.K_d] or self.prev_button[11]:
                if (self.x_state == 'WALK' or self.x_state == 'RUN') and self.flip == False:
                    self.dtap_timer = 10
                    if self.x_state == 'RUN':
                        if self.ease_x:
                            self.ease_x_timer = 20
                            self.input_buffer = True
                            self.input_buffer_timer = 30
                            self.set_animation('slide',0, 'ONCE')
                    self.x_state = 'IDLE'
                    if self.y_state == 'IDLE' and not self.ease_x:
                        self.set_animation('idle',0, 'LOOP')

            if self.key[pygame.K_DOWN] or self.key[pygame.K_s] or self.button[13]:
                if self.x_state == 'IDLE' and self.y_state == 'IDLE':
                        self.x_state = 'DUCK'
                        self.set_animation('duck',0,'LOOP')

                        self.rect = pygame.Rect(self.rect.x, self.rect.y + (self.rect.height / 2), self.rect.width, self.rect.height / 2)
            
            elif self.prev_key[pygame.K_DOWN] or self.prev_key[pygame.K_s] or self.prev_button[13]:
                if self.x_state == 'DUCK':
                    self.x_state = 'IDLE'
                    self.set_animation('idle',0, 'LOOP')
                    self.rect = pygame.Rect(self.rect.x, self.rect.y - self.rect.height, self.rect.width, self.rect.height * 2)

 
        #if floor_collisions['top']:
        #    self.gravity = 0.5

        if floor_collisions['bottom']:
            self.gravity = 0
            if self.y_state != 'IDLE':
                self.y_state = 'IDLE'
                self.ease_x = False
                self.ease_x_timer = 0
                self.afterimage = False
                self.dtap_timer = 0
                if self.x_state != 'DUCK':
                    if self.x_state == 'DAMAGE':
                        self.white_shading = 0
                        self.iframes = True
                        self.iframes_timer = 30
                    self.x_state = 'IDLE'
                    self.set_animation('idle',0, 'LOOP')
                
                if not self.input_buffer:
                    if self.key[pygame.K_LEFT] or self.key[pygame.K_a] or self.button[10]:
                        self.flip = True
                    elif self.key[pygame.K_RIGHT] or self.key[pygame.K_d] or self.button[11]:
                        self.flip = False

        #print('frame:',self.current_frame,'\tattack:',self.key[pygame.K_z], '\thitbox-q:', self.hitbox_q, '\ta-hitbox:', self.active_hitbox)
        #print('ease_x', self.ease_x, 'timer', self.ease_x_timer, '\tvelocity', self.velocity[0])

    def read_input_keydown(self, key, button):
        if (key == pygame.K_z or button == 0):
            if self.y_state != 'IDLE':
                h = self.hitbox['jump-attack']
                self.hitbox_q.append(h)
                self.set_animation('jump-attack',0,'ONCE')
                self.play_sound('jump-attack')

                self.input_buffer = True
                self.input_buffer_timer = 3*6

                if (self.flip and (self.key[pygame.K_RIGHT] or self.key[pygame.K_d] or self.button[11])) or (not self.flip and (self.key[pygame.K_LEFT] or self.key[pygame.K_a] or self.button[10])):
                    self.flip = not self.flip

            elif self.x_state == 'IDLE' or self.x_state == 'WALK':
                h = self.hitbox['idle-attack']
                self.hitbox_q.append(h)
                self.set_animation('idle-attack',0,'ONCE')
                self.play_sound('idle-attack')

                self.input_buffer = True
                self.input_buffer_timer = 4*6
                self.x_state = 'IDLE'
                self.velocity[0] = 0

            elif self.x_state == 'RUN':
                h = self.hitbox['dash-attack']
                self.hitbox_q.append(h)
                self.set_animation('dash-attack',0,'ONCE')
                self.play_sound('dash-attack')

                self.input_buffer = True
                self.input_buffer_timer = 12*6
                self.x_state = 'IDLE'
                self.ease_x = True
                self.after_image = True
                self.ease_x_timer = 7*6
                self.iframes = True
                self.iframes_timer = 7*6
            
            else:
                h = self.hitbox['down-attack']
                self.hitbox_q.append(h)
                self.set_animation('down-attack',0,'ONCE')
                self.play_sound('down-attack')

                self.input_buffer = True
                self.input_buffer_timer = 4*6

        elif (key == pygame.K_x or button == 2) and not self.iframes:
            if (self.x_state == 'IDLE' or self.x_state == "WALK") and self.y_state == 'IDLE':
                h = self.hitbox['guardbox']
                self.hitbox_q.append(h)
                self.set_animation('guard',0,'ONCE')
                self.play_sound('guard')

                self.input_buffer = True
                self.input_buffer_timer = 30

                self.x_state = 'IDLE'
                self.velocity[0] = 0
        
        elif (key == pygame.K_SPACE or button == 4 or button == 5):
            if self.special >= 20 and self.x_state == 'IDLE' and self.y_state == 'IDLE':
                self.x_state = 'SPECIAL'
                self.play_sound('use_special')
                self.special = 0

        if (key == pygame.K_UP or key == pygame.K_w or button == 1 or button == 12):
            if self.gate_collision and self.x_state == 'IDLE' and self.y_state == 'IDLE' and not self.ease_x:
                self.x_state = 'TRANSITION_IN'
                self.y_state = 'IDLE'
                self.set_animation('walk-in',0,'LOOP')
                self.gate_collision = False

            elif self.x_state != 'DUCK' and self.x_state != 'TRANSITION_IN' and self.x_state != 'TRANSITION_OUT' and self.y_state != 'JUMP 2':
                self.gravity = -4
                self.set_animation('jump',0,'ONCE')
                self.play_sound('jump')
                self.ease_x = False
                self.ease_x_timer = 0

                if self.y_state != 'JUMP 1':
                    self.y_state = 'JUMP 1'
                else:
                    self.y_state = 'JUMP 2'
                    

