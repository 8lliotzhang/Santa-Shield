import pygame
import math

pygame.init()
pygame.font.init()
#screen and title here
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Ahoy World")

#bg init? is there a better way
bg = pygame.image.load("map2.png")
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
        original_image = pygame.image.load("sleigh2.png").convert_alpha()
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
        # atan2 expects (y, x), and pygame's y-axis is downward
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
        self.image = pygame.image.load("city.png")
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
        self.image = pygame.image.load("airbase.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.scaleX = int(scale * self.image.get_width())
        self.scaleY = int(scale * self.image.get_height())
        self.image = pygame.transform.scale(self.image, (self.scaleX, self.scaleY))

        self.id = "Airbase"

class Interceptor(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, spd):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("hornet2.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.spd = spd

        self.scaleX = int(scale * self.image.get_width())
        self.scaleY = int(scale * self.image.get_height())
        self.image = pygame.transform.scale(self.image, (self.scaleX, self.scaleY))

        self.id = "Interceptor"


#list of all sprites
sprites = pygame.sprite.Group()
hasSetUpHQ = False
hasSetUpAirbases = False
hasABomber = False



#setup done?? ok, were starting now
running = True
weJustLost = False

while running:
    
    #for time.deltatime
    clock = pygame.time.Clock()
    dt = clock.tick(60) / 1000.0

    #stop condition
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            #TEMP BOMBER SPAWN
            if event.key == pygame.K_SPACE:
                newBomber = Bomber(
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
                hasBomber = True
                print("new bomber!!")
        #CLICK CHECK - TEMP INTERCEPTOR SPAWN
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clickPos = pygame.mouse.get_pos()
                print("click at ", clickPos)
                if airbase1.rect.collidepoint(clickPos):
                    print("airbase 1 clicked")
                    #interceptor spawn
                    newInterceptor = Interceptor(
                        x = clickPos[0], 
                        y = clickPos[1], 
                        scale = 0.5, 
                        spd = 100
                        )
                    sprites.add(newInterceptor)
                    print("new interceptor at ", clickPos)
                
                else: 
                    if airbase2.rect.collidepoint(clickPos):
                        print("airbase 2 clicked")
                    #interceptor spawn
                        newInterceptor = Interceptor(
                        x = clickPos[0]+16, 
                        y = clickPos[1]+16, 
                        scale = 0.5, 
                        spd = 100
                        )
                        sprites.add(newInterceptor)
                        print("new interceptor at ", clickPos)
                    else:
                        print("no airbase clicked, no interceptor spawned")
                

                
    
    #here begins the while running step of the code.
    #a black bg
    screen.fill((0,0,0))
    
    #bg image of canada
    screen.blit(bg, (0,0))
    

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
                move_dist = min(bomber.spd * dt, distance)  # assuming 60 FPS
                bomber.initPos += direction * move_dist
                bomber.rect.x, bomber.rect.y = int(bomber.initPos.x), int(bomber.initPos.y)

            else:
                sprites.remove(bomber)
                #killit!!!
                NoradHQ.hp = NoradHQ.hp - 1 
                print("took hit! hp = " + str(NoradHQ.hp))
                if NoradHQ.hp <= 0:
                    print("you dead man!")
                    text_surface = font.render("The last bastion of humanity burns in a nuclear inferno. \n Santa is victorious.", 0, text_color)
                    weJustLost = True
                    for sprite in sprites:
                        if sprite.id =="Target":
                            sprite.image = pygame.image.load("bombedcity.png")
    

    for interceptor in sprites:
        if interceptor.id == "Interceptor":
            #move interceptor
            #mouse_x, mouse_y = pygame.mouse.get_pos()
            #interceptor.rect.x = mouse_x
            #interceptor.rect.y = mouse_y

            #find closest bomber
            closest_bomber = None
            closest_distance = float('inf')
            for bomber in sprites:
                if bomber.id == "Bomber":
                    distance = interceptor.rect.centerx - bomber.rect.centerx
                    if abs(distance) < closest_distance:
                        closest_distance = abs(distance)
                        closest_bomber = bomber
            #if we have a closest bomber, move towards it
            if closest_bomber:
                direction = pygame.Vector2(closest_bomber.rect.centerx - interceptor.rect.centerx, 
                                           closest_bomber.rect.centery - interceptor.rect.centery
                                           )
                
                distance = direction.length()
                
                if distance > 0:
                    direction = direction.normalize()
                    move_dist = min(interceptor.spd * dt, distance)  # assuming 60 FPS
                    interceptor.rect.x += direction.x * move_dist
                    interceptor.rect.y += direction.y * move_dist
                    # rotate interceptor to face bomber only once, when it starts moving toward a bomber
                    if not hasattr(interceptor, 'has_rotated') or not interceptor.has_rotated:
                        angle = -math.degrees(math.atan2(direction.y, direction.x))
                        interceptor.image = pygame.transform.rotate(interceptor.image, angle)
                        interceptor.has_rotated = True
                else:
                    #if the interceptor is at the bomber, remove it
                    print("interceptor reached bomber")

                    #implement return to base here
                    


            
            #check for collisions with bombers
            for bomber in sprites:
                if bomber.id == "Bomber" and interceptor.rect.colliderect(bomber.rect):
                    print("interceptor hit bomber")
                    sprites.remove(bomber)
                    sprites.remove(interceptor)
                    #add some explosion effect here?

    #mousepos
    if not weJustLost:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        text_surface = font.render("Mouse X: " + str(mouse_x) + ", Y: " + str(mouse_y), 0, text_color)
    
    
    
    screen.blit(text_surface, (10, 10))
    sprites.draw(screen)
    
    #update everything
    pygame.display.flip()


pygame.quit()