#
# Brains for Team Argon --
#     Only Sophia and Maxwell should edit this file!
#
from geo2d.geometry import *

Users.initial = "Ar"

class HibernationBrain(CritterBrain):
    code = "h"
    def __init__(self):
        CritterBrain.__init__(self)
        self.hit_food = 0
        self.eating = 0
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
        food_seen = [x for x in can_see if x.color == 'green']
        moving = senses['body'].moving
        if not can_see:
            turn = uniform(-0.1,+0.1)*randrange(1,4)
        else:
            closest = min(can_see, key=lambda s: s.distance)
            if closest.color == 'green':
                if closest.distance < 5:
                    if moving:
                        return "Accelerate 0.1"
                    else:
                        return "Eat"
                if closest.distance > 5 and not moving:
                    return "Accelerate 10.0"
                turn = closest.direction
            elif closest.direction > 0:
                turn = -0.5
            else:
                turn = 0.5
        if not moving:
            if not food_seen:
                return "Accelerate 10.0"
        if not food_seen:
            return "Accelerate 0.0"
        return "Turn {}".format(turn)
Brains.register(HibernationBrain)

class TastingBrain(CritterBrain):
    code = "t"
    def __init__(self):
        CritterBrain.__init__(self)
    def on_collision(self,dir,other,senses):
        pass
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        can_see = senses['sight']
        moving = senses['body'].moving
        if Food in senses['taste']:
            if moving and randrange(0,4) == 0:
                return "Stop"
            else:
                return "Eat"
        elif not moving:
            return "Go"
        else:
            if not can_see:
                turn = uniform(-0.1,+0.1)*randrange(1,4)
            else:
                closest = min(can_see, key=lambda s: s.distance)
                if closest.color == 'green':
                    turn = closest.direction
                elif closest.direction > 0:
                    turn = -0.5
                else:
                    turn = 0.5
            return "Turn {}".format(turn)
Brains.register(TastingBrain)


class RacerBrain(CritterBrain):
    code = "R"
    max_speed = 1.322
    max_acceleration = 1.2
    def on_collision(self,dir,other,senses):
        pass
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        acceleration = self.max_speed/senses['body'].speed
        if acceleration > self.max_acceleration:
            acceleration = self.max_acceleration
        return "Accelerate {}".format(acceleration)

Brains.register(RacerBrain)
class MazeBrain(CritterBrain):
    code = "M"
    def __init__(self):
        CritterBrain.__init__(self)
    def on_collision(self,dir,other,senses):
        if isinstance(other,Food):
          return "Eat"
        else:
          return "Turn {}".format(-dir.phi)
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        can_see = senses['sight']
        moving = senses['body'].moving
        closest = min(can_see, key=lambda s: s.distance)
        visible_food = [x for x in can_see if x.color == 'green']
        if len(visible_food) > 0:
            closest_food = min(visible_food, key=lambda s: s.distance)
        else:
            closest_food = None
        if closest.color == 'brown' and closest.distance < 10 and abs(closest.direction) < 0.5:
            return "Turn 1.0"
        elif closest_food:
            if closest_food.distance < 5 and moving:
               return "Accelerate 0.1"
            elif closest_food.distance < 5 :
                return "Eat"
            elif not moving:
                return "Accelerate 10.0"
            else:
                return "Turn {}".format(closest.direction)
        elif senses['body'].speed < 1.0:
            return "Accelerate 1.2"
        elif closest.distance > 5:
            return "Pass"
        elif closest.direction > 0:
            return "Turn -0.5"
        else:
            return "Turn 0.5"
Brains.register(MazeBrain)

