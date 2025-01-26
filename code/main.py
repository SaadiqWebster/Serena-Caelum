import pygame, math, sys, time
import engine as e
import inputreader as _ir
from engine import *
from objects import *

#### -- command to use pyinstaller
#### C:\users\saadi\appdata\local\packages\pythonsoftwarefoundation.python.3.9_qbz5n2kfra8p0\localcache\local-packages\python39\Scripts\pyinstaller.exe
#### -- full copy-and-paste command
#### C:\users\saadi\appdata\local\packages\pythonsoftwarefoundation.python.3.9_qbz5n2kfra8p0\localcache\local-packages\python39\Scripts\pyinstaller.exe --onefile main.py --noconsole --icon application-icon.ico


MUSIC = True # for debug
input = _ir.InputReader()


def START_SCREEN():
    pygame.mixer.music.load('assets/sounds/music/menu.wav')
    pygame.mixer.music.set_volume(e.settings['Music Volume']/10)
    if MUSIC:
        pygame.mixer.music.play(-1)
    fancy_font = Font('assets/fonts/fancy.png',0)
    background = SkyBackground(e.tilesets_database, CAMERA_SIZE, CHUNK_SIZE)
    transition = Transition('FADE-OUT',WHITE,255,3,CAMERA_SIZE)
    state = 'START'
    select = -1
    instruction = ''
    instr_surf = pygame.Surface(CAMERA_SIZE)
    instr_surf.set_colorkey((0,0,0))
    alpha = 0

    while True:
        e.last_time = time.time()
        #print('FPS:', str(int(e.clock.get_fps())), '\tdt:', dT)
        background.update()
        camera.fill((0,0,0))
        camera.blit(background.draw(),(0,0))
        camera.blit(e.tilesets_database['backgrounds_list']['game_logo'],(0,0))

        instr_surf.fill((0,0,0))

        if state == 'START' or state == 'TRANSITION_TO_SELECT':
            instruction = 'Press Start'
            alpha = (255 / 2) * math.sin(time.time()*2) + (255 / 2) if state == 'START' else alpha-5
            # shadow
            instr_surf.blit(fancy_font.draw(instruction, (62, 131, 209)), ((CAMERA_SIZE[0] / 2) - (fancy_font.get_width(instruction) / 2)+1, (CAMERA_SIZE[1] * (7/10)) - (fancy_font.height / 2)))
            instr_surf.blit(fancy_font.draw(instruction, (62, 131, 209)), ((CAMERA_SIZE[0] / 2) - (fancy_font.get_width(instruction) / 2)+1, (CAMERA_SIZE[1] * (7/10)) - (fancy_font.height / 2)+1))
            # text
            instr_surf.blit(fancy_font.draw(instruction, WHITE), ((CAMERA_SIZE[0] / 2) - (fancy_font.get_width(instruction) / 2), (CAMERA_SIZE[1] * (7/10)) - (fancy_font.height / 2)))
            instr_surf.set_alpha(alpha)

            if state == 'TRANSITION_TO_SELECT' and alpha <= 0:
                state = 'SELECT'

        elif state == 'SELECT' or state == 'TRANSITION_TO_GAME':
            instruction = ['Start Game','Options','Quit Game']
            alpha = min(alpha+5, 255)
            for i in range(len(instruction)):
                font_color = (255, 255, 255) if select == i else (125, 125, 125)
                
                shadow_color = (62, 131, 209) if select == i else (60, 60, 60)
                y_offset = 2 * ((2/math.pi)*math.asin(math.sin(time.time()*math.pi*3))) if select == i else 0
                
                # shadow
                instr_surf.blit(fancy_font.draw(instruction[i], shadow_color), (((CAMERA_SIZE[0] * (i+1)/4)) - (fancy_font.get_width(instruction[i]) / 2) +1, (CAMERA_SIZE[1] * (7/10)) - (fancy_font.height / 2) + y_offset))
                instr_surf.blit(fancy_font.draw(instruction[i], shadow_color), (((CAMERA_SIZE[0] * (i+1)/4)) - (fancy_font.get_width(instruction[i]) / 2) +1, (CAMERA_SIZE[1] * (7/10)) - (fancy_font.height / 2)+1 + y_offset))
                # text
                instr_surf.blit(fancy_font.draw(instruction[i], font_color), (((CAMERA_SIZE[0] * (i+1)/4)) - (fancy_font.get_width(instruction[i]) / 2), (CAMERA_SIZE[1] * (7/10)) - (fancy_font.height / 2) + y_offset))
                instr_surf.set_alpha(alpha)
            
        camera.blit(instr_surf,(0,0))
        
        input.refresh()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            input.read_event(event)

        if input.isbuttonpressed(0) or input.isbuttonpressed(7) or input.iskeypressed('return') or input.iskeypressed('z'):
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

        elif (input.isbuttonpressed(11) or input.isbuttonpressed(13) or input.isbuttonpressed('left stick up') or input.isbuttonpressed('left stick left') or input.iskeypressed('up') or input.iskeypressed('left') or input.iskeypressed('w') or input.iskeypressed('a')) and state == 'SELECT':
            select -= 1
            e.play_sound('cursor')
            if select < 0:
                select = len(instruction)-1
            
        elif (input.isbuttonpressed(12) or input.isbuttonpressed(14) or input.isbuttonpressed('left stick down') or input.isbuttonpressed('left stick right') or input.iskeypressed('down') or input.iskeypressed('right') or input.iskeypressed('s') or input.iskeypressed('d')) and state == 'SELECT':
            select += 1
            e.play_sound('cursor')
            if select >= len(instruction):
                select = 0

        if transition is not None:
            camera.blit(transition.draw(), (0,0))
            if transition.end:
                transition = None

                if state == 'TRANSITION_TO_GAME':
                    game_win = False
                    if select == 0:
                        game_win = GAME_INTRO()
                        pygame.mixer.music.load('assets/sounds/music/menu.wav')
                        pygame.mixer.music.set_volume(e.settings['Music Volume']/10)
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

        scaled_camera_size = [main_display.get_height() * float(e.CAMERA_SIZE[0] / e.CAMERA_SIZE[1]), main_display.get_width() * float(e.CAMERA_SIZE[1] / e.CAMERA_SIZE[0])]
        if main_display.get_width() < scaled_camera_size[0]:
            scaled_camera_size[0] = main_display.get_width()
        else:
            scaled_camera_size[1] = main_display.get_height()
        main_display.blit(pygame.transform.scale(camera, scaled_camera_size), ((main_display.get_width() / 2) - (scaled_camera_size[0] / 2), (main_display.get_height() / 2) - (scaled_camera_size[1] / 2)))
        pygame.display.update()
        e.clock.tick(FPS)       


