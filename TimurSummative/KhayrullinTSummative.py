#imports necessary modules
from pygame import *
from sys import *
from math import *
import random
init()

# screen init
backg = ('background.png') 
SIZE = WIDTH, HEIGHT = (1000,700)
screen = display.set_mode(SIZE)
bk = image.load(backg).convert_alpha()
bk = transform.scale(bk, (WIDTH, HEIGHT))

# color init 
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
GREY = (128,128,128)

# font init 
fontCal = font.Font('resources/fonts/Calibri.ttf', 35)
fontGeneral = font.Font('resources/fonts/Calibri.ttf', 30)
fontHealth = font.Font('resources/fonts/Calibri Bold.ttf', 15)
fontTitle = font.Font('resources/fonts/FORCED SQUARE.ttf', 100)


#class that handles everything related to the player
class Player:
    
    
    def __init__(self, mouse_x, mouse_y):
        #directions is a list containing states for moving up, down, left or right
        #speed is thepllayers speed constant (subject to change if upgrades are implemented)
        #x and y are thepllayers technical x and yplosition value, but they do not represent the hitbox. Think of them as theplosition of the top-left corner of the IMAGE for thepllayer.
        #original_image acts as a constant reference to the original image, and is used to avoid distortion
        #image is what changes during theplrogram
        #rect is the box of the IMAGE for thepllayer, it does not represent the hitbox.
        #hitbox w and h are the Height and Width of the hitbox for the player. they are constant.
        #center x and y represent the middle of the box of the IMAGE for thepllayer.
        #hitbox is what the enemy is going to want to hit in order to lower thepllayers' health. it's dimensions are constant, but it moves with thepllayer.
        self.directions = [False, False, False, False] 
        self.x = x
        self.y = y
        self.mouse_x, self.mouse_y = mouse_x, mouse_y
        self.original_image = image.load('resources/player/cannonEnd1.png').convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.hitbox_w = self.rect[2]
        self.hitbox_h = self.rect[3]
        self.center_x, self.center_y = self.x + self.hitbox_w//2, self.y + self.hitbox_h//2
        self.hitbox = (self.center_x - 20, self.center_y - 20, 40, 40)
        self.muzzle_x = int(10 * (self.mouse_x - self.center_x) /
                      (sqrt((self.mouse_x - self.center_x) ** 2 +
                                 (self.mouse_y - self.center_y) ** 2)))
        self.muzzle_y = int(10 * (self.mouse_y - self.center_y) /
                      (sqrt((self.mouse_x - self.center_x) ** 2 +
                                 (self.mouse_y - self.center_y) ** 2)))
        #player stats
        self.gun = 1
        self.speed = 10
        self.max_health = 1000
        self.health = 1000
        self.dmg_upG = 0
        self.firingSpeed_upG = 0
        self.shotSpeed_upG = 0
        self.dmg_mult = 1
    
    #handles player orientation towards the mouse
    def rotate(self, mouseX, mouseY):
        #rel x and y finds the "vector" of the xplosition to the y position
        rel_x, rel_y = mouseX - self.x, mouseY - self.y
        
        angle = (180 / pi) * -atan2(rel_y, rel_x) + 5
        # Rotate the original image without modifying it.
        self.image = transform.rotate(self.original_image, int(angle))
        # Get a new rect with the center of the old rect.
        self.rect = self.image.get_rect(center = self.rect.center)
     
    #handles movement and health of player
    def update(self, mouse_x, mouse_y, enemies, enemyBullets):
        #if any direction states are true, movespllayer in said direction using self.speed
        if self.directions[0]:
            if 0 < self.center_y:
                self.y -= self.speed
        if self.directions[1]:
            if self.center_y < 700:
                self.y += self.speed
        if self.directions[2]:
            if 0 < self.center_x:
                self.x -= self.speed
        if self.directions[3]:
            if self.center_x < 1000:
                self.x += self.speed  
        #update hitBox and muzzle x/y
        self.center_x, self.center_y= self.x + self.hitbox_w//2, self.y + self.hitbox_h//2
        self.hitbox = Rect(self.center_x - 20, self.center_y - 20, 40, 40)
        # updates mouse x and y interpretation
        self.mouse_x, self.mouse_y = mouse_x, mouse_y
        
        # creates a line from the center of the player to the muzzle
        
        denom = (sqrt((self.mouse_x - self.center_x) ** 2 +
                                     (self.mouse_y - self.center_y) ** 2))
        
        if denom != 0:
            self.muzzle_x = self.center_x + int(35 * (self.mouse_x - self.center_x) / denom )
            self.muzzle_y = self.center_y + int(35 * (self.mouse_y - self.center_y) / denom )
        
        #checks if any enemies hit the player
        for e in enemies:
            if self.hitbox.colliderect(e.hitbox):
                self.health -= e.dmg
        
        #check if any enemy bullets hit the player
        for b in enemyBullets:
            if self.hitbox.colliderect(b.rect):
                self.health -= b.dmg
                
        
        
    #Draws player and player health in top-left   
    def draw(self):
        #draws player
        screen.blit(self.image, (self.rect[0] + self.x, self.rect[1] + self.y, self.rect[2], self.rect[3]))
        
        #draws health
        if self.health > 0:
            draw.rect(screen, (255 * (1 - self.health // self.max_health), 255 * self.health // self.max_health, 0), (15, 15, int(500 * self.health / self.max_health), 25))  
            screen.blit(fontHealth.render("%i/%i" %(self.health, self.max_health), 1, (0, 0, 255)), (250 - fontHealth.size("%i/%i" %(self.health, self.max_health))[0] // 2, 20))
            
    #Draws debug info like hitboxes and timers
    def debug(self, firingSpeed):
        #Draws hitbox of Player
        draw.rect(screen,(255,0,0),(self.hitbox),4)
        
        #Draws bullet timer for the current gun (which has marker for when next shot is allowed)
        draw.rect(screen, (255,255,0), (self.x, self.y + self.rect[3] + 27, (time.get_ticks() - startTicks) // 10, 25))
        draw.rect(screen, (255,0,0), (self.x + firingSpeed // 10, self.y + self.rect[3] + 27, 4, 25))
        
        #draws line of fire
        draw.line(screen, (128,128,128), (self.muzzle_x, self.muzzle_y), (self.mouse_x, self.mouse_y), 2)
        

#list of displayable guns
bulletDisplay = [image.load('resources/player/gattling_bullet.png').convert_alpha(), image.load('resources/player/sniper_bullet.png').convert_alpha()]
bullets = []
class Bullet:
    def __init__(self, x, y, target_x, target_y):
        #loads image of bullet
        self.image = image.load('resources/player/sniper_bullet.png').convert_alpha()
        # x is the x position of the bullet        
        self.x = x
        # y is the y position of the bullet
        self.y = y
        # originalx is the original x position of the bullet, 
        self.originalx = x
        # originaly is the original y position of the bullet, 
        self.originaly = y
        # target_x is where the bullet is going to, 
        self.target_x = target_x
        # target_y is the where the bullet is going to, 
        self.target_y = target_y
        # vel is the velocity that the bullet moves at
        self.vel = 20
        # rnge is the range of the bullet, in frames
        self.rnge = 50
        # prog is the progress of the bullet, in frames
        self.prog = 0
        # dmg is the damage that the bullet will do upon impact
        self.dmg = 1 
        self.dmg_mult = 1
        # deathtick is the timer for enemy death
        self.deathTick = 0
        # rect is the hitbox of the bullet
        self.w, self.h = self.image.get_width(), self.image.get_height()
        self.rect = Rect(self.x, self.y, self.w, self.h)

    def update(self):
        # Increases Progress of the bullet
        
        denom = (sqrt((self.target_x - self.originalx) ** 2 +
                                     (self.target_y - self.originaly) ** 2))
        
        if denom != 0:
            self.x += int((self.vel + pl.shotSpeed_upG) * (self.target_x - self.originalx) / denom)
            self.y += int((self.vel + pl.shotSpeed_upG) * (self.target_y - self.originaly) / denom)
     
        self.rect.center = [self.x, self.y]
    
    def check(self, enemies):
        # Checks if the bullet is out of range, then deletes it, if it is
        if self.prog >= self.rnge:
            bullets.remove(self)
        #checks if bullets are out of bounds
        elif not 0 < self.x < WIDTH - self.w or not 0 < self.y < HEIGHT - self.h:
            bullets.remove(self)
            
        else:    
            #checks if bullet hits target hitbox, if so, starts a timer that kills the bullet after 1 frame
            for e in enemies:
                if self.rect.colliderect(e.hitbox):
                    self.deathTick += 1
            
            if bossFight and self.rect.colliderect(bs.rect):
                self.deathTick += 1
            
            if self.deathTick > 1:
                bullets.remove(self)
     
    #draws each bullet      
    def draw(self):
        screen.blit(self.image, self.rect)
        
    #displays current bullet picture in top-left 
    def display(self):
        screen.blit(self.image, Rect(15, 45, self.w * 5, self.h * 5))        
    
    #draws bullet hitboxes
    def debug(self):
        draw.rect(screen, (0,0,0), self.rect, 2)  
        draw.line(screen, (255,255,255), (self.x, self.y), (self.target_x, self.target_y), 4)

class Gattling(Bullet):
    # very fast fire rate, low damage bullet (never used in final version)
    def __init__(self, x, y, target_x, target_y):
        Bullet.__init__(self, x, y, target_x, target_y)
        self.image = image.load('resources/player/gattling_bullet.png').convert_alpha()
        self.hold = True
        self.vel = 20
        self.rnge = 20
        self.dmg = 2     
        self.dmg_mult = 0.5
        self.firing_speed = 1 #ticks before allowed to fire again (1000 ticks in a second)
        self.w, self.h = self.image.get_width(), self.image.get_height()
        self.rect = Rect(self.x, self.y, self.w, self.h)        

class Sniper(Bullet):
    #normal bullet
    def __init__(self, x, y, target_x, target_y):
        Bullet.__init__(self, x, y, target_x, target_y)
        self.image = image.load('resources/player/sniper_bullet.png').convert_alpha()
        self.hold = False
        self.vel = 20
        self.rnge = 50 
        self.dmg = 30
        self.dmg_mult = 1        
        self.firing_speed = 333 #ticks before allowed to fire again (1000 ticks in a second)
        self.w, self.h = self.image.get_width(), self.image.get_height()
        self.rect = Rect(self.x, self.y, self.w, self.h)        


enemyBullets = []
class EnemyBullet(Bullet):
    #these bullets are fired only by enemies
    def __init__(self, x, y, target_x, target_y, damage = 100):
        Bullet.__init__(self, x, y, target_x, target_y)
        self.image = image.load('resources/enemies/enemy_bullet.png').convert_alpha()
        self.w, self.h = self.image.get_width(), self.image.get_height()
        self.rect = Rect(self.x, self.y, self.w, self.h)        
        self.hold = False
        self.vel = 10
        self.rnge = 90
        self.dmg = damage
        
    def check(self, playerHitbox):
        # Checks if the bullet is out of range, then deletes it, if it is
        if self.prog >= self.rnge:
            enemyBullets.remove(self)
        
        elif not 0 < self.x < WIDTH or not 0 < self.y < HEIGHT:
            enemyBullets.remove(self) 
            
        #checks if bullet hits target hitbox, if so, starts a timer that kills the bulle after 1 frame
        elif self.rect.colliderect(playerHitbox):
            self.deathTick += 1

        if self.deathTick > 1:
            enemyBullets.remove(self)    


enemies = []
spawnX = 0
spawnY = 0
class Enemy():
    #basic grunt. Slow, only does contact damage
    def __init__(self, x, y):
        #init for images and hitboxes and such
        self.image = image.load("resources/enemies/Enemy1.png").convert_alpha()
        self.original_img = image.load("resources/enemies/Enemy1.png").convert_alpha()
        self.w = self.image.get_width()
        self.h = self.image.get_height()
        self.x = x
        self.y = y
        self.center_x = self.x + self.w
        self.center_y = self.y + self.h
        self.rect = Rect(self.x, self.y, self.w, self.h)
        self.hitbox_side = int(sqrt(2) * self.w / 2)
        self.hitbox = Rect(self.center_x - self.hitbox_side, self.center_y - self.hitbox_side, self.hitbox_side, self.hitbox_side)        
        
        #init for default enemy properties (changed in each sub-class)
        self.speed = 5
        self.life_span = 120000
        self.age = 0
        self.health = 100
        self.dmg = 10
        self.health_drop_chance = random.random()
        
    def update(self, tox, toy, enemies): 
        #updates target x and y
        self.tox = tox - self.w // 2
        self.toy = toy - self.h // 2 
        
        #checks if colliding with any other enemies other than itself. if so, moves in opposite direction by the speed value
        for e in enemies:
            if self.hitbox.colliderect(e.hitbox) and e != self:
                
                denom = hypot(e.x - self.x, e.y - self.y)
                
                if(denom != 0):
                    self.x -= int(self.speed * (e.x - self.x) / hypot(e.x - self.x, e.y - self.y) )
                    self.y -= int(self.speed * (e.y - self.y) / hypot(e.x - self.x, e.y - self.y) )
                
        #moves towards player
        denom = hypot(self.tox - self.x, self.toy - self.y)
        if denom != 0:
            self.x += int(self.speed * (self.tox - self.x) / denom )
            self.y += int(self.speed * (self.toy - self.y) / denom )
        
        #updates hitboxes and such
        self.rect = Rect(self.x, self.y, self.w, self.h)
        self.center_x = self.x + self.w // 2
        self.center_y = self.y + self.h // 2      
        self.hitbox = Rect(self.center_x - self.hitbox_side // 2, self.center_y - self.hitbox_side // 2, self.hitbox_side, self.hitbox_side)        
        
        #updates age
        self.age += 1
        
        
    
    def check(self, bullets, pickups):  
        #checks if any player bullets hit, if so, deletes some hp
        for b in bullets:
            self.image = self.original_img
            if self.hitbox.colliderect(b.rect):
                self.image = image.load("resources/enemies/EnemyHit.png").convert_alpha()
                self.health -= (b.dmg + pl.dmg_upG) * pl.dmg_mult * b.dmg_mult
        self.image = self.original_img
        
        #checks if enemy should die, if so, kills self and drops heart if it can (15% chance) 
        if self.age >= self.life_span:
            enemies.remove(self)
            
        if self.health <= 0:
            enemies.remove(self)
            if self.health_drop_chance <= .15:
                pickups.append(Heart(self.x, self.y, 200))
    
    #function for drawing the enemy
    def draw(self):
        screen.blit(self.image, self.rect)
        
    #debug draw for enemy hitboxes, and enemy health
    def debug(self, tox, toy):
        draw.rect(screen, (0,0,0), enemy.hitbox, 4) 
        draw.rect(screen, (0,0,255), (enemy.x, enemy.y + enemy.h, int(enemy.health), 25))       
        
        #draws a line between self and target
        draw.line(screen, (128,128,128), (self.center_x, self.center_y), (tox, toy), 2)    
             
   
class Shooter(Enemy):
    #super slow, shoots bullets at slow orig_imgs
    def __init__(self, x, y):
        Enemy.__init__(self, x, y)
        self.image = image.load("resources/enemies/Enemy2.png").convert_alpha()
        self.original_img = image.load("resources/enemies/Enemy2.png").convert_alpha()
        self.speed = 2
        self.life_span = 120000
        self.age = 0
        self.health = 125
        self.dmg = 10
        
        self.firing_speed = 50
        self.fire_time = self.firing_speed // 5 * random.randint(0, 5)
        
class Wolf(Enemy):
    # very fast, does a lot of contact damage but has little health
    def __init__(self, x, y):
        Enemy.__init__(self, x, y)
        self.image = image.load("resources/enemies/Enemy3.png").convert_alpha()
        self.original_img = image.load("resources/enemies/Enemy3.png").convert_alpha()
        self.speed = 10
        self.life_span = 120000
        self.health = 50
        self.dmg = 20
        
class Turret(Enemy):
    # super slow, stops if gets too close to player, shoots in cardinal/diagonal directions
    def __init__(self, x, y):
        Enemy.__init__(self, x, y)
        self.image = image.load("resources/enemies/Enemy4.png").convert_alpha()
        self.original_img = image.load("resources/enemies/Enemy4.png").convert_alpha()
        self.speed = 2
        self.life_span = 120000
        self.health = 200
        self.dmg = 20  
        
        self.firing_speed = 35
        self.fire_time = self.firing_speed // 5 * random.randint(0, 5)     
        self.gun_state = 0
        self.angles_1 = [0, 90, 180, 270]
        self.angles_2 = [45, 135, 225, 315]
        self.TurretTarget = (0,0)
    
    #stops turret from moving if too close
    def update(self, tox, toy, enemies):
        if hypot((self.x - tox), (self.y - toy)) > 400:
            Enemy.update(self, tox, toy, enemies)

class Boss():
    
    def __init__(self):
        #image and position
        self.orig_imgs = [image.load('resources/boss.png').convert_alpha(), image.load('resources/boss2.png').convert_alpha(), image.load('resources/boss3.png').convert_alpha()]
        self.x = 100
        self.y = 50
        self.rect = Rect(self.x, self.y, 800, 100)

        #boss properties init
        self.phase = 0
        self.max_health = 12000
        self.health = self.max_health
        self.vulnerable = True
        ##timers for attack balancing
        self.pause_timer = 120
        #firing time is reset if firing speed is reached
        self.firing_speed = [25, 20, 15]
        self.firing_time = 0
        #grace time is reset if grace time is reached
        self.grace_timers = [120, 90, 65]
        self.grace_time = 180
        #attacks init (similar to pl.directions)
        self.attacks = [False, False, False, False]
        self.directions = 0
        #counter of how much boss moved
        self.frames_spent_moving = 0

        ##vars for gun positions and angles for attack patterns
        self.gun_pos = [(75, 100), (235, 75), (395, 100), (555, 75), (715, 100)]
        self.weakpoint = 2
        self.weakpoint_rect = (self.gun_pos[self.weakpoint][0] + self.x, self.gun_pos[self.weakpoint][1] + self.y , 53, 53)
        self.gun_queue = random.sample(self.gun_pos, len(self.gun_pos))
        #chosen angle and chosen gun 
        self.target_angle = 0
        self.target_gun = (75, 100)
        #angles to shoot at 
        self.angles_double = [85, 95]
        self.angles_triple = [45, 90, 135]
        self.angles_quad = [18, 36, 54, 72]
        self.angles_quint = [15, 30, 45, 60, 75]
        
    def move(self):
        #very similar to pl.directions, moves if it can
        if self.directions == 0:
            if self.y < 100:
                self.y += 3
        elif self.directions == 1:
            if 0 < self.y:
                self.y -= 3
        elif self.directions == 2:
            if 0 < self.x:
                self.x -= 3
        elif self.directions == 3:
            if self.x + 800 < WIDTH:
                self.x += 3   
    
    
    #attack coreography
    def attack1(self):  
        #shoots 5 pellet spread from random gun
        if self.attacks[0]:
            self.target_gun = self.gun_pos[random.randint(0,4)]
            for angle in self.angles_quad:
                #finds point on circle based on angle and radius, fires enemyBullet there
                self.target_angle = (self.target_gun[0]+self.x + 50 * cos(radians(angle + 45)), 
                                          self.target_gun[1]+self.y + 50 * sin(radians(angle + 45)))            
                enemyBullets.append(EnemyBullet(self.target_gun[0]+self.x, self.target_gun[1]+self.y, self.target_angle[0], self.target_angle[1], 15 * self.phase))
            #ends attack
            self.attacks[0] = False
    
    def attack2(self):
        # shoots triple shots in random gun pattern
        if self.attacks[1]:
            for i in range(len(self.gun_queue)):
                #checks if timer conditions are just right
                if self.firing_time == self.firing_speed[self.phase] * i:
                    #sets target gun based on random queue
                    self.target_gun = self.gun_queue[i]
                    for angle in self.angles_triple:
                        #finds point on circle based on angle and radius, fires enemyBullet there
                        self.target_angle = (self.target_gun[0]+self.x + 50 * cos(radians(angle)), 
                                                  self.target_gun[1]+self.y + 50 * sin(radians(angle)))            
                        enemyBullets.append(EnemyBullet(self.target_gun[0]+self.x, self.target_gun[1]+self.y, self.target_angle[0], self.target_angle[1], 15 * self.phase))
                #ends attack
                if self.firing_time == self.firing_speed[self.phase] * len(self.gun_queue):
                    self.attacks[1] = False
                    self.firing_time = 0 
                    break
            else:
                self.firing_time += 1
            
    def attack3(self):
        #shoots stream of bullets from left to right from random guns
        if self.attacks[2]:
            for angle in range(60, 120, -self.phase + 3):
                #checks if timer conditions are just right
                if self.firing_time + 60 == angle:
                    for i in range(2):
                        #chooses random gun (twice)
                        self.target_gun = self.gun_queue[i]
                        #finds point on circle based on angle and radius, fires enemyBullet there
                        self.target_angle = (self.target_gun[0]+self.x + 50 * cos(radians(angle)), 
                                                  self.target_gun[1]+self.y + 50 * sin(radians(angle)))            
                        enemyBullets.append(EnemyBullet(self.target_gun[0]+self.x, self.target_gun[1]+self.y, self.target_angle[0], self.target_angle[1], 15 * self.phase))
                #ends attack
                if self.firing_time + 60 >= 120:
                    self.attacks[2] = False
                    self.firing_time = 0
                    break
            else: self.firing_time += 1
            
    def attack4(self):
        #shoots stream of bullets from left to right
        if self.attacks[3]:
            for angle in range(120, 60, -(-self.phase + 3)):
                #checks if timer conditions are just right
                if self.firing_time + 60 == angle:
                    for i in range(2):
                        #chooses random gun (twice)
                        self.target_gun = self.gun_queue[i]
                        #finds point on circle based on angle and radius, fires enemyBullet there
                        self.target_angle = (self.target_gun[0]+self.x + 50 * cos(radians(180 - angle)), 
                                                  self.target_gun[1]+self.y + 50 * sin(radians(180 -angle)))            
                        enemyBullets.append(EnemyBullet(self.target_gun[0]+self.x, self.target_gun[1]+self.y, self.target_angle[0], self.target_angle[1], 15 * self.phase))
                #ends attack
                if self.firing_time + 60 >= 120:
                    self.attacks[3] = False
                    self.firing_time = 0
                    break
            else: self.firing_time += 1        
    
    #if player is out of range, shoots beam straight at player (to encourage player to stay within borderlines)
    def outOfRangeAttack(self):
        if pl.center_x < self.x - 100:
            enemyBullets.append(EnemyBullet(self.gun_pos[0][0]+self.x, self.gun_pos[0][1]+self.y, pl.center_x, pl.center_y, 15 * self.phase))
        elif pl.center_x > self.x + 800 + 100:
            enemyBullets.append(EnemyBullet(self.gun_pos[4][0]+self.x, self.gun_pos[4][1]+self.y, pl.center_x, pl.center_y, 15 * self.phase))
    
    #draws itself and it's health
    def draw(self):
        screen.blit(self.orig_imgs[self.phase], (self.x, self.y))
        self.rect = Rect(self.x, self.y, 800, 100)
        draw.circle(screen, RED, (self.gun_pos[self.weakpoint][0] +self.x, self.gun_pos[self.weakpoint][1] +self.y), 53)
        draw.rect(screen, (255, 255,0), (15, HEIGHT - 85, int(985 * self.health / self.max_health), 75))
        screen.blit(fontGeneral.render("Boss health: %i/%i" %(self.health, self.max_health), 1, (0, 0, 255)), (467 - fontHealth.size("Boss health: %i/%i" %(self.health, self.max_health))[0] // 2, HEIGHT - 55 - fontHealth.size("Boss health: %i/%i" %(self.health, self.max_health))[1] // 2))
    
    
    def update(self):
        if self.grace_time == 0:
            #handles attack timings with some randomness
            self.attacks[random.randint(0,3)] = True
            self.gun_queue = random.sample(self.gun_pos, len(self.gun_pos))
            self.directions = random.randint(0,3)
            
            #resets movement during attacks
            self.frames_spent_moving = 0
            
            #handles in between attack grace timers
            if self.attacks[0] == True: 
                self.grace_time = self.grace_timers[self.phase] // 8
            else: self.grace_time = self.grace_timers[self.phase]
        else: 
            #handles movement between attacks
            if self.frames_spent_moving <= 30:
                self.move()
                self.frames_spent_moving += 1
            self.grace_time -= 1
        
        #updates weakpoint
        self.weakpoint_rect = (self.gun_pos[self.weakpoint][0] + self.x - 53, self.gun_pos[self.weakpoint][1] + self.y - 53 , 106, 106)
        
        #tries to fire each attack
        self.attack1() # random quad shot
        self.attack2() # random sequence of triple shots
        self.attack3() #chooses 2 random guns to fire from, goes from left to right
        self.attack4() #chooses 2 random guns to fire from, goes from right to left
        self.outOfRangeAttack() #shoots player if player is out of range
    
    #checks itself for health, changes phases after certain point
    def check(self):
        for b in bullets:
            if b.rect.colliderect(self.weakpoint_rect):
                self.health -= b.dmg 
        
        #if health permits, spawns a randomly placed heart 
        if 0 <= self.health%500 <= 10 and self.health != self.max_health:
            pickups.append(Heart(random.randint(300, 700), random.randint(200, 500), random.randint(250, 500)))        
        
        if 0 <= self.health%250 <= 10 and self.health != self.max_health:
            self.weakpoint = random.randint(0, 4)
            self.health -= 11
        
        
        
        # checks if it is supposed to die
        if self.health <= 0:
            global bossFight
            bossFight = False
            global level
            level = 6
            self.health = self.max_health
        #changes phases
        elif self.health <= self.max_health // 3:
            self.phase = 2        
        elif self.health <= self.max_health // 3 * 2:
            self.phase = 1
        
        
class Heart():
    #basic heart pickup
    def __init__(self, x, y, hp):
        #image and position (image scales to hp value)
        self.image = transform.scale(image.load('resources/items/heart.png').convert_alpha(), (int((hp / 1000) * image.load('resources/items/heart.png').get_width() * 2), int((hp / 1000) * image.load('resources/items/heart.png').get_height() * 2)))
        self.x = x
        self.y = y
        self.rect = Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.hp = hp
        self.life_span = 300
        self.health = 0
        
    def update(self, player):
        self.health += 1
        #checks if it's supposed to die, if so, dies.
        if self.health >= self.life_span:
            pickups.remove(self)
        
        #checks if player touched it, if so, grants player health, and keels over (if granted health makes player health go over limit, adds however much it can before the limit is reached)
        if self.rect.colliderect(player.hitbox):
            if player.health < player.max_health:
                for hUp in range(self.hp):
                    player.health += 1
                    if player.health >= player.max_health:
                        break
            else:
                player.health = 1000
            pickups.remove(self)
    
    #draws self
    def draw(self):
        screen.blit(self.image, self.rect)
        

mainMenuRect = []
for y in range(200, 500, 100):
    mainMenuRect.append(Rect(400, y, 200, 75))
    
#function for drawing the main menu
def drawMain(): 
    draw.rect(screen, BLACK, (0,0, WIDTH, HEIGHT))
    screen.blit(fontTitle.render("Ultimate Antivirus",  1,  (0,  255,  0)), (100, 5, fontTitle.size("Ultimate Antivirus")[0], fontTitle.size("Ultimate Antivirus")[1]))
    texts = ["Play game", "Exit game"]
    for i in range(2): #sequentially draws buttons for menu, using text from list above if necessary
        draw.rect(screen, WHITE, mainMenuRect[i])
        text = fontGeneral.render(texts[i],  1,  (0,  0,  0))	
        screen.blit(text, mainMenuRect[i].move(5,5)) 

instructImages = ['resources/instructions/instructions1.png', 'resources/instructions/instructions2.png', 'resources/instructions/instructions4.png', 'resources/instructions/instructions5.png',]
def drawInstructions():
    #displays sequence of text and images to give instructions 
    screen.blit(bk, (0,0))
    display.flip()
    
    texts = ["you are an extremely advanced antivirus", "employed by TimKhay industries,", "made to destroy any incoming viruses directly, in real time."]
    #tells story through center-aligned text
    for text in texts: 
        screen.blit(fontGeneral.render(text, 1, WHITE), (WIDTH // 2 - fontGeneral.size(text)[0] // 2, int(.20 * HEIGHT) + int((fontGeneral.size(text)[1] + 3) * texts.index(text))))
        screen.blit(fontGeneral.render("Press and hold space to skip instructions", 1, WHITE), (WIDTH // 2 - fontGeneral.size("press and hold space to skip instructions")[0] // 2, HEIGHT - fontGeneral.size("press and hold space to skip instructions")[1] - 5))
        display.flip()
        
        #checks if skip is wanted, if so, skips instructions
        event.pump()
        for ticks in range(1750):
            if key.get_pressed()[K_SPACE] != 0:
                    break
            time.wait(1) 
        else:
            continue
    else:
        #cycles through intruction images, showing more elaborate info
        for img in instructImages:
            screen.blit(image.load(img), (0,0))
            screen.blit(fontGeneral.render("Press and hold space to skip instructions", 1, WHITE), (200, HEIGHT - fontGeneral.size("press and hold space to skip instructions")[1] - 5))
            display.flip()
            #checks if skip is wanted, if so, skips instructions
            event.pump()
            for ticks in range(4000):
                if key.get_pressed()[K_SPACE] != 0:
                    break
                time.wait(1)
            else:
                continue
            break
    
    #displays final good luck message
    screen.blit(bk, (0,0))
    fontGeneral.render(text, 1, WHITE)
    text = "Good Luck!"
    screen.blit(fontGeneral.render(text, 1, WHITE), (WIDTH // 2 - fontGeneral.size(text)[0] // 2, int(.20 * HEIGHT) + int((fontGeneral.size(text)[1] + 3))))
    display.flip()
    time.wait(3000)    

returnRect = mainMenuRect[2].move(0, mainMenuRect[2][3] + 25)
def drawLoseScreen():
    #displays simple lose screen with a button to go back to main menu
    draw.rect(screen, BLACK, (0,0, WIDTH, HEIGHT))
    screen.blit(fontTitle.render("You Lost!",  1,  (0,  255,  0)), (100, 5, fontTitle.size("You Lost!")[0], fontTitle.size("You Lost!")[1]))    
    draw.rect(screen, WHITE, returnRect)
    text = fontGeneral.render("Return to",  1,  (0,  0,  0))
    screen.blit(text, returnRect)
    text = fontGeneral.render("Main menu",  1,  (0,  0,  0))
    screen.blit(text, returnRect.move(0, fontGeneral.size("Main menu")[1] + 3))

def drawWinScreen():
    #displays simple win screen with a button to go back to main menu, and some credits
    draw.rect(screen, BLACK, (0,0, WIDTH, HEIGHT))
    screen.blit(fontTitle.render("You're winner!",  1,  (0,  255,  0)), (100, 5, fontTitle.size("You're winner!")[0], fontTitle.size("You're winner!")[1]))  
    screen.blit(fontTitle.render("Made by:",  1,  (0,  255,  0)), (100, fontTitle.size("Made by")[1] * 2 + 5, fontTitle.size("Made by")[0], fontTitle.size("Made by")[1]))  
    screen.blit(fontTitle.render("Timur Khayrullin",  1,  (0,  255,  0)), (100, fontTitle.size("Made by")[1] * 3 + 5, fontTitle.size("Timur Khayrullin")[0], fontTitle.size("Timur Khayrullin")[1]))
    screen.blit(fontTitle.render("2018",  1,  (0,  255,  0)), (100, fontTitle.size("Made by")[1] * 4 + 5, fontTitle.size("2018")[0], fontTitle.size("2018")[1]))
    draw.rect(screen, WHITE, returnRect)
    text = fontGeneral.render("Return to",  1,  (0,  0,  0))
    screen.blit(text, returnRect)
    text = fontGeneral.render("Main menu",  1,  (0,  0,  0))
    screen.blit(text, returnRect.move(0, fontGeneral.size("Main menu")[1] + 3))

#list of rects for upgrade buttons
upgradeRect = []
for y in range(200, 500, 115):
    for x in range(200, 800, 200):
        upgradeRect.append(Rect(x, y, 185, 100))
    
def drawUpgradeScreen():
    #as long as boss level isn't ahead, displays upgrade instructions
    draw.rect(screen, BLACK, (0,0, WIDTH, HEIGHT))
    if level < 5 :
        screen.blit(fontTitle.render("Level Up!",  1,  (0,  255,  0)), (50, 5, fontTitle.size("Level Up! Choose your upgrade")[0], fontTitle.size("Level Up! Choose your upgrade")[1]))  
        screen.blit(fontTitle.render("Choose your upgrade",  1,  (0,  255,  0)), (50, fontTitle.size("Choose your upgrade")[1]+5, fontTitle.size("Choose your upgrade")[0], fontTitle.size("Choose your upgrade")[1]))
    else:
        #shows boss warning
        screen.blit(fontTitle.render("Warning:",  1,  (255,  0,  0)), (50, 5, fontTitle.size("Warning:")[0], fontTitle.size("Warning")[1]))  
        screen.blit(fontTitle.render("Boss Battle Ahead",  1,  (255,  0,  0)), (50, fontTitle.size("Boss Battle Ahead")[1]+5, fontTitle.size("Boss Battle Ahead")[0], fontTitle.size("Boss Battle Ahead")[1]))        
    #for each text, displays corresponding upgrade button with text on it
    texts = ['+ damage', '+ speed', '+ firing speed', 'Restore health', '+ max health', '+ shot speed']
    for i in range(len(texts)):
        draw.rect(screen, WHITE, upgradeRect[i])  
        #draw.rect(screen, RED, rect, 4)
        text = fontGeneral.render(texts[i],  1,  (0,  0,  0))	
        screen.blit(text, upgradeRect[i].move(5,5))

#general var init
clock = time.Clock()
running = True
x = WIDTH // 2 - 50
y = HEIGHT // 2 - 50
button = 0
mx, my = 0,0

#menu state init
menu = 0
MAIN = 0
START = 1
HIGHSCORES = 2
LOSE = 3
WIN = 6
PAUSE = 4
UPGRADE = 5
runMenu = True
game = False

#level var init
level = 1
wave = 0
waitingEnemies = []
pickups = []
enemyWaitTime = 0
enemySpawnTime = 500
enemyChoice = 0
enemyPoints = 0
graceTimer = 0

#used for debugging the game (set to true for cheats)
debug = False          



#list of class names for all bullet types
guns = [Gattling, Sniper]
# list of pngs of all bullets in the game
bulletPics = [image.load('resources/player/gattling_bullet.png').convert_alpha(), image.load('resources/player/sniper_bullet.png').convert_alpha()]
#abreviation for player class
bossFight = False
pl = Player(mx, my)
bs = Boss()
# var init for player bullet timer
startTicks = 0

#main loop
while running:
    
    #menu loop
    while runMenu:
        for evnt in event.get():
            if evnt.type == QUIT:
                quit()
            if evnt.type == MOUSEBUTTONDOWN:
                # checks if any mouse button is down,  if so sets clicking to true
                button = evnt.button
            if evnt.type == MOUSEBUTTONUP:
                # checks if any mouse button is down,  if so sets clicking to true
                button = 0       
            if evnt.type == MOUSEMOTION:
                # sets mx and my to mouse x backgand y if mouse is moving
                mx, my  = evnt.pos 
        if menu == MAIN:
            drawMain()
            if button == 1:
                #starts or exits the game
                if mainMenuRect[0].collidepoint(mx, my):
                    menu = START
                elif mainMenuRect[1].collidepoint(mx, my):                        
                    running = False
                    runMenu = False 
        if menu == START:
            #initializes all game-related vars and starts game
            '''Shows instructions, stops menu'''
            drawInstructions()
            runMenu = False 
            
            '''Resets all variables used for game'''
            #general var init
            x = WIDTH // 2 - 50
            y = HEIGHT // 2 - 50
            button = 0
            mx, my = 0,0
            
            #level var init
            pl.health = 1000
            level = 1
            wave = 0
            pickups = []
            enemies = []
            bullets = []
            enemyBullets = []
            waitingEnemies = []
            enemyWaitTime = 0
            enemySpawnTime = 500
            enemyChoice = 0
            enemyPoints = 0 
            graceTimer = 0
            bossFight = False
            
            '''Starts game loop'''
            game = True
        
        # checks for return to menu button for win and lose screens
        if menu == LOSE:
            drawLoseScreen()
            if button == 1:
                if returnRect.collidepoint((mx, my)):
                    menu = MAIN
        
        if menu == WIN:
            drawLoseScreen()
            if button == 1:
                if returnRect.collidepoint((mx, my)):
                    menu = MAIN        
              
        if menu == UPGRADE:
            
            drawUpgradeScreen()
            if button == 1:
                #if clicked upgrade button, changes appropriate stat and resumes game 
                if upgradeRect[0].collidepoint(mx, my):
                    pl.dmg_upG += 7
                if upgradeRect[1].collidepoint(mx, my):
                    pl.speed += 5
                if upgradeRect[2].collidepoint(mx, my):
                    pl.firingSpeed_upG += 44
                if upgradeRect[3].collidepoint(mx, my):
                    pl.health = pl.max_health                
                if upgradeRect[4].collidepoint(mx, my):
                    pl.max_health += 500
                if upgradeRect[5].collidepoint(mx, my):
                    pl.shotSpeed_upG += 1                
                for r in upgradeRect[:6]:
                    if r.collidepoint(mx, my):
                        runMenu = False
                        game = True
                
                
    
        # obligatory frame-check and display flip
        clock.tick(60)
        display.flip()
    while game:
        for evnt in event.get():
            if evnt.type == QUIT:
                quit()
            if evnt .type == MOUSEBUTTONDOWN:
                # checks if any mouse button is down,  if so sets clicking to true
                button = evnt.button
                #startTicks = time.get_ticks()            
            if evnt.type == MOUSEBUTTONUP:
                # checks if any mouse button is down,  if so sets clicking to true
                button = 0       
            if evnt.type == MOUSEMOTION:
                # sets mx and my to mouse x backgand y if mouse is moving
                mx, my  = evnt.pos
            
            if evnt.type == KEYDOWN:
                #handles keyboard movement (if key pressed, corresponding direction = True)
                if evnt.key == K_w:
                    pl.directions[0] = True
                if evnt.key == K_s:
                    pl.directions[1] = True
                if evnt.key == K_a:
                    pl.directions[2] = True
                if evnt.key == K_d:
                    pl.directions[3] = True
                if evnt.key == K_m:
                    enemies = []
                    waitingEnemies = []
                    
                #debug binds (cheats to test stuff)
                if debug == True:
                    #triggers upgrade screen
                    if evnt.key == K_g:
                        level += 1
                        game = False
                        runMenu = True
                        menu = UPGRADE
                    
                    #adds wave
                    if evnt.key == K_h:
                        wave += 1    
                    
                    #spawns enemies based on number key pressed
                    if evnt.key == K_1:
                        enemies.append(Enemy(0,0))
                    if evnt.key == K_2:
                        enemies.append(Shooter(0,0))    
                    if evnt.key == K_3:
                        enemies.append(Wolf(0,0)) 
                    if evnt.key == K_4:
                        enemies.append(Turret(0,0))
                    if evnt.key == K_b:
                        #toggles bossfight
                        bossFight = not bossFight
                    #cycles guns
                    if evnt.key == K_SPACE:
                        if pl.gun == len(guns)-1:
                            pl.gun = 0
                        else:
                            pl.gun += 1
                
            #sets apt. directions to false if key is no longer pressed
            if evnt.type == KEYUP:
                if evnt.key == K_w:
                    pl.directions[0] = False
                if evnt.key == K_s:
                    pl.directions[1] = False
                if evnt.key == K_a:
                    pl.directions[2] = False
                if evnt.key == K_d:
                    pl.directions[3] = False  
        
        if button == 1:
            
            #if bullet timer is met, creates a new bullet at appropriate x and y, catches fire rates less than 2 (because bullets start going backwards or don't move a all if they hit a fire rate of < 2)
            totalFiringSpeed = guns[pl.gun](pl.muzzle_x, pl.muzzle_y, mx, my).firing_speed - pl.firingSpeed_upG
            if totalFiringSpeed < 2:
                totalFiringSpeed = 2
            if time.get_ticks() - startTicks > totalFiringSpeed:
                bullets.append(guns[pl.gun](pl.muzzle_x, pl.muzzle_y, mx, my))
                startTicks = time.get_ticks()
        
        
        
        #after level 5, gets ready for bossfight
        if level == 5:
            bossFight = True
        
        #ends game at level 6
        elif level == 6:
            game = False
            runMenu = True
            menu = WIN
        
        
        #goes to new level once waves are completed, prompts upgrade screen
        if wave == 5 and enemies == [] and waitingEnemies == []:
            if graceTimer >= 90:
                level +=1
                wave = 1
                game = False
                runMenu = True
                menu = UPGRADE
                pl.x, pl.y = WIDTH//2, HEIGHT//2
                button = 0
                graceTimer = 0
                pl.directions = [False, False, False, False]
                
            else:
                graceTimer += 1
        #handles enemy spawn plan (number of enemies, type of enemy, damage, speed etc)
        elif enemies == [] and waitingEnemies == [] and graceTimer == 0 and not debug and not bossFight:
            enemyPoints = int((wave * 2) + (2 * level) + 1)
            #enemy points decrease with every enemy planned (different reduction for each enemy)
            while enemyPoints > 0:
                spawnX = random.choice([random.randint(0 - 100, WIDTH), random.choice([0 - 100, WIDTH])])
                
                if spawnX == 0 or spawnX == WIDTH:
                    spawnY = random.randint(0 - 100, HEIGHT)
                else:
                    spawnY = random.choice([0 - 100, HEIGHT])
                
                #on level 1, can only spawn grunts
                if level < 2:
                    waitingEnemies.append(Enemy(spawnX, spawnY)) 
                    enemyPoints -= 1
                # on level 2, can spawn grunts and shooters
                elif level < 3:
                    enemyChoice = random.randint(0, 100)
                    if enemyChoice >= 80:
                        waitingEnemies.append(Shooter(spawnX, spawnY))
                        enemyPoints -= 2
                    else:
                        waitingEnemies.append(Enemy(spawnX, spawnY))
                        enemyPoints -= 1
                #on level 3, can spawn grunts, shooters or wolves
                elif level < 4:
                    enemyChoice = random.randint(0, 100)
                    if enemyChoice >= 85:
                        enemyPoints -= 3
                        waitingEnemies.append(Wolf(spawnX, spawnY))
                    elif enemyChoice >= 75:
                        waitingEnemies.append(Shooter(spawnX, spawnY))
                        enemyPoints -= 2
                    else:
                        waitingEnemies.append(Enemy(spawnX, spawnY))      
                        enemyPoints -= 1
                else:
                    #on any level after, can spawn grunts, shooters, wolves and turrets
                    enemyChoice = random.randint(0, 100)
                    if enemyChoice >= 85:
                        enemyPoints -= 3
                        waitingEnemies.append(Wolf(spawnX, spawnY))
                    elif enemyChoice >= 75:
                        waitingEnemies.append(Shooter(spawnX, spawnY))
                        enemyPoints -= 2
                    elif enemyChoice >= 65:
                        waitingEnemies.append(Turret(spawnX, spawnY))
                        enemyPoints -= 7                    
                    else:
                        waitingEnemies.append(Enemy(spawnX, spawnY))      
                        enemyPoints -= 2     
            #adds to wave
            wave+=1
            
    
        #handles waiting enemy spawning, if timer allows, pops object(s) from waitingEnemies and appends it to enemies (spawns multiple at once if it can). 
        if len(waitingEnemies) > 0:
            if time.get_ticks() - enemyWaitTime >= enemySpawnTime:
                if len(waitingEnemies) > ceil(wave / 2):
                    for i in range(ceil(wave / 2)):
                        enemies.append(waitingEnemies.pop())
                else:
                    enemies.append(waitingEnemies.pop())
                
                #Timer decreases alot with level, a little with wave too
                enemySpawnTime = 3000 - level * 250 - wave * 150
                
                #if timer is less than 200, sets timer to 200
                if enemySpawnTime < 200: 
                    enemySpawnTime = 200
                    
                enemyWaitTime = time.get_ticks()
        
        #Enemy bullet append
        for enemy in enemies:
            if isinstance(enemy, Shooter):
                if enemy.fire_time >= enemy.firing_speed:
                    enemyBullets.append(EnemyBullet(enemy.center_x, enemy.center_y, pl.center_x, pl.center_y))
                    enemy.fire_time = 0
                else:
                    enemy.fire_time += 1
                    
            #If enemy is turret, shoot 4 bullets at alternating angles
            elif isinstance(enemy, Turret):
                if enemy.fire_time >= enemy.firing_speed:
                    if enemy.gun_state == 1:
                        for i in enemy.angles_1:
                            #gets point from angle and radius
                            enemy.turretTarget = (enemy.center_x + enemy.w // 2 * cos(radians(i)), 
                                                  enemy.center_y + enemy.w // 2 * sin(radians(i)))
                            enemyBullets.append(EnemyBullet(enemy.center_x, enemy.center_y, enemy.turretTarget[0], enemy.turretTarget[1]))
                            enemy.gun_state = 0
                    else:
                        for i in enemy.angles_2:
                            #gets point from angle and radius
                            enemy.turretTarget = (enemy.center_x + enemy.w // 2 * cos(radians(i)), 
                                                  enemy.center_y + enemy.w // 2 * sin(radians(i)))
                            enemyBullets.append(EnemyBullet(enemy.center_x, enemy.center_y, enemy.turretTarget[0], enemy.turretTarget[1]))
                            enemy.gun_state = 1
                            
                    enemy.fire_time = 0                        
                else:
                    enemy.fire_time += 1                
        
        screen.blit(bk, (0, 0))
        
        """Drawing of everything"""
        # Draws pickups
        for item in pickups:
            item.draw()
            item.update(pl)        
        
        # Draws all enemies
        for enemy in enemies:
            enemy.draw()
            #enemy.debug(pl.center_x, pl.center_y) #debug info display for enemy
            enemy.update(pl.center_x, pl.center_y, enemies)
            enemy.check(bullets, pickups)
            
        #draws boss, if it can
        if bossFight:
            bs.draw()
            bs.update()
            bs.check()

            
            
        # Draws all enemy bullets
        for bullet in enemyBullets:
            bullet.draw()
            #bullet.debug() #draws debug info for bullets
            bullet.update()
            bullet.check(pl.hitbox)
            
        # Draws bullets
        for bullet in bullets:
            bullet.draw()
            #bullet.debug()
            bullet.update()
            bullet.check(enemies)        
            
        # Draws player
        pl.rotate(mx, my)
        pl.update(mx, my, enemies, enemyBullets)
        #if health goes to or below 0, ends game and starts menu loop
        if pl.health <= 0 and debug == False:
            game = False
            runMenu = True
            menu = LOSE        
        pl.draw()
        #pl.debug(guns[pl.gun](pl.muzzle_x, pl.muzzle_y, mx, my).firing_speed) #debug info display for player
    
        """HUD drawing"""
    
        #displays current gun's bullet at 3x size
        bullDisplayW = int(bulletPics[pl.gun].get_width() * 1.5)
        bullDisplayH = int(bulletPics[pl.gun].get_height() * 1.5)
        screen.blit(transform.scale(bulletPics[pl.gun], (bullDisplayW, bullDisplayH)), Rect(15 + 12 - bullDisplayW // 2, 45 + 12 - bullDisplayH // 2, bullDisplayW, bullDisplayH))
        
        #displays current level, wave and remaining enemies
        text = fontCal.render("level %i" %level, 1,BLACK)
        textSize = fontCal.size("level %i" %level)
        screen.blit(text, (WIDTH - textSize[0] - 15, textSize[1] - 15))
        
        text = fontCal.render("wave %i" %wave, 1,BLACK)
        textSize = fontCal.size("wave %i" %wave)
        screen.blit(text, (WIDTH - textSize[0] - 15, textSize[1] * 2 - 15))        
        
        text = fontCal.render("Remaining viruses: %i" %(len(waitingEnemies) + len(enemies)) , 1,BLACK)
        textSize = fontCal.size("Remaining viruses: %i" %(len(waitingEnemies) + len(enemies)) )
        screen.blit(text, (WIDTH - textSize[0] - 15, textSize[1] * 3 - 15))
        
        
        # obligatory frame-check and display flip
        clock.tick(60)
        display.flip()
        
quit()
