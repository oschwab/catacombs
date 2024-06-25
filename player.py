from apps.Catacombs import world

class Player(world.LivingThing):
    def __init__(self,pos,world,image):
        super().__init__(pos,world,image)
        self.fov = 6