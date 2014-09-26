class WanderBrain(CritterBrain):
    def on_collision(self,dir,other):
        pass
    def on_attack(self,dir,attacker):
        pass
    def on_tick(self):
        self.body.turn(uniform(-0.1,+0.1)*randrange(1,4))
