import random
import queue
from .actors import *
from .events import *

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
    def __init__(self, player):
        self.terrain = [[point for point in line.strip()]
                        for line in MAPPING.strip().split('\n')]
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
            elif monster.close_to(self.player):
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
                
