import curses
import random

class Actor:
    symbol = '?'
    name = '?'
    hitpoints = 0
    attack = 0
    def __init__(self):
        self.x = 0
        self.y = 0

    def draw(self, window):
        window.move(self.x, self.y)
        window.delch()
        window.insch(self.symbol)
        

class Player(Actor):
    symbol = '@'
    hitpoints = 10
    attack = 1
    def __init__(self, name):
        self.name = name
        super().__init__()


class Monster(Actor):
    def is_alive(self):
        return self.hitpoints > 0

class Rat(Monster):
    symbol = 'r'
    name = 'rat'
    hitpoints = 1
    attack = 1

def handle_move_down(world):
    return world.move_player_to(1, 0)

def handle_move_up(world):
    return world.move_player_to(-1, 0)

def handle_move_left(world):
    return world.move_player_to(0, -1)

def handle_move_right(world):
    return world.move_player_to(0, 1)

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
        self.randomly_place_monsters(player, *self.monsters)

    def monster_positions(self):
        return {(monster.x, monster.y) : monster
                for monster in self.monsters}

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
    
    def has_monster_at(self, xx, yy):
        return (xx, yy) in self.monster_positions().keys()

    def attack_monster_at(self, xx, yy):
        monster = self.monster_positions()[(xx, yy)]
        monster.hitpoints -= self.player.attack
        if not monster.is_alive():
            self.add_redraw_terrain((xx, yy))
            self.monsters.remove(monster)

    def move_player_to(self, diff_x, diff_y):
        xx = self.player.x + diff_x
        yy = self.player.y + diff_y
        if self.has_monster_at(xx, yy):
            self.attack_monster_at(xx, yy)
        elif self.occupiable(xx, yy):
            self.add_redraw_terrain((self.player.x, self.player.y))
            self.player.x = xx
            self.player.y = yy

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
        for monster in self.world.monsters:
            if monster.is_alive():
                monster.draw(self.window)
        self.world.player.draw(self.window)
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
    
