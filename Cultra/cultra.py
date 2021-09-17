#Made by Callum Gilles between may 29th and june 21st
#simple top down shooter in vein of hotline miami
#thanks for playing

import pygame, os, random, time, math, collections, copy
from pygame.locals import *


# set up the window
NATX = 1920
NATY = 1080

#change windowsize
WINDOWWIDTH = 1600
WINDOWHEIGHT = 900

#ratios for scalling
XRATIO = WINDOWWIDTH/NATX
YRATIO = WINDOWHEIGHT/NATY

NODEDISTANCE = 90

# set up the colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)

# set up the frame rate
FRAMERATE = 60

# file path
FILEPATH = os.path.dirname(__file__)
print(FILEPATH)

def load(file):
    #print(file)
    return pygame.image.load(file).convert_alpha()

def terminate():
    """ This function is called when the user closes the window or presses ESC """
    pygame.quit()
    os._exit(1)
    



def LineCollision(Ax1, Ay1, Ax2, Ay2, Bx1, By1, Bx2, By2):
    """ returns a (x, y) tuple or None if there is no intersection """
    d = (By2 - By1) * (Ax2 - Ax1) - (Bx2 - Bx1) * (Ay2 - Ay1)
    if d:
        uA = ((Bx2 - Bx1) * (Ay1 - By1) - (By2 - By1) * (Ax1 - Bx1)) / d
        uB = ((Ax2 - Ax1) * (Ay1 - By1) - (Ay2 - Ay1) * (Ax1 - Bx1)) / d
        
    else:
        return False
    
    if not(0 <= uA <= 1 and 0 <= uB <= 1):
        return False
 
    return True

def RectLineCol(rect, lx1, ly1, lx2, ly2):

    #define points of the rectangle
    topleftx, toplefty = rect.topleft 
    bottomleftx, bottomlefty = rect.bottomleft
    toprightx, toprighty = rect.topright
    bottomrightx, bottomrighty = rect.bottomright

    #do line collision on all sides of the rectangle
    top = LineCollision(lx1, ly1, lx2, ly2, toprightx, toprighty, topleftx, toplefty)
    left = LineCollision(lx1, ly1, lx2, ly2, topleftx, toplefty, bottomleftx, bottomlefty)
    right = LineCollision(lx1, ly1, lx2, ly2, toprightx, toprighty, bottomrightx, bottomrighty)
    bottom = LineCollision(lx1, ly1, lx2, ly2, bottomleftx, bottomlefty, bottomrightx, bottomrighty)

    #print("COLLISON", top or left or right or bottom)
    return top or left or right or bottom

def make_graph(nodes, obstas):
    """makes a graph for the nodes in each screen"""
    graph = {}
    for node in nodes:
        graph[node] = []
        for onode in nodes:
            distance = math.sqrt((node[0] - onode[0])**2 + (node[1] - onode[1])**2)
            connect = True
            for obsta in obstas:
                if RectLineCol(obsta.rect, node[0], node[1], onode[0], onode[1]):
                    connect = False
                    #print(disthold)
                    #print(node,onode)
                    
            
            if connect and node != onode and distance <= NODEDISTANCE*1.5:
                graph[node].append(onode)
                #print("bruh")
    #print(graph)
    return graph

        
def find_shortest_path(graph, start, goal):
    """finds shortest path inside graph"""
    explored = []
     
    # Queue for traversing the
    # graph in the BFS
    queue = [[start]]
     

    # Loop to traverse the graph
    # with the help of the queue
    while queue:
        path = queue.pop(0)
        node = path[-1]
         
        # Condition to check if the
        # current node is not visited
        if node not in explored:
            neighbours = graph[node]
             
            # Loop to iterate over the
            # neighbours of the node
            for neighbour in neighbours:
                new_path = list(path)
                new_path.append(neighbour)
                queue.append(new_path)
                 
                # Condition to check if the
                # neighbour node is the goal
                if neighbour == goal:
                    return new_path
                
            explored.append(node)
            

 
def AngleRangeChange(angle):
    """change angle from -360 and 360 to -180 and 180"""
    if -180 <= angle <= 180:
        return angle
    elif angle < -180:
        return 360 + angle
    elif angle > 180:
        return -360 + angle
    
def AngleSignChange(angle):
    """gives equivalent angle in other sign"""
    if angle > 0:
        return -360 + angle
    if angle < 0:
        return 360 + angle
    else:
        return 0
    
class Player(pygame.sprite.Sprite):
    """ The player controlled by the user """

    def __init__(self, weapon):
        self.weapon = weapon
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(self.weapon.images[0], (int(110*XRATIO),int(110*YRATIO)))
        self.rotate = self.image
        self.images = self.weapon.images
        self.rect = self.image.get_rect()
    
        # set up movement variables
        self.moveLeft = False
        self.moveRight = False
        self.moveUp = False
        self.moveDown = False
        self.movespeed = self.weapon.walkspeed
        self.acel = 0
        
        self.count = 32
        
        #closest node
        self.closest = ()

        self.dead = False

    def update(self, angle, obstas, graph):
        """ Change the position of the player's rectangle """
        prevleft = self.rect.left
        prevtop = self.rect.top
        
        move = (self.movespeed + int(self.acel))

        #diagonals decrease individual move speed
        count = int(self.moveDown) +int(self.moveUp) + int(self.moveLeft) +int(self.moveRight)
        if count >= 2:
            move = move//1.414
            
        if self.moveDown:
            self.rect.top += move
            
        if self.moveUp:
            self.rect.top -= move

        #check collision after up and down movement and return back to previous if collide   
        if pygame.sprite.spritecollide(self,obstas, False) != []:
            self.rect.top = prevtop
            
        if self.moveLeft:
            self.rect.left -= move

        if self.moveRight:
            self.rect.right += move

        #check collision after left and right movement and return back to previous if collide     
        if pygame.sprite.spritecollide(self,obstas, False) != []:
            self.rect.left = prevleft 


        #use move animations if moving
        if self.moveLeft or self.moveRight or self.moveUp or self.moveDown:
            if not self.weapon.attacking:
                if 25 <= self.count <= 32:
                    self.rotate = self.weapon.images[0]
                elif 17 <= self.count <= 24:
                    self.rotate = self.weapon.images[1]
                elif 9 <= self.count <= 16:
                    self.rotate = self.weapon.images[2]
                elif 1 <= self.count <= 8:
                    self.rotate = self.weapon.images[3]
                else:
                    self.count = 32
                self.count -=1
                
        #update rotation    
        self.image = pygame.transform.rotate(pygame.transform.scale(self.rotate, (int(110*XRATIO),int(110*YRATIO))), -angle)

        #update weapon rect
        self.weapon.rect.center = self.rect.center

        #arbitrary big number
        distance = WINDOWWIDTH


        #find closest node to player for enemy pathing
        for node in graph:
            connect = True
            for obsta in obstas:
                if RectLineCol(obsta.rect, node[0], node[1], self.rect.centerx, self.rect.centery):
                    connect = False
            
            if connect:
                disthold = math.sqrt((node[0] - self.rect.centerx)**2 + (node[1] - self.rect.centery)**2)
                if disthold < distance:
                    distance = disthold
                    self.closest = node
                   
        
        
        
