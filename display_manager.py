print("#Display_Manager")
from lib import st7789fbuf, mhconfig, keyboard
from machine import Pin, PWM, SPI, soft_reset, SDCard
import os,time
import random

_DISPLAY_HEIGHT = const(135)
_DISPLAY_WIDTH = const(240)
_DISPLAY_WIDTH_HALF = const(_DISPLAY_WIDTH // 2)

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

def clear_screen():
    #clear framebuffer 
    tft.fill(config['bg_color'])

def init():
    pass


def before_loop():
    #asciimap()
    pass


ViewPort_DISPLAY_HEIGHT = const(17)
ViewPort_DISPLAY_WIDTH = const(30)


## 8x8
from apps.Catacombs import vga2_8x8 as font
_CHAR_WIDTH = const(8)
_CHAR_WIDTH_HALF = const(_CHAR_WIDTH // 2)
_CHAR_HEIGHT = _CHAR_WIDTH





# object for reading keypresses
kb = keyboard.KeyBoard()

from apps.Catacombs import dungeon 

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


def get_tile_color(tile):
    if dungeon.Tile.is_lit(tile):
        return 0xFFFF
    if dungeon.Tile.is_seen(tile) and not dungeon.Tile.is_opaque(tile):
        return 0x3131
    else:
        return 0x0000

from apps.Catacombs import monsters

def get_monster_color(monster):
    if isinstance(monster, monsters.Bat):
        return 0x7788

def display_monster(y, x, monster):
    display_text(monster.image, x,y,get_monster_color(monster))


def display_tile(y, x, tile):
    color = get_tile_color(tile)
    char = TilesDisplay[dungeon.Tile.get_type(tile)]
    display_text(char, x,y,color)


def display_player(y, x, player):
    display_text(player.image, x, y, st7789fbuf.GREEN)


def screen_refresh():
    # write framebuffer to display
    tft.show()


def get_key():
        keys=[]
        # if there are keys, convert them to a string, and store for display
        while not keys:
            # get list of newly pressed keys
            keys = kb.get_new_keys()
        return keys[0]



def display_text(text,col,line,color = config['ui_color']):
    tft.bitmap_text(font,text, col * _CHAR_WIDTH,_CHAR_HEIGHT * line, color)


def terminate():
    tft.fill(config['bg_color'])
    tft.soft_reset()

# def what_screen_size():
#     #clear framebuffer 
#     tft.fill(config['bg_color'])
#     line ="123456789012345678901234567890123456789012345678901234567890"
#     line_number = 0
#     while line_number < 30:
#         display_text(line,0,line_number)
#         line_number = line_number + 1
#     
#     tft.show()            
# 
#     keys=[]
#     # if there are keys, convert them to a string, and store for display
#     while not keys:
#         # get list of newly pressed keys
#         keys = kb.get_new_keys()
#     
# 
# def ascii_map():
#     #clear framebuffer 
#     tft.fill(config['bg_color'])
#     y= 169
#     line =""
#     line_number = 0
#     color = 0xEEEE
#     while y < 255:
#         if (y-169) % 5 == 0:
#             tft.bitmap_text(font,line, 0,_CHAR_HEIGHT * (line_number-1), color)
#             line = ""
#             line_number=line_number+1
#             color = color + 16
#         line = line + str(y) + ":" + chr(y)+ " "
#         y=y+1
#     tft.show()            
# 
#     keys=[]
#     # if there are keys, convert them to a string, and store for display
#     while not keys:
#         # get list of newly pressed keys
#         keys = kb.get_new_keys()
# 
# 
# def color_map2():
#     #clear framebuffer 
#     tft.fill(config['bg_color'])
#     y= 0
#     line_number = 0
#     color = 0x0000
#     ratio = (ViewPort_DISPLAY_HEIGHT*ViewPort_DISPLAY_WIDTH)
#     for y in range(ViewPort_DISPLAY_HEIGHT):
#         for x in range(5):            
#             color = ((y * ViewPort_DISPLAY_HEIGHT + x * ViewPort_DISPLAY_WIDTH) * 0xFFFF) // ratio
#             tft.bitmap_text(font,hex(color), x * 6 * _CHAR_WIDTH ,_CHAR_HEIGHT * y, color)
# 
#     tft.show()            
# 
#     keys=[]
#     # if there are keys, convert them to a string, and store for display
#     while not keys:
#         # get list of newly pressed keys
#         keys = kb.get_new_keys()
#         
#         
# def color_map():
#     #clear framebuffer 
#     tft.fill(config['bg_color'])
#     y= 0
#     line_number = 0
#     color = 0x0000
#     ratio = (ViewPort_DISPLAY_HEIGHT*ViewPort_DISPLAY_WIDTH)
#     for y in range(ViewPort_DISPLAY_HEIGHT):
#         for x in range(ViewPort_DISPLAY_WIDTH):
#             color = ((y * ViewPort_DISPLAY_HEIGHT + x * ViewPort_DISPLAY_WIDTH) * 0xFFFF) // ratio
#             tft.bitmap_text(font,chr(219), x * _CHAR_WIDTH ,_CHAR_HEIGHT * y, color)
# 
#     tft.show()            
# 
#     keys=[]
#     # if there are keys, convert them to a string, and store for display
#     while not keys:
#         # get list of newly pressed keys
#         keys = kb.get_new_keys()     

print(">Display_Manager")
