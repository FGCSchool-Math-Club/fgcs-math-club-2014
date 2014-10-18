#
# Brains for Team Radon --
#     Only Sam or   Ulee  should edit this file!
#
from geo2d.geometry import *

Users.initial = "Rn"

class LookingBrain(CritterBrain):
    code = "l"
    def __init__(self):
        CritterBrain.__init__(self)
        self.hit_food = 0
        self.eating = 0
        self.moving = True
        self.time_since_yum = 0
    def on_collision(self,dir,other,senses):
        if isinstance(other,Food):
            self.hit_food += 2
            return "Eat"
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        yums = [s for s in senses['hearing'] if s.text == "Yum"]
        if yums:
            self.time_since_yum = 0
        else:
            self.time_since_yum = self.time_since_yum + 1
        if self.hit_food > 0:  self.hit_food -= 1
        if self.hit_food >= 5:
            self.eating    = 3
            self.hit_food -= 1
        self.eating -= 1
        can_see = senses['sight']
        if self.time_since_yum > 100:
            return "Stop"
        if not can_see:
            turn = uniform(-0.1,+0.1)*randrange(1,4)
        else:
            closest = min(can_see, key=lambda s: s.distance)
            if closest.color == 'dark green':
                if closest.distance < 5:
                    if self.moving:
                        self.moving = False
                        return "Accelerate 0.1"
                    else:
                        return "Eat"
                if closest.distance > 5 and not self.moving:
                    self.moving = True
                    return "Accelerate 10.0"
                turn = closest.direction
            elif closest.direction > 0:
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
                closest = min(can_see, key=lambda s: s.distance)
                if closest.color == 'dark green':
                    turn = closest.direction
                elif closest.direction > 0:
                    turn = -0.5
                else:
                    turn = 0.5
            return "Turn {}".format(turn)
Brains.register(TastingBrain)