class Enemy(pygame.sprite.Sprite):
    def __init__(self, weapon, left, top, size, rotation, distance):
        pygame.sprite.Sprite.__init__(self)
        
        #sprite stuff
        if weapon[1] == "BAT":
            self.weapon = Bat(weapon[0],weapon[1],weapon[2],weapon[3],weapon[4],weapon[5])
        else:
            self.weapon = Weapon(weapon[0],weapon[1],weapon[2],weapon[3],weapon[4],weapon[5],weapon[6],weapon[7],weapon[8],weapon[9],weapon[10],weapon[11],weapon[12],weapon[13],weapon[14])
        self.deadimage = load("dead.png")
        self.images = []
        
        for x in self.weapon.images:
            self.images.append(pygame.transform.scale(x, (int(size*XRATIO),int(size*YRATIO))))
                               
        self.image = self.images[0]
        self.rotate = self.image
        self.imagepos = 0
        self.rect = pygame.Rect(int(left*XRATIO), int(top*YRATIO), int(size*XRATIO), int(size*YRATIO))
        self.rotation = rotation

        #path finding stuff and states
        self.distance = distance
        self.see = False
        self.chase = False
        self.search = False
        self.look = 0
        self.lookinc = 1
        self.attack = False
        self.dead = False
        self.lastloc = ()
        self.wait = 15
        self.wait2 = 60
        self.path = None
        self.pos = 1
        self.loc = pygame.Rect(0,0,50,50)
        self.newpath = True
        self.seecounter = 0
        
    def update(self, player, obstas, graph, windowSurface, level):
        if not self.dead:
            #update enemy's weapon
            if type(self.weapon) == Weapon:
                self.weapon.update(self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery)
                
            else:
                self.weapon.update(self, player, level)
                
                #so the enemy only swings while in distance
                self.distance = player.rect.width

            #check to see if enemy can see player
            self.seecounter += 1
            for obsta in obstas:
                if RectLineCol(obsta.rect, player.rect.centerx, player.rect.centery, self.rect.centerx, self.rect.centery):
                    self.seecounter = 0
                    
            #distance from player for calc         
            distance = math.sqrt((player.rect.centerx - self.rect.centerx)**2 + (player.rect.centery - self.rect.centery)**2)

            #angle to player
            angle =  AngleRangeChange(math.degrees(math.atan2((self.rect.centerx - player.rect.centerx),(self.rect.centery- player.rect.centery)))) + random.randrange(-2, 2)

            #check if the enemy is seeing you and inside fov
            if self.seecounter > 5 and (self.rotation +100 >= angle >= self.rotation - 100 or self.rotation +100 >= AngleSignChange(angle) >= self.rotation - 100):

                #start attacking/chasing
                self.rotation = angle
                if self.wait == 0:
                    if distance < self.distance:
                        #attacking
                        self.weapon.attacking = True
                        
                    else:
                        #move
                        self.weapon.attacking = False
                        self.rect.centery -= math.cos(math.radians(angle))*self.weapon.walkspeed
                        self.rect.centerx -= math.sin(math.radians(angle))*self.weapon.walkspeed
                        self.imagepos += 1

                        #update images
                        if self.imagepos == 32:
                            self.imagepos = 0
                                
                        if 0 <= self.imagepos <=7:
                            num = 0
                        elif 8 <= self.imagepos <=15:
                            num = 1
                        elif 16 <= self.imagepos <=23:
                            num = 2
                        elif 24 <= self.imagepos <=31:
                            num = 3
                                
                        self.rotate = self.images[num]
                        
                else:
                    #enemy has a slight delay before attacking so player has a chance to shoot
                    self.wait -=1

                #will chase     
                self.chase = True
                
            elif self.chase:
                #chase after player while not in sight after having seen the player
                self.weapon.attacking = False
                self.wait = 20
                
                if self.newpath or self.wait2 == 0:
                    #find new path for the enemy to follow towards the player
                    distance = 3000
                    closest = ()
                    for node in graph:
                        if closest == ():
                            closest = node
                        connect = True
                        for obsta in obstas:
                            if RectLineCol(obsta.rect, node[0], node[1], self.rect.centerx, self.rect.centery):
                                connect = False
                    
                        if connect:
                            disthold = math.sqrt((node[0] - self.rect.centerx)**2 + (node[1] - self.rect.centery)**2)
                            if disthold < distance:
                                distance = disthold
                                closest = node
                                
                    self.path = find_shortest_path(graph, closest, player.closest)
                    self.pos = 1
                    self.loc = pygame.Rect(0,0,50,50)
                    self.loc.center = self.path[self.pos]
                    self.newpath = False
                    self.wait2 = 60
                    
                if self.loc.colliderect(self.rect):
                    if self.pos != len(self.path)-1:
                        
                        #go onto next node in path
                        self.pos +=1
                        self.loc = pygame.Rect(0,0,50,50)
                        self.loc.center = self.path[self.pos]
                    else:
                        #create new path if reached final node and still in chase
                        self.newpath = True
                
                self.wait2 -=1

                #update angles
                angle =  AngleRangeChange(math.degrees(math.atan2((self.rect.centerx - self.loc.centerx),(self.rect.centery - self.loc.centery))))
                self.rotation = angle

                #move
                self.rect.centery -= math.cos(math.radians(self.rotation))*self.weapon.walkspeed
                self.rect.centerx -= math.sin(math.radians(self.rotation))*self.weapon.walkspeed

                #update sprites
                if not self.weapon.attacking:
                
                    self.imagepos += 1
                    if self.imagepos == 32:
                        self.imagepos = 0
                        
                    if 0 <= self.imagepos <=7:
                        num = 0
                    elif 8 <= self.imagepos <=15:
                        num = 1
                    elif 16 <= self.imagepos <=23:
                        num = 2
                    elif 24 <= self.imagepos <=31:
                        num = 3
                        
                    self.rotate = self.images[num]

            #enemy goes into chase if they can "hear" gunshot
            if player.weapon.attacking and distance < 700 and player.weapon.name != "BAT" and player.weapon.name != "PISTOL":
                self.chase = True
                    
            
            #update image and weapon rect 
            self.image = pygame.transform.rotate(pygame.transform.scale(self.rotate, (int(110*XRATIO),int(110*YRATIO))),self.rotation)
            self.weapon.rect.center = self.rect.center
            
        else:
            #show dead image of enemy
            self.image = pygame.transform.scale(self.deadimage, (int(110*XRATIO),int(110*YRATIO)))
           
 
class Bat(pygame.sprite.Sprite):
    def __init__(self,walkspeed, name, sfx, enemytype, groundtype, groundloc):
        #sprite stuff
        pygame.sprite.Sprite.__init__(self)
        self.playerwalk = PLAYERBATWALK
        self.enemywalk = ENEMYBATWALK
        self.playerswing = PLAYERBATSWING
        self.enemyswing = ENEMYBATSWING
        
        self.image = BATGROUND
        self.rect = self.image.get_rect()
        if enemytype:
            self.images = ENEMYBATWALK
            self.images2 = ENEMYBATSWING
        else:
            self.images = PLAYERBATWALK
            self.images2 = PLAYERBATSWING

        self.attacking = False
            
        self.walkspeed = walkspeed
        
        self.name = name
        
        self.sfx = pygame.mixer.Sound(sfx)
        self.sfx.set_volume(0.5)

        #droping and switching based variables
        self.groundtype = groundtype
        self.groundloc = groundloc
        self.groundrect = pygame.Rect(0,0,50,50)
        self.enemytype = enemytype
        
        
        self.swing = True
        self.count = 0
        self.wait = 0
        
    def update(self, user, against, level):
        #update if not on ground
        if not self.groundtype:
            if self.wait > 0:
                
                self.wait -= 1
                
            elif self.attacking and not self.swing:
                
                self.swing = True
                self.count = 16
                self.sfx.play()
                

            if self.swing:
                self.swinging(user, against, level)
        
            
        
    def swinging(self, user, against, level):
        #change swing animations
        if 13 <= self.count <= 16:
            user.rotate = self.images2[0]
        elif 9 <= self.count <= 12:
            user.rotate = self.images2[1]
        elif 5 <= self.count <= 8:
            user.rotate = self.images2[2]
        elif 1 <= self.count <= 4:
            user.rotate = self.images2[3]
        else:
            self.swing = False

        self.count -=1

        #check collisions when swinging
        if type(user) == Player:
            for enemy in against:
                if pygame.sprite.collide_rect(enemy,user) and not enemy.dead:
                    enemy.dead = True
                    enemy.weapon.groundtype = True
                    level.score += 100 * level.combo
                    level.combo +=1
                    level.comboframes = 90
        else:
            if pygame.sprite.collide_rect(against,user):
                against.dead = True
        
        

        
            
        
    
class Weapon(pygame.sprite.Sprite):
    def __init__(self, playerimages, enemyimages, shootdelay, bullets, walkspeed, accuracy, bulletspeed, bulletsize, ammo, name, sfx, enemytype, groundtype, groundloc, groundimage):
        #sprite stuff
        pygame.sprite.Sprite.__init__(self)
        self.playerimages = playerimages
        self.enemyimages = enemyimages
        self.image = groundimage
        self.rect = self.image.get_rect()
        
        if enemytype:
            self.images = enemyimages #player/enemy walk animation
        else:
            self.images = playerimages

        self.shootdelay = shootdelay #delay frames between shooting
        self.wait = 0

        self.bullets = bullets #amount of bullets shot per shot (shotgun uses more)

        self.walkspeed = walkspeed #"weight" of weapon affecting walkspeed

        # how accurately the bullets go to the location wanted
        #0 = absolute accuracy, anything greater or less will make the bullets less accurate
        self.accuracy = accuracy

        self.bulletspeed = bulletspeed #speed of bullet

        self.bulletsize = bulletsize

        self.bulletgroup = pygame.sprite.Group() #group of weapons bullets

        self.ammo = ammo #ammo

        self.attacking = False

        self.name = name

        self.sfx = pygame.mixer.Sound(sfx)
        self.sfx.set_volume(0.5)

        #dropped and switching variables
        self.enemytype = enemytype
        self.groundtype = groundtype
        self.groundloc = (0,0)
        self.groundrect = pygame.Rect(0,0,50,50)
        
    def update(self, curx, cury, x, y):
        #update if not on ground
        if not self.groundtype:
            if self.wait > 0:
                
                self.wait -= 1
                
            elif self.attacking:
                
                self.shoot(curx,cury, x, y)
        
                
        
        

    def shoot(self, curx, cury, shootx, shooty):
        #shoots if they ammo or they're a weapon
        if self.ammo > 0 or self.enemytype:
            
            for x in range(self.bullets):
                
                angle = AngleRangeChange(math.atan2((shootx+random.randrange(-self.accuracy,self.accuracy)-curx),(shooty+random.randrange(-self.accuracy,self.accuracy)-cury)))
                
                self.bulletgroup.add(Bullet(curx, cury, self.bulletsize, math.degrees(angle), self.bulletsize, self.bulletspeed))
                
            if not self.enemytype:    
                self.ammo -= 1
            
            self.wait = self.shootdelay

            self.sfx.play()