def OPTIONS_SCREEN():
    fancy_font = Font('assets/fonts/fancy.png',0)
    plain_font = Font('assets/fonts/plain.png')
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
            font_color = (255, 255, 255) if select == i else (100, 100, 100) 
            shadow_color = (100, 100, 100) if select == i else (70, 70, 70)

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

        input.refresh()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            input.read_event(event)
            
        if select != -2:
            if input.isbuttonpressed(11) or input.isbuttonpressed('left stick up') or input.iskeypressed('up') or input.iskeypressed('w'):
                select -= 1
                e.play_sound('cursor')
                if select < -1:
                    select = len(options)-1

            elif input.isbuttonpressed(12) or input.isbuttonpressed('left stick down') or input.iskeypressed('down') or input.iskeypressed('s'):
                select += 1
                e.play_sound('cursor')
                if select >= len(options):
                    select = -1
            
            elif (input.isbuttonpressed(13) or input.isbuttonpressed('left stick left') or input.iskeypressed('left') or input.iskeypressed('a')) and select >= 0:
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

            elif (input.isbuttonpressed(14) or input.isbuttonpressed('left stick right') or input.iskeypressed('right') or input.iskeypressed('d')) and select >= 0:
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
            
            elif (input.isbuttonpressed(1) or input.iskeypressed('x')) and select != -1:
                    e.play_sound('back')
                    select = -1  

            elif (input.isbuttonpressed(0) or input.isbuttonpressed(7) or input.iskeypressed('return') or input.iskeypressed('z')) and select == -1:
                e.play_sound('select')
                select = -2
                transition = Transition('FADE-IN',(0,0,0),0,5,CAMERA_SIZE)
        
        if transition is not None:
            camera.blit(transition.draw(), (0,0))
            if transition.end:
                if transition.transition_type == 'FADE-IN':
                    Run = False
                transition = None

        scaled_camera_size = [main_display.get_height() * float(e.CAMERA_SIZE[0] / e.CAMERA_SIZE[1]), main_display.get_width() * float(e.CAMERA_SIZE[1] / e.CAMERA_SIZE[0])]
        if main_display.get_width() < scaled_camera_size[0]:
            scaled_camera_size[0] = main_display.get_width()
        else:
            scaled_camera_size[1] = main_display.get_height()
        main_display.blit(pygame.transform.scale(camera, scaled_camera_size), ((main_display.get_width() / 2) - (scaled_camera_size[0] / 2), (main_display.get_height() / 2) - (scaled_camera_size[1] / 2)))
        pygame.display.update()
        e.clock.tick(FPS)


def HOW_TO_PLAY():
    transition = Transition('FADE-OUT',BLACK,255,6,CAMERA_SIZE)
    Run = True

    while Run:
        camera.fill((0,0,0))
        camera.blit(e.tilesets_database['backgrounds_list']['tutorial'],(0,0))
        
        input.refresh()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            input.read_event(event)

            if (event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN) and transition is None:
                transition = Transition('FADE-IN',BLACK,0,4,CAMERA_SIZE)

        if transition is not None:
                camera.blit(transition.draw(), (0,0))
                if transition.end:
                    if transition.transition_type == 'FADE-IN':
                        Run = False
                    transition = None

        scaled_camera_size = [main_display.get_height() * float(e.CAMERA_SIZE[0] / e.CAMERA_SIZE[1]), main_display.get_width() * float(e.CAMERA_SIZE[1] / e.CAMERA_SIZE[0])]
        if main_display.get_width() < scaled_camera_size[0]:
            scaled_camera_size[0] = main_display.get_width()
        else:
            scaled_camera_size[1] = main_display.get_height()
        main_display.blit(pygame.transform.scale(camera, scaled_camera_size), ((main_display.get_width() / 2) - (scaled_camera_size[0] / 2), (main_display.get_height() / 2) - (scaled_camera_size[1] / 2)))
        pygame.display.update()
        e.clock.tick(FPS)

    START_SCREEN()


