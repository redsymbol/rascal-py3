import curses
import queue
from .handlers import handler_map
from .world import World
from .events import PlayerDeadEvent

class View:
    def __init__(self, player):
        self.world = World(player)
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
            if len(self.world.monsters) == 0:
                self.last_message = 'You have killed all the monsters. You win!'
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
            retval = handler_map[ch](self.world)
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
    