class Bullet(pygame.sprite.Sprite):
    def __init__(self, startx, starty, size, angle, bulletsize, speed):
        #sprite stuff
        pygame.sprite.Sprite.__init__(self)
        
        self.rect = pygame.Rect(0,0,size,size)
        self.rect.centerx = startx
        self.rect.centery = starty
        
        self.image = pygame.transform.rotate(pygame.Surface([int(size*XRATIO), int(size*YRATIO)]), angle+180)
        self.image.fill(WHITE)

        #movespeed
        self.movey = -math.cos(math.radians(angle))
        self.movex = math.sin(math.radians(angle))
        self.speed = speed
        
        self.size = size
        self.delete = False
        
    def update(self, obstas, other, level):

        #check collision of bullet with between frame checks for accuracy
        for i in range(1,self.speed+1):
            holder = pygame.Rect(0,0,self.size,self.size)
            holder.centerx = self.rect.centerx + self.movex*i
            holder.centery = self.rect.centery - self.movey*i
            for x in obstas:
                if holder.colliderect(x.rect):
                    self.delete = True

            for x in other:
                if not x.dead:
                    if holder.colliderect(x.rect):
                        self.delete = True   
                        x.dead = True
                        if type(x) != Player:
                            level.score += 100*level.combo
                            level.combo +=1
                            level.comboframes = 90
                            x.weapon.groundtype = True
                        
                    
                
        #move the bullet                
        self.rect.centerx += self.movex*self.speed
        self.rect.centery -= self.movey*self.speed
        
            
        
        
class Obs(pygame.sprite.Sprite):
    def __init__(self,image,centerx,centery,width,height):
        pygame.sprite.Sprite.__init__(self)
        
        if image != "":
            #textured object
            self.image = pygame.transform.scale(load(image), (int(width*XRATIO), int(height*YRATIO)))
            self.rect = self.image.get_rect()

        else:
            #walls
            self.image = pygame.Surface([int(width*XRATIO), int(height*YRATIO)])
            self.image.fill(BLACK)
            self.rect = pygame.Rect((0,0),(int(width*XRATIO),int(height*YRATIO)))

        self.rect.centerx = int(centerx*XRATIO)
        self.rect.centery = int(centery*YRATIO)   

class Screen(pygame.sprite.Sprite):
    def __init__(self, background, obstas, enemies, endrect, playerpos):
        """background = background image, obstas = list of file locations for obstacles, obstacles, etc, enemies = sprite group of enemies, endrect = where player leaves, player pos = start pos"""
        #sprite stuff for drawing background
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(load(background),(WINDOWWIDTH,WINDOWHEIGHT))
        self.rect = self.image.get_rect()
        
        #create nodes and graph on screen
        self.nodes = []
        for x in range(20,WINDOWWIDTH,NODEDISTANCE):
            for y in range(20,WINDOWHEIGHT,NODEDISTANCE):
                do = True
                for obsta in obstas:
                    if obsta.rect.collidepoint((x,y)):
                        do = False
                if do:
                    self.nodes.append((x,y))

        self.graph = make_graph(self.nodes, obstas)

        #set up obstacles in screen
        self.obstalist = obstas
        self.obstas = pygame.sprite.Group()
        for obsta in obstas:
            self.obstas.add(obsta)
        self.obstas.add(Obs("",-10,NATY/2,20,NATY*2),Obs("",NATX+10,NATY/2,20,NATY*2), Obs("",NATX/2, -10, NATX,20), Obs("",NATX/2, NATY+10, NATX,20))
        

        self.enemies = pygame.sprite.Group()
        for enemy in enemies:
            self.enemies.add(Enemy(enemy[0],enemy[1],enemy[2],enemy[3],enemy[4],enemy[5]))

        
        self.endrect = endrect

        self.playerpos = playerpos
            