def CREDITS():
    plain_font = Font('assets/fonts/plain.png')
    transition = Transition('FADE-OUT',BLACK,255,6,CAMERA_SIZE)
    display_duration = 180
    black_duration = 30
    timer = 0
    developer = 'Righteous Lions'
    pixelartist = 'Lazer_chef'
    digitalartist = 'Nick Bai Bai'
    Run = True

    while Run:
        camera.fill((0,0,0))
        camera.blit(plain_font.draw('Developed By', (255,255,255)), ((CAMERA_SIZE[0] * 0.1), CAMERA_SIZE[1] * 0.33))
        camera.blit(plain_font.draw(developer, (255,255,255)), ((CAMERA_SIZE[0] - CAMERA_SIZE[0] * 0.1) - (plain_font.get_width(developer)), (CAMERA_SIZE[1] * 0.33)))

        camera.blit(plain_font.draw('Pixel Art By', (255,255,255)), ((CAMERA_SIZE[0] * 0.1), CAMERA_SIZE[1] * 0.48))
        camera.blit(plain_font.draw(pixelartist, (255,255,255)), ((CAMERA_SIZE[0] - CAMERA_SIZE[0] * 0.1) - (plain_font.get_width(pixelartist)), (CAMERA_SIZE[1] * 0.48)))

        camera.blit(plain_font.draw('Digital Art By', (255,255,255)), ((CAMERA_SIZE[0] * 0.1), CAMERA_SIZE[1] * 0.63))
        camera.blit(plain_font.draw(digitalartist, (255,255,255)), ((CAMERA_SIZE[0] - CAMERA_SIZE[0] * 0.1) - (plain_font.get_width(digitalartist)), (CAMERA_SIZE[1] * 0.63)))
        
        if transition.end:
            timer += 1
        
        if timer > display_duration and transition.transition_type == 'FADE-OUT':
            transition = Transition('FADE-IN',BLACK,0,6,CAMERA_SIZE)
        
        if timer > display_duration + black_duration:
            Run = False

        input.refresh()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            input.read_event(event)

            if (event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN) and transition.transition_type == 'FADE-OUT' and transition.end:
                transition = Transition('FADE-IN',BLACK,0,6,CAMERA_SIZE)
                timer = display_duration

        if transition is not None:
                camera.blit(transition.draw(), (0,0))


        scaled_camera_size = [main_display.get_height() * float(e.CAMERA_SIZE[0] / e.CAMERA_SIZE[1]), main_display.get_width() * float(e.CAMERA_SIZE[1] / e.CAMERA_SIZE[0])]
        if main_display.get_width() < scaled_camera_size[0]:
            scaled_camera_size[0] = main_display.get_width()
        else:
            scaled_camera_size[1] = main_display.get_height()
        main_display.blit(pygame.transform.scale(camera, scaled_camera_size), ((main_display.get_width() / 2) - (scaled_camera_size[0] / 2), (main_display.get_height() / 2) - (scaled_camera_size[1] / 2)))
        pygame.display.update()
        e.clock.tick(FPS)


def GAME_INTRO():
    pygame.mixer.music.load('assets/sounds/music/intro.wav')
    pygame.mixer.music.set_volume(e.settings['Music Volume']/10)
    if MUSIC:
        pygame.mixer.music.play(-1)
    scene = 0
    timer = 0
    censor_pos = [0, CAMERA_SIZE[1] / 2]
    y_offset = 0
    timer_duration = 180
    text = ['The sky is shattered','but the sun is still there','so the High Priestess must be safe.',
            'She disappeared last night and told no one.','As her guardian, it\'s my duty to protect her.','I must find her before it\'s too late!',
            'Soleanna!','Even if the sky is falling down','I will find you!']
    fancy_font = Font('assets/fonts/fancy.png',0)
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
                    text_scroll.color = (255,255,0)
                    pygame.mixer.music.fadeout(50)
                
                if scene == 6:
                    text_scroll.color = (255,255,255)
                    timer_duration = 240
                    if MUSIC:
                        pygame.mixer.music.load('assets/sounds/music/level_C.wav')
                        pygame.mixer.music.play(-1)

        elif scene < 8:
            timer += 1
            if timer < 120:
                camera.blit(pygame.transform.scale(e.tilesets_database['backgrounds_list']['intro_'+str(scene-5)], (240,160)),(0,0+(12*(scene-6))))
                censor_pos[0] -= 4 if censor_pos[0] > 0-(CAMERA_SIZE[1]/2)+24 else 0
                censor_pos[1] += 4 if censor_pos[1] < CAMERA_SIZE[1]-24 else 0
                pygame.draw.rect(camera, (0,0,0), pygame.Rect(0,censor_pos[0],CAMERA_SIZE[0],CAMERA_SIZE[1]/2))
                pygame.draw.rect(camera, (0,0,0), pygame.Rect(0,censor_pos[1],CAMERA_SIZE[0],CAMERA_SIZE[1]/2))
            elif timer < timer_duration:
                camera.blit(fancy_font.draw(text[0],(255,255,255)),((CAMERA_SIZE[0]/2)-(fancy_font.get_width(text[0])/2), (CAMERA_SIZE[1]/2)-(fancy_font.height/2)))
            else:
                timer = 0
                censor_pos = [0,CAMERA_SIZE[1]/2]
                y_offset = 288-160
                scene += 1
                text.pop(0)

                if scene == 6:
                    timer_duration = 120
                if scene == 8:
                    censor_pos = [0,CAMERA_SIZE[0]/2]
        
        elif scene == 8:
            img = e.tilesets_database['backgrounds_list']['intro_'+str(scene-5)]
            camera.blit(pygame.transform.scale(img, (192,288)),(24,0-y_offset))
            censor_pos[0] -= 4 if censor_pos[0] > 0-(CAMERA_SIZE[0]/2) else 0
            censor_pos[1] += 4 if censor_pos[1] < CAMERA_SIZE[0] else 0
            pygame.draw.rect(camera, (0,0,0), pygame.Rect(censor_pos[0],0,CAMERA_SIZE[0]/2,CAMERA_SIZE[1]))
            pygame.draw.rect(camera, (0,0,0), pygame.Rect(censor_pos[1],0,CAMERA_SIZE[0]/2,CAMERA_SIZE[1]))
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
            
        input.refresh()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            input.read_event(event)

        if input.iskeypressed('return') or input.isbuttondown(7):
            Run = False
            if scene < 6 and MUSIC:
                pygame.mixer.music.load('assets/sounds/music/level_C.wav')
                pygame.mixer.music.set_volume(e.settings['Music Volume']/10)
                pygame.mixer.music.play(-1)

        scaled_camera_size = [main_display.get_height() * float(e.CAMERA_SIZE[0] / e.CAMERA_SIZE[1]), main_display.get_width() * float(e.CAMERA_SIZE[1] / e.CAMERA_SIZE[0])]
        if main_display.get_width() < scaled_camera_size[0]:
            scaled_camera_size[0] = main_display.get_width()
        else:
            scaled_camera_size[1] = main_display.get_height()
        main_display.blit(pygame.transform.scale(camera, scaled_camera_size), ((main_display.get_width() / 2) - (scaled_camera_size[0] / 2), (main_display.get_height() / 2) - (scaled_camera_size[1] / 2)))
        pygame.display.update()
        e.clock.tick(FPS)
    
    return GAME_LOOP()


