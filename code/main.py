import pygame, math, sys, time
import engine as e
from engine import *
from objects import *

#### C:\users\saadi\appdata\local\packages\pythonsoftwarefoundation.python.3.9_qbz5n2kfra8p0\localcache\local-packages\python39\Scripts\pyinstaller.exe
#### command to use pyinstaller

# for debug
MUSIC = True

def START_SCREEN():
    pygame.mixer.music.load('code/assets/sounds/music/menu.wav')
    pygame.mixer.music.set_volume(e.settings['Music Volume']/10)
    if MUSIC:
        pygame.mixer.music.play(-1)
    fancy_font = Font('code/assets/fonts/fancy.png',0)
    background = SkyBackground(e.tilesets_database, CAMERA_SIZE, CHUNK_SIZE)
    transition = Transition('FADE-OUT',WHITE,255,3,CAMERA_SIZE)
    state = 'START'
    select = -1
    instruction = ''
    instr_surf = pygame.Surface(CAMERA_SIZE)
    instr_surf.set_colorkey((0,0,0))
    alpha = 0

    text_scroller = TextScroller(['Serena Caelum'], fancy_font, (255,255,255), 200, 100, 5)

    while True:
        e.last_time = time.time()
        #print('FPS:', str(int(e.clock.get_fps())), '\tdt:', dT)
        background.update()
        camera.fill((0,0,0))
        camera.blit(background.draw(),(0,0))

        instr_surf.fill((0,0,0))

        if state == 'START' or state == 'TRANSITION_TO_SELECT':
            instruction = 'Press Start'
            alpha = (255 / 2) * math.sin(time.time()*2) + (255 / 2) if state == 'START' else alpha-5
            # shadow
            instr_surf.blit(fancy_font.draw(instruction, (60, 60, 60)), ((CAMERA_SIZE[0] / 2) - (fancy_font.get_width(instruction) / 2)+1, (CAMERA_SIZE[1] * (3/4)) - (fancy_font.height / 2)))
            instr_surf.blit(fancy_font.draw(instruction, (60, 60, 60)), ((CAMERA_SIZE[0] / 2) - (fancy_font.get_width(instruction) / 2)+1, (CAMERA_SIZE[1] * (3/4)) - (fancy_font.height / 2)+1))
            # text
            instr_surf.blit(fancy_font.draw(instruction, WHITE), ((CAMERA_SIZE[0] / 2) - (fancy_font.get_width(instruction) / 2), (CAMERA_SIZE[1] * (3/4)) - (fancy_font.height / 2)))
            instr_surf.set_alpha(alpha)

            if state == 'TRANSITION_TO_SELECT' and alpha <= 0:
                state = 'SELECT'

        elif state == 'SELECT' or state == 'TRANSITION_TO_GAME':
            instruction = ['Start Game','Options','Quit Game']
            alpha = min(alpha+5, 255)
            for i in range(len(instruction)):
                font_color = (255, 255, 255) if select == i else (60, 60, 60)
                
                shadow_color = (100, 100, 100) if select == i else (40, 40, 40)
                y_offset = 2 * ((2/math.pi)*math.asin(math.sin(time.time()*math.pi*3))) if select == i else 0
                
                # shadow
                instr_surf.blit(fancy_font.draw(instruction[i], shadow_color), (((CAMERA_SIZE[0] * (i+1)/4)) - (fancy_font.get_width(instruction[i]) / 2) +1, (CAMERA_SIZE[1] * (3/4)) - (fancy_font.height / 2) + y_offset))
                instr_surf.blit(fancy_font.draw(instruction[i], shadow_color), (((CAMERA_SIZE[0] * (i+1)/4)) - (fancy_font.get_width(instruction[i]) / 2) +1, (CAMERA_SIZE[1] * (3/4)) - (fancy_font.height / 2)+1 + y_offset))
                # text
                instr_surf.blit(fancy_font.draw(instruction[i], font_color), (((CAMERA_SIZE[0] * (i+1)/4)) - (fancy_font.get_width(instruction[i]) / 2), (CAMERA_SIZE[1] * (3/4)) - (fancy_font.height / 2) + y_offset))
                instr_surf.set_alpha(alpha)
            
        camera.blit(instr_surf,(0,0))
        
        text_scroller.update()
        camera.blit(text_scroller.draw(),((CAMERA_SIZE[0]/2)-(fancy_font.get_width('Serena Caelum')/2), 60))
        
        for event in pygame.event.get():
            joystick_buttonpress = -1
            if event.type == pygame.JOYDEVICEADDED:
                e.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if event.type == pygame.JOYDEVICEREMOVED:
                e.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP or event.type == pygame.JOYHATMOTION:
                joystick_buttonpress = e.read_input_joystick(event)

            if joystick_buttonpress == 0 or joystick_buttonpress == 7 or (event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_z)):
                if state == 'START':
                    e.play_sound('press_start')
                    state = 'TRANSITION_TO_SELECT'
                elif state == 'SELECT' and select > -1:
                    if select != 1:
                        pygame.mixer.music.fadeout(1000)
                        transition = Transition('FADE-IN',(0,0,0),0,2,CAMERA_SIZE)
                    else:
                        transition = Transition('FADE-IN',(0,0,0),0,5,CAMERA_SIZE)

                    if select == 0:
                        e.play_sound('start_game')
                    elif select == 1:
                        e.play_sound('select')

                    state = 'TRANSITION_TO_GAME'

            elif (joystick_buttonpress == 10 or joystick_buttonpress == 12 or (event.type == pygame.KEYDOWN and (event.key == pygame.K_UP or event.key == pygame.K_LEFT or event.key == pygame.K_w or event.key == pygame.K_a))) and state == 'SELECT':
                select -= 1
                e.play_sound('cursor')
                if select < 0:
                    select = len(instruction)-1
                
            elif (joystick_buttonpress == 11 or joystick_buttonpress == 13 or (event.type == pygame.KEYDOWN and (event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT or event.key == pygame.K_s or event.key == pygame.K_d))) and state == 'SELECT':
                select += 1
                e.play_sound('cursor')
                if select >= len(instruction):
                    select = 0

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if transition is not None:
            camera.blit(transition.draw(), (0,0))
            if transition.end:
                transition = None

                if state == 'TRANSITION_TO_GAME':
                    game_win = False
                    if select == 0:
                        game_win = GAME_INTRO()
                        pygame.mixer.music.load('code/assets/sounds/music/menu.wav')
                        if MUSIC:
                            pygame.mixer.music.play(-1)
                    elif select == 1:
                        OPTIONS_SCREEN()
                    elif select == 2:
                        pygame.quit()
                        sys.exit()

                    state = 'START'
                    select = -1
                    if game_win:
                        transition = Transition('FADE-OUT',(255,255,255),255,3,CAMERA_SIZE)
                    else:
                        transition = Transition('FADE-OUT',(0,0,0),255,3,CAMERA_SIZE)
                    select = -1
                    alpha = 0

        main_display.blit(pygame.transform.scale(camera, e.WINDOW_SIZE), ((main_display.get_width()/2)-(e.WINDOW_SIZE[0]/2), (main_display.get_height()/2)-(e.WINDOW_SIZE[1]/2)))
        pygame.display.update()
        e.clock.tick(FPS)        