class Level():
    def __init__(self,screens, music, dialogue,player):
        #screen stuff
        self.screens = screens
        self.curnum = 0
        self.current = Screen(screens[self.curnum][0], screens[self.curnum][1], screens[self.curnum][2], screens[self.curnum][3], screens[self.curnum][4])

        #pre level text
        self.dialogue = dialogue
        
        # set up music
        pygame.mixer.music.load(music)
        
        #player stuff
        self.player = player
        self.player.rect.center = self.current.playerpos
        self.playergroup = pygame.sprite.GroupSingle()
        self.playergroup.add(self.player)
        
        #background of current screen
        self.backgroundgroup = pygame.sprite.GroupSingle()
        self.backgroundgroup.add(self.current)
        
        
        
        self.bullets = pygame.sprite.Group()

        
        
        #bools
        self.fadeout = False
        self.retry = False
        self.hold = False
        self.deadscreen = None
    
        #counters and stuff
        self.deathcounter = 0
        self.retrycount = 0
        self.starttime = 0
        self.exitimer = 120
        self.score = 0
        self.prevscore = 0
        self.combo = 1
        self.prevcombo = 0
        self.endtime = 0
        self.comboframes = 90
        self.prevcomboframes = 0

        #pre saved weapon 
        if type(self.player.weapon) == Weapon:
            self.weapon = [self.player.weapon.playerimages, self.player.weapon.enemyimages,self.player.weapon.image,self.player.weapon.rect, self.player.weapon.images,
                      self.player.weapon.shootdelay, self.player.weapon.wait, self.player.weapon.bullets, self.player.weapon.walkspeed, self.player.weapon.accuracy,
                      self.player.weapon.bulletspeed, self.player.weapon.bulletsize, self.player.weapon.bulletgroup, self.player.weapon.ammo, self.player.weapon.attacking,
                      self.player.weapon.name, self.player.weapon.sfx, self.player.weapon.enemytype, self.player.weapon.groundtype, self.player.weapon.groundloc,self.player.weapon.groundrect]
        else:
            self.weapon = Bat(10, "BAT", "Weapons\Bat\swing.wav", False, False, (0,0))
        
        
    def run_logic(self, windowSurface):
        if not self.dialogue.cont and not self.fadeout and not self.retry:
            #normal logic
            self.comboframes -=1
            if self.comboframes  < 0:
                self.combo = 1
                self.comboframes = 90
                
            #get angle for facing of character model
            mousex, mousey = pygame.mouse.get_pos()
            angle = math.degrees(math.atan2((mousey-self.player.rect.centery),(mousex-self.player.rect.centerx))) + 90
            if (self.player.moveLeft or self.player.moveRight or self.player.moveUp or self.player.moveDown):
                if self.player.acel < self.player.movespeed*0.5:
                    self.player.acel += 0.2
            else:
                self.player.acel = 0
                        
            # update the player's position
            self.player.update(angle, self.current.obstas, self.current.graph)

            # update the enemies stuff
            
            self.current.enemies.update(self.player, self.current.obstas, self.current.graph, windowSurface, self)

            #update enemy bullets
            for enemy in self.current.enemies.sprites():
                if type(enemy.weapon) == Weapon:
                    enemy.weapon.bulletgroup.update(self.current.obstas, [self.player], self)
                    
                    for x in enemy.weapon.bulletgroup.sprites():
                        if x.delete:
                            enemy.weapon.bulletgroup.remove(x)
            #update player bullets        
            if type(self.player.weapon) == Weapon:
                self.player.weapon.bulletgroup.update(self.current.obstas, self.current.enemies, self)


                for x in self.player.weapon.bulletgroup.sprites():
                    if x.delete:
                        self.player.weapon.bulletgroup.remove(x)

                    
            if self.player.dead:
                #if player is dead
                #reset back to how screen was originally was

                #reset stuff
                self.retry = True
                self.current = Screen(self.screens[self.curnum][0], self.screens[self.curnum][1], self.screens[self.curnum][2], self.screens[self.curnum][3], self.screens[self.curnum][4])
                self.player.dead = False
                self.player.rect.center = self.current.playerpos
                self.deadscreen = windowSurface
                self.score = self.prevscore
                self.combo = self.prevcombo
                self.comboframes = self.prevcomboframes

                #reset weapon attributes
                if type(self.weapon) != Bat:
                    self.player.weapon = Weapon(PLAYERPISTOL, ENEMYPISTOL, 20, 1, 12, 5, 80, 7, 6, "PISTOL", "Weapons/Pistol/pistol.wav", True, False, (0,0), PISTOLGROUND)
                    self.player.weapon.playerimages = self.weapon[0]
                    self.player.weapon.enemyimages = self.weapon[1]   
                    self.player.weapon.image = self.weapon[2]      
                    self.player.weapon.rect = self.weapon[3]       
                    self.player.weapon.images = self.weapon[4]           
                    self.player.weapon.shootdelay = self.weapon[5]             
                    self.player.weapon.wait = self.weapon[6]
                    self.player.weapon.bullets = self.weapon[7]
                    self.player.weapon.walkspeed = self.weapon[8]  
                    self.player.weapon.accuracy = self.weapon[9] 
                    self.player.weapon.bulletspeed = self.weapon[10]
                    self.player.weapon.bulletsize = self.weapon[11]
                    self.player.weapon.bulletgroup = self.weapon[12]
                    self.player.weapon.ammo = self.weapon[13]
                    self.player.weapon.attacking = self.weapon[14]
                    self.player.weapon.name = self.weapon[15]
                    self.player.weapon.sfx = self.weapon[16]                
                    self.player.weapon.enemytype = self.weapon[17]
                    self.player.weapon.groundtype = self.weapon[18]
                    self.player.weapon.groundloc = self.weapon[19]
                    self.player.weapon.groundrect = self.weapon[20]

                    if self.player.weapon.ammo == 0:
                        self.player.weapon.ammo = 1
                else:
                    self.player.weapon = Bat(10, "BAT", "Weapons\Bat\swing.wav", False, False, (0,0))
                    
                self.player.moveUp = False
                self.player.moveDown = False
                self.player.moveLeft = False
                self.player.moveRight = False
                    
            x, y = pygame.mouse.get_pos()

            #update player weapon
            if type(self.player.weapon) == Weapon:
                self.player.weapon.update(self.player.rect.centerx,self.player.rect.centery, x, y)
                
            else:
                
                self.player.weapon.update(self.player, self.current.enemies, self)
                
            self.exit = True

            #check if all enemies are dead
            for enemy in self.current.enemies.sprites():
               if enemy.dead == False:
                   self.exit = False

            #if player leaves screen or ends level    
            if self.player.rect.colliderect(self.current.endrect) and self.exit:
                self.exitimer = 120
                self.curnum +=1
                self.backgroundgroup.remove(self.current)
                if self.curnum <= len(self.screens)-1:
                    self.current = Screen(self.screens[self.curnum][0], self.screens[self.curnum][1], self.screens[self.curnum][2], self.screens[self.curnum][3], self.screens[self.curnum][4])
                    self.player.rect.center = self.current.playerpos
                    self.backgroundgroup.add(self.current)
                    self.prevscore = self.score
                    self.prevcombo = self.combo
                    self.prevcomboframes = self.comboframes
                    if type(self.player.weapon) == Weapon:
                        self.weapon = [self.player.weapon.playerimages, self.player.weapon.enemyimages,self.player.weapon.image,self.player.weapon.rect, self.player.weapon.images,
                            self.player.weapon.shootdelay, self.player.weapon.wait, self.player.weapon.bullets, self.player.weapon.walkspeed, self.player.weapon.accuracy,
                            self.player.weapon.bulletspeed, self.player.weapon.bulletsize, self.player.weapon.bulletgroup, self.player.weapon.ammo, self.player.weapon.attacking,
                            self.player.weapon.name, self.player.weapon.sfx, self.player.weapon.enemytype, self.player.weapon.groundtype, self.player.weapon.groundloc,self.player.weapon.groundrect]
                    else:
                        self.weapon = Bat(10, "BAT", "Weapons\Bat\swing.wav", False, False, (0,0))
                    print()
                    print(self.weapon)
                else:
                    self.fadeout = True
                    self.endtime = time.time()
                    self.deadscreen = windowSurface
                    pygame.mixer.music.load("Music/voxeldrum.wav")
                    pygame.mixer.music.play(-1, 0.0)
                        
                    
        
        

        
    def process(self, windowSurface, game):
        """ Process all of the keyboard and mouse events.  """
        #print(self.player.rect.centerx,self.player.rect.centery)
        pause = False
        if self.dialogue.cont:
            pass
        
        elif self.fadeout:
            #allow user to exit
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                elif event.type == KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game.ingame = False
                        pygame.mixer.music.load("Music/bullet.wav")
                        pygame.mixer.music.play(-1, 0.0)

        elif self.retry:
            #allows user to retry
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()  
                elif event.type == KEYDOWN:
                    if event.key == ord("r"):
                        self.retrycount = 0
                        self.retry = False
                        #RESET SCREEN
        else:
            #normal in game logic
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()  
                elif event.type == KEYDOWN:
                    
                    # update the direction of the player  
                    if event.key == ord('a'):
                        self.player.moveLeft = True


                    if event.key == ord('d'):
                        self.player.moveRight = True



                    if event.key == ord('w'):
                        self.player.moveUp = True


                    if event.key == ord('s'):
                        self.player.moveDown = True
                        
                    if event.key == K_ESCAPE:
                        game.pause = True
                        #pauses game


                elif event.type == KEYUP:
                    if event.key == ord('a'):
                        self.player.moveLeft = False


                    if event.key == ord('d'):
                        self.player.moveRight = False


                    if event.key == ord('w'):
                        self.player.moveUp = False


                    if event.key == ord('s'):
                        self.player.moveDown = False

                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player.weapon.attacking = True
                        
                    elif event.button == 3 and not self.hold:
                        for enemy in self.current.enemies:

                            #ALLOWS FOR WEAPON SWITCHING
                            #VERY STUPID
                            if enemy.weapon.groundtype and pygame.sprite.collide_rect(self.player, enemy.weapon):
                                #player has gun and switches with gun on floor
                                if type(enemy.weapon) == Weapon and type(self.player.weapon) == Weapon:
                                    playerweapon = [self.player.weapon.playerimages, self.player.weapon.enemyimages,self.player.weapon.image,self.player.weapon.rect, self.player.weapon.images,
                                      self.player.weapon.shootdelay, self.player.weapon.wait, self.player.weapon.bullets, self.player.weapon.walkspeed, self.player.weapon.accuracy,
                                      self.player.weapon.bulletspeed, self.player.weapon.bulletsize, self.player.weapon.bulletgroup, self.player.weapon.ammo, self.player.weapon.attacking,
                                      self.player.weapon.name, self.player.weapon.sfx, self.player.weapon.enemytype, self.player.weapon.groundtype, self.player.weapon.groundloc,self.player.weapon.groundrect]
                                   
                                    enemyweapon = [enemy.weapon.playerimages, enemy.weapon.enemyimages,enemy.weapon.image,enemy.weapon.rect, enemy.weapon.images,
                                      enemy.weapon.shootdelay, enemy.weapon.wait, enemy.weapon.bullets, enemy.weapon.walkspeed, enemy.weapon.accuracy,
                                      enemy.weapon.bulletspeed, enemy.weapon.bulletsize, enemy.weapon.bulletgroup, enemy.weapon.ammo, enemy.weapon.attacking,
                                      enemy.weapon.name, enemy.weapon.sfx, enemy.weapon.enemytype, enemy.weapon.groundtype, enemy.weapon.groundloc, enemy.weapon.groundrect]

                                    self.player.weapon.playerimages = enemyweapon[0]
                                    self.player.weapon.enemyimages = enemyweapon[1]   
                                    self.player.weapon.image = enemyweapon[2]      
                                    self.player.weapon.rect = enemyweapon[3]       
                                    self.player.weapon.images = self.player.weapon.playerimages           
                                    self.player.weapon.shootdelay = enemyweapon[5]             
                                    self.player.weapon.wait = enemyweapon[6]
                                    self.player.weapon.bullets = enemyweapon[7]
                                    self.player.weapon.walkspeed = enemyweapon[8]  
                                    self.player.weapon.accuracy = enemyweapon[9] 
                                    self.player.weapon.bulletspeed = enemyweapon[10]
                                    self.player.weapon.bulletsize = enemyweapon[11]
                                    self.player.weapon.bulletgroup = enemyweapon[12]
                                    self.player.weapon.ammo = enemyweapon[13]
                                    self.player.weapon.attacking = enemyweapon[14]
                                    self.player.weapon.name = enemyweapon[15]
                                    self.player.weapon.sfx = enemyweapon[16]                
                                    self.player.weapon.enemytype = False
                                    self.player.weapon.groundtype = False
                                    self.player.weapon.groundloc = enemyweapon[19]
                                    self.player.weapon.groundrect = enemyweapon[20]

                                    enemy.weapon.playerimages = playerweapon[0]
                                    enemy.weapon.enemyimages = playerweapon[1]   
                                    enemy.weapon.image = playerweapon[2]      
                                    enemy.weapon.rect = playerweapon[3]       
                                    enemy.weapon.images = enemy.weapon.playerimages           
                                    enemy.weapon.shootdelay = playerweapon[5]             
                                    enemy.weapon.wait = playerweapon[6]
                                    enemy.weapon.bullets = playerweapon[7]
                                    enemy.weapon.walkspeed = playerweapon[8]  
                                    enemy.weapon.accuracy = playerweapon[9] 
                                    enemy.weapon.bulletspeed = playerweapon[10]
                                    enemy.weapon.bulletsize = playerweapon[11]
                                    enemy.weapon.bulletgroup = playerweapon[12]
                                    enemy.weapon.ammo = playerweapon[13]
                                    enemy.weapon.attacking = playerweapon[14]
                                    enemy.weapon.name = playerweapon[15]
                                    enemy.weapon.sfx = playerweapon[16]                
                                    enemy.weapon.enemytype = True
                                    enemy.weapon.groundtype = True
                                    enemy.weapon.groundloc = playerweapon[19]
                                    enemy.weapon.groundrect = playerweapon[20]
                                    
                                elif type(enemy.weapon) == Weapon and type(self.player.weapon) == Bat:
                                    enemyweapon = [enemy.weapon.playerimages, enemy.weapon.enemyimages,enemy.weapon.image,enemy.weapon.rect, enemy.weapon.images,
                                      enemy.weapon.shootdelay, enemy.weapon.wait, enemy.weapon.bullets, enemy.weapon.walkspeed, enemy.weapon.accuracy,
                                      enemy.weapon.bulletspeed, enemy.weapon.bulletsize, enemy.weapon.bulletgroup, enemy.weapon.ammo, enemy.weapon.attacking,
                                      enemy.weapon.name, enemy.weapon.sfx, enemy.weapon.enemytype, enemy.weapon.groundtype, enemy.weapon.groundloc, enemy.weapon.groundrect]
                                    
                                    loc = self.player.weapon.rect.center
                                    
                                    self.player.weapon = Weapon(PLAYERPISTOL, ENEMYPISTOL, 20, 1, 7, 5, 80, 7, 12, "ENEMYPISTOL", "Weapons\Pistol\pistol.wav", True, False, (0,0), PISTOLGROUND)
                                    self.player.weapon.playerimages = enemyweapon[0]
                                    self.player.weapon.enemyimages = enemyweapon[1]   
                                    self.player.weapon.image = enemyweapon[2]      
                                    self.player.weapon.rect = enemyweapon[3]       
                                    self.player.weapon.images = self.player.weapon.playerimages           
                                    self.player.weapon.shootdelay = enemyweapon[5]             
                                    self.player.weapon.wait = enemyweapon[6]
                                    self.player.weapon.bullets = enemyweapon[7]
                                    self.player.weapon.walkspeed = enemyweapon[8]  
                                    self.player.weapon.accuracy = enemyweapon[9] 
                                    self.player.weapon.bulletspeed = enemyweapon[10]
                                    self.player.weapon.bulletsize = enemyweapon[11]
                                    self.player.weapon.bulletgroup = enemyweapon[12]
                                    self.player.weapon.ammo = enemyweapon[13]
                                    self.player.weapon.attacking = enemyweapon[14]
                                    self.player.weapon.name = enemyweapon[15]
                                    self.player.weapon.sfx = enemyweapon[16]                
                                    self.player.weapon.enemytype = False
                                    self.player.weapon.groundtype = False
                                    self.player.weapon.groundloc = enemyweapon[19]
                                    self.player.weapon.groundrect = enemyweapon[20]

                                    enemy.weapon = Bat(10, "BAT", "Weapons\Bat\swing.wav", True, True, (0,0))
                                    enemy.weapon.rect.center = loc

                                elif type(enemy.weapon) == Bat and type(self.player.weapon) == Weapon:
                                    playerweapon = [self.player.weapon.playerimages, self.player.weapon.enemyimages,self.player.weapon.image,self.player.weapon.rect, self.player.weapon.images,
                                      self.player.weapon.shootdelay, self.player.weapon.wait, self.player.weapon.bullets, self.player.weapon.walkspeed, self.player.weapon.accuracy,
                                      self.player.weapon.bulletspeed, self.player.weapon.bulletsize, self.player.weapon.bulletgroup, self.player.weapon.ammo, self.player.weapon.attacking,
                                      self.player.weapon.name, self.player.weapon.sfx, self.player.weapon.enemytype, self.player.weapon.groundtype, self.player.weapon.groundloc,self.player.weapon.groundrect]
                                    
                                    loc = enemy.weapon.rect.center
                                    
                                    enemy.weapon = Weapon(PLAYERPISTOL, ENEMYPISTOL, 20, 1, 7, 5, 80, 7, 12, "ENEMYPISTOL", "Weapons\Pistol\pistol.wav", True, False, (0,0), PISTOLGROUND)
                                    enemy.weapon.playerimages = playerweapon[0]
                                    enemy.weapon.enemyimages = playerweapon[1]   
                                    enemy.weapon.image = playerweapon[2]      
                                    enemy.weapon.rect = playerweapon[3]       
                                    enemy.weapon.images = enemy.weapon.playerimages           
                                    enemy.weapon.shootdelay = playerweapon[5]             
                                    enemy.weapon.wait = playerweapon[6]
                                    enemy.weapon.bullets = playerweapon[7]
                                    enemy.weapon.walkspeed = playerweapon[8]  
                                    enemy.weapon.accuracy = playerweapon[9] 
                                    enemy.weapon.bulletspeed = playerweapon[10]
                                    enemy.weapon.bulletsize = playerweapon[11]
                                    enemy.weapon.bulletgroup = playerweapon[12]
                                    enemy.weapon.ammo = playerweapon[13]
                                    enemy.weapon.attacking = playerweapon[14]
                                    enemy.weapon.name = playerweapon[15]
                                    enemy.weapon.sfx = playerweapon[16]                
                                    enemy.weapon.enemytype = True
                                    enemy.weapon.groundtype = True
                                    enemy.weapon.groundloc = playerweapon[19]
                                    enemy.weapon.groundrect = playerweapon[20]

                                    self.player.weapon = Bat(10, "BAT", "Weapons\Bat\swing.wav", False, False, (0,0))
                                    self.player.weapon.rect.center = loc
                                    
                                
                                
                                
     
                                
                    
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.player.weapon.attacking = False
                    elif event.button == 3:
                        self.hold = False
        
    def display(self, windowSurface):
        if self.dialogue.cont:
            #display dialogue before level start
            self.dialogue.display(windowSurface, self)
        
        elif self.fadeout:

            #fades to black and shows score and time
            windowSurface = self.deadscreen
            if self.retrycount % 10 == 0:
                self.deadscreen.fill((random.randrange(200,255),random.randrange(200,255),random.randrange(200,255), 25), None, pygame.BLEND_RGBA_MULT)
            basicFont = pygame.font.Font('joystix monospace.ttf', 70)
            
            if self.retrycount > 120:
                text = basicFont.render("LEVEL COMPLETE", True, YELLOW)
                textRect = text.get_rect()
                textRect.center = (WINDOWWIDTH/2, 200)
                windowSurface.blit(text, textRect)
                
            if self.retrycount > 240:
                text = basicFont.render("SCORE: "+str(self.score), True, YELLOW)
                textRect = text.get_rect()
                textRect.center = (WINDOWWIDTH/2, 400)
                windowSurface.blit(text, textRect)
                
            if self.retrycount > 360:
                text = basicFont.render("Time: "+str(round(self.endtime-self.starttime,2)), True, YELLOW)
                textRect = text.get_rect()
                textRect.center = (WINDOWWIDTH/2, 600)
                windowSurface.blit(text, textRect)
            
                
            pygame.display.update()
            self.retrycount +=1
            
        elif self.retry:
            #fades to red and asks to retry
            
            windowSurface = self.deadscreen
            if self.retrycount < 100:
                self.deadscreen.fill((255, 0, 0, 12), None, pygame.BLEND_RGBA_MULT)
                
            else:
                basicFont = pygame.font.Font('joystix monospace.ttf', 70)
                text = basicFont.render("PRESS R TO RETRY", True, WHITE)
                textRect = text.get_rect()
                textRect.center = (WINDOWWIDTH/2, WINDOWHEIGHT/2)
                windowSurface.blit(text, textRect)
            self.retrycount +=1
            pygame.display.update()
            
        else:
            # draw the black background onto the surface
            windowSurface.fill(BLACK)
            self.backgroundgroup.draw(windowSurface)
            self.current.obstas.draw(windowSurface)
            self.current.enemies.draw(windowSurface)

            #draw enemy bullets and dropped weapon
            for enemy in self.current.enemies.sprites():
                if type(enemy.weapon) == Weapon:
                    enemy.weapon.bulletgroup.draw(windowSurface)
                if enemy.weapon.groundtype:
                    pygame.draw.rect(windowSurface, (random.randrange(200,255),random.randrange(200,255),random.randrange(200,255)), enemy.weapon.rect, 3)
                    windowSurface.blit(enemy.weapon.image, enemy.weapon.rect)
                    
            #updates player bullets  
            if type(self.player.weapon) == Weapon:
                self.player.weapon.bulletgroup.draw(windowSurface)
            
            

            #draws player        
            self.playergroup.draw(windowSurface)
            

            
            #draw the ammo count
            if type(self.player.weapon) == Weapon:
                string = str(self.player.weapon.name)+": "+str(self.player.weapon.ammo)
            else:
                string = str(self.player.weapon.name)
                
            basicFont = pygame.font.Font('joystix monospace.ttf', 40)
            text = basicFont.render(string, True, WHITE, BLACK)
            textRect = text.get_rect()
            textRect.bottomright = (WINDOWWIDTH + random.randrange(-self.combo,self.combo),WINDOWHEIGHT + random.randrange(-self.combo,self.combo)) 
            pygame.draw.rect(windowSurface, BLACK, (textRect.left, textRect.top, textRect.width, textRect.height))
            windowSurface.blit(text, textRect)

            #draw the score
            basicFont = pygame.font.Font('joystix monospace.ttf', 40)
            text = basicFont.render("Score: "+str(self.score), True, WHITE, BLACK)
            textRect = text.get_rect()
            textRect.bottomleft = (0 + random.randrange(-self.combo,self.combo),WINDOWHEIGHT + random.randrange(-self.combo,self.combo)) 
            pygame.draw.rect(windowSurface, BLACK, (textRect.left, textRect.top, textRect.width, textRect.height))
            windowSurface.blit(text, textRect)

            #draw the time
            basicFont = pygame.font.Font('joystix monospace.ttf', 40)
            text = basicFont.render("Time: "+str(round(time.time()-self.starttime, 2)), True, WHITE, BLACK)
            textRect = text.get_rect()
            textRect.topleft = (0 + random.randrange(-self.combo,self.combo),0 + random.randrange(-self.combo,self.combo)) 
            pygame.draw.rect(windowSurface, BLACK, (textRect.left, textRect.top, textRect.width, textRect.height))
            windowSurface.blit(text, textRect)

            #draw the combo meter
            basicFont = pygame.font.Font('joystix monospace.ttf', 40)
            text = basicFont.render("Combo: "+str(self.combo), True, WHITE, BLACK)
            textRect = text.get_rect()
            textRect.topright = (WINDOWWIDTH + random.randrange(-self.combo,self.combo),0 + random.randrange(-self.combo,self.combo)) 
            pygame.draw.rect(windowSurface, BLACK, (textRect.left, textRect.top, textRect.width, textRect.height))
            windowSurface.blit(text, textRect)


            #tells user screens complete
            if self.exit and self.exitimer > 0:
                if random.randrange(0,2) == 1:
                    colour = RED
                else:
                    colour = WHITE
                    
                basicFont = pygame.font.Font('joystix monospace.ttf', 70)
                text = basicFont.render("SCREEN "+str(self.curnum+1)+" COMPLETE", True, colour)
                rect = text.get_rect()
                rect.centerx = WINDOWWIDTH/2
                
                windowSurface.blit(text, rect)
                self.exitimer -= 1
            # draw the window onto the screen
            pygame.display.update()

            
            
            
