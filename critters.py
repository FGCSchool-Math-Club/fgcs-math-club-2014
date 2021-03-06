import argparse
from random import *
import math
from geo2d.geometry import *
import itertools
from tkinter import *
import time
from intervalset import AngularIntervalSet,odd
import sys,traceback
from collections import namedtuple

def random_color():
    return "#%02x%02x%02x" % (randrange(0,255),randrange(0,255),randrange(0,255))

def as_color(r,g,b):
    return "#%02x%02x%02x" % (255*r,255*g,255*b)

def gray(x):
    return as_color(x,x,x)

def Heading(dir,rho=None):
    return Vector(rho or 1.0,dir,coordinates="polar")

def overlap(poly1,poly2,c1=None,c2=None,r1=None,r2=None):
    b1 = poly1.bounding_box
    b2 = poly2.bounding_box
    c1 = c1 or poly1.centroid
    c2 = c2 or poly1.centroid
    r1 = r1 or poly1.diameter
    r2 = r2 or poly2.diameter
    d = r1+r2
    c = Point((r1*c1.x+r2*c2.x)/d,(r1*c1.y+r2*c2.y)/d)
    # This isn't the right value for o -- the real overlap is lense shaped.
    o = d - c1.distance_to(c2)
    if o < 0 or b1.left > b2.right or b1.right < b2.left or b1.top < b2.bottom or b1.bottom > b2.top:
        return False
    for p1 in poly1.vertices:
        if c.distance_to(p1) < o and poly2.has(p1):
            return True
    for p2 in poly2.vertices:
        if c.distance_to(p2) < o and poly1.has(p2):
            return True
    e2_near_edges = [e for e in poly2.edges if c.distance_to(e) < o and e.length > 0]
    for e1 in poly1.edges:
        if c.distance_to(e1) < o and e1.length > 0:
            for e2 in e2_near_edges:
                if e1.intersection(e2):
                    return True
    return False

class DisplayObject:
    def __init__(self,world,loc):
        self.world = world
        self.location = loc
    def on_tick(self):
        pass
    def draw(self, canvas,s):
        pass
    def remove_image(self,canvas):
        for part in self.tk_ids.values(): canvas.delete(part)
        self.tk_ids = {}
    def place_image_part(self,part,canvas,s,*coords):
        canvas.coords(self.tk_ids[part],*[s*coord for coord in coords])
    def displacement_to(self,other):
        loc = other.location if hasattr(other, "location") else other
        return self.world.wrap(Vector(self.location,loc))
    def distance_to(self,other):
        return self.displacement_to(other).rho

def stipple(r):
    if   r < 12: return 'gray12'
    elif r < 25: return 'gray25'
    elif r < 50: return 'gray50'
    elif r < 75: return 'gray75'
    else:        return 'gray75' #None


class Sound(DisplayObject):
    def __init__(self,world,loc,volume,text):
        DisplayObject.__init__(self,world,loc)
        self.volume = volume
        self.text   = text
        self.tk_ids = {}
        self.age    = 1
        self.faded  = False
    def on_tick(self):
        self.age += 1
    def draw(self, canvas, s):
        self.remove_image(canvas)
        if self.age < self.volume:
            loc  = self.location
            self.tk_ids = {
                'text': canvas.create_text(
                    s*loc.x, s*loc.y-20,
                    text=self.text,
                    font=('Helvetica',int(s*((self.volume+self.age)/10)**2)),
                    fill=gray(max(self.age/self.volume-0.2,0)),
                    stipple=stipple(100-(self.age*100)/self.volume)
                    )
                }
        else:
            self.faded = True