def GAME_LOOP():
    full_transition = Transition('FADE-OUT',(255,255,255),255,3,CAMERA_SIZE)
    level_transition = None
    plain_font = Font('assets/fonts/plain.png')
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
    score = {'Total Time':time.time(),'Hits Taken':0,'Enemies Defeated':0,'Items Used':0,'Specials Used':0}
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
                player.set_input(input)
            player.set_velocity()
            floor_collisions, object_collisions = move_and_test(player.rect, player.velocity, tile_rect_list, obj_list)
            if len(player.inventory) >= player.inventory_size:
                object_collisions['items'].clear()
            prev_health = player.health
            player.sound_volume = e.settings['Sound Volume']/10
            player.update(floor_collisions, object_collisions)
            score['Hits Taken'] += prev_health - player.health
            
            if player.health <= 0:
                pygame.mixer.music.stop()
                score['Total Time'] = time.time() - score['Total Time']
                GAME_OVER(player, camera_pos, score)
                return False
            
            if player.x_state == 'SPECIAL' and special_transition is None:
                special_transition = SpecialTransition(player.rect.x+(player.rect.width / 2)-camera_pos[0], CAMERA_SIZE)
                score['Specials Used'] += 1

            enemy_obj_list = {'player':[player]}
            enemy_obj_list['hitboxes'] = player.active_hitbox
            player.active_hitbox = []
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
                obj_list['projectiles'] += enemy.projectile_q
                enemy.projectile_q.clear()

                if enemy.id == 'Lux Furem' and enemy.health <= 0:
                    score['Enemies Defeated'] += 1
                    score['Total Time'] = time.time() - score['Total Time']
                    BOSS_DEFEATED(enemy, player, score)
                    return True
                
                if enemy.DESTROY:
                    if enemy.item_drop is not None:
                        obj_list['items'].append(enemy.item_drop)
                    obj_list['enemies'].remove(enemy)
                    score['Enemies Defeated'] += 1
            
            for projectile in obj_list['projectiles']:
                floor_collisions, proj_object_collisions = move_and_test(projectile.rect, projectile.velocity, tile_rect_list, enemy_obj_list, True)
                
                if proj_object_collisions['hitboxes'] and proj_object_collisions['hitboxes'][0].id == 'guardbox':
                    player.guard()
                    player.increase_special(projectile.damage)

                projectile.update()
                if projectile.DESTROY:
                    obj_list['projectiles'].remove(projectile)


            for item in obj_list['items']:
                item.update()
                if object_collisions['items'] and item is object_collisions['items'][0]:
                    item.destroy()
                if item.DESTROY:
                    obj_list['items'].remove(item)
            

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
        for projectile in obj_list['projectiles']:
            camera.blit(projectile.draw(),(projectile.rect.x-camera_pos[0], projectile.rect.y-camera_pos[1]))
            for particle in projectile.particle_q:
                    camera.blit(particle.draw(), (particle.cor[0]-camera_pos[0], particle.cor[1]-camera_pos[1]))

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
            arrow = e.tilesets_database['hud_list']['arrow']
            mask = pygame.mask.from_surface(arrow)
            mask.invert()
            arrow_shadow = mask.to_surface()
            arrow_shadow.set_colorkey((255,255,255))
            camera.blit(arrow_shadow, (player.rect.x + 4 - camera_pos[0] + 1, y_pos + 1))
            camera.blit(arrow_shadow, (player.rect.x + 4 - camera_pos[0] - 1, y_pos + 1))
            camera.blit(arrow_shadow, (player.rect.x + 4 - camera_pos[0] - 1, y_pos))
            camera.blit(arrow_shadow, (player.rect.x + 4 - camera_pos[0] + 1, y_pos))
            camera.blit(arrow_shadow, (player.rect.x + 4 - camera_pos[0], y_pos - 1))
            camera.blit(arrow_shadow, (player.rect.x + 4 - camera_pos[0], y_pos + 1))
            camera.blit(e.tilesets_database['hud_list']['arrow'], (player.rect.x + 4 - camera_pos[0], y_pos))

        if full_transition is None and not title_card.end:
            camera.blit(title_card.draw(), (0, (CAMERA_SIZE[1]/2)-12))


        # -- INPUT ---
        input.refresh()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            input.read_event(event)
            
        if title_card.end:
            if (input.isbuttonpressed(7) or input.iskeypressed('return')) and not player.input_buffer and full_transition is None and item_select == -1:
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
            elif (input.isbuttonpressed(6) or input.iskeypressed('tab')) and pause_select == -1 and item_select == -1:
                    draw_hud = not draw_hud
            elif (input.isbuttonpressed(3) or input.iskeypressed('c')) and not player.input_buffer and pause_select == -1 and len(player.inventory) > 0:
                if item_select == -1:
                    item_select = 0
                    e.play_sound('item_menu')
                else:
                    item_select = -1
                    e.play_sound('back')

            if item_select > -1:
                if input.isbuttonpressed(13) or input.isbuttonpressed('left stick left') or input.iskeypressed('left') or input.iskeypressed('a'):
                    item_select -= 1
                    if len(player.inventory) != 1:
                        e.play_sound('cursor')
                    if item_select < 0:
                        item_select = len(player.inventory)-1
                if input.isbuttonpressed(14) or input.isbuttonpressed('left stick right') or input.iskeypressed('right') or input.iskeypressed('d'):
                    item_select += 1
                    if len(player.inventory) != 1:
                        e.play_sound('cursor')
                    if item_select >= len(player.inventory):
                        item_select = 0
                if input.isbuttonpressed(0) or input.iskeypressed('z'):
                    if player.inventory[item_select].id < 2 or (player.inventory[item_select].id == 2 and player.special < 10) or (player.inventory[item_select].id < 5 and player.special >= 20):
                        e.play_sound('select')
                    player.use_item(player.inventory[item_select].id)
                    player.inventory.pop(item_select)
                    score['Items Used'] += 1
                    item_select = -1
                if input.isbuttonpressed(1) or input.iskeypressed('x'):
                    item_select = -1
                    e.play_sound('back')

            elif pause_select != -1 and full_transition is None:
                if input.isbuttonpressed(11) or input.isbuttonpressed('left stick up') or input.iskeypressed('up') or input.iskeypressed('w'):
                    pause_select = pause_select - 1 if pause_select > 0 else len(pause_options)-1
                    e.play_sound('cursor')
                if input.isbuttonpressed(12) or input.isbuttonpressed('left stick down') or input.iskeypressed('down') or input.iskeypressed('s'):
                    pause_select = pause_select + 1 if pause_select < len(pause_options)-1 else 0
                    e.play_sound('cursor')
                if input.isbuttonpressed(0) or input.iskeypressed('z'):
                    if pause_select != 0:
                        e.play_sound('select')
                        full_transition = Transition('FADE-IN',(0,0,0),0,4,CAMERA_SIZE)
                        if pause_select == 2:
                            pygame.mixer.music.fadeout(1000)
                    else:
                        pause_select = -1
                        e.sounds_database['pause'].stop()
                        e.play_sound('back')
                if input.iskeypressed('x'):
                        pause_select = -1
                        e.sounds_database['pause'].stop()
                        e.play_sound('back')
            
            elif not player.input_buffer and pause_select == -1 and item_select == -1:
                player.read_pressed_input(input.key_pressed, input.button_pressed)


        # -- DRAW TRANSITIONS, HUD, PAUSE SCREEN ---
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
                        player.fairy.cor = [player.rect.x-12, player.rect.y+8]
                        back_layer0 = BossBackground(e.tilesets_database, CAMERA_SIZE, CHUNK_SIZE, COLORSET, GREYSCALE)
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
                
        scaled_camera_size = [main_display.get_height() * float(e.CAMERA_SIZE[0] / e.CAMERA_SIZE[1]), main_display.get_width() * float(e.CAMERA_SIZE[1] / e.CAMERA_SIZE[0])]
        if main_display.get_width() < scaled_camera_size[0]:
            scaled_camera_size[0] = main_display.get_width()
        else:
            scaled_camera_size[1] = main_display.get_height()
        main_display.blit(pygame.transform.scale(camera, scaled_camera_size), ((main_display.get_width() / 2) - (scaled_camera_size[0] / 2), (main_display.get_height() / 2) - (scaled_camera_size[1] / 2)))
        pygame.display.update()
        e.clock.tick(FPS)

    return False


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
    
        scaled_camera_size = [main_display.get_height() * float(e.CAMERA_SIZE[0] / e.CAMERA_SIZE[1]), main_display.get_width() * float(e.CAMERA_SIZE[1] / e.CAMERA_SIZE[0])]
        if main_display.get_width() < scaled_camera_size[0]:
            scaled_camera_size[0] = main_display.get_width()
        else:
            scaled_camera_size[1] = main_display.get_height()
        main_display.blit(pygame.transform.scale(camera, scaled_camera_size), ((main_display.get_width() / 2) - (scaled_camera_size[0] / 2), (main_display.get_height() / 2) - (scaled_camera_size[1] / 2)))
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
            RESULTS_SCREEN((0,0,0), (255,255,255), (0, 0, 0), 'Try Again...', score)
            Run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        scaled_camera_size = [main_display.get_height() * float(e.CAMERA_SIZE[0] / e.CAMERA_SIZE[1]), main_display.get_width() * float(e.CAMERA_SIZE[1] / e.CAMERA_SIZE[0])]
        if main_display.get_width() < scaled_camera_size[0]:
            scaled_camera_size[0] = main_display.get_width()
        else:
            scaled_camera_size[1] = main_display.get_height()
        main_display.blit(pygame.transform.scale(camera, scaled_camera_size), ((main_display.get_width() / 2) - (scaled_camera_size[0] / 2), (main_display.get_height() / 2) - (scaled_camera_size[1] / 2)))
        pygame.display.update()
        e.clock.tick(FPS)


