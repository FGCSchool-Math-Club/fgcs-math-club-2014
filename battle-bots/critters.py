from random import *
import math
import geo2d.geometry
                 
class Critter:
    name  = None
    brain = None
    body  = None
    world = None
    def __init__(self,world,brain_class,name):
        self.name  = name
        self.world = world
        self.body  = CritterBody()
        self.brain = brain_class(self.body)
        world.spawn(self)
    def dump_status(self):
        print(self.name)
        self.brain.dump_status()
        self.body.dump_status()
    def on_tick(self):
        self.brain.on_tick()
        self.body.on_tick()

class CritterBrain:
    def __init__(self,body):
        self.body = body
    def dump_status(self):
        pass
    def on_collision(self,other):
        pass
    def on_attack(self,attacker):
        pass
    def on_tick(self):
        pass
    def left(self,n):
        pass
    def right(self,n):
        pass
    def forward(self,n):
        pass
    def attack(self,target):
        pass
    def eat(self,target):
        pass
    def sight(self,n):
        pass
        # return set of n tuples: (color,distance,direction,width,change)
    def smell(self,n):
        pass
        # return set of n tuples (strength,smell,change)  

class CritterBody:
    world    = None
    location = None
    shape    = None
    heading  = None
    def __init__(self):
        self.heading = Heading(uniform(0.0,2*math.pi))
    def dump_status(self):
        print(self.location)
    def teleport_to(self,world,loc):
        self.world    = world
        self.location = loc
    def on_tick(self):
        self.location.translate(self.heading.x,self.heading.y)
        self.location = self.world.wrap(self.location)

Location = geo2d.geometry.Point
def Heading(dir):
    return geo2d.geometry.Vector(1.0,dir,coordinates="polar")

class World:
    height = 100
    width  = 100
    def __init__(self):
        self.critters = []
    def spawn(self,critter):
        self.critters.append(critter)
        critter.body.teleport_to(self,Location(randrange(0,self.width),randrange(0,self.height)))
    def dump_status(self):
        for c in self.critters:
             c.dump_status()
    def run(self):
        for tick in range(0,100):
            for c in self.critters:
                 c.on_tick()
    def wrap(self,p):
        x = p.x % self.width
        y = p.y % self.height
        if x == p.x and y == p.y:
            return p
        else:
            return Location(x,y)

w = World()
cs = [Critter(w,CritterBrain,"c{}".format(i)) for i in range(1,10)]
w.dump_status()

w.run()

w.dump_status()
