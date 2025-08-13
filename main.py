import pygame

import random
import math
import time

import threading

import os
import sys

def path(relative):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


pygame.init()
pygame.font.init()
#screen and title here
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SANTA SHIELD")



#UI CONSTS
LIGHT_GREY = (120,120,120)
MID_GREY = (41,41,41)
DARK_GREY = (20,20,20)
GREEN = (0,255,0)
WHITE = (255,255,255)

BORDER_WIDTH = 3

#bg init? is there a better way
#offset
mapX, mapY = (20, 40)

bg = pygame.image.load(path("imgs/newmap2.png"))
bgScaleFactor = 1.25 #umm woops! accidentally scaled down map :( 
bgScaleX = bg.get_width() * bgScaleFactor
bgScaleY = bg.get_height() * bgScaleFactor
bg = pygame.transform.scale(bg,(bgScaleX,bgScaleY))

bgRect = bg.get_rect()
pygame.draw.rect(bg, (MID_GREY), bgRect, BORDER_WIDTH)

font = pygame.font.SysFont("monospace", 16)

#UI DEFINITIONS
UI_RECT_width = 240
UI_RECT_height = 125

uiRect1 = pygame.Rect(540,40,UI_RECT_width,UI_RECT_height)
uiRect2 = pygame.Rect(540,190,UI_RECT_width,UI_RECT_height)
uiRect3 = pygame.Rect(540,340,UI_RECT_width,UI_RECT_height)

scanline_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
scanline_surface.fill((0, 0, 0, 0)) # Start fully transparent

# Draw semi-transparent black lines
for y in range(0, SCREEN_HEIGHT, 2): # Draw a line every 2 pixels
    pygame.draw.line(scanline_surface, (0, 0, 0, 128), (0, y), (SCREEN_WIDTH, y))


#maybe create a uiSurface which can just be blitted instead??


ICON = pygame.image.load(path("imgs/santashield2.png"))
pygame.display.set_icon(ICON)

#reset vars
#umm if you add anything that changes in gamestate you will have to reset it here.
def reset_game():
    global waveNumber, planeDelay, waveDelay, hasSetUpHQAndBases, weJustLost, sprites
    global bombSpawnY, bomberScale, bomberSpd, targetX, targetY
    global tacPoints
    
    # Reset game state variables
    waveNumber = 0
    weJustLost = False
    hasSetUpHQAndBases = False
    tacPoints = 0
    # Clear all sprites
    sprites.empty()
    
    # Reset other game variables to their initial values - not that they gonna be changed...
    #bombSpawnX = 300
    #bombSpawnY = 0
    #bomberScale = 0.35
    #bomberSpd = 50
    #targetX = 205
    #targetY = 350
    # Reset wave timing
    #planeDelay = 1.5
    #waveDelay = 10
    
    # Reset the wave thread flag
    pygame.wave_thread_started = False

#the HQ
class Target(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, hp):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path("imgs/city.png"))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.scaleX = int(scale * self.image.get_width())
        self.scaleY = int(scale * self.image.get_height())
        self.image = pygame.transform.scale(self.image, (self.scaleX, self.scaleY))
        
        self.hp = hp
        self.MAX_HP = hp


        self.id = "Target"

#targetX = 305
#targetY = 430
targetX = 250
targetY = 400
#and the launchers
class Airbase(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, hp, planeLimit):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path("imgs/airbase.png"))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.scaleX = int(scale * self.image.get_width())
        self.scaleY = int(scale * self.image.get_height())
        self.image = pygame.transform.scale(self.image, (self.scaleX, self.scaleY))
        
        self.hp = hp
        self.MAX_HP = hp

        self.id = "Airbase"
        self.planeLimit = planeLimit
        self.planesReady = planeLimit

# we wanna deploy a fighter
def upgradeAirbase(airbase, cost):
    global tacPoints #hey! I wanna modify tacPoints!
    if tacPoints >= cost:
        tacPoints -= cost #(modify)
        airbase.planeLimit += 1
        airbase.planesReady += 1

def repair(facility):
    global tacPoints
    cost = 2
    try:
        if facility.hp < facility.MAX_HP and tacPoints >= cost:
            print("success repair")
            facility.hp += 1
            tacPoints -= cost
        else:
            print("either facility at full health or not enough TP. idk, do better diagnostics")
    except:
        print("uh oh, did you call repair() on a thing without hp??")

