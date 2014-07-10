import curses
import random

class Player:
    def __init__(self, name):
        self.name = name
        self.x = 5
        self.y = 5


class Monster:
    symbol = '?'
    name = '?'
    def __init__(self):
        self.x = 0
        self.y = 0

class Rat(Monster):
    symbol = 'r'
    name = 'rat'

def hd_redraw_original_player_pos(handle):
    def newhandle(world):
        world.add_redraw_terrain((world.player.x, world.player.y))
        return handle(world)
    return newhandle

@hd_redraw_original_player_pos
def handle_move_down(world):
    new_x = world.player.x + 1
    if world.occupiable(new_x, world.player.y):
        world.player.x = new_x

@hd_redraw_original_player_pos
def handle_move_up(world):
    new_x = world.player.x - 1
    if world.occupiable(new_x, world.player.y):
        world.player.x = new_x

@hd_redraw_original_player_pos
def handle_move_left(world):
    new_y = world.player.y - 1
    if world.occupiable(world.player.x, new_y):
        world.player.y = new_y

@hd_redraw_original_player_pos
def handle_move_right(world):
    new_y = world.player.y + 1
    if world.occupiable(world.player.x, new_y):
        world.player.y = new_y

def handle_quit(world):
    return True

handlers = {
    'j' : handle_move_down,
    'k' : handle_move_up,
    'h' : handle_move_left,
    'l' : handle_move_right,
    'q' : handle_quit,
    }


MAPPING = '''
############################################################
#                                                          #
#                                                          #
#                                                          #
#                                                          #
#              ##########                                  #
#              #        #                                  #
#                       ###########################        #
#              #                                  #        #
#              ########################           #        #
#                                     #           #        #
#                                     #############        #
#############                                              #
#                                                          #
#           #                                              #
#           #                                              #
#           #                                              #
#############                                              #
#                                                          #
#                                                          #
############################################################
'''

class World:
    def __init__(self, mapping, player):
        self.terrain = [[point for point in line.strip()]
                        for line in mapping.strip().split('\n')]
        widths = set(len(row) for row in self.terrain)
        assert len(widths) == 1, 'Got varying widths: {}'.format(widths)
        self.width = widths.pop()
        self.height = len(self.terrain)
        self.player = player
        self._redraw_points = set()
        self.monsters = [Rat(), Rat(), Rat()]
        self.randomly_place_monsters(*self.monsters)

    def occupiable(self, x, y):
        if self.terrain[x][y] == '#':
            return False
        if (x, y) in set((m.x, m.y) for m in self.monsters):
            return False
        return True

    def randomly_place_monsters(self, *monsters):
        actor_positions = set((self.player.x, self.player.y))
        for monster in monsters:
            while True:
                xx = random.randrange(0, self.height)
                yy = random.randrange(0, self.width)
                if (xx, yy) in actor_positions:
                    continue
                if not self.occupiable(xx, yy):
                    continue
                monster.x = xx
                monster.y = yy
                actor_positions.add((xx, yy))
                break

    def add_redraw_terrain(self, point):
        self._redraw_points.add(point)

    def get_and_clear_redraw_points(self):
        points = self._redraw_points
        self._redraw_points = set()
        return points

class View:
    def __init__(self, player):
        self.world = World(MAPPING, player)

    def run_forever(self):
        try:
            self.window = curses.initscr()
            curses.cbreak()
            curses.noecho()
            self._run_forever()
        except:
            curses.endwin()
            raise
        curses.endwin()
        print('Bye!')

    def _run_forever(self):
        self.init_paint()
        while True:
            ch = self.window.getkey()
            stop = self.handle_input(ch)
            if stop:
                break
            self.paint()

    def init_paint(self):
        self.window.clear()
        for xx in range(self.world.height):
            for yy in range(self.world.width):
                self.window.move(xx, yy)
                self.window.delch()
                self.window.insch(self.world.terrain[xx][yy])
        self.paint()
        self.window.refresh()

    def paint(self):
        for xx, yy in self.world.get_and_clear_redraw_points():
            self.window.move(xx, yy)
            self.window.delch()
            self.window.insch(self.world.terrain[xx][yy])
        self.window.move(self.world.player.x, self.world.player.y)
        self.window.delch()
        self.window.insch('@')
        for monster in self.world.monsters:
            self.window.move(monster.x, monster.y)
            self.window.delch()
            self.window.insch(monster.symbol)
        self.window.move(self.world.player.x, self.world.player.y)
        self.window.refresh()
    
    def handle_input(self, ch):
        retval = None
        try:
            retval = handlers[ch](self.world)
        except KeyError:
            pass # unmapped key
        return retval

    def is_stop(self, ch):
        return ch == 'q'
        
def main(args):
    player = Player('Aaron')
    View(player).run_forever()
    
