Users.initial = "Q"

class WanderBrain(CritterBrain):
    code = "w"
    def on_collision(self,dir,other,senses):
        pass
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        return "Turn {}".format(uniform(-0.1,+0.1)*randrange(1,4))

Brains.register(WanderBrain)

class ZigBrain(CritterBrain):
    code = "z"
    def on_collision(self,dir,other,senses):
        pass
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        if randrange(1,10) == 1:
            return "Turn {}".format(uniform(-1,1))
        else:
            return "Accelerate 1.1"

Brains.register(ZigBrain)

class MuncherBrain(CritterBrain):
    code = "m"
    def on_collision(self,dir,other,senses):
        return "Eat"
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        if randrange(1,10) == 1:
            return "Turn {}".format(uniform(-1,1))
        else:
            return "Eat"

Brains.register(MuncherBrain)

class RunnerBrain(CritterBrain):
    code = "r"
    def on_collision(self,dir,other,senses):
        pass
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        if randrange(1,10) == 1:
            return "Turn {}".format(uniform(-1,1))
        else:
            return "Accelerate 2.0"

Brains.register(RunnerBrain)

class RacerBrain(CritterBrain):
    code = "R"
    max_speed = None
    max_acceleration = None
    def on_collision(self,dir,other,senses):
        pass
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        if self.max_speed is None:
            self.max_speed = uniform(0.8,2.0)
            self.max_acceleration = uniform(1.01,max([1.1,self.max_speed]))
            #print((self.max_speed,self.max_acceleration))
        acceleration = self.max_speed/senses['body'].speed
        if acceleration > self.max_acceleration:
            acceleration = self.max_acceleration
        return "Accelerate {}".format(acceleration)

Brains.register(RacerBrain)