class Dialogue():
    def __init__(self, wordlist, wait):
        #string, counters and booleans for displaying text
        # + sfx
        self.q = 0
        self.countframes = 0
        self.words = wordlist
        self.word = 0
        self.cont = True
        self.stab = pygame.mixer.Sound("Music/hit.wav")
        self.stab.play()
        self.wait = wait

        

        
    def display(self, windowSurface, level):
        
        if self.word < len(self.words):
            
            #random colours backgrounds 
            windowSurface.fill((random.randrange(1,255), random.randrange(1,255), random.randrange(1,255)))

            #line movement
            self.q +=random.randrange(1,10)

            #makes the radial line
            colour = (random.randrange(1,255), random.randrange(1,255), random.randrange(1,255))
            for i in range(-180+self.q,+180+self.q, random.randrange(1,10)):
                    x = WINDOWWIDTH*math.cos(math.radians(i))+WINDOWWIDTH/2
                    y = WINDOWWIDTH*math.sin(math.radians(i))+WINDOWHEIGHT/2
                    pygame.draw.aaline(windowSurface, YELLOW, (WINDOWWIDTH/2,WINDOWHEIGHT/2),(x,y), 10)
                    
            #displays random sized text    
            basicFont = pygame.font.Font('joystix monospace.ttf', 110 + (random.randrange(-100,100) ))
            text = basicFont.render(self.words[self.word], True, BLACK)
            textRect = text.get_rect()
            textRect.center = (WINDOWWIDTH/2,WINDOWHEIGHT/2)
            windowSurface.blit(text, textRect)
            
            pygame.display.update()

            #counters increased
            self.countframes += 1

            #counter checks
            if self.countframes == self.wait:
                self.countframes = 0
                self.word += 1
                if self.word < len(self.words):
                    self.stab.play()
        else:
            #ends dialogue
            self.cont = False
            pygame.mixer.music.play(-1, 0.0)
            level.starttime = time.time()
            
