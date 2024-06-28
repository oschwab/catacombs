
class WorldObject:
    def __init__(self,pos,dungeon,image):
        if pos != ():
            self.x = pos[0]
            self.y = pos[1]
        self.dungeon = dungeon
        self.image = image

    def current_pos(self):
        return self.x,self.y
    
class LivingThing(WorldObject):
        def __init__(self,pos,world,image):
            super().__init__(pos,world,image)
            self.fov_radius = 5