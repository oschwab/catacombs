from apps.Catacombs import dungeon
from apps.Catacombs import los
from apps.Catacombs import player
from apps.Catacombs import monsters
import math

Dungeon_WIDTH = 30 # 100
Dungeon_HEIGHT = 10 # 60

NORTH = 1
SOUTH = 2
EAST = 3
WEST = 4
NORTHEAST = 5
NORTHWEST = 6
SOUTHEAST = 7
SOUTHWEST = 8
CENTER = 9

Directions = {
    NORTH: (0, -1),
    SOUTH: (0, 1),
    EAST: (1, 0),
    WEST: (-1, 0),
    NORTHEAST: (1, -1),
    NORTHWEST: (-1, -1),
    SOUTHEAST: (1, 1),
    SOUTHWEST: (-1, 1),
    CENTER: (0, 0)
}


            


class World:
    def __init__(self):
        print("World initialization")
        self.current_dungeon = dungeon.Dungeon(Dungeon_WIDTH, Dungeon_HEIGHT)
        self.current_dungeon.generate_maze()
        self.player = player.Player((), self.current_dungeon, "@")
        self.current_dungeon.set_player(self.player)
        self.current_dungeon.generate_monsters()

    def move_object(self, world_object, direction):
        (x,y) = Directions[direction]
        world_object.x = world_object.x + x
        world_object.y = world_object.y + y

    def end_turn(self):
        self.current_dungeon.do_monsters_actions()
    def try_move_player(self, move):
        test_object = WorldObject(self.player.current_pos(), self, "?")
        self.move_object(test_object, move)
        if self.current_dungeon.can_go_to(test_object.current_pos()):
            self.move_object(self.player, move)
            self.end_turn()
            #print("player moved to " + str(self.player.x)+ "," + str(self.player.y) )

    def get_monster(self,x, y, width, height):
        pos = self.current_dungeon.get_object_real_position((x,y), self.player.current_pos(), width, height)
        return self.current_dungeon.get_monster(pos[0],pos[1])

    def get_current_map(self, width, height):
        d_map = self.current_dungeon.get_map_view(self.player.current_pos(), width, height)
        (x,y) = self.current_dungeon.get_object_relative_position(self.player.current_pos(), width, height)
        los_map = los.LosMap(self.current_dungeon,d_map)
        los_map.do_fov(x, y, self.player.fov_radius)

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
    


def distance_to(start, other):
    # return the distance to another object
    dx = other[0] - start[0]
    dy = other[1] - start[1]
    return math.sqrt(dx ** 2 + dy ** 2)


# lifted from Incursion
def direction_to(start, target):
    # convert to tuple if not already one
    if hasattr(start, "x"):
        start = (start.x, start.y)
    if hasattr(target, "x"):
        target = (target.x, target.y)

    sx, sy = start[0], start[1]
    tx, ty = target[0], target[1]

    if tx == sx:
        if ty > sy:
            return Directions[SOUTH]
        if ty < sy:
            return Directions[NORTH]
        else:
            return Directions[CENTER]
    if tx < sx:
        if ty > sy:
            return Directions[SOUTHWEST]
        if ty < sy:
            return Directions[NORTHWEST]
        else:
            return Directions[WEST]
    if ty > sy:
        return Directions[SOUTHEAST]
    if ty < sy:
        return Directions[NORTHEAST]

    return Directions[EAST]