class Game():

    def __init__(self):

        # set up the player and food groups
        

        
        #holds level (MAIN GAME LOGIC)
        # and booleans and a couple counters for display
        self.level = ()
        self.pause = False
        self.ingame = False
        self.levels = False
        self.help = False
        self.credits = False

        self.count = 0
        self.rectwidth = 10

        pygame.mixer.music.load("Music/bullet.wav")
        pygame.mixer.music.play(-1, 0.0)
        
    def process_events(self, windowSurface):
        if self.ingame and not self.pause:
            #ingame processing
            self.level.process(windowSurface, self)
            
        elif self.ingame and self.pause:
            #pause menu processing
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                    
                elif event.type == KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.pause = False
                        
                    elif event.key == pygame.K_m:
                        self.pause = False
                        self.ingame = False
                        pygame.mixer.music.load("Music/bullet.wav")
                        pygame.mixer.music.play(-1, 0.0)

                        
                    
        elif self.levels:
            #self.levels processing
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                    
                elif event.type == KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.levels = False
                        
                    elif event.key == pygame.K_1:
                        #sets self.level as level 1
                        # and starts ingame loop
                        self.levels = False
                        self.ingame = True
                        pygame.mixer.music.stop()
                        self.level = Level(
                                    [
                        (
                                    "Acts/Lone Road/section1.png",
                        [
                        Obs(OBSTACLES["barrier"],1200,NATY/2,50,600),
                        

                        ],
                        [(ENEMYPISTOLCLASS, 1250, 360, 110, 270, 500),
                        (ENEMYPISTOLCLASS, 1250, 720, 110, 270, 500)],
                                    pygame.Rect(int((NATX-20)*XRATIO), 0, int(20*XRATIO), int(NATY*YRATIO)),
                                    (int(100*XRATIO), int(NATY/2*YRATIO))
                        ),

                        (
                                    "Acts/Lone Road/section2.png",
                                    [Obs(OBSTACLES["redcar"],800,600,610,266)],
                                    [(ENEMYBATCLASS, 1600, 600, 110, 90, 500),
                                    (ENEMYSHOTGUNCLASS, 1400, 200, 110, 90, 1000)],
                                    pygame.Rect(int((NATX-20)*XRATIO), 0, int(20*XRATIO), int(NATY*YRATIO)),
                                    (int(100*XRATIO), int(NATY/2*YRATIO))
                        ),
			(
                                    "Acts/Lone Road/section3.png",
                                    [],
                                    [(ENEMYBATCLASS, 800, 216, 110, 90, 500),
                                     (ENEMYBATCLASS, 1000, 432, 110, 90, 500),
                                     (ENEMYBATCLASS, 1200, 648, 110, 90, 500),
				     (ENEMYBATCLASS, 1400, 864, 110, 90, 500),
					
                        ],
                                    pygame.Rect(int((NATX-20)*XRATIO), 0, int(20*XRATIO), int(NATY*YRATIO)),
                                    (int(100*XRATIO), int(NATY/2*YRATIO))
                        ),
			(
                                    "Acts/Lone Road/section4.png",
                                    
                                    [Obs(OBSTACLES["brownchair"],802,216,138,126),
					Obs(OBSTACLES["table1"], 700, 547, 294, 294),
					Obs(OBSTACLES["plant"], 545, 955, 174, 174),
					Obs(OBSTACLES["couch"], 1115, 535, 168, 336),
					Obs(OBSTACLES["table2"], 1547, 750, 252, 384),
					Obs(OBSTACLES["kitchen1"], 1590, 68, 402, 126),
					Obs(OBSTACLES["kitchen2"], 1849, 203, 132, 396),
					Obs("",391, 855, 22, 450),
					Obs("",391, 224, 22, 450),
					Obs("",1206, 347, 10, 720),
					Obs("",1206, 984, 10, 192)],
				[(ENEMYBATCLASS, 200, 200, 110, 180, 500),(ENEMYBATCLASS, 200, 880, 110, 0, 500),
				(ENEMYSMGCLASS, 1050, 120, 120, 135, 1000), (ENEMYSHOTGUNCLASS, 1800, 850, 110, 0, 500), 
				 (ENEMYSHOTGUNCLASS, 1325, 550, 110, 180, 500), (ENEMYPISTOLCLASS, 950, 950, 110, 45, 700)
				
],
					
                                    pygame.Rect(int(1770*XRATIO), int(952*YRATIO), int(129*XRATIO), int(151*YRATIO)),
                                    (int(100*XRATIO), int(NATY/2*YRATIO))
                        ),
			(
                                    "Acts/Lone Road/section5.png",
                                    
                                    [
					Obs("",1458, 118, 20, 236),
					Obs("",734, 10, 1430, 20),
					Obs("",10, 544, 20, 1087),
					Obs("",420, 1070, 1070, 20),
					Obs("",1130, 800, 20, 520),
					Obs("",1520, 1070, 800, 20),
					Obs("",1910, 650, 20, 825),
					Obs("",1760, 225, 320, 20),
					Obs("",375, 295, 250, 250),
					Obs("",375, 784, 250, 250),
					Obs("",1515, 784, 250, 250),
					Obs("",800, 550, 45, 750)],

				[(ENEMYPISTOLCLASS, 925, 420, 110, -90, 500),
				(ENEMYBATCLASS, 925, 600, 110, 0, 500),
				(ENEMYBATCLASS, 925, 780, 110, 0, 500),
				(ENEMYSMGCLASS, 1200, 725, 110, -10, 500),
				(ENEMYBATCLASS, 1450, 950, 110, 0, 500),
				(ENEMYSHOTGUNCLASS, 1715, 750, 110, 10, 500),
				(ENEMYBATCLASS, 580, 250, 110, 0, 500),
				(ENEMYBATCLASS, 580, 750, 110, 180, 500),
				(ENEMYPISTOLCLASS, 310, 50, 110, -90, 500),
				(ENEMYSHOTGUNCLASS, 310, 500, 110, -90, 500),
				(ENEMYSMGCLASS, 310, 950, 110, -90, 500),
				(ENEMYSMGCLASS, 30, 230, 110, -90, 500),
				(ENEMYSMGCLASS, 30, 740, 110, -90, 500)],
					
                                    pygame.Rect(int(820*XRATIO), int(1060*YRATIO), int(300*XRATIO), int(20*YRATIO)),
                                    (int(1800*XRATIO), int(50))),
			(
                                    "Acts/Lone Road/section6.png",
                                    
                                    [
					Obs("",400, 540, 820, 1080),
					Obs("",1520, 540, 820, 1080),
					],

				[
				(ENEMYBATCLASS, 910,400 , 110, 0, 500),
				(ENEMYBATCLASS, 910, 550, 110, 0, 500),
				(ENEMYBATCLASS, 910, 700, 110, 0, 500),
				(ENEMYBATCLASS, 960, 850, 110, 0, 500),
				(ENEMYBATCLASS, 960, 1000, 110, 0, 500),
				],
					
                                    pygame.Rect(int(820*XRATIO), int(1060*YRATIO), int(300*XRATIO), int(20*YRATIO)),
                                    (int(960*XRATIO), int(50*YRATIO))),
			(
                                    "Acts/Lone Road/section7.png",
                                    
                                    [
					Obs("",125, 540, 250, 1080),
					Obs("",1795, 540, 250, 1080),
					Obs("",870, 840, 1245, 480),
					Obs("",550, 225, 250, 420),
					Obs("",1300, 120, 1300, 275),
					],

				[
				(ENEMYBATCLASS, 280,460 , 110, 0, 500),
				(ENEMYBATCLASS, 1530,930 , 110, 0, 500),
				(ENEMYSHOTGUNCLASS, 1530, 430 , 110, 90, 800),
				(ENEMYSMGCLASS, 1100, 310 , 130, 180, 500),
				(ENEMYPISTOLCLASS, 750, 310 , 130, 220, 500),
				
				],
					
                                    pygame.Rect(int(1490*XRATIO), int(1010*YRATIO), int(170*XRATIO), int(50*YRATIO)),
                                    (int(350*XRATIO), int(50*YRATIO))),
(
                                    "Acts/Lone Road/section8.png",
                                    
                                    [
					Obs("",410, 10, 820, 20),
					Obs("",10, 540, 20, 1080),
					Obs("",960, 1070, 1920, 20),
					Obs("",1910, 540, 20, 1080),
					Obs("",1510, 10, 820, 20),
					Obs(OBSTACLES["barrier"],960, 315, 1120, 80),
					Obs("",960, 730, 50, 480),
					],

				[
				(ENEMYBATCLASS, 1820,100 , 110, 90, 500),
				(ENEMYBATCLASS, 100,100 , 110, -90, 500),
				(ENEMYSHOTGUNCLASS, 100,900 , 110, 0, 500),
				(ENEMYBATCLASS, 250,600 , 110, 0, 500),
				(ENEMYSMGCLASS, 400,900 , 110, 0, 500),
				(ENEMYBATCLASS, 550,600 , 110, 0, 500),
				(ENEMYPISTOLCLASS, 700,900 , 110, 0, 500),
				(ENEMYSHOTGUNCLASS, 1820,900 , 110, 0, 500),
				(ENEMYBATCLASS, 1670,600 , 110, 0, 500),
				(ENEMYSMGCLASS, 1520,900 , 110, 0, 500),
				(ENEMYBATCLASS, 1370,600 , 110, 0, 500),
				(ENEMYPISTOLCLASS, 1220,900 , 110, 0, 500),
				],
					
                                    pygame.Rect(int(0*XRATIO), int(0*YRATIO), int(NATX*XRATIO), int(NATY*YRATIO)),
                                    (int(960*XRATIO), int(50*YRATIO))),
]
                        
                                    ,

                                "Music/skyline.wav",
                                    Dialogue(str("ENTER THE TOWN.").split(), 60),
                                    Player(Bat(10, "BAT", "Weapons/Bat/swing.wav", False, False, (0,0))))


                        
        elif self.help or self.credits:
            #help and credits lprocessing
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                    
                elif event.type == KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.help = False
                        self.credits = False

                        
        else:
            #menu processing
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                    
                elif event.type == KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        terminate()
                        
                    elif event.key == pygame.K_1:
                        self.levels = True
                    
                    elif event.key == pygame.K_2:
                        self.help = True
                    
                    elif event.key == pygame.K_3:
                        self.credits = True
            
    def run_logic(self, windowSurface):
        if self.ingame and not self.pause:
            #run logic for ingame
            self.level.run_logic(windowSurface)
            

        
    def display_frame(self, windowSurface):
        """ Display everything to the screen for the game. """
        if self.ingame and not self.pause:
            #ingame display
            self.level.display(windowSurface)
            
        elif self.ingame and self.pause:
            #display paused screen
            basicFont = pygame.font.Font('joystix monospace.ttf', 110)
            text = basicFont.render("PAUSED", True, RED, WHITE)
            textRect = text.get_rect()
            textRect.center = (WINDOWWIDTH/2,WINDOWHEIGHT/2)
            windowSurface.blit(text, textRect)
            pygame.display.update()
            
        elif self.levels:
            #display level screen
            windowSurface.fill(BLACK)
            self.count += 1
            if self.count > self.rectwidth*2:
                self.count = 0
            for x in range(-10,WINDOWWIDTH, self.rectwidth*2):
                
                pygame.draw.rect(windowSurface, GREEN, (x+self.count, 0, self.rectwidth, WINDOWHEIGHT/2+self.count))
                pygame.draw.rect(windowSurface, WHITE, (x-self.count, WINDOWHEIGHT/2+self.count, self.rectwidth, WINDOWHEIGHT))
            bottom = 170 + random.randrange(-2,2)
            pygame.draw.rect(windowSurface, WHITE, (150, 150, WINDOWWIDTH-300, WINDOWHEIGHT-300))
            basicFont = pygame.font.Font('joystix monospace.ttf', 70 + random.randrange(-1,1))
            for string in ["A C T S", " ", "1. L o n e  R o a d"," ", "MORE TBD"]:
                text = basicFont.render(string, True, BLACK)
                textRect = text.get_rect()
                textRect.centerx = WINDOWWIDTH/2 
                textRect.top = bottom 
                bottom = textRect.bottom
                windowSurface.blit(text, textRect)

            pygame.display.update()
            
        elif self.help:
            #display help
            windowSurface.fill(BLACK)
            self.count += 1
            if self.count > self.rectwidth*2:
                self.count = 0
            for x in range(-10,WINDOWWIDTH, self.rectwidth*2):
                
                pygame.draw.rect(windowSurface, BLUE, (x+self.count, 0, self.rectwidth, WINDOWHEIGHT/2+self.count))
                pygame.draw.rect(windowSurface, WHITE, (x-self.count, WINDOWHEIGHT/2+self.count, self.rectwidth, WINDOWHEIGHT))
            bottom = 170 + random.randrange(-2,2)
            counter = 0
            pygame.draw.rect(windowSurface, WHITE, (150, 150, WINDOWWIDTH-300, WINDOWHEIGHT-300))
            for string in ["I N S T R U C T I O N S"," ", "WASD TO MOVE", " ",   "MOUSE TO AIM"," ",   "LEFT CLICK TO SHOOT, RIGHT CLICK TO PICK UP"," ", "DISPATCH ENEMIES TO GET TO NEXT SCREEN"," ",  "COMPLETE ALL SCREENS TO FINISH LEVEL", " ", "TRY NOT TO DIE"]:
                basicFont = pygame.font.Font('joystix monospace.ttf', 45 -counter + random.randrange(-1,1))
                text = basicFont.render(string, True, BLACK)
                textRect = text.get_rect()
                textRect.centerx = WINDOWWIDTH/2 
                textRect.top = bottom 
                bottom = textRect.bottom
                windowSurface.blit(text, textRect)
                counter += 2
            pygame.display.update()

            
        elif self.credits:
            #display credits
            windowSurface.fill(BLACK)
            self.count += 1
            if self.count > self.rectwidth*2:
                self.count = 0
            for x in range(-10,WINDOWWIDTH, self.rectwidth*2):
                
                pygame.draw.rect(windowSurface, YELLOW, (x+self.count, 0, self.rectwidth, WINDOWHEIGHT/2+self.count))
                pygame.draw.rect(windowSurface, WHITE, (x-self.count, WINDOWHEIGHT/2+self.count, self.rectwidth, WINDOWHEIGHT))
            bottom = 170 + random.randrange(-2,2)
            counter = 0
            pygame.draw.rect(windowSurface, WHITE, (150, 150, WINDOWWIDTH-300, WINDOWHEIGHT-300))
            for string in ["C R E D I T S"," ", "PROGRAMMING BY CALLUM GILLIES", " ",   "ARTWORK BY REGAN GILLIES"," ",   "MUSIC BY CALLUM GILLIES", " ", "LOOSELY INSPIRE BY HOTLINE MIAMI 1 + 2", " ", "THANKS FOR PLAYING :)"]:
                basicFont = pygame.font.Font('joystix monospace.ttf', 45 -counter + random.randrange(-1,1))
                text = basicFont.render(string, True, BLACK)
                textRect = text.get_rect()
                textRect.centerx = WINDOWWIDTH/2 
                textRect.top = bottom 
                bottom = textRect.bottom
                windowSurface.blit(text, textRect)
                counter += 2
            pygame.display.update()
            
        else:
            #displays main menu
            windowSurface.fill(BLACK)
            self.count += 1
            if self.count > self.rectwidth*2:
                self.count = 0
            for x in range(-10,WINDOWWIDTH, self.rectwidth*2):
                
                pygame.draw.rect(windowSurface, WHITE, (x+self.count, 0, self.rectwidth, WINDOWHEIGHT/2+self.count))
                pygame.draw.rect(windowSurface, RED, (x-self.count, WINDOWHEIGHT/2+self.count, self.rectwidth, WINDOWHEIGHT))
            bottom = 170 + random.randrange(-2,2)
            pygame.draw.rect(windowSurface, WHITE, (150, 150, WINDOWWIDTH-300, WINDOWHEIGHT-300))
            
            for string in ["C U L T R A"," ", "1. P L A Y", " ", "2. H E L P", " ", "3. C R E D I T S"]:
                basicFont = pygame.font.Font('joystix monospace.ttf', 65  + random.randrange(-1,1))
                text = basicFont.render(string, True, BLACK)
                textRect = text.get_rect()
                
                textRect.centerx = WINDOWWIDTH/2 + random.randrange(-1,1)
                textRect.top = bottom + random.randrange(-1,1)
                bottom = textRect.bottom
                windowSurface.blit(text, textRect)
                
            pygame.display.update()
        

