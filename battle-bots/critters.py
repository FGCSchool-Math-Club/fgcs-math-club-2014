from random import *
import math
import geo2d.geometry
import itertools
from tkinter import *
import time

def random_color():
    return "#%02x%02x%02x" % (randrange(0,255),randrange(0,255),randrange(0,255))

Location = geo2d.geometry.Point
def Heading(dir):
    return geo2d.geometry.Vector(1.0,dir,coordinates="polar")

class PhysicalObject:
    def __init__(self,world,loc):
        self.world = world
        self.location = loc
        self.tk_id = None
        self.color = {"fill": "black"}
    def dump_status(self):
        print(self.location)
    def on_tick(self):
        pass
    def on_collision(self,dir,other):
        pass
    def radius(self):
        return 1
    def draw(self, canvas,s):
        r = self.radius()
        if r > 0:
            if self.tk_id is None:
                self.tk_id = canvas.create_oval(50, 50, s*2*r, s*2*r, **self.color)
            canvas.tag_lower(self.tk_id)
            loc = self.location
            canvas.coords(self.tk_id,      s*loc.x-s*r, s*loc.y-s*r,s*loc.x+s*r, s*loc.y+s*r)
        else:
            if self.tk_id:
                canvas.delete(self.tk_id)
                self.tk_id = None

class Critter:
    def __init__(self,world,brain_class,name):
        self.name  = name
        self.world = world
        self.heading = Heading(uniform(0.0,2*math.pi))
        profile = [uniform(0.5,0.8) for i in range(0,10)]
        self.shape   = [1.0,1.0]+profile+list(reversed(profile))
        self.radius = 5
        self.tk_id = None
        self.brain = brain_class()
        world.spawn(self)
    def dump_status(self):
        print(self.name)
        self.brain.dump_status()
        print(self.location)
    def on_tick(self):
        self.act(self.brain.on_tick(self.senses()))
        self.location.translate(self.heading.x,self.heading.y)
        self.location = self.world.wrap(self.location)
    def on_collision(self,dir,other):
        self.radius  *= 0.9
        self.heading -= dir
        self.act(self.brain.on_collision(dir,other,self.senses()))
    def teleport_to(self,world,loc):
        self.world    = world
        self.location = loc
    def act(self,cmd):
        if not cmd is None:
            word = cmd.split()
            if word[0] == "Stop":
                self.heading /= 10000
            elif word[0] == "Turn":
                self.heading = Heading(self.heading.phi+float(word[1]))
            elif word[0] == "Accelerate":
                self.heading *= float(word[1])
            elif word[0] == "Attack":
                pass
            elif word[0] == "Eat":
                pass
            else:
                print("Unknown command: {}".format(cmd))
    def senses(self):
        return {
            'sight':   set(), # return set tuples: (color,distance,direction,width,change)
            'smell':   set(), # return set tuples: (strength,smell,change)
            'gps':     self.location,
            'compass': self.heading,
          }
    def draw(self, canvas,s):
        r    = self.radius
        loc  = self.location
        phi  = self.heading.phi
        q    = 2*math.pi/len(self.shape)
        outline = [coord for a, d in enumerate(self.shape) for coord in (s*loc.x+s*r*d*math.cos(a*q+phi),s*loc.y+s*r*d*math.sin(a*q+phi))]
        if self.tk_id is None:
            self.tk_id = canvas.create_polygon(*outline, fill=random_color(), smooth=1, stipple='gray50')
            self.tk_text_id = canvas.create_text(50,50, text=self.name)
        canvas.coords(self.tk_text_id, s*loc.x, s*loc.y)
        canvas.coords(self.tk_id,      *outline)

class CritterBrain:
    def dump_status(self):
        pass
    def on_collision(self,dir,other,senses):
        pass
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        pass

class Food(PhysicalObject):
    def __init__(self,world,loc,value):
        PhysicalObject.__init__(self,world,loc)
        self.value = value
        self.color = {"fill": "dark green", "outline": "green"}
    def on_tick(self):
        # Could spoil, spread, or...?
        pass
    def on_collision(self,dir,other):
        self.radius  *= 0.9
        self.heading -= dir
    def radius(self):
        return math.sqrt(self.value)

class World:
    height = 100
    width  = 250
    def __init__(self):
        self.critters = []
        self.world_view = WorldView(self,5)
        self.food = [Food(self,self.random_location(),randrange(2,8)) for i in range(0,50)]
    def random_location(self):
        return Location(randrange(0,self.width),randrange(0,self.height))
    def spawn(self,critter):
        self.critters.append(critter)
        critter.teleport_to(self,self.random_location())
    def dump_status(self):
        for c in self.critters:
             c.dump_status()
    def display_objects(self):
        return self.critters + self.food
    def run(self):
        while self.world_view.window_open:
            shuffle(self.critters)
            for f in self.food:
                if f.value <= 0:
                    self.food.remove(f)
            for c in self.critters:
                 c.on_tick()
                 for f in self.food:
                     if f.value > 0 and c.location.distance_to(f.location) < c.radius:
                         f.value -= 1
                         c.radius = math.sqrt(c.radius**2+1)
            for c1,c2 in itertools.combinations(self.critters,2):
                 if c1.location.distance_to(c2.location) < c1.radius + c2.radius:
                     v = geo2d.geometry.Vector(c2.location,c1.location).normalized
                     c1.on_collision(-v,c2)
                     c2.on_collision( v,c1)
            self.world_view.on_tick()
            time.sleep(0.1)
    def wrap(self,p):
        return Location(p.x % self.width,p.y % self.height)

class WorldView:
    def __init__(self,world,scale):
        self.world = world
        self.scale = scale
        self.tk = Tk()
        self.tk.title("Battle bots")
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
            for sprite in self.world.display_objects():
                sprite.draw(self.canvas,self.scale)
            self.tk.update_idletasks()
            self.tk.update()

class Users:
    registered = []
    current = None
    def register(name):
        Users.registered.append(name)
        Users.current = name

class Brains:
    registered = {}
    available = []
    def register(brain_class):
        u = Users.current
        if not u in Brains.registered.keys():
            Brains.registered[u] = []
        Brains.registered[u].append(brain_class)
        Brains.available.append(brain_class)

import glob,re
for file in glob.glob("*_brains.py"):
    match = re.search('^(.+)_brains.py$', file)
    if match:
        Users.register(match.group(1))
        exec(open(file, "r").read())

w = World()
[Critter(w,choice(Brains.available),"c{}".format(i)) for i in range(1,10)]
w.run()
