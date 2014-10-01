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
            return "Accelerate 1.01"

Brains.register(ZigBrain)
