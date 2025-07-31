import pygame
import random
import math
import time
import threading

pygame.init()
pygame.font.init()
#screen and title here
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Ahoy World")

#bg init? is there a better way
bg = pygame.image.load("imgs/map2.png")
bgScaleFactor = 2.5
bgScaleX = bg.get_width() * bgScaleFactor
bgScaleY = bg.get_height() * bgScaleFactor
bg = pygame.transform.scale(bg,(bgScaleX,bgScaleY))

font = pygame.font.SysFont("monospace", 12)
text_color = (255,255,255)


bombSpawnX = 300
bombSpawnY = 0

bomberScale = .35
bomberSpd = 50

class Bomber(pygame.sprite.Sprite):
    def __init__(self, x, y, targX, targY, scaleX, scaleY, spd):
        pygame.sprite.Sprite.__init__(self)
        # img setup and scale
        original_image = pygame.image.load("imgs/sleigh2.png").convert_alpha()
        self.scaleX = int(scaleX * original_image.get_width())
        self.scaleY = int(scaleY * original_image.get_height())
        scaled_image = pygame.transform.scale(original_image, (self.scaleX, self.scaleY))
        
        self.initPos = pygame.Vector2(x, y)
        self.targetPos = pygame.Vector2(targX, targY)
        self.spd = spd
        self.direction = self.targetPos - self.initPos
        if self.direction.length() != 0:
            self.direction = self.direction.normalize()
        else:
            self.direction = pygame.Vector2(1, 0)
        
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
targetX = 205
targetY = 350

