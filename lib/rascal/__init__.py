import curses
import random
import queue

class Event:
    def format(self):
        return ''

class PlayerDeadEvent(Event):
    def format(self):
        return 'You have died!'

class PlayerSlainByEvent(PlayerDeadEvent):
    def __init__(self, monster):
        self.slayer = monster

    def format(self):
        return 'You have been slain by a {}!'.format(self.slayer.name)

class MonsterAttackEvent(Event):
    def __init__(self, monster):
        self.monster = monster

    def format(self):
        return 'The {} attacks you for {} damage!'.format(self.monster.name, self.monster.attack)

class SlainMonsterEvent(Event):
    def __init__(self, monster):
        self.monster = monster

    def format(self):
        return 'You have slain the {}!'.format(self.monster.name)

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

    def adjacent_to(self, other : 'Actor'):
        diff_x = abs(self.x - other.x)
        diff_y = abs(self.y - other.y)
        return (diff_x <= 1) and (diff_y <= 1)

    def is_alive(self):
        return self.hitpoints > 0

class Player(Actor):
    symbol = '@'
    hitpoints = 10
    attack = 1
    def __init__(self, name):
        self.name = name
        super().__init__()

class Monster(Actor):
    pass

class Rat(Monster):
    symbol = 'r'
    name = 'rat'
    hitpoints = 1
    attack = 1

class GiantRat(Monster):
    symbol = 'R'
    name = 'giant rat'
    hitpoints = 2
    attack = 1

class Goblin(Monster):
    symbol = 'g'
    name = 'goblin'
    hitpoints = 1
    attack = 2

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
        self.monsters = [
            Rat(),
            Rat(),
            GiantRat(),
            Goblin(),
            ]
        self.randomly_place_monsters(player, *self.monsters)
        self.events = queue.Queue()

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
            self.events.put_nowait(SlainMonsterEvent(monster))

    def move_player_to(self, diff_x, diff_y):
        xx = self.player.x + diff_x
        yy = self.player.y + diff_y
        if self.has_monster_at(xx, yy):
            self.attack_monster_at(xx, yy)
        elif self.occupiable(xx, yy):
            self.add_redraw_terrain((self.player.x, self.player.y))
            self.player.x = xx
            self.player.y = yy

    def move_monster_to(self, monster, diff_x, diff_y):
        xx = monster.x + diff_x
        yy = monster.y + diff_y
        if self.occupiable(xx, yy):
            self.add_redraw_terrain((monster.x, monster.y))
            monster.x = xx
            monster.y = yy
            
    def run_monster_actions(self):
        for monster in self.monsters:
            if monster.adjacent_to(self.player):
                # attack
                self.events.put_nowait(MonsterAttackEvent(monster))
                self.player.hitpoints -= monster.attack
                if not self.player.is_alive():
                    self.events.put_nowait(PlayerSlainByEvent(monster))
            else:
                # move
                dx = self.player.x - monster.x
                dy = self.player.y - monster.y
                if abs(dx) > abs(dy):
                    dx = 1 if dx > 0 else -1
                    dy = 0
                else:
                    dx = 0
                    dy = 1 if dy > 0 else -1
                self.move_monster_to(monster, dx, dy)
                
class View:
    def __init__(self, player):
        self.world = World(MAPPING, player)
        self.stats_line = self.world.height
        self.message_line = self.world.height + 1
        self.last_message = 'Bye!'

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
        print(self.last_message)

    def _run_forever(self):
        self.init_paint()
        self.message('Kill all monsters!')
        while True:
            ch = self.window.getkey()
            stop = self.handle_input(ch)
            if stop:
                break
            self.world.run_monster_actions()
            self.paint()
            if not self.world.player.is_alive():
                return
            self.inc_message_display_count()
            if self.message_display_done():
                self.message('')

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
        # draw terrain
        for xx, yy in self.world.get_and_clear_redraw_points():
            self.window.move(xx, yy)
            self.window.delch()
            self.window.insch(self.world.terrain[xx][yy])
        # monsters
        for monster in self.world.monsters:
            assert monster.is_alive(), (monster, self.world.monsters)
            monster.draw(self.window)
        # stats line
        self.window.move(self.stats_line, 0)
        self.window.deleteln()
        self.window.insertln()
        status_msg = 'HP {}'.format(self.world.player.hitpoints)
        status_msg = status_msg[:self.world.width]
        self.window.insstr(status_msg)
        # messages
        while True:
            try:
                event = self.world.events.get_nowait()
            except queue.Empty:
                break
            if isinstance(event, PlayerDeadEvent):
                self.last_message = event.format()
            self.message(event.format())
        # player
        self.world.player.draw(self.window)
        self.window.refresh()

    def message(self, content):
        self.reset_message_display_count()
        xx, yy = self.window.getyx()
        content = content[:self.world.width]
        self.window.move(self.message_line, 0)
        self.window.deleteln()
        self.window.insertln()
        self.window.insstr(content)
        self.window.move(xx, yy)
    
    def handle_input(self, ch):
        retval = None
        try:
            retval = handlers[ch](self.world)
        except KeyError:
            pass # unmapped key
        return retval

    def is_stop(self, ch):
        return ch == 'q'

    def reset_message_display_count(self):
        self._message_display_count = 0

    def inc_message_display_count(self):
        self._message_display_count += 1

    def message_display_done(self):
        return self._message_display_count > 5
    
def main(args):
    player = Player('Aaron')
    View(player).run_forever()
    
