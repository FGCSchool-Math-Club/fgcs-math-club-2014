#
# Brains for Team Xenon --
#     Only August and Ian should edit this file!
#
from geo2d.geometry import *

Users.initial = "Xe"

class LookingBrain(CritterBrain):
    code = "I"
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
        if senses['body'].age>200:
            return "Stop"
        if self.hit_food > 0:  self.hit_food -= 1
        if self.hit_food >= 5:
            self.eating    = 3
            self.hit_food -= 1
        self.eating -= 1
        can_see = senses['sight']
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
            return "Accelerate 10.0"
        return "Turn {}".format(turn)
Brains.register(LookingBrain)

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
    max_speed = 1.32139573
    max_acceleration = 1.0170292
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
        self.prefers_left = True
    def on_collision(self,dir,other,senses):
        if isinstance(other,Food):
          return "Eat"
        else:
          return "Turn {}".format(-dir.phi)
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        if randrange(0,100) == 0: self.prefers_left = not self.prefers_left
        can_see = senses['sight']
        moving = senses['body'].moving
        closest  = min(can_see, key=lambda s: s.distance)
        farthest = max(can_see, key=lambda s: s.distance)
        visible_food = [x for x in can_see if x.color == 'green']
        if len(visible_food) > 0:
            closest_food = min(visible_food, key=lambda s: s.distance)
        else:
            closest_food = None
        visible_stars = [x for x in can_see if x.color == 'gold']
        if len(visible_stars) > 0:
            closest_star = min(visible_stars, key=lambda s: s.distance)
        else:
            closest_star = None
        if senses ['body'].health>5:
            closest_target=closest_star
        else:
            closest_target=closest_food
        if closest_target:
            if closest_target.distance < 1 and moving:
                return "Accelerate 0.7
            elif closest_target.distance < 0.1:
                if moving:
                    return "Stop"
                else:
                    return "Eat"
            else:
                if not moving:
                    return "Go"
                else:
                    return "Turn {}".format(closest_target.direction/2)
        elif farthest.distance > 4:
            if abs(farthest.direction) > 0.1:
                return "Turn {}".format(farthest.direction/2)
            elif randrange(0,10) == 0:
                if self.prefers_left:
                    return "Turn -1.0"
                else:
                    return "Turn 1.0"
            else:
                return "Go"
        elif closest.distance < 5:
            if closest.color == 'brown':
                if self.prefers_left:
                    return "Turn -1.0"
                else:
                    return "Turn 1.0"
            else:
                if closest.direction > 0:
                    return "Turn -0.5"
                else:
                    return "Turn 0.5"
        else:
            return "Go"
Brains.register(MazeBrain)

