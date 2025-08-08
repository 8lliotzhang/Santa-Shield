# BY ELLIOT ZHANG
# YOU CAN MODIFY, REDISTRIBUTE, USE, WHATEVER TO MY CODE
# AS LONG AS YOU ARE A PRIVATE INDIVIDUAL AND NOT ACTING AS PART OF ANY CORPORATE, GOVERNMENT, LEGAL, BUSINESS, OR OTHER ENTITY (COLLLECTIVELY "OTHER ENTITIES")
# THIS PROGRAM NOT TO BE USED FOR EVIL OF ANY KIND, MALWARE, PROPAGANDA, OR PROFIT IN EXCESS OF 1000 $CAD A MONTH BY PRIVATE INDIVIDUALS (1 $CAD A YEAR FOR ALL OTHER ENTITIES)

# if you plan on open defiance of the above policy:
#   1) kindly don't
#   2) advertising includes propaganda. Though I'm open to negotiations if you have the money :-)

# if you do manage to make $12000 a year:
#   1) congrats!
#   2) really? you did that with *my* code???
#   3) please send me, as royalties, the percentage of your earnings equal to the percentage of existing code utilized from my program plus one percent, via e-transfer or mailed cheque, in $CAD.

# I ATTEST THAT THIS SOFTWARE PROBABLY DOESN'T HAVE ANY CRITICAL BUGS AND IS NOT INTENTONALLY MALWARE
# STILL THOUGH IT IS PROVIDED AS-IS WITH ALL RISKS, INTENTIONAL OR OTHERWISE SO DON'T SUE ME 
# TODO BUG  


import pygame
import random
import math
import time
import threading

pygame.init()
pygame.font.init()
#screen and title here
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("SANTA SHIELD")


#bg init? is there a better way
#offset
mapX, mapY = (20, 40)

bg = pygame.image.load("imgs/newmap.png")
bgScaleFactor = 2.5
bgScaleX = bg.get_width() * bgScaleFactor
bgScaleY = bg.get_height() * bgScaleFactor
bg = pygame.transform.scale(bg,(bgScaleX,bgScaleY))

bgRect = bg.get_rect()
pygame.draw.rect(bg, (0,255,0), bgRect, 2)

font = pygame.font.SysFont("monospace", 16)
text_color = (255,255,255)

ICON = pygame.image.load("imgs/santashield2.png")
pygame.display.set_icon(ICON)