def OPTIONS_SCREEN():
    fancy_font = Font('code/assets/fonts/fancy.png',0)
    plain_font = Font('code/assets/fonts/plain.png')
    transition = Transition('FADE-OUT',BLACK,255,5,CAMERA_SIZE)
    options = ['Window Size','Window Border','Full Screen','Music Volume','Sound Volume']
    options_surf = pygame.Surface(CAMERA_SIZE)
    options_surf.set_colorkey((0,0,0))
    select = -1
    Run = True

    while Run:
        camera.fill((0,0,0))
        camera.blit(e.tilesets_database['backgrounds_list']['options_screen'],(0,0))
        options_surf.fill((0,0,0))
        
        # - title
        options_surf.blit(fancy_font.draw('Options', (60, 60, 60)), ((CAMERA_SIZE[0] / 2) - (fancy_font.get_width('Options') / 2) +1, 8))
        options_surf.blit(fancy_font.draw('Options', (60, 60, 60)), ((CAMERA_SIZE[0] / 2) - (fancy_font.get_width('Options') / 2) +1, 8+1))
        options_surf.blit(fancy_font.draw('Options', (255, 255, 255)), ((CAMERA_SIZE[0] / 2) - (fancy_font.get_width('Options') / 2), 8))
        
        y_offset = 16+fancy_font.height+12
        for i in range(len(options)):
            font_color = (255, 255, 255) if select == i else (60, 60, 60) 
            shadow_color = (100, 100, 100) if select == i else (40, 40, 40)

            # - options
            # shadow
            options_surf.blit(plain_font.draw(options[i], shadow_color), ((CAMERA_SIZE[0] / 10)-10 +1, y_offset))
            options_surf.blit(plain_font.draw(options[i], shadow_color), ((CAMERA_SIZE[0] / 10)-10 +1, y_offset +1))
            # text
            options_surf.blit(plain_font.draw(options[i], font_color), ((CAMERA_SIZE[0] / 10)-10, y_offset))

            # - settings
            setting = ''
            if options[i] == 'Full Screen' or options[i] == 'Window Border':
                setting = 'ON' if e.settings[options[i]] == 1 else 'OFF'
            elif options[i] == 'Window Size':
                setting = str(e.settings[options[i]]) + 'x'
            elif options[i] == 'Music Volume' or options[i] == 'Sound Volume':
                setting = str(e.settings[options[i]])
            
            # shadow
            options_surf.blit(plain_font.draw(setting, shadow_color), ((CAMERA_SIZE[0] * (8/10)) - (plain_font.get_width(setting) / 2) +1, y_offset))
            options_surf.blit(plain_font.draw(setting, shadow_color), ((CAMERA_SIZE[0] * (8/10)) - (plain_font.get_width(setting) / 2) +1, y_offset +1))
            # text
            options_surf.blit(plain_font.draw(setting, font_color), ((CAMERA_SIZE[0] * (8/10)) - (plain_font.get_width(setting) / 2), y_offset))
            options_surf.blit(plain_font.draw('<', font_color), ((CAMERA_SIZE[0] * (8/10)) - 20, y_offset))
            options_surf.blit(plain_font.draw('>', font_color), ((CAMERA_SIZE[0] * (8/10)) + 15, y_offset))

            y_offset += plain_font.height + 12
            if i == 2:
                y_offset += 12
        
        font_color = (255, 255, 255) if select < 0 else (60, 60, 60)
        shadow_color = (100, 100, 100) if select < 0 else (40, 40, 40)
         
        options_surf.blit(plain_font.draw('Back', shadow_color), ((CAMERA_SIZE[0] / 2) - (plain_font.get_width('Back') / 2) +1, y_offset+8))
        options_surf.blit(plain_font.draw('Back', shadow_color), ((CAMERA_SIZE[0] / 2) - (plain_font.get_width('Back') / 2) +1, y_offset+8 +1))
        options_surf.blit(plain_font.draw('Back', font_color), ((CAMERA_SIZE[0] / 2) - (plain_font.get_width('Back') / 2), y_offset+8))

        camera.blit(options_surf,(0,0))

        for event in pygame.event.get():
            joystick_buttonpress = -1
            if event.type == pygame.JOYDEVICEADDED:
                e.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if event.type == pygame.JOYDEVICEREMOVED:
                e.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP or event.type == pygame.JOYHATMOTION:
                joystick_buttonpress = e.read_input_joystick(event)
            
            if select != -2:
                if joystick_buttonpress == 12 or (event.type == pygame.KEYDOWN and (event.key == pygame.K_UP or event.key == pygame.K_w)):
                    select -= 1
                    e.play_sound('cursor')
                    if select < -1:
                        select = len(options)-1

                elif joystick_buttonpress == 13 or (event.type == pygame.KEYDOWN and (event.key == pygame.K_DOWN or event.key == pygame.K_s)):
                    select += 1
                    e.play_sound('cursor')
                    if select >= len(options):
                        select = -1
                
                elif (joystick_buttonpress == 10 or (event.type == pygame.KEYDOWN and (event.key == pygame.K_LEFT or event.key == pygame.K_a))) and select >= 0:
                    if options[select] == 'Full Screen' or options[select] == 'Window Border':
                        e.settings[options[select]] = 0 if e.settings[options[select]] == 1 else 1
                        e.play_sound('cursor')
                    elif options[select] == 'Window Size':
                        e.settings[options[select]] = e.settings[options[select]] - 1 if e.settings[options[select]] > 1 else 5
                        e.play_sound('cursor')
                    elif options[i] == 'Music Volume' or options[i] == 'Sound Volume':
                        if e.settings[options[select]] > 0:
                            e.settings[options[select]] -= 1
                            e.play_sound('cursor')

                    e.main_display = apply_settings(e.settings)

                elif (joystick_buttonpress == 11 or (event.type == pygame.KEYDOWN and (event.key == pygame.K_RIGHT or event.key == pygame.K_d))) and select >= 0:
                    if options[select] == 'Full Screen' or options[select] == 'Window Border':
                        e.settings[options[select]] = 0 if e.settings[options[select]] == 1 else 1
                        e.play_sound('cursor')
                    elif options[select] == 'Window Size':
                        e.settings[options[select]] = e.settings[options[select]] + 1 if e.settings[options[select]] < 5 else 1
                        e.play_sound('cursor')
                    elif options[i] == 'Music Volume' or options[i] == 'Sound Volume':
                        if e.settings[options[select]] < 10:
                            e.settings[options[select]] += 1
                            e.play_sound('cursor')

                    e.main_display = apply_settings(e.settings)
                
                elif (joystick_buttonpress == 1 or (event.type == pygame.KEYDOWN and event.key == pygame.K_x)):
                    if select != -1:
                        e.play_sound('back')
                        select = -1  

                elif (joystick_buttonpress == 0 or joystick_buttonpress == 7 or (event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_z))) and select == -1:
                    e.play_sound('select')
                    select = -2
                    transition = Transition('FADE-IN',(0,0,0),0,5,CAMERA_SIZE)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        if transition is not None:
            camera.blit(transition.draw(), (0,0))
            if transition.end:
                if transition.transition_type == 'FADE-IN':
                    Run = False
                transition = None

        main_display.blit(pygame.transform.scale(camera, e.WINDOW_SIZE), ((main_display.get_width()/2)-(e.WINDOW_SIZE[0]/2), (main_display.get_height()/2)-(e.WINDOW_SIZE[1]/2)))
        pygame.display.update()
        e.clock.tick(FPS)


