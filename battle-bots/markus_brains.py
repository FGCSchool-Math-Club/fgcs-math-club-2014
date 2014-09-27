class WanderBrain(CritterBrain):
    def on_collision(self,dir,other):
        pass
    def on_attack(self,dir,attacker):
        pass
    def on_tick(self):
        self.body.turn(uniform(-0.1,+0.1)*randrange(1,4))

Brains.register(WanderBrain)

class ZigBrain(CritterBrain):
    def on_collision(self,dir,other):
        pass
    def on_attack(self,dir,attacker):
        pass
    def on_tick(self):
        if randrange(1,10) == 1:
            self.body.turn(uniform(-1,1))
        else:
            self.body.heading *= 1.1

Brains.register(ZigBrain)
