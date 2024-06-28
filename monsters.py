from apps.Catacombs import world 
from apps.Catacombs import los
from apps.Catacombs import dungeon
from apps.Catacombs import entities
from apps.Catacombs import utils

import math
import random
import sys
from collections import deque

class Monster(entities.LivingThing):

    STATE_SLEEPING = 0
    STATE_ATTACKING = 1
    STATE_HUNTING = 2
    STATE_FLEEING = 3

    DEQUE_MAX_SIZE = 20
    
    def __init__(self,pos,curr_dungeon,image):
        super().__init__(pos,curr_dungeon,image)
        self.fov_radius = 6
        self.dungeon = curr_dungeon
        self.fov = []
        self.fov_map_size = self.fov_radius * 2
        self.curr_target = None
        self.curr_path = deque((),self.DEQUE_MAX_SIZE)
        self.placed = False
        self.energy = 0  # How many energy points this entity has. Used to control movement speed.
        self.description = ""
        self.state = self.STATE_SLEEPING

    def action(self):
        if self.state == self.STATE_SLEEPING :
            """ look if player in fov"""
            self.calc_fov()
            if self.dungeon.player.current_pos() in self.fov:
                self.state = self.STATE_HUNTING
            else:
                return

        if self.state == self.STATE_HUNTING:
            self.path_towards(self.dungeon.player.current_pos())
            dist = self.distance(self.dungeon.player)
            if dist <= 1:
                self.state = self.STATE_ATTACKING
            else:
                return

        if self.state == self.STATE_ATTACKING:
            #print("Attacking !!!")
            # TODO Verify if still in LOS, if not, sleep
            dist = self.distance(self.dungeon.player)
            if dist <= 1:
                """Attack"""
                pass
            else:
                self.state = self.STATE_HUNTING


    def calc_fov(self):
        "Calculates all tiles an entity can see from the current position"
        self.fov = []

        d_map = self.dungeon.get_map_view(self.current_pos(), self.fov_map_size , self.fov_map_size)
        (x,y) = self.dungeon.get_object_relative_position(self.current_pos(), self.fov_map_size ,self.fov_map_size)
        offset = self.dungeon.get_map_view_top_left_corner(self.current_pos(), self.fov_map_size, self.fov_map_size)
        los_map = los.LosMap(self.dungeon,d_map)
        los_map.do_fov(x, y, self.fov_radius)
        for y in range(self.fov_map_size):
            for x in range(self.fov_map_size):
                if los_map.is_lit(x,y):
                    self.fov.append((x + offset[0],y + offset[1]))

    def can_see(self, x, y):
        return (x, y) in self.fov

    def distance(self, other, manhattan=True):
        dx = abs(self.x - other.x)
        dy = abs(self.y - other.y)
        if manhattan:
            return dx + dy
        return max(dx, dy)

    def distance_pos(self, pos):
        return abs(self.x - pos[0]) + abs(self.y - pos[1])

    def clear_path(self):
        self.curr_path.clear()

    def path_towards(self, target_pos , maxlen=None):
        (x,y) = target_pos
        if self.curr_target == (x, y) and self.curr_path and self.move_to(*self.curr_path.popleft()):
            if (self.x, self.y) == (x, y):
                self.clear_path()
            return
        path = self.dungeon.pathfind((self.x, self.y), (x, y), rand=True)
        if len(path) < 2:
            return
        if maxlen and len(path) > maxlen + 1:
            return
        currX, currY = self.x, self.y
        self.curr_target = (x, y)
        self.curr_path = deque(path[1:],self.DEQUE_MAX_SIZE)
        newX, newY = self.curr_path.popleft()
        dx = newX - currX
        dy = newY - currY
        self.move(dx, dy)

    def set_path(self, path):
        self.curr_path = deque(path)

    def can_place(self, x, y):
        if (x, y) == (self.dungeon.player.x,  self.dungeon.player.y):
            return False
        if not self.dungeon.is_passable(x, y):
            return False
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        for xp, yp in neighbors:
            if self.dungeon.is_passable(xp, yp):
                return True
        return False

    def place_randomly(self):
        board_cols = self.dungeon.width
        board_rows = self.dungeon.height
        for _ in range(200):
            x = random.randint(1, board_cols - 2)
            y = random.randint(1, board_rows - 2)
            if self.can_place(x, y):
                break
        else:  # We couldn't place the player randomly, so let's search all possible positions in a random order
            row_ind = list(range(1, board_rows - 1))
            random.shuffle(row_ind)
            found = False
            for y_pos in row_ind:
                col_ind = list(range(1, board_cols - 1))
                random.shuffle(col_ind)
                for xpos in col_ind:
                    if self.can_place(xpos, y_pos):
                        x, y = xpos, y_pos
                        found = True
                        break
                if found:
                    break
            else:
                return False
        self.place_at(x, y)
        return True

    def place_at(self, x, y):
        old = (self.x, self.y)
        self.x = x
        self.y = y
        if self.placed:
            self.dungeon.swap_cache(old, (self.x, self.y))
        else:
            self.placed = True
            self.dungeon.set_cache(x, y, self)

    def swap_with(self, other):
        tmp = (self.x, self.y)
        self.x, self.y = other.x, other.y
        other.x, other.y = tmp

    def can_move(self, x, y):
        return self.dungeon.is_passable(x, y)

    def move_to(self, x, y):
        if self.can_move(x, y):
            old_pos = (self.x, self.y)
            self.x = x
            self.y = y
            return True
        return False

    def move(self, dx, dy):
        return self.move_to(self.x + dx, self.y + dy)

"""
 ███████████                    █████     ███                                
░░███░░░░░███                  ░░███     ░░░                                 
 ░███    ░███  ██████   █████  ███████   ████   ██████   ████████  █████ ████
 ░██████████  ███░░███ ███░░  ░░░███░   ░░███  ░░░░░███ ░░███░░███░░███ ░███ 
 ░███░░░░░███░███████ ░░█████   ░███     ░███   ███████  ░███ ░░░  ░███ ░███ 
 ░███    ░███░███░░░   ░░░░███  ░███ ███ ░███  ███░░███  ░███      ░███ ░███ 
 ███████████ ░░██████  ██████   ░░█████  █████░░████████ █████     ░░███████ 
░░░░░░░░░░░   ░░░░░░  ░░░░░░     ░░░░░  ░░░░░  ░░░░░░░░ ░░░░░       ░░░░░███ 
                                                                    ███ ░███ 
                                                                   ░░██████  
                                                                    ░░░░░░   
 """

class Bat(Monster):
    min_level = 1
    diff = 1
    DEX = 15
    WIS = 12
#     attacks = [
#         Attack((1, 3), 0, "The {0} bites {1}")
#     ]

    def __init__(self,pos,cur_dungeon):
        super().__init__(pos,cur_dungeon,"B")
        self.description = "dark and ugly bat"
