
from apps.Catacombs import dungeon
from apps.Catacombs import los

Dungeon_WIDTH = 100
Dungeon_HEIGHT = 60

Move_Down_Left = 'b'
Move_Down = 'n'
Move_Down_Right = 'm'
Move_Left = 'h'
Move_Wait = 'j'
Move_Right = 'k'
Move_Up_Left = 'u'
Move_Up = 'i'
Move_Up_Right = 'o'

class WorldObject:
    def __init__(self,pos,world,image):
        self.posX = pos[0]
        self.posY = pos[1]
        self.world = world
        self.image = image

    def current_pos(self):
        return self.posX,self.posY
    
class LivingThing(WorldObject):
        def __init__(self,pos,world,image):
            super().__init__(pos,world,image)
            self.fov = 5
            


from apps.Catacombs import player

class World:
    def __init__(self):
        print("World initialization")
        self.current_dungeon = dungeon.Dungeon(Dungeon_WIDTH, Dungeon_HEIGHT)
        self.current_dungeon.generate()
        self.player = player.Player(self.current_dungeon.get_player_startup_pos(), self, "@")

    def move_object(self, world_object, direction):
        if direction == Move_Down_Left:
            world_object.posX = world_object.posX - 1
            world_object.posY = world_object.posY + 1
        elif direction == Move_Down:
            world_object.posY = world_object.posY + 1
        elif direction == Move_Down_Right:
            world_object.posX = world_object.posX + 1
            world_object.posY = world_object.posY + 1
        elif direction == Move_Left:
            world_object.posX = world_object.posX - 1
        elif direction == Move_Wait:
            pass
        elif direction == Move_Right:
            world_object.posX = world_object.posX + 1
        elif direction == Move_Up_Left:
            world_object.posX = world_object.posX - 1
            world_object.posY = world_object.posY - 1
        elif direction == Move_Up:
            world_object.posY = world_object.posY - 1
        elif direction == Move_Up_Right:
            world_object.posX = world_object.posX + 1
            world_object.posY = world_object.posY - 1

    def try_move_player(self, move):
        test_object = WorldObject(self.player.current_pos(), self, "?")
        self.move_object(test_object, move)
        if self.current_dungeon.can_go_to(test_object.current_pos()):
            self.move_object(self.player, move)

    def get_current_map(self, width, height):
        d_map = self.current_dungeon.get_map_view(self.player.current_pos(), width, height)
        (x,y) = self.current_dungeon.get_object_relative_position(self.player.current_pos(), width, height)
        los_map = los.LosMap(self,d_map)
        los_map.do_fov(x, y, self.player.fov)
        

        for y in range(height):
            for x in range(width):
                d_map[y][x] = dungeon.Tile.set_lit(d_map[y][x],0)
                if not los_map.lit(x,y):
                    tile = d_map[y][x]
                elif y < 0:
                    tile = dungeon.Tile.set_lit(dungeon.DungeonTileType_Earth,0)
                elif x < 0:
                    tile = dungeon.Tile.set_lit(dungeon.DungeonTileType_Earth,0)
                else:
                    d_map[y][x] = dungeon.Tile.set_seen(d_map[y][x],1)
                    d_map[y][x] = dungeon.Tile.set_lit(d_map[y][x],1)
                    tile = d_map[y][x]
                #print("set seen :" ,x,y, dungeon.Tile.get_description(d_map[y][x]) )


        self.current_dungeon.set_seen_map(d_map,self.player.current_pos(), width, height)

        return d_map