class PhysicalObject(DisplayObject):
    collision_cost    = 10
    def __init__(self,world,loc):
        DisplayObject.__init__(self,world,loc)
        self.tk_ids = {}
        self.color = {"fill": "black"}
        self.mass = 10000.0        # Achored to the ground
        self.heading = Vector(0,0) # Going nowhere
        self.hardness = 0.01
        self.dead = False
        self.goal = False
        self.anchored = False
        self.floor_mat = False
    def dump_status(self):
        print(self.location)
    def on_collision(self,dir,other):
        pass
    def on_damage(self,amount):
        pass
    def radius(self):
        return 1
    def core_radius(self):
        return self.radius()
    def outline(self):
        r    = self.radius()
        loc  = self.location
        sides = 8
        q    = 2*math.pi/sides
        return [(loc.x+r*math.cos(a*q),loc.y+r*math.sin(a*q)) for a in range(0,sides)]
    def die(self,*args):
        self.dead = True
    def draw(self, canvas,s):
        r = self.radius()
        if r > 0 and not self.dead:
            if not self.tk_ids:
                self.tk_ids = { 'image': canvas.create_oval(50, 50, s*2*r, s*2*r, **self.color) }
            canvas.tag_lower(self.tk_ids['image'])
            loc = self.location
            self.place_image_part('image',canvas,s,loc.x-r, loc.y-r,loc.x+r, loc.y+r)
        else:
            self.remove_image(canvas)

class Block(PhysicalObject):
    def __init__(self,world,loc,l=10,w=1,heading=None,density=1):
        PhysicalObject.__init__(self,world,loc)
        self.heading = heading or Heading(uniform(0.0,2*math.pi))*0.0001
        self.length = l
        self.width  = w
        self.mass   = l*w*density
        self.color  = {"fill":"brown", "stipple":'gray75'}
        self.hardness = 1.0
        self.anchored = True
    def outline(self):
        loc = self.location
        h = self.heading.normalized
        l = self.length
        w = self.width
        lx,ly = l*h.x, l*h.y
        wx,wy = w*h.y,-w*h.x
        return [
            (loc.x+lx+wx,loc.y+ly+wy),
            (loc.x+lx-wx,loc.y+ly-wy),
            (loc.x-lx-wx,loc.y-ly-wy),
            (loc.x-lx+wx,loc.y-ly+wy),
            ]
    #def on_tick(self):
    #    self.heading = Heading(self.heading.phi+0.01)*0.0001
    def core_radius(self):
        return min(self.length,self.width)
    def create_image(self,canvas):
        self.tk_ids = { 'body':  canvas.create_polygon(1,1,**self.color) }
    def place_image(self,canvas,s):
        self.place_image_part('body', canvas,s,*[coord for p in self.outline() for coord in p])
    def draw(self, canvas,s):
        if self.dead:
            self.remove_image(canvas)
        else:
            if not self.tk_ids: self.create_image(canvas)
            self.place_image(canvas,s)
    def radius(self):
        return math.sqrt(self.length**2+self.width**2)

class Secretion(DisplayObject):
    trails = []
    undrawn = []
    dead = set()
    resized = set()
    def __init__(self,world,loc):
        DisplayObject.__init__(self,world,loc)
        self.size = 2
        self.tk_id = None
        Secretion.undrawn.append(self)
    def on_tick():
        for t in range(0,100):
            i = randrange(0,1000)
            if i < len(Secretion.trails):
                if Secretion.trails[i].size < 15:
                    Secretion.resized.add(Secretion.trails[i])
                else:
                    Secretion.dead.add(Secretion.trails.pop(i))
        while len(Secretion.trails) > 1000:
            Secretion.dead.add(Secretion.trails.pop(randrange(0,len(Secretion.trails))))
    def on_draw(canvas,s):
        for t in Secretion.undrawn:
            loc = t.location
            t.tk_id = canvas.create_oval(loc.x*s-1, loc.y*s-1, loc.x*s+1, loc.y*s+1, outline="blue")
            Secretion.trails.append(t)
        Secretion.undrawn = []
        for t in Secretion.resized:
            x1,y1,x2,y2 = canvas.coords(t.tk_id)
            canvas.coords(t.tk_id,x1-1,y1-1,x2+1,y2+1)
            canvas.itemconfig(t.tk_id,outlinestipple=stipple(100-3*(x2-x1)))
        for t in Secretion.dead: canvas.delete(t.tk_id)
        Secretion.dead.clear()
        Secretion.resized.clear()