class Interceptor(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, spd, base, ammo):
        pygame.sprite.Sprite.__init__(self)
        #image and transforming
        self.original_image = pygame.image.load(path("imgs/hornet2-1.png")).convert_alpha()
        self.scaleX = int(scale * self.original_image.get_width())
        self.scaleY = int(scale * self.original_image.get_height())
        self.original_image = pygame.transform.scale(self.original_image, (self.scaleX, self.scaleY))
        self.image = self.original_image.copy()
        
        #rect, ammo, speed
        self.rect = self.image.get_rect(center=(x, y))
        self.ammo = ammo
        self.pos = pygame.Vector2(self.rect.center) 
        self.spd = spd
        self.id = "Interceptor"
        
        #home and how to get there
        self.homeBase = base
        self.shouldRTB = False
        
        self.angle = 0
        #old targeting
        self.hasATarget = False
        self.targetBomber = None
        self.target_pos = None
        
        #newadd
        self.locked_target = None  # The bomber we're committed to
        self.target_assigned = False  # Flag for target assignment
        #builtin rotation
    
    def rotate_to_target(self, target):
        direction = pygame.Vector2(target[0] - self.rect.centerx, target[1] - self.rect.centery)
        
        if direction.length() > 0.01:
            new_angle = math.degrees(math.atan2(-direction.y, direction.x))
            
            if abs(new_angle-self.angle) > 1:
                self.angle = new_angle
                self.image =  pygame.transform.rotate(self.original_image, self.angle)   
            
                old_center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = old_center     

#set up list of all sprites
sprites = pygame.sprite.Group()
interceptors = pygame.sprite.Group()
hasSetUpHQAndBases = False


#instantiating interceptors 
def spawnInterceptor(airbase):
    if airbase.planesReady > 0:
        newInterceptor = Interceptor(
                                x = airbase.rect.centerx,
                                y = airbase.rect.centery,
                                scale = 0.5, 
                                spd = 40,
                                base = airbase,
                                ammo = 2
                                )
        
        newInterceptor.homeBase.planesReady -= 1
        sprites.add(newInterceptor)
        interceptors.add(newInterceptor)
        # print(f"new interceptor at {clickPos}. interceptors remaining is {airbase.planesReady}")
    else:
        print("every plane sortied!!")

#targeting script for interceptors
def findClosestTarget(interceptor):
    bombers = [s for s in sprites if s.id=="Bomber"]
    if not bombers:
        interceptor.locked_target = None
        interceptor.target_assigned = False
        return
    closest = min(bombers, key=lambda b:math.hypot(b.rect.centerx - interceptor.rect.centerx,
                                         b.rect.centery - interceptor.rect.centery))
    interceptor.locked_target = closest
    interceptor.target_assgined = True
    interceptor.hasATarget = True

#going home, going home
def ReturnToBase(interceptor): # sadly this is called every single frame. Too bad!
    basePos = pygame.Vector2(interceptor.homeBase.rect.center)
    current = pygame.Vector2(interceptor.rect.center)
    direction = basePos - current
    distance = direction.length()
    interceptor.rotate_to_target(basePos)

    direction = basePos - current
    distance = direction.length()
    
    if distance > 3: # not at BASE, move to it

        if direction.length() > 0:
            direction = direction.normalize()     
        
        move_dist = min(interceptor.spd * dt, distance)  
        interceptor.pos += direction * move_dist
        interceptor.rect.center = int(interceptor.pos.x), int(interceptor.pos.y)
    # rotate interceptor to face BASE only once, when it starts moving toward BASE
    else:
        interceptor.homeBase.planesReady += 1
        sprites.remove(interceptor)
        interceptors.remove(interceptor)
        print(f"interceptor returned to base. planes ready at {interceptor.homeBase} is now {interceptor.homeBase.planesReady}")

# managing the enemy!!! 
#targ sel
def targetSelection():
    targets = [s for s in sprites if s.id=="Airbase" or s.id=="Target"]
    # print(targets) - debug check of targarr - works
    try:
        selectedTarget = targets[random.randint(0,len(targets)-1)]
        # thing we aim at
        #create the targetPos vector2 via 
        targetPos = pygame.Vector2(selectedTarget.rect[0], selectedTarget.rect[1])
        print(f"tgt {selectedTarget} @ {targetPos}")
        return selectedTarget, targetPos 
    except:
        print("probably no targs")

