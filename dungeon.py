from random import *
from apps.Catacombs import monsters
from apps.Catacombs import utils

# Opaque tiles
DungeonTileType_Earth = 0
DungeonTileType_WallUpLeft = 1
DungeonTileType_WallUp = 2
DungeonTileType_WallUpRight = 3
DungeonTileType_WallLeft = 4
DungeonTileType_WallDownLeft = 5
DungeonTileType_WallDown = 6
DungeonTileType_WallDownRight = 7
DungeonTileType_WallRight = 8
DungeonTileType_SecretDoor = 9
DungeonTileType_ClosedDoor = 10

# Transparent tiles
DungeonTileType_Empty = 11
DungeonTileType_OpenedDoor = 12
DungeonTileStairsUp = 13
DungeonTileStairsDown = 14


class Tile:
    """
    Tile storage : 1 byte
    Type  : 6 first bits (1 to 63)
    Seen : bit 7
    Lit : bit 8
    """
    @staticmethod
    def get_type(value):
        return value & 0x3F

    @staticmethod
    def set_type(value, new_type):
        current_bits = value & 0xC0  # 1100 0000
        return new_type | current_bits

    @staticmethod
    def set_seen(tile_value, seen):
        if seen == 1:
            return utils.set_bit(tile_value,7 )
        else:
            return utils.clear_bit(tile_value, 7)

    @staticmethod
    def is_seen(tile_value):
        return utils.get_bit(tile_value, 7) == 1

    @staticmethod
    def set_lit(tile_value, lit):
        if lit == 1:
            return utils.set_bit(tile_value, 8)
        else:
            return utils.clear_bit(tile_value, 8)

    @staticmethod
    def is_lit(tile_value):
        return utils.get_bit(tile_value, 8) == 1

    @staticmethod
    def get_description(tile_value):
        tv = 'type: ' + str(Tile.get_type(tile_value)) + ' lit:' + str(Tile.is_lit(tile_value)) + ' seen:' + str(
            Tile.is_seen(tile_value)) + " (" + str(tile_value) + ")"
        return tv

    @staticmethod
    def is_opaque(tile_value):
        return Tile.get_type(tile_value) == DungeonTileType_Earth


class OpenSet:

    def __init__(self, key=None):
        self._data = []
        self._dup = set()
        self.key = key or (lambda v: v)

    def add(self, value):
        if value in self._dup:
            return
        self._dup.add(value)
        a = self._data
        key = self.key
        i = len(a)
        a.append(value)
        while i > 0:
            parent = i // 2
            if key(a[parent]) < key(a[i]):
                break
            a[parent], a[i] = a[i], a[parent]
            i = parent

    def pop(self):
        if len(self._data) == 0:
            raise IndexError("pop from an empty heap")
        a = self._data
        val = a[0]
        a[0] = a[-1]
        a.pop()
        key = self.key
        i = 0
        while True:
            left = 2 * i + 1
            right = 2 * i + 2
            if left >= len(a):
                break
            node = left
            if right < len(a) and key(a[right]) < key(a[left]):
                node = right
            if key(a[i]) > key(a[node]):
                a[i], a[node] = a[node], a[i]
                i = node
            else:
                break
        self._dup.remove(val)
        return val

    def __contains__(self, value):
        return value in self._dup

    def __bool__(self):
        return len(self._data) > 0