class Critter(PhysicalObject):
    def __init__(self,world,brain_class,name):
        PhysicalObject.__init__(self,world,None)
        if isinstance(name,int):
            name = brain_class.owner + brain_class.code + str(name)
        self.name  = name
        self.heading = Heading(uniform(0.0,2*math.pi))
        profile = [uniform(0.5,0.8) for i in range(0,10)]
        self.shape   = [1.0,0.8]+profile+list(reversed(profile))+[0.8]
        self.mass = 25
        self.color = {"fill":random_color(), "smooth":1, "stipple":'gray50'}
        self.brain = brain_class()
        self.last_spoke = -10
        self.sense_data = None
        self.whats_under = set()
        self.age = 0
        self.hardness = 0.5
        self.secreting = None
        self.finished = 0
        self.sense_depiction_ids = []
        world.spawn(self)
    def dump_status(self):
        print(self.name)
        self.brain.dump_status()
        print(self.location)
    metabolic_cost    = 0.01
    movement_cost     = 0.1
    acceleration_cost = 40
    def on_tick(self):
        if self.dead: return
        if not self.undead(): self.age += 1
        for x in list(self.whats_under):
            if x.radius() <= 0 or self.distance_to(x) > self.radius() + x.radius():
                self.whats_under.remove(x)
        self.sense_data = self.senses()
        self.mass -= self.metabolic_cost + self.movement_cost*self.heading.rho*self.heading.rho
        if self.mass <= 0:
            self.die(sound="..nnn...nnn..nnn...",volume=6)
        else:
            self.act(self.brain_on_tick() or "Pass")
            self.location.translate(self.heading.x,self.heading.y)
            self.location = self.world.wrap(self.location)
    def on_damage(self,amount):
        if amount > 0.1:
            self.say("Ooof!")
        self.mass  -= amount
        if self.mass <= 0:
            self.die(volume=0)
    def on_collision(self,dir,other):
        if other.goal:
            self.die("Yes!")
            self.finished += self.age
        self.whats_under.add(other)
        self.act(self.brain_on_collision(dir,other) or ("Eat" if isinstance(other,Food) else "Pass"))
    def teleport_to(self,world,loc):
        self.world    = world
        self.location = loc
    def die(self,sound="Aaaaaaaaa...!",volume=20):
        self.mass = 0
        if not self.dead:
            self.say(sound,volume=volume)
            PhysicalObject.die(self)
    def arise(self):
        if self.dead:
            self.dead = None
            self.mass = 15
            self.metabolic_cost = 0.0
            self.movement_cost  = 0.0
            self.color["outline"] = "green"
            self.color["width"] = 2
            self.brain = ZombieBrain()
    def undead(self):
        return (self.dead is not True) and (self.dead is not False)
    def say(self,msg,volume=10):
        if not self.dead:
            if self.world.clock - self.last_spoke > 10:
                self.world.sound(self.location,volume,msg)
                self.last_spoke = self.world.clock
    max_speed = 2.5
    def act(self,cmd):
        if self.dead: return
        if self.secreting and randrange(0,2) == 0:
            Secretion(self.world,self.location)
        sharpest_turn = 0.5
        if not cmd is None:
            word = cmd.split()
            if word[0] == "Stop":
                self.heading = self.heading.normalized*(1/10000)
            elif word[0] == "Go":
                self.heading = self.heading.normalized
            elif word[0] == "Turn":
                self.heading = Heading(self.heading.phi+sorted([-sharpest_turn,float(word[1]),sharpest_turn])[1],rho=self.heading.rho)
            elif word[0] == "Accelerate":
                initial_speed = self.heading.rho
                self.heading *= float(word[1])
                if self.heading.rho > self.max_speed:
                    self.heading *= self.max_speed/self.heading.rho
                #if self.heading.rho != initial_speed:
                #    print("%s lost %5.3f accelerating %5.3f -> %5.3f" %
                #        (self.name,self.acceleration_cost*(self.heading.rho-initial_speed)**2,initial_speed,self.heading.rho))
                self.mass -= self.acceleration_cost*(self.heading.rho-initial_speed)**2
            elif word[0] == "Attack":
                pass
            elif word[0] == "Eat":
                for f in self.whats_under:
                    if isinstance(f,Food) and f.value > 0:
                        self.say("Yum")
                        f.value -= 0.1
                        self.mass += 0.1
                        break
            elif word[0] == "Pass":
                pass
            elif word[0] == "Secrete":
                if word[1] == "Nothing" or word[1] == "0":
                    self.secreting = None
                else:
                    self.secreting = int(word[1])
            elif word[0] == "Say":
                self.say(cmd[4:])
            else:
                print("Unknown command: {}".format(cmd))
    def radius(self):
        return math.sqrt(self.mass) if self.mass > 0 else 0
    def core_radius(self):
        return self.radius()*min(self.shape)
    def relative_heading(self,x):
        return (x-self.heading.phi+math.pi) % 2*math.pi + math.pi
    def relative_heading_to(self,x):
        return self.relative_heading(self.displacement_to(x).phi)
    Sight = namedtuple("Sight", "color distance direction width change")
    Sound = namedtuple("Sound", "text direction volume age")
    Smell = namedtuple("Smell", "smell strength change")
    State = namedtuple("State", "moving speed health age")
    def senses(self):
        return {
            'sight':   self.sight(), # set of tuples: (color,distance,direction,width,change)
            'smell':   set(), # set of tuples: (smell,strength,change)
            'hearing': set([Critter.Sound(s.text,self.relative_heading_to(s),s.volume/(1+self.distance_to(s)),s.age) for s in self.world.sounds]),
            'taste':   set([type(x) for x in self.whats_under]),
            'body':    Critter.State(self.heading.rho>0.1,self.heading.rho,self.mass,self.age),
            'gps':     self.location,
            'compass': self.heading.phi,
          }
    def sight(self):
        objects = [((self.world.width+self.world.height)/8,0,AngularIntervalSet(-1.0,1.0),self.world)]
        forward = self.heading.phi
        for o in self.world.neighbors_of(self):
            if o != self:
               d = self.displacement_to(o)-self.eye_offset()
               d -= d*(o.radius()/d.rho)
               # We can only see things above our horizon, which we aproximate be saying they have
               #     to be within a quarter of the way around in either direction.
               if (d.x/self.world.width)**2 + (d.y/self.world.height)**2 < (1/4)**2:
                   # We can only see things in front of us
                   a = (d.phi-forward+math.pi) % (2*math.pi) - math.pi
                   delta_a = math.atan2(o.radius(),d.rho)
                   if abs(a)-abs(delta_a) < 1:
                       objects.append((d.rho,uniform(0.0,1.0),AngularIntervalSet(a-delta_a,a+delta_a),o))
        # We can only see things within a two radian field of view
        view_mask = AngularIntervalSet(-1,+1)
        sights = set()
        for dist,rand,image,obj in sorted(objects):
             # we see all of the object not blocked by something closer
             visable_part = view_mask.intersection(image)
             # the object blocks things that are further
             view_mask    = view_mask.intersection(image.inverse())
             for segment in visable_part.ranges():
                 color = obj.color['outline'] if 'outline' in obj.color else obj.color['fill']
                 sights.add(Critter.Sight(color,dist,(segment[0]+segment[1])/2,segment[1]-segment[0],0))
             # stop when our field of view is full
             if view_mask.trivial(): break
        # TODO: figure out how to calculate change
        return sights
    def outline(self):
        r    = self.radius()
        loc  = self.location
        phi  = self.heading.phi
        q    = 2*math.pi/len(self.shape)
        return [(loc.x+r*d*math.cos(a*q+phi),loc.y+r*d*math.sin(a*q+phi)) for a, d in enumerate(self.shape)]
    def eye_offset(self):
        r    = self.radius()
        phi  = self.heading.phi
        d    = self.shape[0]*0.7
        return Vector(r*d*math.cos(phi),r*d*math.sin(phi))
    def create_image(self,canvas):
        self.tk_ids = {
            'body':  canvas.create_polygon(1,1,**self.color),
            'text':  canvas.create_text(50,50, text=self.name),
            'eye':   canvas.create_oval(50, 50, 1, 1, fill = "white"),
            'pupil': canvas.create_oval(50, 50, 1, 1, fill = "black", outline="blue"),
        }
    def place_image(self,canvas,s):
        outline = self.outline()
        loc  = self.location
        px = 1/s
        eye_off = self.eye_offset()
        x,y = loc.x+eye_off.x,loc.y+eye_off.y
        pp = self.displacement_to(self.world.pits[0] if self.world.pits else self.world.random_location()).normalized
        self.place_image_part('text', canvas,s,loc.x,loc.y)
        self.place_image_part('body', canvas,s,*[coord for p in outline for coord in p])
        self.place_image_part('eye',  canvas,s,   x-1, y-1, x+1, y+1)
        self.place_image_part('pupil',canvas,s, x+pp.x/2-px, y+pp.y/2-px, x+pp.x/2+px, y+pp.y/2+px)
    def draw(self, canvas,s):
        if self.dead:
            self.remove_image(canvas)
        else:
            if not self.tk_ids: self.create_image(canvas)
            self.place_image(canvas,s)
            self.draw_senses(canvas,s)
    def draw_senses(self,canvas,s):
        for part in self.sense_depiction_ids: canvas.delete(part)
        outline = self.outline()
        x,y = outline[0]
        sd = self.sight()
        for sight in sd: #self.sense_data['sight']:
            d = sight.distance
            h = sight.direction + self.heading.phi
            self.sense_depiction_ids.append(
                canvas.create_line(x*s,y*s, s*(x+d*math.cos(h)),s*(y+d*math.sin(h)), fill=sight.color,stipple=stipple(200/(d+1)))
                )
    def brain_on_tick(self):
        try:
            return self.brain.on_tick(self.sense_data)
        except Exception as e:
            traceback.print_tb(sys.exc_info()[-1], limit=3)
            self.die()
    def brain_on_collision(self,dir,other):
        try:
            return self.brain.on_collision(dir,other,self.sense_data)
        except Exception as e:
            traceback.print_tb(sys.exc_info()[-1], limit=3)
            self.die()