class Bomber(pygame.sprite.Sprite):
   

    def __init__(self, x, y, scaleX, scaleY, spd):
        pygame.sprite.Sprite.__init__(self)
        
        # img setup and scale
        original_image = pygame.image.load(path("imgs/sleigh3.png")).convert_alpha()
        self.scaleX = int(scaleX * original_image.get_width())
        self.scaleY = int(scaleY * original_image.get_height())
        scaled_image = pygame.transform.scale(original_image, (self.scaleX, self.scaleY))
        
        self.initPos = pygame.Vector2(x, y)
        #OOOHHHHH BECAUSE WE NEED TO UNIFY THE TWO SUCH THAT THE TARGET FOR HP AND POS ARE THE SAME woops thats kinda embarassing
        self.targSelResponse = targetSelection()
        self.target = self.targSelResponse[0]
        self.targetPos = self.targSelResponse[1]
        self.spd = spd
        #self.direction = self.targetPos - self.initPos
        #if self.direction.length() != 0:
        #    self.direction = self.direction.normalize()
        #else:
        #    self.direction = pygame.Vector2(1, 0)
    
        # Calculate angle from (x, y) to (targX, targY)
        # at*n2 expects (y, x), and pygame's y-axis is downward 
        dx = self.targetPos.x - self.initPos.x
        dy = self.targetPos.y - self.initPos.y
        #angle towards target
        angle = -math.degrees(math.atan2(dy, dx))
        self.image = pygame.transform.rotate(scaled_image, angle)
        self.rect = self.image.get_rect(center=(x, y))
        
        #self.targX = targX
        #self.targY = targY
        #id for cols
        self.id = "Bomber"
    
# BOMBER SPAWNER CODE
# Use these to control wave spawning
if not hasattr(pygame, "wave_thread_started"):
    pygame.wave_thread_started = False
    pygame.next_wave_time = time.time()
def bomber_wave_spawner():
    global waveNumber, tacPoints, weJustLost
    while running and not weJustLost:
        waveNumber += 1
        tacPoints += 1  # Increment tac points for surviving a wave
        if not weJustLost:
            for _ in range(waveNumber + random.randint(0, 2)): 
                # number of bombers is wave + (random int from 0 to 2)
                newBomber()
                time.sleep(planeDelay)
                # delay between each bomber
            time.sleep(waveDelay)
            # between each wave
        else:
            break

#bomber random x pos
def randomBombX():
    center = 150
    range = 150
    result = center + random.randint(-range, range)
    print(result)
    return result

#other bomber consts:
bombSpawnY = 45
bomberScale = .5
bomberSpd = 50 

#create the bomber
def newBomber():
    #try:
        newBomber = Bomber (
            x = randomBombX(), 
            y = bombSpawnY, 
            scaleX = bomberScale, 
            scaleY = bomberScale, 
            spd = bomberSpd
        )
        sprites.add(newBomber)
        sprites.update()
        print("new bomber!!")
    #except:
    #    print("eh, prob no targs")

# END BOMBER STUFF ABOVE
#

#ok, init vars


#wave control variables
waveNumber = 0
planeDelay = 1.5  # seconds between planes in a wave
waveDelay = 10 # seconds between waves
#tacpoints
global tacPoints 
tacPoints = 0
#we did not just lose, were just starting
weJustLost = False


#MAKE SURE ALL INIT IS DONE ABOVE!!
#--------------------
#BEGIN RUN!!!!