def REUNION_CUTSCENE():
    pygame.mixer.music.fadeout(1000)
    pygame.mixer.music.load('assets/sounds/music/reunion_A.wav')
    priestess_anim = []
    priestess_frame = 0
    priestess_pos = [160, 96]
    priestess_destination = [96, 48]
    priestess_speed = 0.4
    circle_radius = 0
    circle_max_radius = 28
    circle_thickness = 1
    circle_speed = 0.8
    circle_color = (255, 249, 130)
    circle_pause_duration = 60
    circle_timer = circle_pause_duration
    boss_anim = enemy_animation_database['Lux Furem']['idle']
    boss_frame = 0
    boss_pos = [80, -64]
    boss_destination = [80, 31]
    boss_speed = 0.25
    player_anim = player.animation_database['idle']
    player_frame = 0
    player_pos = [32, 96]
    scene = 0
    timer = 0
    text_p1 = ['C:Soleanna!','S:...Caelum?']
    text_p2 = ['C:I\'ve been worried about you all|this time. You really scared me.', 'S:I\'m so sorry Caelum, but it was|important for us to be alone.',
                'S:So I chose to hide myself in the|one place only you and I know.','C:The sky is shattered. The animals|have gone mad.','C:What is going on?',
                'S:The sky barrier was completely|blown apart through the power of a','S:single spell.','S:It was cast by a wizard who has|been living within the darkness of the','S:other side.','S:It calls itself Lux Furem.',
                'C:Why run away from the city? It\'s|walls could\'ve protected you.','C:...I was there. I would have|protected you. Do you doubt my strength?',
                'S:Lux Furem has been following me|since the shattering.','S:Staying in the city puts everyone|in danger.','S:I had to get away quickly and|quietly.','S:But you found me Caelum... and|I\'m so happy you did.',
                'C:It\'s really been following you?|What does it want from you?','S:As High Priestess of the Sun, it|is my responsibility to keep the sun bright.','S:It means to halt my duty to|keep the barrier open for more creatures.',
                'C:More of them?! This cannot come|true!','C:I will stop it right here, right now!|Where is it hiding?','S:It sits within the shadows of|the trees surrounding us.','S:If I perform the rite again it will|surely come back to stop me.',
                'S:My guardian. I will ask for you|to once again fight for me.','C:For you and only you, I will do all|this and more, as I always have and','C:always will.','S:Caelum... let\'s finally end this|together. I will call it here.','C:Bring it on!']
    fancy_font = Font('assets/fonts/fancy.png',0)
    dialog_box = DialogBox(text_p1,fancy_font,3)
    dim_light_transition = Transition('FADE-IN',(0,0,0),0,5,CAMERA_SIZE)
    transition = Transition('FADE-IN',(255,255,255),0,3,CAMERA_SIZE)
    transition_pause_duration = 120
    transition_pause_timer = 0
    camera_fill_color = (0,0,0)
    sfx_1_played = False
    sfx_2_played = False
    sfx_3_played = False
    Run = True

    while Run:
        camera.fill(camera_fill_color)

        if scene == 0:
            timer += 1
            if timer == 5:
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
                    transition = Transition('FADE-OUT',(255,255,255),255,2,CAMERA_SIZE)
                    if MUSIC:
                        pygame.mixer.music.play(-1)
        
        elif scene == 2:
            player_frame = (player_frame + 1) % len(player_anim)
            # priestess_frame = (priestess_frame + 1) % len(priestess_anim)

            camera.blit(e.tilesets_database['backgrounds_list']['cutscene_back'], (0,0))
            for i in range(15):
                camera.blit(e.tilesets_database['tiles_list']['carpet'],(i*16, CHUNK_SIZE[1]-16))
            camera.blit(player.animation_frames_database[player_anim[player_frame]], player_pos)
            #camera.blit(player.animation_frames_database[player_anim[player_frame]], priestess_pos)
            camera.blit(transition.draw(), (0,0))

            if transition.end:
                camera.blit(dialog_box.draw(), (0,0))
                dialog_box.update()
                if dialog_box.end:
                    scene += 1
                    pygame.mixer.music.fadeout(1000)
                    transition = None
        
        elif scene == 3:
            player_frame = (player_frame + 1) % len(player_anim)
            # priestess_frame = (priestess_frame + 1) % len(priestess_anim)

            camera.blit(e.tilesets_database['backgrounds_list']['cutscene_back'], (0,0))
            for i in range(15):
                camera.blit(e.tilesets_database['tiles_list']['carpet'],(i*16, CHUNK_SIZE[1]-16))
            camera.blit(player.animation_frames_database[player_anim[player_frame]], player_pos)
            camera.blit(dim_light_transition.draw(), (0,0))
            pygame.draw.circle(camera, circle_color, (priestess_pos[0] + 24, priestess_pos[1] + 32), circle_radius, circle_thickness)
            #camera.blit(player.animation_frames_database[player_anim[player_frame]], priestess_pos)

            if dim_light_transition.end:
                circle_timer += 1
                if circle_timer > circle_pause_duration:
                    circle_radius += circle_speed

                    if circle_color == (255, 249, 130) and not sfx_1_played:
                        play_sound('small_glow')
                        sfx_1_played = True  
                    elif circle_color == (255,255,255) and not sfx_2_played:
                        play_sound('big_glow')
                        sfx_2_played = True

                    if circle_radius > circle_max_radius:
                        circle_radius = 0
                        circle_timer = 0
                        sfx_1_played = False
            
                    if transition is not None:
                        camera.blit(transition.draw(), (0,0))      

                vector = [(priestess_destination[0] - priestess_pos[0]), (priestess_destination[1] - priestess_pos[1])]
                magnitude = math.sqrt(vector[0]**2 + vector[1]**2)
                vector = [x / magnitude if x != 0 else 0 for x in vector]
                priestess_pos[0] = max(priestess_pos[0] + vector[0] * priestess_speed, priestess_destination[0])
                priestess_pos[1] = max(priestess_pos[1] + vector[1] * priestess_speed, priestess_destination[1])
                
                if priestess_pos == priestess_destination and transition is None:
                    transition_pause_timer += 1
                    if transition_pause_timer > transition_pause_duration:
                        transition = Transition('FADE-IN',(255,255,255),0,3,CAMERA_SIZE)
                        transition_pause_duration = 120
                        transition_pause_timer = 0
                        circle_radius = 0
                        circle_max_radius = 1000
                        circle_thickness = 0
                        circle_speed = 1
                        circle_color = (255, 255, 255)
                        circle_pause_duration = 120
                        circle_timer = 0

            if transition is not None and transition.end:
                transition_pause_timer += 1

                if not sfx_3_played:
                    play_sound('boss_appear')
                    sfx_3_played = True 

            if transition_pause_timer > transition_pause_duration:
                camera_fill_color = (255, 255, 255)
                player_pos = [96, 96]
                transition = Transition('FADE-OUT',(255,255,255),255,3,CAMERA_SIZE)
                transition_pause_duration = 30
                transition_pause_timer = 0
                # loading the music is causing slowness, might fix itself when the priestess is implemented
                pygame.mixer.music.load('assets/sounds/music/boss_A.wav')
                pygame.mixer.music.set_volume(e.settings['Music Volume']/10)
                if MUSIC:
                        pygame.mixer.music.play(-1)
                scene += 1

        elif scene == 4:
            boss_pos[1] = min(boss_pos[1] + boss_speed, boss_destination[1])
            if boss_pos[1] >= boss_destination[1] - 16 and transition.transition_type == 'FADE-OUT':
                transition = Transition('FADE-IN',(255,255,255),0,6,CAMERA_SIZE)

            player_frame = (player_frame + 1) % len(player_anim)
            boss_frame = (boss_frame + 1) % len(boss_anim)

            objects_surf = pygame.Surface(CAMERA_SIZE)
            objects_surf.fill((0,255,0))
            objects_surf.set_colorkey((0,255,0))
            objects_surf.blit(player.animation_frames_database[player_anim[player_frame]], player_pos)
            objects_surf.blit(boss_anim[boss_frame], boss_pos)
            mask = pygame.mask.from_surface(objects_surf)
            mask_surf = pygame.Surface(CAMERA_SIZE)
            mask_surf.set_colorkey((0,255,0))
            mask_surf.blit(mask.to_surface(unsetcolor=(0,255,0),setcolor=(0,0,0)), (0,0))
            
            camera.blit(mask_surf, (0,0))
            camera.blit(transition.draw(), (0,0))

            if transition.end and transition.transition_type == 'FADE-IN':
                transition_pause_timer += 1 
            
            if transition_pause_timer > transition_pause_duration:
                Run = False
        
        input.refresh()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            input.read_event(event)
                
            if (scene == 1 or scene == 2) and transition.transition_alpha <= 0 and (input.iskeypressed('return') or input.isbuttonpressed(7)):
                dialog_box.end = True
            elif (scene == 1 or scene == 2) and transition.transition_alpha <= 0 and (event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN):
                dialog_box.next_line()

        scaled_camera_size = [main_display.get_height() * float(e.CAMERA_SIZE[0] / e.CAMERA_SIZE[1]), main_display.get_width() * float(e.CAMERA_SIZE[1] / e.CAMERA_SIZE[0])]
        if main_display.get_width() < scaled_camera_size[0]:
            scaled_camera_size[0] = main_display.get_width()
        else:
            scaled_camera_size[1] = main_display.get_height()
        main_display.blit(pygame.transform.scale(camera, scaled_camera_size), ((main_display.get_width() / 2) - (scaled_camera_size[0] / 2), (main_display.get_height() / 2) - (scaled_camera_size[1] / 2)))
        pygame.display.update()
        e.clock.tick(FPS)