def HOW_TO_PLAY():
    transition = Transition('FADE-OUT',BLACK,255,6,CAMERA_SIZE)
    Run = True

    while Run:
        camera.fill((0,0,0))
        camera.blit(e.tilesets_database['backgrounds_list']['tutorial'],(0,0))
        
        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEADDED:
                e.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if event.type == pygame.JOYDEVICEREMOVED:
                e.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if (event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN) and transition is None:
                transition = Transition('FADE-IN',BLACK,0,4,CAMERA_SIZE)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if transition is not None:
                camera.blit(transition.draw(), (0,0))
                if transition.end:
                    if transition.transition_type == 'FADE-IN':
                        Run = False
                    transition = None

        main_display.blit(pygame.transform.scale(camera, e.WINDOW_SIZE), ((main_display.get_width()/2)-(e.WINDOW_SIZE[0]/2), (main_display.get_height()/2)-(e.WINDOW_SIZE[1]/2)))
        pygame.display.update()
        e.clock.tick(FPS)

    START_SCREEN()


def GAME_INTRO():
    pygame.mixer.music.load('code/assets/sounds/music/intro.wav')
    pygame.mixer.music.set_volume(e.settings['Music Volume']/10)
    if MUSIC:
        pygame.mixer.music.play(-1)
    scene = 0
    timer = 0
    y_offset = 0
    timer_duration = 180
    text = ['The sky is shattered','but the sun is still there','so the High Priestess must be safe.',
            'She left so fast and told no one.','As her guardian, it\'s my duty to protect her.','Where did she go?',
            'Soleanna!','Even if the sky is falling down','I will find you!']
    fancy_font = Font('code/assets/fonts/fancy.png',0)
    text_scroll = TextScroller(text, fancy_font,(255,255,255),fancy_font.get_width(text[0]),fancy_font.height,5)
    transition = Transition('FADE-IN',(255,255,255),0,3,CAMERA_SIZE)
    Run = True

    while Run:
        camera.fill((0,0,0))

        if scene < 6:
            camera.blit(text_scroll.draw(),((CAMERA_SIZE[0]/2)-(fancy_font.get_width(text[0])/2), (CAMERA_SIZE[1]/2)-(fancy_font.height/2)))

            if not text_scroll.end:
                text_scroll.update()
            else:
                timer += 1
            
            if timer >= timer_duration:
                timer = 0
                scene += 1
                text_scroll.next_line() # pops text list from this loop as well
                text_scroll.width = fancy_font.get_width(text[0])

                if len(text_scroll.text) == 4:
                    pygame.mixer.music.fadeout(50)
                
                if scene == 6:
                    timer_duration = 240
                    if MUSIC:
                        pygame.mixer.music.load('code/assets/sounds/music/level_A.wav')
                        pygame.mixer.music.play(-1)

        elif scene < 8:
            timer += 1
            if timer < 120:
                camera.blit(pygame.transform.scale(e.tilesets_database['backgrounds_list']['intro_'+str(scene-5)], (240,160)),(0,0+(12*(scene-6))))
                pygame.draw.rect(camera, (0,0,0), pygame.Rect(0,0,CAMERA_SIZE[0],24))
                pygame.draw.rect(camera, (0,0,0), pygame.Rect(0,CAMERA_SIZE[1]-24,CAMERA_SIZE[0],24))
            elif timer < timer_duration:
                camera.blit(fancy_font.draw(text[0],(255,255,255)),((CAMERA_SIZE[0]/2)-(fancy_font.get_width(text[0])/2), (CAMERA_SIZE[1]/2)-(fancy_font.height/2)))
            else:
                timer = 0
                y_offset = 288-160
                scene += 1
                text.pop(0)

                if scene == 6:
                    timer_duration = 120
        
        elif scene == 8:
            img = e.tilesets_database['backgrounds_list']['intro_'+str(scene-5)]
            camera.blit(pygame.transform.scale(img, (192,288)),(24,0-y_offset))
            if timer < 60:
                timer += 1
            elif timer > 120:
                camera.blit(transition.draw(), (0,0))
                if transition.end:
                    timer = 0
                    scene += 1
                    timer_duration = 120
                    transition = Transition('FADE-IN',(255,255,255),0,3,CAMERA_SIZE)
            else:
                y_offset -= 1
                if y_offset < 20:
                    y_offset = 20
                    timer += 1

        else:
            camera.fill((255,255,255))
            camera.blit(fancy_font.draw(text[0]),((CAMERA_SIZE[0]/2)-(fancy_font.get_width(text[0])/2), (CAMERA_SIZE[1]/2)-(fancy_font.height/2)))

            timer += 1
            if timer >= timer_duration:
                camera.blit(transition.draw(), (0,0))
                if transition.end:
                    Run = False
            
        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEADDED:
                e.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if event.type == pygame.JOYDEVICEREMOVED:
                e.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or (event.type == pygame.JOYBUTTONDOWN and event.button == 7):
                Run = False
                if scene < 6 and MUSIC:
                    pygame.mixer.music.load('code/assets/sounds/music/level_A.wav')
                    pygame.mixer.music.set_volume(e.settings['Music Volume']/10)
                    pygame.mixer.music.play(-1)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        main_display.blit(pygame.transform.scale(camera, e.WINDOW_SIZE), ((main_display.get_width()/2)-(e.WINDOW_SIZE[0]/2), (main_display.get_height()/2)-(e.WINDOW_SIZE[1]/2)))
        pygame.display.update()
        e.clock.tick(FPS)
    
    return GAME_LOOP()


