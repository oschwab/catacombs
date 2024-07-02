print("#Catacombs")
import sys
from apps.Catacombs import world
from apps.Catacombs import dungeon
from apps.Catacombs import display_manager

    
class Game(object):
    

    def __init__(self):     
        self.current_world = world.World()

        

    def handle_key(self,key):
        try:        
            is_dir = key in ('u','i','o','h','j','k','b','n','m')        
            if is_dir:
                dir= world.CENTER
                if key == 'm':
                    dir= world.SOUTHEAST
                elif key == 'n':
                    dir= world.SOUTH
                elif key == 'b':
                    dir= world.SOUTHWEST
                elif key == 'h':
                    dir= world.WEST
                elif key == 'j':
                    dir= world.CENTER
                elif key == 'k':
                    dir= world.EAST
                elif key == 'o':
                    dir= world.NORTHEAST
                elif key == 'i':
                    dir= world.NORTH
                elif key == 'u':
                    dir= world.NORTHWEST
              
                self.current_world.try_move_player(dir)
                return
            if key in ('q','Q'):
                #clear framebuffer 
                display_manager.terminate();
                sys.exit()
            
        except ValueError:
            pass
        
    def main_loop(self):
        display_manager.before_loop()

        while True:
            width = display_manager.ViewPort_DISPLAY_WIDTH
            height = display_manager.ViewPort_DISPLAY_HEIGHT

            d_map= self.current_world.get_current_map(width, height)

            display_manager.clear_screen()

            line_number = 0

            for y in range(height):
                for x in range(width):
                    if dungeon.Tile.is_lit(d_map[y][x]) or dungeon.Tile.is_seen(d_map[y][x]):
                        monster= self.current_world.get_monster(x, y, width, height)
                        if dungeon.Tile.is_lit(d_map[y][x]) and (monster is not None):
                            display_manager.display_monster(y, x, monster)
                        else:
                            display_manager.display_tile(y, x, d_map[y][x])

                line_number = line_number + 1
            player_pos= self.current_world.current_dungeon.get_object_relative_position(
                self.current_world.player.current_pos(),
                width,
                height)
            display_manager.display_player(player_pos[1], player_pos[0], self.current_world.player)

            display_manager.screen_refresh()
            self.current_world.end_turn()
            key = display_manager.get_key()
            self.handle_key(key)


game = Game()
game.main_loop()
print(">Catacombs")