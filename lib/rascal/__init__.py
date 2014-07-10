import curses

class Player:
    def __init__(self, name):
        self.name = name
        self.x = 5
        self.y = 5

def hd_redraw_original_player_pos(handle):
    def newhandle(world):
        world.add_redraw_terrain((world.player.x, world.player.y))
        return handle(world)
    return newhandle

@hd_redraw_original_player_pos
def handle_move_down(world):
    new_x = world.player.x + 1
    if world.terrain[new_x][world.player.y] == ' ':
        world.player.x = new_x

@hd_redraw_original_player_pos
def handle_move_up(world):
    new_x = world.player.x - 1
    if world.terrain[new_x][world.player.y] == ' ':
        world.player.x = new_x

@hd_redraw_original_player_pos
def handle_move_left(world):
    new_y = world.player.y - 1
    if world.terrain[world.player.x][new_y] == ' ':
        world.player.y = new_y

@hd_redraw_original_player_pos
def handle_move_right(world):
    new_y = world.player.y + 1
    if world.terrain[world.player.x][new_y] == ' ':
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
    