def REUNION_CUTSCENE():
    pygame.mixer.music.fadeout(1000)
    pygame.mixer.music.load('code/assets/sounds/music/reunion_A.wav')
    scene = 0
    timer = 0
    text_p1 = ['C:Soleanna!','S:...Caelum?']
    text_p2 = ['S:I\'m glad you found me.','C:You left no clues where you would be...','C:and yet I knew exactly where to find you.',
            'S:I couldn\'t let anyone know where I was.','S:This was the one place only you and I know.','S:We can be alone here.',
            'C:The sky is cracked. The animals have gone mad.','C:What is going on?','S:A great calamity has ripped through the atmosphere and slipped through to our surface.',
            'S:This malice has been sending whispers in my mind.','S:It\'s looking for the light of the sun... It\'s looking for me.','S:Caelum, if it gets to me... if my prayers stop',
            'S:then the sun will never rise again and the world will-','C:I know, and I want to help. Why did you leave without me?','S:It\'s not fair. You do so much for me and I give nothing in return.',
            'S:I just hope and pray. I want to do more.','C:...','C:Soleanna, my strength comes from your light.','C:I fight because I don\'t want to live in a world without you.',
            'S:The enemy is almost here. Our time has run up.','C:I\'ll fight and I\'ll win.','C:And then, we can watch the sun rise together.','S:Caelum, my guardian, my blue bird... I pray for your safe return.']
    fancy_font = Font('code/assets/fonts/fancy.png',0)
    dialog_box = DialogBox(text_p1,fancy_font,3)
    transition = Transition('FADE-IN',(255,255,255),0,5,CAMERA_SIZE)
    Run = True

    while Run:
        camera.fill((0,0,0))

        if scene == 0:
            timer += 1
            if timer == 10:
                pygame.mixer.music.set_volume(e.settings['Music Volume']/10)
                e.play_sound('door')
            if timer > 150:
                timer = 0
                scene += 1
        
        elif scene == 1:
            camera.blit(dialog_box.draw(), (0,0))
            dialog_box.update()
            if dialog_box.end:
                camera.blit(transition.draw(), (0,0))
                if transition.end:
                    scene += 1
                    dialog_box = DialogBox(text_p2,fancy_font,3)
                    transition = Transition('FADE-OUT',(255,255,255),255,3,CAMERA_SIZE)
                    if MUSIC:
                        pygame.mixer.music.play(-1)
        
        elif scene == 2:
            camera.blit(e.tilesets_database['backgrounds_list']['options_screen'],(0,0))
            camera.blit(transition.draw(), (0,0))
            if transition.end:
                camera.blit(dialog_box.draw(), (0,0))
                dialog_box.update()
                if dialog_box.end:
                    scene += 1
                    transition = Transition('FADE-IN',(255,255,255),0,3,CAMERA_SIZE)
        
        elif scene == 3:
            camera.blit(e.tilesets_database['backgrounds_list']['options_screen'],(0,0))
            pygame.mixer.music.fadeout(1000)
            camera.blit(transition.draw(), (0,0))
            
            if transition.end:
                pygame.mixer.music.load('code/assets/sounds/music/boss.wav')
                pygame.mixer.music.set_volume(e.settings['Music Volume']/10)
                Run = False
        
        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEADDED:
                e.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if event.type == pygame.JOYDEVICEREMOVED:
                e.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or (event.type == pygame.JOYBUTTONDOWN and event.button == 7):
                dialog_box.next_line()

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        main_display.blit(pygame.transform.scale(camera, e.WINDOW_SIZE), ((main_display.get_width()/2)-(e.WINDOW_SIZE[0]/2), (main_display.get_height()/2)-(e.WINDOW_SIZE[1]/2)))
        pygame.display.update()
        e.clock.tick(FPS)