class Dungeon:

    def __init__(self, width, height):
        self.roomList = []
        self.cList = []
        self.width = width
        self.height = height
        self.current_map = None
        self.monsters_list = []
        self.player = None

    @staticmethod
    def tile_blocks_light(tile):
        return int(Tile.get_type(tile)) <= 10

    @staticmethod
    def tile_blocks_path(tile):
        tile_type = Tile.get_type(tile)
        return tile_type <= 10

    def make_raw_map(self, x_size, y_size, fail, b1, max_rooms):
        """Generate random layout of rooms, corridors and other features"""
        # makeMap can be modified to accept arguments for values of failed, and percentile of features.
        # Create first room
        self.size_x = x_size
        self.size_y = y_size
        # initialize map to all walls
        self.current_map = utils.ByteArray2D(x_size,y_size)
        for y in range(y_size):
            tmp = []
            for x in range(x_size):
                tmp.append(DungeonTileType_Earth)
            self.current_map[y] = tmp

        w, l, t = self.make_room(y_size)

        while len(self.roomList) == 0:
            y = randrange(y_size - 1 - l) + 1
            x = randrange(x_size - 1 - w) + 1
            p = self.place_room(l, w, x, y, x_size, y_size, 6, 0)

        failed = 0

        while failed < fail:
            # The lower the value that failed< , the smaller the dungeon
            chooseRoom = randrange(len(self.roomList))
            ex, ey, ex2, ey2, et = self.make_exit(chooseRoom)
            feature = randrange(100)
            if feature < b1:  # Begin feature choosing (more features to be added here)
                w, l, t = self.make_corridor()
            else:
                w, l, t = self.make_room(y_size)
            roomDone = self.place_room(l, w, ex2, ey2, x_size, y_size, t, et)
            if roomDone == 0:  # If placement failed increase possibility map is full
                failed += 1
            elif roomDone == 2:  # Possiblilty of linking rooms
                if self.current_map[ey2][ex2] == DungeonTileType_Empty:
                    if randrange(100) < 7:
                        self.make_portal(ex, ey)
                    failed += 1
            else:  # Otherwise, link up the 2 rooms
                self.make_portal(ex, ey)
                failed = 0
                if t < 5:
                    tc = [len(self.roomList) - 1, ex2, ey2, t]
                    self.cList.append(tc)
                    self.join_corridor(len(self.roomList) - 1, ex2, ey2, t, 50)
            if len(self.roomList) == max_rooms:
                failed = fail
        self.final_joins()

    @staticmethod
    def make_room(length_limit):
        """Randomly produce room size"""
        rtype = 5
        rwide = randrange(8) + 3
        rlong = randrange(length_limit - 5) + 3
        return rwide, rlong, rtype

    @staticmethod
    def make_corridor():
        """Randomly produce corridor length and heading"""
        clength = randrange(18) + 3
        heading = randrange(4)
        if heading == 0:  # North
            wd = 1
            lg = -clength
        elif heading == 1:  # East
            wd = clength
            lg = 1
        elif heading == 2:  # South
            wd = 1
            lg = clength
        elif heading == 3:  # West
            wd = -clength
            lg = 1
        return wd, lg, heading

    def place_room(self, ll, ww, xposs, yposs, xsize, ysize, rty, ext):
        """Place feature if enough space and return canPlace as true or false"""
        # Arrange for heading
        xpos = xposs
        ypos = yposs
        if ll < 0:
            ypos += ll + 1
            ll = abs(ll)
        if ww < 0:
            xpos += ww + 1
            ww = abs(ww)
        # Make offset if type is room
        if rty == 5:
            if ext == 0 or ext == 2:
                offset = randrange(ww)
                xpos -= offset
            else:
                offset = randrange(ll)
                ypos -= offset
        # Then check if there is space
        canPlace = 1
        if ww + xpos + 1 > xsize - 1 or ll + ypos + 1 > ysize:
            canPlace = 0
            return canPlace
        elif xpos < 1 or ypos < 1:
            canPlace = 0
            return canPlace
        else:
            for j in range(ll):
                for k in range(ww):
                    if self.current_map[(ypos) + j][(xpos) + k] != DungeonTileType_Earth:
                        canPlace = 2
        # If there is space, add to list of rooms
        if canPlace == 1:
            temp = [ll, ww, xpos, ypos]
            self.roomList.append(temp)
            for j in range(ll + 2):  # Then build walls
                for k in range(ww + 2):
                    self.current_map[(ypos - 1) + j][(xpos - 1) + k] = DungeonTileType_WallUp
            for j in range(ll):  # Then build floor
                for k in range(ww):
                    self.current_map[ypos + j][xpos + k] = DungeonTileType_Empty
        return canPlace  # Return whether placed is true/false

    def make_exit(self, rn):
        """Pick random wall and random point along that wall"""
        room = self.roomList[rn]
        while True:
            rw = randrange(4)
            if rw == 0:  # North wall
                rx = randrange(room[1]) + room[2]
                ry = room[3] - 1
                rx2 = rx
                ry2 = ry - 1
            elif rw == 1:  # East wall
                ry = randrange(room[0]) + room[3]
                rx = room[2] + room[1]
                rx2 = rx + 1
                ry2 = ry
            elif rw == 2:  # South wall
                rx = randrange(room[1]) + room[2]
                ry = room[3] + room[0]
                rx2 = rx
                ry2 = ry + 1
            elif rw == 3:  # West wall
                ry = randrange(room[0]) + room[3]
                rx = room[2] - 1
                rx2 = rx - 1
                ry2 = ry
            if self.current_map[ry][rx] == DungeonTileType_WallUp:  # If space is a wall, exit
                break
        return rx, ry, rx2, ry2, rw

    def make_portal(self, px, py):
        """Create doors in walls"""
        ptype = randrange(100)
        if ptype > 90:  # Secret door
            self.current_map[py][px] = DungeonTileType_SecretDoor
            return
        elif ptype > 75:  # Closed door
            self.current_map[py][px] = DungeonTileType_ClosedDoor
            return
        elif ptype > 40:  # Open door
            self.current_map[py][px] = DungeonTileType_OpenedDoor
            return
        else:  # Hole in the wall
            self.current_map[py][px] = DungeonTileType_Empty

    def join_corridor(self, cno, xp, yp, ed, psb):
        """Check corridor endpoint and make an exit if it links to another room"""
        cArea = self.roomList[cno]
        if xp != cArea[2] or yp != cArea[3]:  # Find the corridor endpoint
            endx = xp - (cArea[1] - 1)
            endy = yp - (cArea[0] - 1)
        else:
            endx = xp + (cArea[1] - 1)
            endy = yp + (cArea[0] - 1)
        checkExit = []
        if ed == 0:  # North corridor
            if endx > 1:
                coords = [endx - 2, endy, endx - 1, endy]
                checkExit.append(coords)
            if endy > 1:
                coords = [endx, endy - 2, endx, endy - 1]
                checkExit.append(coords)
            if endx < self.size_x - 2:
                coords = [endx + 2, endy, endx + 1, endy]
                checkExit.append(coords)
        elif ed == 1:  # East corridor
            if endy > 1:
                coords = [endx, endy - 2, endx, endy - 1]
                checkExit.append(coords)
            if endx < self.size_x - 2:
                coords = [endx + 2, endy, endx + 1, endy]
                checkExit.append(coords)
            if endy < self.size_y - 2:
                coords = [endx, endy + 2, endx, endy + 1]
                checkExit.append(coords)
        elif ed == 2:  # South corridor
            if endx < self.size_x - 2:
                coords = [endx + 2, endy, endx + 1, endy]
                checkExit.append(coords)
            if endy < self.size_y - 2:
                coords = [endx, endy + 2, endx, endy + 1]
                checkExit.append(coords)
            if endx > 1:
                coords = [endx - 2, endy, endx - 1, endy]
                checkExit.append(coords)
        elif ed == 3:  # West corridor
            if endx > 1:
                coords = [endx - 2, endy, endx - 1, endy]
                checkExit.append(coords)
            if endy > 1:
                coords = [endx, endy - 2, endx, endy - 1]
                checkExit.append(coords)
            if endy < self.size_y - 2:
                coords = [endx, endy + 2, endx, endy + 1]
                checkExit.append(coords)
        for xxx, yyy, xxx1, yyy1 in checkExit:  # Loop through possible exits
            if self.current_map[yyy][xxx] == DungeonTileType_Empty:  # If joins to a room
                if randrange(100) < psb:  # Possibility of linking rooms
                    self.make_portal(xxx1, yyy1)

    def final_joins(self):
        """Final stage, loops through all the corridors to see if any can be joined to other rooms"""
        for x in self.cList:
            self.join_corridor(x[0], x[1], x[2], x[3], 10)

    def generate_maze(self):
        print("dungeon generation")
        self.make_raw_map(self.width, self.height, 110, 50, 10)
        # self.make_raw_map(self.width, self.height, 110, 50, 1)

    def generate_monsters(self):
        for i in range(1):
            monster = monsters.Bat((), self)
            placed = False
            while not placed:
                x = randrange(self.width - 1)
                y = randrange(self.height - 1)
                if monster.can_place(x, y):
                    monster.x = x
                    monster.y = y
                    self.set_cache(monster)
                    print("Put a " + monster.description + " in " + str(x) + "," + str(y))
                    placed = True

    def set_seen_map(self, d_map, center, width, height):
        (x, y) = center
        min_x = x - width // 2
        min_y = y - height // 2

        before_los = []
        maxy = len(self.current_map)
        maxx = len(self.current_map[0])
        for y in range(min_y, min_y + height):
            for x in range(min_x, min_x + width):
                if y >= 0 and y < maxy and x >= 0 and x < maxx:
                    if Tile.is_seen(d_map[y - min_y][x - min_x]):
                        seen = 1
                    else:
                        seen = 0

                    self.current_map[y][x] = Tile.set_seen(self.current_map[y][x], seen)

    def get_object_real_position(self,object_pos, center, width, height):
        (min_x, min_y) = self.get_map_view_top_left_corner(center, width, height)
        return (min_x + object_pos[0],min_y + object_pos[1])
    def get_map_view_top_left_corner(self, center, width, height):
        (x, y) = center
        min_x = x - width // 2
        min_y = y - height // 2
        return min_x, min_y

    def get_map_view(self, center, width, height):
        (min_x, min_y) = self.get_map_view_top_left_corner(center, width, height)

        before_los = []
        maxy = len(self.current_map)
        maxx = len(self.current_map[0])
        for y in range(min_y, min_y + height):
            tmp_los = []
            for x in range(min_x, min_x + width):
                if y < 0 or y >= maxy:
                    tmp_los.append(DungeonTileType_Earth)
                elif x < 0 or x >= maxx:
                    tmp_los.append(DungeonTileType_Earth)
                else:
                    tmp_los.append(self.current_map[y][x])

            before_los.append(tmp_los)

        return before_los

    @staticmethod
    def get_object_relative_position(object_pos, width, height):
        (x, y) = object_pos
        min_x = x - width // 2
        min_y = y - height // 2
        return (x - min_x, y - min_y)

    def set_player(self, player):
        ok = False
        while not ok:
            x = randrange(self.width - 1)
            y = randrange(self.height - 1)
            ok = self.current_map[y][x] == DungeonTileType_Empty
        player.x = x
        player.y = y
        self.player = player

    def door_opened(self, pos):
        # TODO
        pass

    def can_go_to(self, pos):
        (x, y) = pos
        if (x < 0) or (x > self.width):
            return False

        if (y < 0) or (y > self.height):
            return False

        if self.get_monster(x,y) is not None:
            return False

        tile_type = Tile.get_type(self.current_map[y][x])

        if tile_type in (DungeonTileType_Empty, DungeonTileType_OpenedDoor):
            return True

        if tile_type == DungeonTileType_ClosedDoor:
            self.current_map[y][x] = DungeonTileType_OpenedDoor
            self.door_opened(pos)
            return False

        if tile_type == DungeonTileType_SecretDoor:
            self.current_map[y][x] = DungeonTileType_ClosedDoor
            return False

    def get_tile(self, x, y):
        return self.current_map[y][x]

    def set_cache(self, mon):
        self.monsters_list.append(mon)

    def unset_cache(self, x, y):
        for mons in self.monsters_list:
            if mons.x == x  and mons.y == y:
                self.monsters_list.remove(mons)
                return

    def get_monster(self, x, y):
        for mons in self.monsters_list:
            if mons.x == x and mons.y == y:
                return mons
        return None

    def is_passable(self, col, row):
        if Tile.is_opaque(self.current_map[row][col]):
            return False
        return self.get_monster(col, row) is None

    def pathfind(self, start, end, *, rand=False):
        # Actual A* Search algorithm
        def h(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        g_score = {} # defaultdict(lambda: float("inf"))
        g_score[start] = 0
        f_score = {}
        f_score[start] = h(start, end)
        open_set = OpenSet(f_score.__getitem__)
        open_set.add(start)
        came_from = {}
        rows = len(self.current_map)
        cols = len(self.current_map[0])

        def can_pass(x, y):
            if (x, y) == end:
                return not Tile.is_opaque(self.current_map[y][x])
            return self.is_passable(x, y)

        while open_set:
            curr = open_set.pop()
            if curr == end:
                path = [curr]
                while curr in came_from:
                    curr = came_from[curr]
                    path.append(curr)
                path.reverse()
                return path
            neighbors = []
            x, y = curr
            if x + 1 < cols and can_pass(x + 1, y):
                neighbors.append((x + 1, y))
            if x - 1 >= 0 and can_pass(x - 1, y):
                neighbors.append((x - 1, y))
            if y + 1 < rows and can_pass(x, y + 1):
                neighbors.append((x, y + 1))
            if y - 1 >= 0 and can_pass(x, y - 1):
                neighbors.append((x, y - 1))
            if rand:
                utils.shuffle(neighbors)

            for n in neighbors:
                cost = 1
                t = g_score[curr] + cost
                if n not in g_score:
                    g_score[n] = float("inf")

                if t < g_score[n]:
                    came_from[n] = curr
                    g_score[n] = t
                    f_score[n] = t + h(n, end)

                    if n not in open_set:
                        open_set.add(n)
        return []

    def do_monsters_actions(self):
        for monster in self.monsters_list:
            monster.action()
