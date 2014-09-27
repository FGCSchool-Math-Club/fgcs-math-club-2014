class WanderBrain(CritterBrain):
    def on_collision(self,dir,other,senses):
        pass
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        self.body.turn(uniform(-0.1,+0.1)*randrange(1,4))

Brains.register(WanderBrain)

class ZigBrain(CritterBrain):
    def on_collision(self,dir,other,senses):
        pass
    def on_attack(self,dir,attacker,senses):
        pass
    def on_tick(self,senses):
        if randrange(1,10) == 1:
            self.body.turn(uniform(-1,1))
        else:
            self.body.heading *= 1.1

Brains.register(ZigBrain)