def BOSS_DEFEATED(enemy, player, score):
    pygame.mixer.music.fadeout(2000)
    background = BossBackground(e.tilesets_database, CAMERA_SIZE, CHUNK_SIZE, COLORSET, GREYSCALE)
    background_fade = Transition('FADE-IN',(255,255,255),0,5,CAMERA_SIZE)
    fullscreen_fade = Transition('FADE-OUT',(255,255,255),255,3,CAMERA_SIZE)
    player.restart()
    enemy.set_animation('death',0,'LOOP')
    enemy.white_shading = 0
    player_pos = [6*16, 6*16]
    enemy_warp_pos = [[5*16, 2*16-4], [1*16, 0*16-4], [9*16, 0*16-4]]
    current_enemy_pos = 0
    rumble_offset = [0,0]
    rumble_intensity = 2
    rumble_speed = 4
    rumble_timer = 0
    rumble_duration = 720
    explosion_animation = enemy.animation_database['explosion']
    explosion_q = []
    explosion_pos_q = []
    explosion_duration = 120
    explosion_intensity = 16
    explosion_speed = 45
    explosion_timer = 0
    silhouette_alpha = 0
    silhouette_speed = background_fade.transition_speed
    earthquake_sfx_duration = 60
    earthquake_timer = 0
    play_sound('earthquake2')
    scene_timer = 0
    Run = True

    while Run:
        # UPDATE
        camera.fill((0,0,0))
        background.update()
        player.update_timer_events()
        enemy.update_timer_events()

        scene_timer += 1

        if scene_timer == 300 or scene_timer == 300 + 120 or scene_timer == 300 + 240:
            enemy.set_animation('warp_out',0,'ONCE')
            enemy.play_sound('warp')

        if scene_timer < rumble_duration - (180 - 70) and enemy.current_animation == 'death':
            rumble_timer += 1
            if rumble_timer >= rumble_speed:
                rumble_timer = 0
                rumble_offset = [random.randint(-rumble_intensity, rumble_intensity), random.randint(-rumble_intensity, rumble_intensity)]
        else:
            rumble_offset = [0, 0]

        if scene_timer < rumble_duration - (180 - 12):
            earthquake_timer += 1
            if earthquake_timer > earthquake_sfx_duration:
                play_sound('earthquake2')
                earthquake_timer = 0

        if (scene_timer < rumble_duration - 180 or scene_timer > rumble_duration) and enemy.current_animation == 'death':
            explosion_timer += 1
            if explosion_timer > explosion_speed:
                explosion_q.append(0)
                explosion_pos_q.append([enemy_warp_pos[current_enemy_pos][0] + 8 + random.randint(-explosion_intensity, explosion_intensity), enemy_warp_pos[current_enemy_pos][1] + 8 + random.randint(-explosion_intensity, explosion_intensity)])
                enemy.play_sound('explosion')
                explosion_timer = 0
                
        if scene_timer == rumble_duration:
            pygame.mixer.music.load('assets/sounds/music/credits.wav')
            pygame.mixer.music.set_volume(e.settings['Music Volume']/10)
            if MUSIC:
                pygame.mixer.music.play()
            explosion_speed = 10
            explosion_timer = explosion_speed
            explosion_intensity = 32
            enemy.play_sound('boss_scream')
        
        if scene_timer > rumble_duration:
            silhouette_alpha = min(silhouette_alpha+silhouette_speed, 255)

        if scene_timer == rumble_duration + explosion_duration:
            fullscreen_fade = Transition('FADE-IN',(255,255,255),0,1,CAMERA_SIZE)

        if fullscreen_fade.transition_type == 'FADE-IN' and fullscreen_fade.end:
            RESULTS_SCREEN((255,255,255), (80,185,235), (255,255,255), 'Well Done!', score)
            Run = False
        
        if enemy.current_animation == 'warp_in' and enemy.animation_play == 'STOP':
            enemy.set_animation('death',0,'LOOP')
            explosion_speed = 30
            explosion_timer = 30

        if enemy.current_animation == 'warp_out' and enemy.animation_play == 'STOP':
            current_enemy_pos = (current_enemy_pos + 1) % len(enemy_warp_pos)
            enemy.set_animation('warp_in',0,'ONCE')
            enemy.play_sound('warp')

        for i, current_frame in reversed(list(enumerate(explosion_q))):
            explosion_q[i] = current_frame + 1
            if explosion_q[i] >= len(explosion_animation):
                explosion_q.pop(i)
                explosion_pos_q.pop(i)

        # DRAW
        camera.blit(background.draw(), (0,0))
        draw_background_parallax((0,0))
        draw_chunks((0,0), e.current_chunk)
        camera.blit(enemy.draw(), (enemy_warp_pos[current_enemy_pos][0] + rumble_offset[0], enemy_warp_pos[current_enemy_pos][1] + rumble_offset[1]))
        
        if scene_timer > rumble_duration:
            camera.blit(background_fade.draw(), (0,0))

        objects_surf = pygame.Surface(CAMERA_SIZE)
        objects_surf.fill((0,255,0))
        objects_surf.set_colorkey((0,255,0))
        objects_surf.blit(player.draw(), player_pos)
        #objects_surf.blit(enemy.draw(), (enemy_warp_pos[current_enemy_pos][0] + rumble_offset[0], enemy_warp_pos[current_enemy_pos][1] + rumble_offset[1]))
        for i, current_frame in enumerate(explosion_q):
            objects_surf.blit(explosion_animation[current_frame], explosion_pos_q[i])
        camera.blit(objects_surf, (0,0))

        mask = pygame.mask.from_surface(objects_surf)
        mask_surf = pygame.Surface(CAMERA_SIZE)
        mask_surf.set_colorkey((0,255,0))
        mask_surf.blit(mask.to_surface(unsetcolor=(0,255,0),setcolor=(0,0,0)), (0,0))
        mask_surf.set_alpha(silhouette_alpha)
        camera.blit(mask_surf, (0,0))
        
        camera.blit(fullscreen_fade.draw(), (0,0))

        input.refresh()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            input.read_event(event)  

        scaled_camera_size = [main_display.get_height() * float(e.CAMERA_SIZE[0] / e.CAMERA_SIZE[1]), main_display.get_width() * float(e.CAMERA_SIZE[1] / e.CAMERA_SIZE[0])]
        if main_display.get_width() < scaled_camera_size[0]:
            scaled_camera_size[0] = main_display.get_width()
        else:
            scaled_camera_size[1] = main_display.get_height()
        main_display.blit(pygame.transform.scale(camera, scaled_camera_size), ((main_display.get_width() / 2) - (scaled_camera_size[0] / 2), (main_display.get_height() / 2) - (scaled_camera_size[1] / 2)))
        pygame.display.update()
        e.clock.tick(FPS)