class CritterBrain:
    code  = ''
    owner = None
    def dump_status(self):
        pass
    def on_collision(self,dir,other,senses):
        pass
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        pass

class ZombieBrain(CritterBrain):
    def on_tick(self,senses):
        non_green = [c for c in senses['sight'] if c.color != 'green']
        closest = min(non_green, key=lambda s: s.distance) if non_green else None
        target  = closest.direction if closest else uniform(-0.2,0.1) if senses['compass'] > math.pi else uniform(-0.1,0.2)
        if randrange(0,50) == 0:
            return "Say Brains...."
        elif randrange(0,50) == 0:
            return "Say Urrrr...."
        elif senses['body'].speed > 0.2:
            return "Accelerate {}".format(0.1/senses['body'].speed)
        else:
            return "Turn {}".format(target)

class Food(PhysicalObject):
    def __init__(self,world,loc,value):
        PhysicalObject.__init__(self,world,loc)
        self.value = value
        self.color = {"fill": "dark green", "outline": "green", "width":3}
        self.anchored = True
        self.floor_mat = True
    def on_tick(self):
        # Could spoil, spread, or...?
        pass
    def on_collision(self,dir,other):
        pass
    def radius(self):
        if self.value < 0: self.value = 0
        return math.sqrt(self.value)

