from lib import st7789fbuf, mhconfig, keyboard
from machine import Pin, PWM, SPI, soft_reset, SDCard
import os,time
import random
import sys

from apps.Catacombs import world
from apps.Catacombs import dungeon
#from apps.Catacombs import sprites
 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CONSTANTS: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
_DISPLAY_HEIGHT = const(135)
_DISPLAY_WIDTH = const(240)
_DISPLAY_WIDTH_HALF = const(_DISPLAY_WIDTH // 2)


## 8x8
from apps.Catacombs import vga2_8x8 as font
_CHAR_WIDTH = const(8)
_CHAR_WIDTH_HALF = const(_CHAR_WIDTH // 2)
_CHAR_HEIGHT = _CHAR_WIDTH
ViewPort_DISPLAY_HEIGHT = 17
ViewPort_DISPLAY_WIDTH = 30

# from apps.Catacombs import vga2_8x16 as font
# ## 8x16
# _CHAR_WIDTH = const(8)
# _CHAR_WIDTH_HALF = const(_CHAR_WIDTH // 2)
# _CHAR_HEIGHT = 16
# ViewPort_DISPLAY_HEIGHT = 8
# ViewPort_DISPLAY_WIDTH = 30


# ## 16x32
# from font import vga2_16x32 as font
# _CHAR_WIDTH = const(32)
# _CHAR_WIDTH_HALF = const(_CHAR_WIDTH // 2)
# _CHAR_HEIGHT = const(16)
# ViewPort_DISPLAY_HEIGHT = 4
# ViewPort_DISPLAY_WIDTH = 17

TilesDisplay = {
    dungeon.DungeonTileType_WallUpLeft: chr(219),
    dungeon.DungeonTileType_WallUp: chr(219),
    dungeon.DungeonTileType_WallUpRight: chr(219),
    dungeon.DungeonTileType_WallLeft: chr(219),
    dungeon.DungeonTileType_WallDownLeft: chr(219),
    dungeon.DungeonTileType_WallDown: chr(219),
    dungeon.DungeonTileType_WallDownRight: chr(219),
    dungeon.DungeonTileType_WallRight: chr(219),
    dungeon.DungeonTileType_SecretDoor: chr(179),
    dungeon.DungeonTileType_ClosedDoor: chr(179),
    dungeon.DungeonTileType_OpenedDoor: " ",
    dungeon.DungeonTileType_Empty: chr(176),
    dungeon.DungeonTileType_Earth: " ",
    dungeon.DungeonTileStairsUp: "<",
    dungeon.DungeonTileStairsDown: ">",
}




# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GLOBAL OBJECTS: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# init object for accessing display
tft = st7789fbuf.ST7789(
    SPI(
        1,baudrate=40000000,sck=Pin(36),mosi=Pin(35),miso=None),
    _DISPLAY_HEIGHT,
    _DISPLAY_WIDTH,
    reset=Pin(33, Pin.OUT),
    cs=Pin(37, Pin.OUT),
    dc=Pin(34, Pin.OUT),
    backlight=Pin(38, Pin.OUT),
    rotation=1,
    color_order=st7789fbuf.BGR
    )

# object for accessing microhydra config (Delete if unneeded)
config = mhconfig.Config()

# object for reading keypresses
kb = keyboard.KeyBoard()


current_world = world.World()



def handleKey(key):
    try:        
        is_dir = key in ('u','i','o','h','j','k','b','n','m')        
        if is_dir:
            dir = world.CENTER
            if key == 'm':
                dir = world.SOUTHEAST
            elif key == 'n':
                dir = world.SOUTH
            elif key == 'b':
                dir = world.SOUTHWEST
            elif key == 'h':
                dir = world.WEST
            elif key == 'j':
                dir = world.CENTER
            elif key == 'k':
                dir = world.EAST
            elif key == 'o':
                dir = world.NORTHEAST
            elif key == 'i':
                dir = world.NORTH
            elif key == 'u':
                dir = world.NORTHWEST
          
            current_world.try_move_player(dir)
            return
        if key in ('q','Q'):
            #clear framebuffer 
            tft.fill(config['bg_color'])
            tft.soft_reset()
            sys.exit()
        
    except ValueError:
        pass
    
def what_screen_size():
    #clear framebuffer 
    tft.fill(config['bg_color'])
    line ="123456789012345678901234567890123456789012345678901234567890"
    line_number = 0
    while line_number < 30:
        display_text(line,0,line_number)
        line_number = line_number + 1
    
    tft.show()            

    keys=[]
    # if there are keys, convert them to a string, and store for display
    while not keys:
        # get list of newly pressed keys
        keys = kb.get_new_keys()
    

def ascii_map():
    #clear framebuffer 
    tft.fill(config['bg_color'])
    y= 169
    line =""
    line_number = 0
    color = 0xEEEE
    while y < 255:
        if (y-169) % 5 == 0:
            tft.bitmap_text(font,line, 0,_CHAR_HEIGHT * (line_number-1), color)
            line = ""
            line_number=line_number+1
            color = color + 16
        line = line + str(y) + ":" + chr(y)+ " "
        y=y+1
    tft.show()            

    keys=[]
    # if there are keys, convert them to a string, and store for display
    while not keys:
        # get list of newly pressed keys
        keys = kb.get_new_keys()


def color_map2():
    #clear framebuffer 
    tft.fill(config['bg_color'])
    y= 0
    line_number = 0
    color = 0x0000
    ratio = (ViewPort_DISPLAY_HEIGHT*ViewPort_DISPLAY_WIDTH)
    for y in range(ViewPort_DISPLAY_HEIGHT):
        for x in range(5):            
            color = ((y * ViewPort_DISPLAY_HEIGHT + x * ViewPort_DISPLAY_WIDTH) * 0xFFFF) // ratio
            tft.bitmap_text(font,hex(color), x * 6 * _CHAR_WIDTH ,_CHAR_HEIGHT * y, color)

    tft.show()            

    keys=[]
    # if there are keys, convert them to a string, and store for display
    while not keys:
        # get list of newly pressed keys
        keys = kb.get_new_keys()
        
        
def color_map():
    #clear framebuffer 
    tft.fill(config['bg_color'])
    y= 0
    line_number = 0
    color = 0x0000
    ratio = (ViewPort_DISPLAY_HEIGHT*ViewPort_DISPLAY_WIDTH)
    for y in range(ViewPort_DISPLAY_HEIGHT):
        for x in range(ViewPort_DISPLAY_WIDTH):
            color = ((y * ViewPort_DISPLAY_HEIGHT + x * ViewPort_DISPLAY_WIDTH) * 0xFFFF) // ratio
            tft.bitmap_text(font,chr(219), x * _CHAR_WIDTH ,_CHAR_HEIGHT * y, color)

    tft.show()            

    keys=[]
    # if there are keys, convert them to a string, and store for display
    while not keys:
        # get list of newly pressed keys
        keys = kb.get_new_keys()        

        
def display_text(text,col,line,color = config['ui_color']):
    tft.bitmap_text(font,text, col * _CHAR_WIDTH,_CHAR_HEIGHT * line, color)

def display_dungeon():

        #clear framebuffer 
        tft.fill(config['bg_color'])
        d_map = current_world.get_current_map(ViewPort_DISPLAY_WIDTH,ViewPort_DISPLAY_HEIGHT)
        for y in range(ViewPort_DISPLAY_HEIGHT):
            for x in range(ViewPort_DISPLAY_WIDTH):
                if dungeon.Tile.is_lit(d_map[y][x]) or dungeon.Tile.is_seen(d_map[y][x]) :
                  
                    monster = current_world.get_monster(x, y,ViewPort_DISPLAY_WIDTH, ViewPort_DISPLAY_HEIGHT)
                    if dungeon.Tile.is_lit(d_map[y][x]) and ( monster is not None):
                        display_text(monster.image, x,y,get_monster_color(monster))
                    else:
                        color = get_tile_color(d_map[y][x])
                        char = Tiles[dungeon.Tile.get_type(d_map[y][x])]
                        display_text(char, x,y,color)

        player_pos = current_world.current_dungeon.get_object_relative_position(current_world.player.current_pos(),ViewPort_DISPLAY_WIDTH,ViewPort_DISPLAY_HEIGHT)
        display_text(current_world.player.image, player_pos[0],player_pos[1], st7789fbuf.GREEN)
        # write framebuffer to display
        tft.show()

def get_tile_color(tile):
    if dungeon.Tile.is_lit(tile):
        return 0xFFFF
    if dungeon.Tile.is_seen(tile) and not dungeon.Tile.is_opaque(tile):
        return 0x3131
    else:
        return 0x0000

def get_monster_color(monster):
    if isinstance(monster, monsters.Bat):
        return 0x0088


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main Loop: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main_loop():
    #ascii_map()
    #color_map2()
    while True:
        display_dungeon()
        keys=[]
        # if there are keys, convert them to a string, and store for display
        while not keys:
            # get list of newly pressed keys
            keys = kb.get_new_keys()
        #print("k=",keys)
        handleKey(keys[0])        
        
        # do nothing for 10 milliseconds
        time.sleep_ms(10)


# start the main loop
main_loop()