def main():
    pygame.init()
    mainClock = pygame.time.Clock()

    windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
    pygame.display.set_caption('CULTRA')

    #makes global movement sprites and gun classes and obstacles so that the images don't have to get loaded multiple times
    #increasing speed
    
    global ENEMYSHOTGUN
    global PLAYERSHOTGUN
    global SHOTGUNGROUND

    global ENEMYPISTOL
    global PLAYERPISTOL
    global PISTOLGROUND

    global ENEMYSMG
    global PLAYERSMG
    global SMGGROUND

    global ENEMYBATWALK
    global PLAYERBATWALK
    global ENEMYBATSWING
    global PLAYERBATSWING
    global BATGROUND

    global ENEMYSHOTGUNCLASS 

    global ENEMYPISTOLCLASS 

    global ENEMYSMGCLASS 
    
    global ENEMYBATCLASS

    global OBSTACLES
    
    ENEMYSHOTGUN = [pygame.image.load("Weapons\Shotgun\enemywalk\enemyshotgunwalk1.png").convert_alpha(),pygame.image.load("Weapons\Shotgun\enemywalk\enemyshotgunwalk2.png").convert_alpha(),pygame.image.load("Weapons\Shotgun\enemywalk\enemyshotgunwalk3.png").convert_alpha(),pygame.image.load("Weapons\Shotgun\enemywalk\enemyshotgunwalk4.png").convert_alpha()]
    PLAYERSHOTGUN = [pygame.image.load("Weapons\Shotgun\playerwalk\playershotgunwalk1.png").convert_alpha(),pygame.image.load("Weapons\Shotgun\playerwalk\playershotgunwalk2.png").convert_alpha(),pygame.image.load("Weapons\Shotgun\playerwalk\playershotgunwalk3.png").convert_alpha(),pygame.image.load("Weapons\Shotgun\playerwalk\playershotgunwalk4.png").convert_alpha()]
    SHOTGUNGROUND = pygame.image.load("Weapons\Shotgun\shotgunground.png").convert_alpha()
    
    ENEMYPISTOL = [pygame.image.load("Weapons\Pistol\enemywalk\enemypistolwalk1.png").convert_alpha(),pygame.image.load("Weapons\Pistol\enemywalk\enemypistolwalk2.png").convert_alpha(),pygame.image.load("Weapons\Pistol\enemywalk\enemypistolwalk3.png").convert_alpha(),pygame.image.load("Weapons\Pistol\enemywalk\enemypistolwalk4.png").convert_alpha()]
    PLAYERPISTOL = [pygame.image.load("Weapons\Pistol\playerwalk\playerpistolwalk1.png").convert_alpha(),pygame.image.load("Weapons\Pistol\playerwalk\playerpistolwalk2.png").convert_alpha(),pygame.image.load("Weapons\Pistol\playerwalk\playerpistolwalk3.png").convert_alpha(),pygame.image.load("Weapons\Pistol\playerwalk\playerpistolwalk4.png").convert_alpha()]
    PISTOLGROUND = pygame.image.load("Weapons\Pistol\pistolground.png").convert_alpha()
    
    ENEMYSMG = [pygame.image.load("Weapons\Smg\enemywalk\enemysmgwalk1.png").convert_alpha(),pygame.image.load("Weapons\Smg\enemywalk\enemysmgwalk2.png").convert_alpha(),pygame.image.load("Weapons\Smg\enemywalk\enemysmgwalk3.png").convert_alpha(),pygame.image.load("Weapons\Smg\enemywalk\enemysmgwalk4.png").convert_alpha()]
    PLAYERSMG = [pygame.image.load("Weapons\Smg\playerwalk\playersmgwalk1.png").convert_alpha(),pygame.image.load("Weapons\Smg\playerwalk\playersmgwalk2.png").convert_alpha(),pygame.image.load("Weapons\Smg\playerwalk\playersmgwalk3.png").convert_alpha(),pygame.image.load("Weapons\Smg\playerwalk\playersmgwalk4.png").convert_alpha()]
    SMGGROUND = pygame.image.load("Weapons\Smg\smgground.png").convert_alpha()
    
    ENEMYBATWALK = [pygame.image.load("Weapons\Bat\enemywalk\enemybatwalk1.png").convert_alpha(),pygame.image.load("Weapons\Bat\enemywalk\enemybatwalk2.png").convert_alpha(),pygame.image.load("Weapons\Bat\enemywalk\enemybatwalk3.png").convert_alpha(),pygame.image.load("Weapons\Bat\enemywalk\enemybatwalk4.png").convert_alpha()]
    PLAYERBATWALK = [pygame.image.load("Weapons\Bat\playerwalk\playerbatwalk1.png").convert_alpha(),pygame.image.load("Weapons\Bat\playerwalk\playerbatwalk2.png").convert_alpha(),pygame.image.load("Weapons\Bat\playerwalk\playerbatwalk3.png").convert_alpha(),pygame.image.load("Weapons\Bat\playerwalk\playerbatwalk4.png").convert_alpha()]
    ENEMYBATSWING = [pygame.image.load("Weapons\Bat\enemybatswing\enemybatswing1.png").convert_alpha(),pygame.image.load("Weapons\Bat\enemybatswing\enemybatswing2.png").convert_alpha(),pygame.image.load("Weapons\Bat\enemybatswing\enemybatswing3.png").convert_alpha(),pygame.image.load("Weapons\Bat\enemybatswing\enemybatswing4.png").convert_alpha()]
    PLAYERBATSWING = [pygame.image.load("Weapons\Bat\playerbatswing\playerbatswing1.png").convert_alpha(),pygame.image.load("Weapons\Bat\playerbatswing\playerbatswing2.png").convert_alpha(),pygame.image.load("Weapons\Bat\playerbatswing\playerbatswing3.png").convert_alpha(),pygame.image.load("Weapons\Bat\playerbatswing\playerbatswing4.png").convert_alpha()]
    BATGROUND = pygame.image.load("Weapons/Bat/batground.png").convert_alpha()   

    PLAYERSHOTGUNCLASS = (PLAYERSHOTGUN,ENEMYSHOTGUN, 60, 6, 7, 150, 60, 8, 2, "SHOTGUN", "Weapons/Shotgun/shotgun.wav", False, False, (0,0), SHOTGUNGROUND)
    ENEMYSHOTGUNCLASS = (PLAYERSHOTGUN,ENEMYSHOTGUN, 60, 6, 7, 150, 60, 8, 2, "SHOTGUN", "Weapons/Shotgun/shotgun.wav", True, False, (0,0), SHOTGUNGROUND)

    PLAYERPISTOLCLASS = (PLAYERPISTOL, ENEMYPISTOL, 20, 1, 12, 5, 80, 7, 6, "PISTOL", "Weapons/Pistol/pistol.wav", False, False, (0,0), PISTOLGROUND)
    ENEMYPISTOLCLASS = (PLAYERPISTOL, ENEMYPISTOL, 20, 1, 7, 5, 80, 7, 6, "PISTOL", "Weapons/Pistol/pistol.wav", True, False, (0,0), PISTOLGROUND)

    PLAYERSMGCLASS= (PLAYERSMG, ENEMYSMG, 3, 1, 8, 40, 70, 2, 12, "SMG", "Weapons/Smg/smg.wav", False, False, (0,0), SMGGROUND)
    ENEMYSMGCLASS = (PLAYERSMG, ENEMYSMG, 3, 1, 8, 40, 70, 2, 12, "SMG", "Weapons/Smg/smg.wav", True, False, (0,0), SMGGROUND)

    PLAYERBATCLASS = (10, "BAT", "Weapons/Bat/swing.wav", False, False, (0,0))
    ENEMYBATCLASS = (10, "BAT", "Weapons/Bat/swing.wav", True, False, (0,0))

    OBSTACLES = {"bluecar":"Obstacles/bluecar.png","redcar":"Obstacles/redcar.png","box":"Obstacles/box.png","crate":"Obstacles/crate.png", "barrier":"Obstacles/barrier.png", "brownchair":"Obstacles/brownchair.png", "bluechair":"Obstacles/brownchair.png",
                 "couch":"Obstacles/couch.png", "plant":"Obstacles/plant.png", "kitchen1":"Obstacles/kitchen1.png", "kitchen2":"Obstacles/kitchen2.png","table1":"Obstacles/table1.png", "table2":"Obstacles/table2.png", }

    #initializes game
    game = Game()
    

    # run the game loop until the user quits
    while True:
        
        # Process events (keystrokes, mouse clicks, etc)
        game.process_events(windowSurface)

        # Update object positions, check for collisions
        game.run_logic(windowSurface)

        # Draw the current frame
        game.display_frame(windowSurface)

        mainClock.tick(FRAMERATE)

main()
