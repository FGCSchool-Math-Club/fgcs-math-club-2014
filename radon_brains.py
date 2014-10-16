#
# Brains for Team Radon --
#     Only Sam,  Ulle or Alex should edit this file!
#
from geo2d.geometry import *

Users.initial = "Rn"
class EvesdroppingBrain(CritterBrain):
    code = "e"
    def __init__(self):
        CritterBrain.__init__(self)
        self.pit_location_guesses = []
    def on_collision(self,dir,other,senses):
        pass
    def on_attack(self,dir,attacker,senses):
        pass
    def pit_guess(self):
        p = sum(self.pit_location_guesses,Vector(0,0))
        n = len(self.pit_location_guesses)
        #print(Point(p.x/n,p.y/n))
        return Point(p.x/n,p.y/n)
    def on_tick(self,senses):
        my_loc = senses['gps']
        for sound in senses['hearing']:
            if sound[0].startswith('Aaaa'):
                p = Vector(*my_loc) + Vector(sound[1]+senses['compass'],50,coordinates="polar")
                print(p)
                self.pit_location_guesses.append(p)
        if self.pit_location_guesses and my_loc.distance_to(self.pit_guess()) < 20:
            print(self.pit_guess())
            dir = Vector(my_loc,self.pit_guess()).phi
            return "Turn {}".format(dir+math.pi-senses['compass'])
        else:
            return "Turn {}".format(uniform(-0.1,+0.1)*randrange(1,4))
#Brains.register(EvesdroppingBrain)

class LookingBrain(CritterBrain):
    code = "l"
    def __init__(self):
        CritterBrain.__init__(self)
        self.hit_food = 0
        self.eating = 0
        self.moving = True
    def on_collision(self,dir,other,senses):
        if isinstance(other,Food):
            self.hit_food += 2
            return "Eat"
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        if self.hit_food > 0:  self.hit_food -= 1
        if self.hit_food >= 5:
            self.eating    = 3
            self.hit_food -= 1
        self.eating -= 1
        can_see = senses['sight']
        if not can_see:
            turn = uniform(-0.1,+0.1)*randrange(1,4)
        else:
            closest = min(can_see, key=lambda s: s[1])
            if closest[0] == 'dark green':
                if closest[1] < 5:
                    if self.moving:
                        self.moving = False
                        return "Accelerate 0.1"
                    else:
                        return "Eat"
                if closest[1] > 5 and not self.moving:
                    self.moving = True
                    return "Accelerate 10.0"
                turn = closest[2]
            elif closest[2] > 0:
                turn = -0.5
            else:
                turn = 0.5
        if not self.moving:
            self.moving = True
            return "Accelerate 10.0"
        return "Turn {}".format(turn)
Brains.register(LookingBrain)

class TastingBrain(CritterBrain):
    code = "t"
    def __init__(self):
        CritterBrain.__init__(self)
        self.moving = True
    def on_collision(self,dir,other,senses):
        pass
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        can_see = senses['sight']
        if Food in senses['taste']:
            if self.moving and randrange(0,4) == 0:
                self.moving = False
                return "Stop"
            else:
                return "Eat"
        elif not self.moving:
            self.moving = True
            return "Go"
        else:
            if not can_see:
                turn = uniform(-0.1,+0.1)*randrange(1,4)
            else:
                closest = min(can_see, key=lambda s: s[1])
                if closest[0] == 'dark green':
                    turn = closest[2]
                elif closest[2] > 0:
                    turn = -0.5
                else:
                    turn = 0.5
            return "Turn {}".format(turn)
Brains.register(TastingBrain)

class ZigBrain(CritterBrain):
    code = "Z"
    def on_collision(self,dir,other,senses):
        pass
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        if randrange(1,10) == 1:
            return "Turn {}".format(uniform(-1,1))
        else:
            return "Accelerate 1.01"

#Brains.register(ZigBrain)
