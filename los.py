"FOV calculation for roguelike"
FOV_RADIUS = 10

class LosMap(object):
    # Multipliers for transforming coordinates to other octants:
    mult = [
                [1,  0,  0, -1, -1,  0,  0,  1],
                [0,  1, -1,  0,  0, -1,  1,  0],
                [0,  1,  1,  0,  0, -1, -1,  0],
                [1,  0,  0,  1, -1,  0,  0, -1]
            ]

    def __init__(self, dungeon, map):
        self.data = map
        self.dungeon = dungeon
        self.width, self.height = len(map[0]), len(map)
        self.light = []
        for i in range(self.height):
            self.light.append([0] * self.width)
            
        self.flag = 0

    def square(self, x, y):
        return self.data[y][x]

    def blocked(self, x, y):
        return (x < 0 or y < 0
                or x >= self.width or y >= self.height
                or self.dungeon.tile_blocks_light(self.data[y][x]))

    def lit(self, x, y):
        return self.light[y][x] == self.flag

    def set_lit(self, x, y):
        if 1 <= x < self.width and 0 <= y < self.height:
            self.light[y][x] = self.flag

    def is_lit(self, x, y):
        return self.light[y][x] == self.flag

    def _cast_light(self, cx, cy, row, start, end, radius, xx, xy, yx, yy, id):
        "Recursive lightcasting function"
        if start < end:
            return
        radius_squared = radius*radius
        for j in range(row, radius+1):
            dx, dy = -j-1, -j
            blocked = False
            while dx <= 0:
                dx += 1
                # Translate the dx, dy coordinates into map coordinates:
                X, Y = cx + dx * xx + dy * xy, cy + dx * yx + dy * yy
                # l_slope and r_slope store the slopes of the left and right
                # extremities of the square we're considering:
                l_slope, r_slope = (dx-0.5)/(dy+0.5), (dx+0.5)/(dy-0.5)
                if start < r_slope:
                    continue
                elif end > l_slope:
                    break
                else:
                    # Our light beam is touching this square; light it:
                    if dx*dx + dy*dy < radius_squared:
                        self.set_lit(X, Y)
                    if blocked:
                        # we're scanning a row of blocked squares:
                        if self.blocked(X, Y):
                            new_start = r_slope
                            continue
                        else:
                            blocked = False
                            start = new_start
                    else:
                        if self.blocked(X, Y) and j < radius:
                            # This is a blocking square, start a child scan:
                            blocked = True
                            self._cast_light(cx, cy, j+1, start, l_slope,
                                             radius, xx, xy, yx, yy, id+1)
                            new_start = r_slope
            # Row is scanned; do next row unless last square was blocked:
            if blocked:
                break

    def do_fov(self, x, y, radius):
        "Calculate lit squares from the given location and radius"
        self.flag += 1
        for oct in range(8):
            self._cast_light(x, y, 1, 1.0, 0.0, radius,
                             self.mult[0][oct], self.mult[1][oct],
                             self.mult[2][oct], self.mult[3][oct], 0)