def RESULTS_SCREEN(back_color, font_color, shadow_color, header, score):
    plain_font = Font('assets/fonts/plain.png')
    transition = Transition('FADE-IN',back_color,0,4,CAMERA_SIZE)
    results_surf = pygame.Surface(CAMERA_SIZE)
    results_surf.set_colorkey((0,0,0))
    score_stack = {}
    draw_transition = False
    crowd_cheer = True
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
                score_stack[category] += float(0.67) if category == 'Total Time' else 1
                e.play_sound('text')
                break
            elif score_stack[category] > score[category]:
                score_stack[category] = score[category]

            y_offset += plain_font.height + 12

        if len(score_stack) == len(score) and score_stack['Specials Used'] >= score['Specials Used']:
            results_surf.blit(plain_font.draw(header,font_color), ((CAMERA_SIZE[0] / 2)-(plain_font.get_width(header)/2), 25))
            y_offset += plain_font.height
            pointer_img = pygame.mask.from_surface(e.tilesets_database['tiles_list']['pointer'])
            results_surf.blit(pointer_img.to_surface(unsetcolor=(0,0,0),setcolor=font_color), ((CAMERA_SIZE[0]/2)-4 ,y_offset + 2 * ((2/math.pi)*math.asin(math.sin(time.time()*math.pi*3)))))
            if header == 'Well Done!' and crowd_cheer:
                play_sound('cheer')
                crowd_cheer = False

        camera.blit(results_surf,(0,0))

        if draw_transition:
            camera.blit(transition.draw(), (0,0))
        if transition.end:
            Run = False
            
        input.refresh()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            input.read_event(event)

            if (event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN):
                draw_transition = True

                for category in score_stack:
                    if score_stack[category] < score[category]:
                        score_stack[category] = score[category]
                        draw_transition = False

                if draw_transition:
                    pygame.mixer.music.fadeout(1000)

        scaled_camera_size = [main_display.get_height() * float(e.CAMERA_SIZE[0] / e.CAMERA_SIZE[1]), main_display.get_width() * float(e.CAMERA_SIZE[1] / e.CAMERA_SIZE[0])]
        if main_display.get_width() < scaled_camera_size[0]:
            scaled_camera_size[0] = main_display.get_width()
        else:
            scaled_camera_size[1] = main_display.get_height()
        main_display.blit(pygame.transform.scale(camera, scaled_camera_size), ((main_display.get_width() / 2) - (scaled_camera_size[0] / 2), (main_display.get_height() / 2) - (scaled_camera_size[1] / 2)))
        pygame.display.update()
        e.clock.tick(FPS)


if __name__ == "__main__":
    #HOW_TO_PLAY()
    #REUNION_CUTSCENE()
    CREDITS()
    START_SCREEN()
    #GAME_LOOP()