def drawLiterallyAllUI():
    pygame.draw.rect(screen, DARK_GREY, uiRect1)
    pygame.draw.rect(screen, MID_GREY, uiRect1, BORDER_WIDTH)    

    pygame.draw.rect(screen, DARK_GREY, uiRect2)
    pygame.draw.rect(screen, MID_GREY, uiRect2, BORDER_WIDTH)  

    pygame.draw.rect(screen, DARK_GREY, uiRect3)
    pygame.draw.rect(screen, MID_GREY, uiRect3, BORDER_WIDTH)    
    
    ab1 = font.render("MCCHORD AFB", True, GREEN)
    ab1P = font.render(f"[q] - PLANES: {airbase1.planesReady}/{airbase1.planeLimit}",True,GREEN)
    ab1Hp = font.render(f"[a] - HP: {airbase1.hp}/{airbase1.MAX_HP}",True,GREEN)
    
    ab2 = font.render("CFB COLD LAKE", True, GREEN)
    ab2P = font.render(f"[e] - PLANES: {airbase2.planesReady}/{airbase2.planeLimit}",True,GREEN)
    ab2Hp = font.render(f"[d] - HP: {airbase2.hp}/{airbase2.MAX_HP}", True, GREEN)

    hq = font.render("NORAD HQ", True, GREEN)
    hqHp = font.render(f"HP: {NoradHQ.hp}/{NoradHQ.MAX_HP}", True, GREEN)

    #texts must blit one by one.
    screen.blit(ab1, (550,50))
    screen.blit(ab1Hp, (550,90))
    screen.blit(ab1P, (550,70))
    screen.blit(ab2,(550,200))
    screen.blit(ab2Hp,(550,240))
    screen.blit(ab2P, (550,220))
    screen.blit(hq, (550, 350))
    screen.blit(hqHp, (550, 370))

running = True
while running:
    #fill screen
    screen.fill((LIGHT_GREY))
    
    #bg image of canada
    screen.blit(bg, (mapX,mapY))
    #
    if not hasSetUpHQAndBases:
            NoradHQ = Target(
                x = 250, 
                y = 400, 
                hp = 5, 
                scale = 1)
            sprites.add(NoradHQ)
            
            #oh this is actually really bad... uhh the targetX, Y are about 50 lines up.
            #airbase init
            abScale = 0.7
            
            airbase1 = Airbase(
                x = 150, 
                y = 320,
                scale = abScale, 
                planeLimit = 2,
                hp = 3
            )
            airbase2 = Airbase(
                x = 250, 
                y = 300,
                scale = abScale,
                planeLimit = 2,
                hp = 3
            )
            sprites.add(airbase1)
            sprites.add(airbase2)
            hasSetUpHQAndBases = True
        
            # Start the wave spawner thread only once
    
    if not pygame.wave_thread_started:
        wave_thread = threading.Thread(target=bomber_wave_spawner, daemon=True)
        wave_thread.start()
        pygame.wave_thread_started = True


    #update all ai always
    drawLiterallyAllUI()

    #for time.deltatime
    clock = pygame.time.Clock()
    dt = clock.tick(60) / 1000.0

    # ALL INPUT HANDLING GOES HERE I GUESS
    #stop condition and actually, every event is handled here
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if weJustLost == True:
                reset_game()
                print("game reset!")
            #TEMP BOMBER SPAWN
            if event.key == pygame.K_SPACE:
               if hasSetUpHQAndBases:
                    newBomber()
            elif event.key ==pygame.K_q:
                upgradeAirbase(airbase = airbase1,cost=3)
            elif event.key == pygame.K_e:
                upgradeAirbase(airbase = airbase2,cost=3)
            #elif event.key == pygame.K_s:
            #    repair(NoradHQ) nope, no repairing hehehehe >:)
            elif event.key==pygame.K_a:
                repair(airbase1)
            elif event.key == pygame.K_d:
                repair(airbase2)

        #CLICK CHECK - TEMP INTERCEPTOR SPAWN
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clickPos = pygame.mouse.get_pos()
                print("click at ", clickPos)
                
                if  len([sprite for sprite in sprites if sprite.id == "Bomber"]) > 0: #more than 1 bomber?
                    if airbase1.rect.collidepoint(clickPos) and airbase1.hp > 0:
                        print("airbase 1 clicked")
                        spawnInterceptor(airbase1)    
                        #hp issue diagnostic
                        print(f"HP: {airbase1.hp}/{airbase1.MAX_HP} --- PLANES: {airbase1.planesReady}/{airbase1.planeLimit}")        
        
                    if  airbase2.rect.collidepoint(clickPos) and airbase2.hp > 0:
                            print("airbase 2 clicked")
                            spawnInterceptor(airbase2)

                            print(f"HP: {airbase2.hp}/{airbase2.MAX_HP} --- PLANES: {airbase2.planesReady}/{airbase2.planeLimit}")        


                    else:
                        print("enemy bomber airborne BUT no airbase clicked, no interceptor spawned")
                
                else:
                    print("no enemy bombers airborne, no interceptor spawned")
  
    #here begins the while running step of the code.
    #a black bg
   #target init
    