class Bomber(pygame.sprite.Sprite):
    def __init__(self, x, y, targX, targY, scaleX, scaleY, spd):
        pygame.sprite.Sprite.__init__(self)
        # img setup and scale
        original_image = pygame.image.load("imgs/sleigh3.png").convert_alpha()
        self.scaleX = int(scaleX * original_image.get_width())
        self.scaleY = int(scaleY * original_image.get_height())
        scaled_image = pygame.transform.scale(original_image, (self.scaleX, self.scaleY))
        
        self.initPos = pygame.Vector2(x, y)
        self.targetPos = pygame.Vector2(targX, targY)
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
        angle = -math.degrees(math.atan2(dy, dx))
        self.image = pygame.transform.rotate(scaled_image, angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.targX = targX
        self.targY = targY

        #id for cols
        self.id = "Bomber"

class Target(pygame.sprite.Sprite):
    def __init__(self,hp,scale):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("imgs/city.png")
        self.rect = self.image.get_rect()
        self.rect.x = targetX
        self.rect.y = targetY
        
        self.scaleX = int(scale * self.image.get_width())
        self.scaleY = int(scale * self.image.get_height())
        self.image = pygame.transform.scale(self.image, (self.scaleX, self.scaleY))
        
        self.hp = hp
        self.id = "Target"

#targetX = 305
#targetY = 430
targetX = 250
targetY = 400

class Airbase(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, planeLimit):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("imgs/airbase.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.scaleX = int(scale * self.image.get_width())
        self.scaleY = int(scale * self.image.get_height())
        self.image = pygame.transform.scale(self.image, (self.scaleX, self.scaleY))

        self.id = "Airbase"
        self.planeLimit = planeLimit
        self.planesReady = planeLimit

class Interceptor(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, spd, base, ammo):
        pygame.sprite.Sprite.__init__(self)
        #image and transforming
        self.original_image = pygame.image.load("imgs/hornet2-1.png").convert_alpha()
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

#reset vars
#umm if you add anything that changes in gamestate you will have to reset it here.
def reset_game():
    global waveNumber, planeDelay, waveDelay, hasSetUpHQAndBases, weJustLost, sprites
    global bombSpawnX, bombSpawnY, bomberScale, bomberSpd, targetX, targetY
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
        print(f"new interceptor at {clickPos}. interceptors remaining is {airbase.planesReady}")
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
    newBomber = Bomber (
        x = randomBombX(), 
        y = bombSpawnY, 
        targX = targetX, 
        targY = targetY, 
        scaleX = bomberScale, 
        scaleY = bomberScale, 
        spd = bomberSpd
    )
    sprites.add(newBomber)
    sprites.update()
    print("new bomber!!")

#wave control variables
waveNumber = 0
planeDelay = 1.5  # seconds between planes in a wave
waveDelay = 10 # seconds between waves

global tacPoints 
tacPoints = 0

# we wanna deploy a fighter
def upgradeAirbase(airbase, cost):
    global tacPoints #hey! I wanna modify tacPoints!
    if tacPoints >= cost:
        tacPoints -= cost #(modify)
        airbase.planeLimit += 1
        airbase.planesReady += 1



weJustLost = False


#MAKE SURE ALL INIT IS DONE ABOVE!!
#--------------------
#BEGIN RUN!!!!

running = True
while running:
    
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
               newBomber()
            elif event.key ==pygame.K_q:
                upgradeAirbase(airbase = airbase1,cost=3)
            elif event.key == pygame.K_e:
                upgradeAirbase(airbase = airbase2,cost=3)

        #CLICK CHECK - TEMP INTERCEPTOR SPAWN
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clickPos = pygame.mouse.get_pos()
                print("click at ", clickPos)
                
                if  len([sprite for sprite in sprites if sprite.id == "Bomber"]) > 0: #more than 1 bomber?
                    if airbase1.rect.collidepoint(clickPos):
                        print("airbase 1 clicked")
                        spawnInterceptor(airbase1)            
        
                    elif  airbase2.rect.collidepoint(clickPos):
                            print("airbase 2 clicked")
                            spawnInterceptor(airbase2)
                    else:
                        print("enemy bomber airborne BUT no airbase clicked, no interceptor spawned")
                
                else:
                    print("no enemy bombers airborne, no interceptor spawned")
 
    
    #here begins the while running step of the code.
    #a black bg
    screen.fill((0,0,0))
    
    #bg image of canada
    screen.blit(bg, (mapX,mapY))
    
   

    # Start the wave spawner thread only once
    if not pygame.wave_thread_started:
        wave_thread = threading.Thread(target=bomber_wave_spawner, daemon=True)
        wave_thread.start()
        pygame.wave_thread_started = True

    #target init
    if not hasSetUpHQAndBases:
        NoradHQ = Target(hp = 3, scale = 1)
        sprites.add(NoradHQ)
        
        #oh this is actually really bad... uhh the targetX, Y are about 50 lines up.
    
#airbase init
        abScale = 0.7
        
        airbase1 = Airbase(
            x=150, 
            y=320,
            scale=abScale, 
            planeLimit=2)
        airbase2 = Airbase(
            x=250, 
            y=300,
            scale=abScale,
            planeLimit=2)
        sprites.add(airbase1)
        sprites.add(airbase2)
        hasSetUpHQAndBases = True

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
                sprites.remove(bomber)
                #killit!!!
                NoradHQ.hp = NoradHQ.hp - 1 
                print("took hit! hp = " + str(NoradHQ.hp))
                if NoradHQ.hp <= 0:
                    print("you dead man!")
                    weJustLost = True
                    
                    for sprite in sprites:
                        if sprite.id =="Target":
                            sprite.image = pygame.image.load("imgs/bombedcity.png")
    
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

#TEXT HANDLING
# Usage:
    if weJustLost:
        text_surface = font.render(
            f"you survived {waveNumber} waves. Press any button to restart", True, text_color
            )
        # temp skip
        screen.blit(text_surface, (10, 10))

    else:
    # Display wave count and mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        text_surface = font.render(
            f"WAVE {waveNumber} -- MOUSE AT ({mouse_x},{mouse_y}) -- {tacPoints} TP ", True, text_color
            )
        screen.blit(text_surface, (20, 20))

        #TP_surface = font.render(f"RDY: {}", True, text_color)
        #screen.blit(TP_surface, (10, 40))


#DONT MESS WITH STUFF BELOW 
    #draw all sprites
    sprites.draw(screen)
    
    #update everything
    pygame.display.flip()


pygame.quit()