def SPECIAL_MOVE():
    timer = 0 
    transition = Transition('FADE-OUT',(255,255,255),255,3,CAMERA_SIZE)
    swipe = pygame.Rect(0,(CAMERA_SIZE[1]/2),1,1)
    swipe_fade = False
    e.play_sound('special_scream')
    sound_stop = False
    Run = True

    while Run:
        camera.fill((0,0,0))

        if timer < 150:
            camera.blit(e.tilesets_database['backgrounds_list']['firebird'],(0,0))
            timer += 1
        else:
            if not sound_stop:
                e.sounds_database['special_scream'].stop()
                e.play_sound('special_slash')
                sound_stop = True

            pygame.draw.rect(camera, (255,255,255), swipe)
            if not swipe_fade:
                swipe.width += 20
            else:
                swipe.x += 20

        if swipe.width > CAMERA_SIZE[0]:
            swipe_fade = True
            
        if swipe.x > CAMERA_SIZE[0]:
            timer += 1
            if timer < 150:
                camera.fill(BLACK)
            else:
                camera.fill(WHITE)
                Run = False
        
        # if timer >= 160:
        #     Run = False

        camera.blit(transition.draw(),(0,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    
        main_display.blit(pygame.transform.scale(camera, e.WINDOW_SIZE), ((main_display.get_width()/2)-(e.WINDOW_SIZE[0]/2), (main_display.get_height()/2)-(e.WINDOW_SIZE[1]/2)))
        pygame.display.update()
        e.clock.tick(FPS)


def GAME_OVER(player, camera_pos, score):
    player.white_shading = 0
    timer = 0
    sfx_played = False
    Run = True

    while Run:
        camera.fill((0,0,0))
        camera.blit(player.draw(), (player.rect.x-camera_pos[0]-16, player.rect.y-camera_pos[1]-16))
        
        if timer < 120:
            timer += 1
        else:
            player.white_shading += 10
            if not sfx_played:
                sfx_played = True
                e.play_sound('player_down')

        if player.white_shading >= 255:
            player.white_shading = 255
            player.alpha -= 10
        
        if player.alpha <= 0:
            player.alpha = 0
            timer += 1

        if timer > 130:
            RESULTS_SCREEN((0,0,0), (255,255,255), 'Try Again...', score)
            Run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        main_display.blit(pygame.transform.scale(camera, e.WINDOW_SIZE), ((main_display.get_width()/2)-(e.WINDOW_SIZE[0]/2), (main_display.get_height()/2)-(e.WINDOW_SIZE[1]/2)))
        pygame.display.update()
        e.clock.tick(FPS)


def RESULTS_SCREEN(back_color, font_color, header, score, shadow_color=(100, 100, 100)):
    plain_font = Font('code/assets/fonts/plain.png')
    transition = Transition('FADE-IN',(0,0,0),0,4,CAMERA_SIZE)
    results_surf = pygame.Surface(CAMERA_SIZE)
    results_surf.set_colorkey((0,0,0))
    score_stack = {}
    draw_transition = False
    Run = True

    while Run:
        camera.fill(back_color)
        results_surf.fill((0,0,0))

        y_offset = 55
        for category in score:
            if category not in score_stack:
                score_stack[category] = 0
            
            results_surf.blit(plain_font.draw(category,shadow_color), ((CAMERA_SIZE[0]/10)-12+1,y_offset))
            results_surf.blit(plain_font.draw(category,shadow_color), ((CAMERA_SIZE[0]/10)-12+1,y_offset+1))
            results_surf.blit(plain_font.draw(category,font_color), ((CAMERA_SIZE[0]/10)-12,y_offset))
            
            if category == 'Total Time':
                minutes = int(score_stack[category]/60)
                timestamp = str(minutes).zfill(2)+':'+"{:05.2F}".format(score_stack[category]-minutes*60)
                results_surf.blit(plain_font.draw(timestamp,shadow_color), ((CAMERA_SIZE[0] * (9/10))-plain_font.get_width(timestamp)+1, y_offset))
                results_surf.blit(plain_font.draw(timestamp,shadow_color), ((CAMERA_SIZE[0] * (9/10))-plain_font.get_width(timestamp)+1, y_offset+1))
                results_surf.blit(plain_font.draw(timestamp,font_color), ((CAMERA_SIZE[0] * (9/10))-plain_font.get_width(timestamp), y_offset))
            else:
                results_surf.blit(plain_font.draw(str(score_stack[category]),shadow_color), ((CAMERA_SIZE[0] * (9/10))-plain_font.get_width(str(score_stack[category]))+1, y_offset))
                results_surf.blit(plain_font.draw(str(score_stack[category]),shadow_color), ((CAMERA_SIZE[0] * (9/10))-plain_font.get_width(str(score_stack[category]))+1, y_offset+1))
                results_surf.blit(plain_font.draw(str(score_stack[category]),font_color), ((CAMERA_SIZE[0] * (9/10))-plain_font.get_width(str(score_stack[category])), y_offset))

            if score_stack[category] < score[category]:
                score_stack[category] += 0.47 if category == 'Total Time' else 1
                e.play_sound('score')
                break
            elif score_stack[category] > score[category]:
                score_stack[category] = score[category]

            y_offset += plain_font.height + 12

        if len(score_stack) == len(score) and score_stack['No. of Specials Used'] >= score['No. of Specials Used']:
            results_surf.blit(plain_font.draw(header,font_color), ((CAMERA_SIZE[0] / 2)-(plain_font.get_width(header)/2), 25))
            y_offset += plain_font.height
            pointer_img = pygame.mask.from_surface(e.tilesets_database['tiles_list']['pointer'])
            results_surf.blit(pointer_img.to_surface(unsetcolor=(0,0,0),setcolor=font_color), ((CAMERA_SIZE[0]/2)-4 ,y_offset + 2 * ((2/math.pi)*math.asin(math.sin(time.time()*math.pi*3)))))

        camera.blit(results_surf,(0,0))

        if draw_transition:
            camera.blit(transition.draw(), (0,0))
        if transition.end:
            Run = False
            
        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEADDED:
                e.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if event.type == pygame.JOYDEVICEREMOVED:
                e.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if (event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN):
                draw_transition = True

                for category in score_stack:
                    if score_stack[category] < score[category]:
                        score_stack[category] = score[category]
                        draw_transition = False

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        main_display.blit(pygame.transform.scale(camera, e.WINDOW_SIZE), ((main_display.get_width()/2)-(e.WINDOW_SIZE[0]/2), (main_display.get_height()/2)-(e.WINDOW_SIZE[1]/2)))
        pygame.display.update()
        e.clock.tick(FPS)


def GAME_LOOP():
    full_transition = Transition('FADE-OUT',(255,255,255),255,3,CAMERA_SIZE)
    level_transition = None
    plain_font = Font('code/assets/fonts/plain.png')
    back_layer0 = TrippyBackground(e.tilesets_database, CAMERA_SIZE, CHUNK_SIZE, COLORSET, GREYSCALE)
    HUD = Hud()
    title_card = TitleCard("Find the High Priestess!")
    special_transition = None
    draw_hud = True
    hud_target = None
    item_select = -1
    pause_select = -1
    pause_options = ['Resume','Options','Quit']
    draw_objects_q = []

    clear_rect_list(obj_list)    
    e.level_config = load_level_config('1-1')
    score = {'Total Time':time.time(),'Damage Taken':0,'Enemies Defeated':0,'No. of Items Used':0,'No. of Specials Used':0}
    player.restart()
    Run = True

    while Run:
        dT = time.time() - e.last_time
        dT *= 60
        e.last_time = time.time()
        clear_rect_list(tile_rect_list)
        camera.fill(BLACK)
        #print('FPS:', str(int(e.clock.get_fps())), '\tdt:', dT)


        # -- INITIALIZE CHUNK & MOVE CAMERA ---
        camera_pos = set_camera_pos(e.current_chunk, player)
        next_chunk = [int(player.rect.x / CHUNK_SIZE[0]), int(player.rect.y / CHUNK_SIZE[1])]
        set_objects(e.current_chunk, next_chunk)
        e.current_chunk = next_chunk
        set_chunks(e.current_chunk)


        # -- UPDATE ---
        if pause_select == -1 and item_select == -1 and special_transition is None:
            if back_layer0 is not None:
                back_layer0.update()
            draw_objects_q.clear()
            
            if title_card.end:
                player.read_input(pygame.key.get_pressed(),e.joystick_buttonstate)
            player.set_velocity()
            floor_collisions, object_collisions = move_and_test(player.rect, player.velocity, tile_rect_list, obj_list)
            if len(player.inventory) >= player.inventory_size:
                object_collisions['items'].clear()
            prev_health = player.health
            player.sound_volume = e.settings['Sound Volume']/10
            player.update(floor_collisions, object_collisions)
            score['Damage Taken'] += prev_health - player.health
            if player.health <= 0:
                pygame.mixer.music.stop()
                score['Total Time'] = time.time() - score['Total Time']
                GAME_OVER(player, camera_pos, score)
                return False
            
            if player.x_state == 'SPECIAL' and special_transition is None:
                special_transition = SpecialTransition(player.rect.x+(player.rect.width / 2)-camera_pos[0], CAMERA_SIZE)
                score['No. of Specials Used'] += 1


            enemy_obj_list = {'player':[player]}
            enemy_obj_list['hitboxes'] = player.active_hitbox
            hud_target = None
            for enemy in obj_list['enemies']:
                floor_collisions, enemy_object_collisions = move_and_test(enemy.rect, enemy.velocity, tile_rect_list, enemy_obj_list, enemy.id == 'Bean' or enemy.id == 'Joak')
                
                if enemy_object_collisions['hitboxes']:
                    if enemy_object_collisions['hitboxes'][0].id == 'guardbox':
                        player.guard()
                    if not enemy.iframes:
                        hud_target = enemy
                        player.increase_special(enemy_object_collisions['hitboxes'][0].damage)
                        
                enemy.sound_volume = e.settings['Sound Volume']/10
                enemy.update(floor_collisions, enemy_object_collisions, player)
                
                if enemy.DESTROY:
                    if enemy.item_drop is not None:
                        obj_list['items'].append(enemy.item_drop)
                    obj_list['enemies'].remove(enemy)
                    score['Enemies Defeated'] += 1


            for item in obj_list['items']:
                item.update()
                if object_collisions['items'] and item is object_collisions['items'][0]:
                    item.destroy()
                if item.DESTROY:
                    obj_list['items'].remove(item)
        # -- DEBUG ---
        # for _list in e.tile_rect_list:
        #     for rect in e.tile_rect_list[_list]:
        #         pygame.draw.rect(camera, (255,255,255), rect, 1)

        # pygame.draw.rect(camera, (0,0,255), player.rect, 1)

        # for enemy in obj_list['enemies']:
        #     pygame.draw.rect(camera, (255,255,0), enemy.rect, 1)

        # for item in obj_list['items']:
        #     pygame.draw.rect(camera, (0,255,255), item.rect, 1)

        # for hitbox in player.active_hitbox:
        #     if hitbox.id == 'guardbox':
        #         pygame.draw.rect(camera, GREEN, hitbox.rect, 1)
        #     else:
        #         pygame.draw.rect(camera, RED, hitbox.rect, 1)
        player.active_hitbox.clear()
        

        # -- DRAW EVENTS ---
        if back_layer0 is not None:
            camera.blit(back_layer0.draw(),(0,0))
        draw_background_parallax(camera_pos)
        draw_chunks(camera_pos, e.current_chunk)
        
        if player.x_state == 'SPECIAL':
            rect_surf = pygame.Surface(CAMERA_SIZE)
            pygame.draw.rect(rect_surf, (0,0,0),pygame.Rect(0,0,CAMERA_SIZE[0],CAMERA_SIZE[1]))
            rect_surf.set_alpha(200)
            special_transition.update()
            if special_transition.transition and full_transition is None:
                full_transition = Transition('FADE-IN',(255,255,255),0,3,CAMERA_SIZE)
            camera.blit(rect_surf,(0,0))
            camera.blit(special_transition.draw(),(0,0))
        
        y_offset = 0 if pause_select != -1 else 2 * ((2/math.pi)*math.asin(math.sin(time.time()*math.pi)))
        for item in obj_list['items']:
            camera.blit(item.draw(),(item.rect.x-camera_pos[0], item.rect.y+y_offset-camera_pos[1]))
        for enemy in obj_list['enemies']:
            camera.blit(enemy.draw(),(enemy.rect.x-16-camera_pos[0], enemy.rect.y-16-camera_pos[1]))

        for image in player.afterimage_q.q:
            camera.blit(image.draw(), (image.x-camera_pos[0],image.y-camera_pos[1]))
        camera.blit(player.fairy.draw(), (player.fairy.cor[0]-camera_pos[0], player.fairy.cor[1]-camera_pos[1]))
        for fairy_particle in player.fairy.particle_q:
            camera.blit(fairy_particle.draw(), (fairy_particle.cor[0]-camera_pos[0], fairy_particle.cor[1]-camera_pos[1]))
        camera.blit(player.draw(), (player.rect.x-camera_pos[0]-16, player.rect.y-camera_pos[1]-16))
    
        draw_foreground_parallax(camera_pos)

        if object_collisions['gates'] and not player.input_buffer:
            y_pos = player.rect.y - 10 - camera_pos[1]
            y_pos -= 16 if player.x_state == 'DUCK' else 0
            camera.blit(e.tilesets_database['hud_list']['arrow'],(player.rect.x + 4 - camera_pos[0], y_pos))

        if full_transition is None and not title_card.end:
            camera.blit(title_card.draw(), (0, (CAMERA_SIZE[1]/2)-12))


        # -- INPUT ---
        for event in pygame.event.get():
            joystick_buttonpress = -1
            if event.type == pygame.JOYDEVICEADDED:
                e.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if event.type == pygame.JOYDEVICEREMOVED:
                e.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP or event.type == pygame.JOYHATMOTION:
                joystick_buttonpress = e.read_input_joystick(event)
            
            if title_card.end:
                if (joystick_buttonpress == 7 or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN)) and not player.input_buffer and full_transition is None and item_select == -1:
                    if pause_select == -1:
                        pause_select = 0
                        e.sounds_database['back'].stop()
                        e.play_sound('pause')
                    elif pause_select == 0:
                        pause_select = -1
                        e.sounds_database['pause'].stop()
                        e.play_sound('back')
                    else:
                        e.play_sound('select')
                        full_transition = Transition('FADE-IN',(0,0,0),0,5,CAMERA_SIZE)
                        if pause_select == 2:
                            pygame.mixer.music.fadeout(1000)
                elif (joystick_buttonpress == 6 or (event.type == pygame.KEYDOWN and event.key == pygame.K_RSHIFT)) and pause_select == -1 and item_select == -1:
                        draw_hud = not draw_hud
                elif (joystick_buttonpress == 3 or (event.type == pygame.KEYDOWN and event.key == pygame.K_c)) and not player.input_buffer and pause_select == -1 and len(player.inventory) > 0:
                    if item_select == -1:
                        item_select = 0
                        e.play_sound('item_menu')
                    else:
                        item_select = -1
                        e.play_sound('back')

                if item_select > -1:
                    if (joystick_buttonpress == 10 or (event.type == pygame.KEYDOWN and (event.key == pygame.K_LEFT or event.key == pygame.K_a))):
                        item_select -= 1
                        if len(player.inventory) != 1:
                            e.play_sound('cursor')
                        if item_select < 0:
                            item_select = len(player.inventory)-1
                    if (joystick_buttonpress == 11 or (event.type == pygame.KEYDOWN and (event.key == pygame.K_RIGHT or event.key == pygame.K_d))):
                        item_select += 1
                        if len(player.inventory) != 1:
                            e.play_sound('cursor')
                        if item_select >= len(player.inventory):
                            item_select = 0
                    if (joystick_buttonpress == 0 or (event.type == pygame.KEYDOWN and event.key == pygame.K_z)):
                        if player.inventory[item_select].id < 2 or (player.inventory[item_select].id == 2 and player.special < 10) or (player.inventory[item_select].id < 5 and player.special >= 20):
                            e.play_sound('select')
                        player.use_item(player.inventory[item_select].id)
                        player.inventory.pop(item_select)
                        score['No. of Items Used'] += 1
                        item_select = -1
                    if (joystick_buttonpress == 1 or (event.type == pygame.KEYDOWN and event.key == pygame.K_x)):
                        item_select = -1
                        e.play_sound('back')

                elif pause_select != -1 and full_transition is None:
                    if (joystick_buttonpress == 12 or (event.type == pygame.KEYDOWN and (event.key == pygame.K_UP or event.key == pygame.K_w))):
                        pause_select = pause_select - 1 if pause_select > 0 else len(pause_options)-1
                        e.play_sound('cursor')
                    if (joystick_buttonpress == 13 or (event.type == pygame.KEYDOWN and (event.key == pygame.K_DOWN or event.key == pygame.K_s))):
                        pause_select = pause_select + 1 if pause_select < len(pause_options)-1 else 0
                        e.play_sound('cursor')
                    if (joystick_buttonpress == 0 or (event.type == pygame.KEYDOWN and event.key == pygame.K_z)):
                        if pause_select != 0:
                            e.play_sound('select')
                            full_transition = Transition('FADE-IN',(0,0,0),0,4,CAMERA_SIZE)
                            if pause_select == 2:
                                pygame.mixer.music.fadeout(1000)
                        else:
                            pause_select = -1
                            e.sounds_database['pause'].stop()
                            e.play_sound('back')
                    if (event.type == pygame.KEYDOWN and event.key == pygame.K_x):
                            pause_select = -1
                            e.sounds_database['pause'].stop()
                            e.play_sound('back')
                
                elif not player.input_buffer and pause_select == -1 and item_select == -1:
                    key = None
                    if event.type == pygame.KEYDOWN:
                        key = event.key
                    player.read_input_keydown(key, joystick_buttonpress)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


        # -- DRAW TRANSITION, HUD, PAUSE SCREEN
        if player.x_state == 'TRANSITION_IN' and level_transition is None:
            level_transition = Transition('FADE-IN',(0,0,0),0,5,CAMERA_SIZE,object_collisions['gates'][0])
        
        if level_transition is not None:
            camera.blit(level_transition.draw(), (0,0))
            
            if level_transition.end:
                if level_transition.transition_type == 'FADE-IN':
                    if level_transition.next_level.level == '1-4':
                        REUNION_CUTSCENE()
                        hp, sp, inv, fairy, ftimer = player.health, player.special, player.inventory, player.fairy, player.item_timer
                        player.restart()
                        player.health, player.special, player.inventory, player.fairy, player.item_timer = hp, sp, inv, fairy, ftimer
                        back_layer0 = None
                        title_card = TitleCard('Defeat the Boss!')
                        full_transition = Transition('FADE-OUT',(255,255,255),255,3,CAMERA_SIZE)
                        level_transition = None
                    else:
                        player.x_state = 'TRANSITION_OUT'
                        player.set_animation('walk-out',0,'LOOP')
                        level_transition = Transition('FADE-OUT',(0,0,0),255,5,CAMERA_SIZE)

                elif level_transition.transition_type == 'FADE-OUT':
                    level_transition = None
        
        if (item_select != -1 or draw_hud) and title_card.end and player.x_state != 'SPECIAL':
            HUD.draw_player_hud(player)
            HUD.draw_inventory(item_select)
            if item_select == -1:
                HUD.draw_enemy_hud(hud_target)
        
        if pause_select != -1:
            pause_screen = pygame.Surface(CAMERA_SIZE)
            pause_screen.fill((0,0,0))
            pause_screen.set_alpha(155)
            pause_surf = pygame.Surface(CAMERA_SIZE)
            pause_surf.set_colorkey((0,0,0))
            y_offset = CAMERA_SIZE[1] / 2
            for i in range(len(pause_options)):
                font_color = (255, 255, 255) if pause_select == i else (60, 60, 60)
                shadow_color = (100, 100, 100) if pause_select == i else  (40, 40, 40)
                # shadow
                pause_surf.blit(plain_font.draw(pause_options[i], shadow_color), ((CAMERA_SIZE[0] / 2) - (plain_font.get_width(pause_options[i]) / 2) +1, y_offset))
                pause_surf.blit(plain_font.draw(pause_options[i], shadow_color), ((CAMERA_SIZE[0] / 2) - (plain_font.get_width(pause_options[i]) / 2) +1, y_offset +1))
                # text
                pause_surf.blit(plain_font.draw(pause_options[i], font_color), ((CAMERA_SIZE[0] / 2) - (plain_font.get_width(pause_options[i]) / 2), y_offset))

                y_offset += 10

            camera.blit(pause_screen,(0,0))
            camera.blit(pause_surf,(0,0))
        
        if full_transition is not None:
            camera.blit(full_transition.draw(), (0,0))
            if full_transition.end:
                if full_transition.transition_type == 'FADE-IN':
                    if player.x_state == 'SPECIAL':
                        SPECIAL_MOVE()
                        player.x_state = 'IDLE'
                        special_transition = None
                        full_transition = None
                        
                        for enemy in obj_list['enemies']:
                            damage = 4 if player.item_timer > 0 else 2 
                            enemy.hit(damage, player.flip) # should only run once per rendered enemy
                        
                    elif pause_select == 1:
                        OPTIONS_SCREEN()
                        full_transition = Transition('FADE-OUT',(0,0,0),255,3,CAMERA_SIZE)
                        pause_select = 0
                    elif pause_select == 2:
                        Run = False
                else:
                    full_transition = None
                
        
        main_display.blit(pygame.transform.scale(camera, e.WINDOW_SIZE), ((main_display.get_width()/2)-(e.WINDOW_SIZE[0]/2), (main_display.get_height()/2)-(e.WINDOW_SIZE[1]/2)))
        pygame.display.update()
        e.clock.tick(FPS)

    return False


if __name__ == "__main__":
    #HOW_TO_PLAY()
    START_SCREEN()
    #GAME_LOOP()

