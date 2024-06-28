from apps.Catacombs import entities

class Player(entities.LivingThing):
    def __init__(self,pos,dungeon,image):
        super().__init__(pos,dungeon,image)
        self.fov_radius = 6