class Pit(PhysicalObject):
    def __init__(self,world,loc):
        PhysicalObject.__init__(self,world,loc)
        self.r = 10
        self.color = {"fill": "black", "outline": "dark red"}
        self.anchored = True
    def on_tick(self):
        pass
    def on_collision(self,dir,other):
        other.location = self.location
        other.die()
    def radius(self):
        return self.r

class GoldStar(Block):
    def __init__(self,world,loc):
        PhysicalObject.__init__(self,world,loc)
        self.r = 5
        self.color = {"fill": "gold"}
        self.anchored = True
    def on_tick(self):
        pass
    def on_collision(self,dir,other):
        other.finished -= 50
        self.location = self.world.random_location()
    def radius(self):
        return self.r
    def core_radius(self):
        return self.radius()/2
    def outline(self):
        r    = [self.radius(),self.core_radius()]
        loc  = self.location
        sides = 10
        q    = 2*math.pi/sides
        return [(loc.x+r[a%2]*math.cos(a*q),loc.y+r[a%2]*math.sin(a*q)) for a in range(0,sides)]

class World:
    height = 100
    width  = 200
    neighborhood_refresh = 4
    neighborhood_radius_x = width/6 +Critter.max_speed*neighborhood_refresh
    neighborhood_radius_y = height/6+Critter.max_speed*neighborhood_refresh
    color = {"fill":"#000"}
    def __init__(self,tick_time=0.1,tick_limit=-1,food=50,pits=0,stars=0,warn=False,blocks=0,zombies=False,stop_count=None):
        self.critters = []
        self.starting_critters = []
        self.world_view = WorldView(self,5)
        self.food   = [Food(self,self.random_location(),randrange(2,16)) for i in range(0,food)]
        self.pits   = [Pit(self,self.random_location()) for i in range(0,pits)]
        self.stars  = [GoldStar(self,self.random_location()) for i in range(0,stars)]
        self.blocks = [Block(self,self.random_location(),randrange(1,10),randrange(1,10))  for i in range(0,blocks)]
        #self.finish_line()
        self.maze(6,12)
        self.sounds = []
        self.clock = 0
        self.neighbors = {}
        self.tick_time = tick_time
        self.tick_limit = tick_limit
        self.warn = warn
        self.zombies_allowed = zombies
        self.zombies = []
        self.stop_count = stop_count
    def finish_line(self):
        fl_segments = 10
        fl_height = self.height / fl_segments
        for i in range(0,fl_segments):
            self.blocks.append(Block(self,Point(self.width-15,(i+0.5)*fl_height),1,fl_height/2-0.1,Heading(0),10000))
            self.blocks[-1].goal = True
    def maze(self,h,w):
        walls = set([(x,y) for x in range(0,2*w) for y in range(0,2*h) if odd(x) != odd(y)])
        cells = set([(0,0)])
        while len(cells) < h*w:
            x,y = (2*randrange(0,w),2*randrange(0,h))
            dir = randrange(0,2)
            dist = 4*randrange(0,2)-2
            #x0,y0 = ((x+dir*dist) % (2*w),(y+(1-dir)*dist) % (2*h))
            x0,y0 = (x+dir*dist,y+(1-dir)*dist)
            if (0 <= x0 < 2*w) and (0 <= y0 < 2*h) and ((x0,y0) in cells) != ((x,y) in cells):
                cells.add((x0,y0) if (x,y) in cells else (x,y))
                #print((x,y),(x0,y0))
                if dist < 0:
                    walls.remove((x0-(dir*dist)//2,y0-((1-dir)*dist)//2))
                else:
                    walls.remove((x +(dir*dist)//2,y +((1-dir)*dist)//2))
        cell_w = self.width/(2*w)
        cell_h = self.height/(2*h)
        for x,y in walls:
            for i in [-3,-1,1,3]:
                if odd(x):
                    p = Point((x+0.8)*cell_w,(y+0.8+i/4)*cell_h)
                    self.blocks.append(Block(self,p,2,cell_h/4,Heading(0),1000))
                else:
                    p = Point((x+0.8+i/4)*cell_w,(y+0.8)*cell_h)
                    self.blocks.append(Block(self,p,cell_w/4,2,Heading(0),1000))
    def random_location(self):
        return Point(randrange(0,self.width),randrange(0,self.height))
    def spawn(self,critter):
        self.critters.append(critter)
        self.starting_critters.append(critter)
        critter.teleport_to(self,self.random_location())
    def dump_status(self):
        for c in self.critters:
             c.dump_status()
    def physical_objects(self):
        return self.critters + self.food + self.pits + self.stars + self.blocks
    def display_objects(self):
        return self.physical_objects() + self.sounds
    def sound(self,loc,volume,text):
        self.sounds.append(Sound(self,loc,volume,text))
    def find_neighbors(self,c):
        self.neighbors[c] = set([self.blocks[-1]])
        others = set(self.physical_objects())
        others.remove(c)
        for o in others:
            disp = c.displacement_to(o)
            if (disp.x/self.neighborhood_radius_x)**2 + (disp.y/self.neighborhood_radius_y)**2 < 1:
                self.neighbors[c].add(o)
    def neighbors_of(self,c):
        if not c in self.neighbors: self.find_neighbors(c)
        return self.neighbors[c]
    def run(self):
        stop_count = self.stop_count or len(self.starting_critters) and math.log(math.e*len(self.starting_critters))
        while self.world_view.window_open and self.clock != self.tick_limit and len([c for c in self.critters if c.dead == False]) >= stop_count:
            loop_start = time.time()
            self.clock += 1
            self.lighting = sorted([0,2*math.cos(self.clock/1000),1])[1]
            self.sounds   = [s for s in self.sounds if not s.faded]
            self.food     = [f for f in self.food if f.value > 0]
            if self.zombies_allowed:
                self.zombies += [c for c in self.critters if c.dead]
            self.critters = [c for c in self.critters if not c.dead]
            if self.lighting == 0:
                for c in self.zombies:
                    c.arise()
                    self.critters.append(c)
                self.zombies = []
            Secretion.on_tick()
            shuffle(self.critters)
            if self.clock % self.neighborhood_refresh == 0:
                self.neighbors = {}
            for c in self.display_objects():
                c.on_tick()
            changes = []
            checked = {}
            for c in self.critters+self.blocks:
                if not c.anchored:
                    checked[c] = True
                    c_outline = c.outline()
                    c_polygon = Polygon(c_outline)
                    core_radius = c.core_radius()
                    for o in self.neighbors_of(c):
                        if not checked.get(o,False):
                            d = c.distance_to(o)
                            if d >= c.radius() + o.radius():
                                pass # they missed
                            elif d < core_radius + o.core_radius():
                                # solid hit
                                self.process_collision(c,o,changes)
                            elif overlap(c_polygon,Polygon(o.outline()),c1=c.location,c2=o.location,r1=c.radius(),r2=o.radius()):
                                # glancing blow
                                self.process_collision(c,o,changes)
            for o,d_phi,d_loc in changes:
                o.heading = Heading(o.heading.phi+d_phi,rho=o.heading.rho/2)
                o.location = self.wrap(Point(Vector(o.location)+d_loc))
            self.world_view.on_tick()
            excess_time = self.tick_time-(time.time()-loop_start)
            if excess_time > 0:
                time.sleep(excess_time)
            elif self.warn:
                print("Tick over time by ",-excess_time," seconds!")
    def process_collision(self,a,b,changes):
        d = b.displacement_to(a).normalized
        v = a.heading - b.heading
        impact = d.dot(v)**2
        for x,other,s in [[a,b,+1],[b,a,-1]]:
            if not other.floor_mat:
                relative_mass = 1.0 - (0.0 if other.anchored else x.mass/(a.mass+b.mass))
                if not x.anchored:
                    changes.append([x,s*((d-v*0.1*relative_mass).phi-d.phi),d*(1+abs(v.dot(d)))*s*relative_mass])
                x.on_damage(impact*(x.collision_cost/100)*relative_mass*other.hardness/x.hardness)
        a.on_collision(-d,b)
        b.on_collision( d,a)
    def wrap(self,p):
        h = self.height
        w = self.width
        if isinstance(p,Point):  return Point(p.x % w,p.y % h)
        if isinstance(p,Vector): return Vector((p.x+w/2) % w - w/2,(p.y+h/2) % h - h/2)
        return p
    def print_stats(self):
        print("Food remaining: ",sum(f.value for f in self.food))
        print("Brains available:   ",len(Brains.available))
        print("Critters at start:  ",len(self.starting_critters))
        print("Critters remaining: ",len(self.critters))
        for c in sorted(self.starting_critters,key=lambda c: (-(c.finished or self.clock),c.age,c.mass),reverse=True):
            status = ("finished at %5.2f" % (c.finished*self.tick_time)) if c.finished else {False:"alive",True:"%5.2f" % (c.age*self.tick_time),None:"Undead"}[c.dead]
            print("    %5s %20s %5.1f" % (c.name,status,c.mass))

class WorldView:
    def __init__(self,world,scale):
        self.world = world
        self.scale = scale
        self.tk = Tk()
        self.tk.title("Critters")
        self.tk.resizable(0, 0)
        self.tk.wm_attributes("-topmost", 1)
        self.canvas_height = scale*world.height
        self.canvas_width  = scale*world.width
        self.canvas = Canvas(self.tk, width=self.canvas_width, height=self.canvas_height, highlightthickness=0)
        self.canvas.pack()
        self.tk.update()
        self.window_open = True
        def they_hit_close():
            self.window_open = False
        self.tk.protocol("WM_DELETE_WINDOW",they_hit_close)
        def menu(evt):
            tk = Tk()
            btnq = Button(tk, text="Quit", command=tk.destroy)
            btnq.pack({"side": "bottom"})
            tk.title('Menu')
            tk.resizable(0, 0)
            tk.wm_attributes("-topmost", 1)
            tk.update()
        self.canvas.bind_all('<KeyPress-m>', menu)
    def on_tick(self):
        if self.window_open:
            self.canvas.config(background=gray(self.world.lighting))
            Secretion.on_draw(self.canvas,self.scale)
            for sprite in self.world.display_objects():
                sprite.draw(self.canvas,self.scale)
            self.tk.update_idletasks()
            self.tk.update()

class Users:
    registered = []
    current = None
    initial = None
    def register(name):
        Users.registered.append(name)
        Users.current = name
        Users.initial = name[0:1]
    def initial(ch):
        Users.initial = ch

class Brains:
    registered = {}
    available = []
    codes = None
    def register(brain_class):
        u = Users.current
        if (not Brains.codes) or (brain_class.code == Brains.codes):
            if not u in Brains.registered.keys():
                Brains.registered[u] = []
            Brains.registered[u].append(brain_class)
            Brains.available.append(brain_class)
            brain_class.owner = Users.initial

parser = argparse.ArgumentParser()
parser.add_argument('-t', default=0.1, type=float)
parser.add_argument('-n', default= -1, type=int)
parser.add_argument('-c', default= 10, type=int)
parser.add_argument('-f', default=100, type=int)
parser.add_argument('-p', default=  0, type=int)
parser.add_argument('-s', default=  0, type=int)
parser.add_argument('-b', default=  0, type=int)
parser.add_argument('-w', default=False, action='store_true')
parser.add_argument('-z', default=False, action='store_true')
parser.add_argument('--metabolic_cost',     default = 0.01, type=float)
parser.add_argument('--movement_cost',      default = 0.1,  type=float)
parser.add_argument('--acceleration_cost',  default = 40,   type=float)
parser.add_argument('--collision_cost',     default = 10,   type=float)
parser.add_argument('--stop_count',         default = None, type=int)
parser.add_argument('--codes')
parser.add_argument('files', nargs=argparse.REMAINDER)

cmd = parser.parse_args()

Critter.metabolic_cost     = cmd.metabolic_cost
Critter.movement_cost      = cmd.movement_cost
Critter.acceleration_cost  = cmd.acceleration_cost
PhysicalObject.collision_cost  = cmd.collision_cost
Brains.codes = cmd.codes

import atexit
import glob,re


for file in cmd.files or glob.glob("*_brains.py"):
    match = re.search('^(.+)_brains.py$', file)
    if match:
        Users.register(match.group(1))
        try:
            exec(compile(open(file, "r").read(), file, 'exec'))
        except Exception as e:
            traceback.print_exception(*sys.exc_info(),limit=1)

if not Brains.available:
    print("No brains available!")
    exit()

w = World(
    tick_time  = cmd.t,
    tick_limit = cmd.n,
    food       = cmd.f,
    pits       = cmd.p,
    stars      = cmd.s,
    blocks     = cmd.b,
    warn       = cmd.w,
    zombies    = cmd.z,
    stop_count = cmd.stop_count
    )

@atexit.register
def show_stats():
    global w
    w.print_stats()

for i in range(1,cmd.c+1):
    c = Critter(w,Brains.available[i % len(Brains.available)],i)
    #For race
    #c.heading = Heading(0)
    #c.location = Point(10,(i+0.5)*w.height/(cmd.c+1))
    #For maze
    c.location = Point((200/12)*(randrange(0,12)+0.25),(100/6)*(randrange(0,6)+0.25))
    
# [Critter(w,Brains.available[i % len(Brains.available)],i) for i in range(1,cmd.c+1)]
# [Critter(w,choice(Brains.available),i) for i in range(1,cmd.c+1)]
try:
    w.run()
except KeyboardInterrupt:
    pass