class Airbase(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("imgs/airbase.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.scaleX = int(scale * self.image.get_width())
        self.scaleY = int(scale * self.image.get_height())
        self.image = pygame.transform.scale(self.image, (self.scaleX, self.scaleY))

        self.id = "Airbase"

class Interceptor(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, spd, base):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("imgs/hornet2-1.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rect = self.image.get_rect(center=(x, y))  # Use center!

        self.pos = pygame.Vector2(self.rect.center) 
        self.spd = spd

        self.scaleX = int(scale * self.image.get_width())
        self.scaleY = int(scale * self.image.get_height())
        self.image = pygame.transform.scale(self.image, (self.scaleX, self.scaleY))

        self.id = "Interceptor"
        self.homeBase = base

        self.hasATarget = False
        self.shouldRTB = False
        self.hasRotated = False #TODO make camel case probably



#list of all sprites
sprites = pygame.sprite.Group()
hasSetUpHQ = False
hasSetUpAirbases = False



#setup done?? ok, were starting now
running = True
weJustLost = False


def spawnInterceptor(airbase):
    newInterceptor = Interceptor(
                            x = airbase.rect.centerx,
                            y = airbase.rect.centery,
                            scale = 0.5, 
                            spd = 40,
                            base = airbase
                            )
    sprites.add(newInterceptor)
    print("new interceptor at ", clickPos)

def findClosestTarget(interceptor):
    closest_bomber = None
    closest_distance = float('inf')
    for bomber in sprites:
        if bomber.id == "Bomber":
            distance = interceptor.rect.centerx - bomber.rect.centerx
            if abs(distance) < closest_distance:
                closest_distance = abs(distance)
                closest_bomber = bomber
    return closest_bomber

def ReturnToBase(interceptor): # sadly this is called every single frame. Too bad!

    # print("interceptor reached bomber")
    direction = pygame.Vector2(
                                interceptor.homeBase.rect.centerx - interceptor.rect.centerx,
                                interceptor.homeBase.rect.centery - interceptor.rect.centery
                                )
    
    distance = direction.length()
    # print("should rt base active")

    if interceptor.hasRotated == False:
        angle = -90-math.degrees(math.atan2(direction.y, direction.x))
        interceptor.image = pygame.transform.rotate(interceptor.image, 0)
        interceptor.image = pygame.transform.rotate(interceptor.image, angle)
        interceptor.hasRotated = True
        print("rotating to base")
        #TODO fix this stuff!!!!! doesn't work :((
    
    if distance > 2: #not at bomber, move to it
        # print("move to base")
        direction = direction.normalize() 
        move_dist = min(interceptor.spd * dt, distance)  
        interceptor.pos += direction * move_dist
        interceptor.rect.center = int(interceptor.pos.x), int(interceptor.pos.y)
    # rotate interceptor to face bomber only once, when it starts moving toward a bomber
    
    else:
        sprites.remove(interceptor)
        print("interceptor returned to base")

  
def newBomber():
    newBomber = Bomber (
        x = bombSpawnX, 
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


    


while running:
    
    #for time.deltatime
    clock = pygame.time.Clock()
    dt = clock.tick(60) / 1000.0

    #stop condition and actually, every event is handled here
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            #TEMP BOMBER SPAWN
            if event.key == pygame.K_SPACE:
               newBomber()
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
    screen.blit(bg, (0,0))
    
    #BOMBER SPAWNER CODE
    # Use these to control wave spawning
    if not hasattr(pygame, "wave_thread_started"):
        pygame.wave_thread_started = False
        pygame.next_wave_time = time.time()

    def bomber_wave_spawner():
        global waveNumber
        while running and not weJustLost:
            waveNumber += 1
            if not weJustLost:
                for _ in range(waveNumber + random.randint(0, 2)):
                    newBomber()
                    time.sleep(planeDelay)
                time.sleep(waveDelay)
            else:
                break

    # Start the wave spawner thread only once
    if not pygame.wave_thread_started:
        wave_thread = threading.Thread(target=bomber_wave_spawner, daemon=True)
        wave_thread.start()
        pygame.wave_thread_started = True

    #target init
    if not hasSetUpHQ:
        NoradHQ = Target(hp = 3, scale = 1)
        sprites.add(NoradHQ)
        hasSetUpHQ = True
        #oh this is actually really bad... uhh the targetX, Y are about 50 lines up.
    
    if not hasSetUpAirbases:
        #airbase init
        abScale = 0.7
        airbase1 = Airbase(135, 275,abScale)
        airbase2 = Airbase(240, 250,abScale)
        sprites.add(airbase1)
        sprites.add(airbase2)
        hasSetUpAirbases = True

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
                    text_surface = font.render("The last bastion of humanity burns in a nuclear inferno. \n\n Santa is victorious. \n You survived " + str(waveNumber) + " waves.", 0, text_color)
                    weJustLost = True
                    for sprite in sprites:
                        if sprite.id =="Target":
                            sprite.image = pygame.image.load("imgs/bombedcity.png")
    
    #interceptor... intercept
    for interceptor in sprites:
        
        if interceptor.id == "Interceptor":
            
            if not interceptor.hasATarget and len([sprite for sprite in sprites if sprite.id == "Bomber"]) > 0 and not interceptor.shouldRTB:
                closest_bomber = findClosestTarget(interceptor)
                interceptor.hasATarget = True

               
            
            #if we have a closest bomber, move towards it
            if interceptor.hasATarget and not interceptor.shouldRTB:
                direction = pygame.Vector2(closest_bomber.rect.centerx - interceptor.rect.centerx, 
                                           closest_bomber.rect.centery - interceptor.rect.centery
                                           )
                
                distance = direction.length()
                
                if closest_bomber not in sprites:
                    interceptor.hasATarget = False
                    interceptor.hasRotated = False  # Reset rotation state

                    interceptor.shouldRTB = True

                    print("interceptor has no target, RTBing now")




                if distance > 2: #not at bomber, move to it
                    direction = direction.normalize() 
                    move_dist = min(interceptor.spd * dt, distance)  
                    interceptor.pos += direction * move_dist
                    interceptor.rect.center = int(interceptor.pos.x), int(interceptor.pos.y)
                    # rotate interceptor to face bomber only once, when it starts moving toward a bomber
                    
                    
                    if not interceptor.hasRotated:
                        angle = -math.degrees(math.atan2(direction.y, direction.x))
                        interceptor.image = pygame.transform.rotate(interceptor.image, angle)
                        interceptor.hasRotated = True

                    if closest_bomber == None:
                        interceptor.shouldRTB = True
                        #our bombers gone, go home
                        print("interceptor has no target, rtb now")
                
            if interceptor.shouldRTB:
                ReturnToBase(interceptor)

                    
            #check for collisions with bombers
            for bomber in sprites:
                if bomber.id == "Bomber" and interceptor.rect.colliderect(bomber.rect):
                    print("interceptor hit bomber, rtb now")
                    sprites.remove(bomber)
                    interceptor.shouldRTB = True
                    interceptor.hasRotated = False  # Reset rotation state

                    #add some explosion effect here?

    #mousepos
    if not weJustLost:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        text_surface = font.render("Mouse X: " + str(mouse_x) + ", Y: " + str(mouse_y) + ", Wave: " + str(waveNumber), 0, text_color )
    
    
    
    screen.blit(text_surface, (10, 10))
    sprites.draw(screen)
    
    #update everything
    pygame.display.flip()


pygame.quit()