#bomber move towards hq
    for bomber in sprites:
        if bomber.id == "Bomber":
            direction = bomber.targetPos - bomber.initPos
            distance = direction.length()
           

            if distance > 0:
                direction = direction.normalize()
                move_dist = min(bomber.spd * dt, distance)
                bomber.initPos += direction * move_dist
                bomber.rect.x, bomber.rect.y = int(bomber.initPos.x), int(bomber.initPos.y)

            else:
                bomber.target.hp -= 1
                print(f"new hp of {bomber.target} is {bomber.target.hp}")
                #killit!!!
                
                #we got a kill
                if bomber.target.hp <= 0: 
                    if bomber.target.id !="Target": #deal with airbases - remove for now
                        #hopefully it wasnt main base right?
                        sprites.remove(bomber.target)
                    else:
                        #oh no!!! It was main base!!!
                        print("you dead man!")
                        weJustLost = True
                        bomber.target.image = pygame.image.load(path("imgs/bombedcity.png"))

                sprites.remove(bomber)
           
#interceptor... everything, why is this all one file, why am i doing this
    for interceptor in interceptors:
        if interceptor.shouldRTB:
            ReturnToBase(interceptor)
            continue
        
        if not interceptor.target_assigned or interceptor.locked_target not in sprites:
            findClosestTarget(interceptor)
       
        if interceptor.locked_target and interceptor.locked_target in sprites:
            target_pos = interceptor.locked_target.rect.center
            direction = pygame.Vector2(target_pos) - interceptor.rect.center
            distance = direction.length()
            
        if distance > 1:
            #angle = math.degrees(math.atan2(-direction.y, direction.x))
            #interceptor.image = pygame.transform.rotate(interceptor.original_image, -angle)
            #interceptor.rect = interceptor.image.get_rect(center=interceptor.rect.center)
            if direction.length() > 0:
                direction = direction.normalize()
                move_angle =  math.degrees(math.atan2(-direction.y, direction.x))
                interceptor.rotate_to_target(target_pos)
                

            
            move_dist = min(interceptor.spd * dt, distance)
            interceptor.rotate_to_target(target_pos)
            interceptor.pos += direction.normalize() * move_dist
            interceptor.rect.center = (interceptor.pos)
    
        if interceptor.ammo <= 0:
            interceptor.shouldRTB = True
        elif not any(s.id=="Bomber" for s in sprites):
            interceptor.shouldRTB = True

    

        # now! handling bomber-interceptor intercepts
        for bomber in [sprite for sprite in sprites if sprite.id == "Bomber"]:
            if interceptor.rect.colliderect(bomber.rect): 
                if interceptor.ammo > 0:
                    interceptor.ammo -= 1
                    print(f"interceptor hit bomber! ammo:  {interceptor.ammo}")
                    sprites.remove(bomber)
                    interceptor.locked_target = None
                    interceptor.target_assigned = False
                else:
                    interceptor.shouldRTB = True

        
        #should be handled already...
        # elif interceptor.ammo <= 0:
        #    interceptor.shouldRTB = True
            # print("interceptor out of ammo, rtb now")

#maybe i can just directly access it by going


        
#TEXT HANDLING
# Usage:
    if weJustLost:
        text_surface = font.render(
            f"You survived {waveNumber} waves. Press any button to play again!", True, WHITE
            )
        # temp skip
        screen.blit(text_surface, (20, 20))

    else:
    # Display wave count and mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        text_surface = font.render(
            f"WAVE {waveNumber} -- MOUSE AT ({mouse_x},{mouse_y}) -- {tacPoints} TP ", True, WHITE
            )
        screen.blit(text_surface, (20, 20))

        #TP_surface = font.render(f"RDY: {}", True, text_color)
        #screen.blit(TP_surface, (10, 40))


#DONT MESS WITH STUFF BELOW 
    #draw all sprites
    sprites.draw(screen)

    screen.blit(scanline_surface, (0,0))

    #update everything
    pygame.display.flip()


pygame.quit()