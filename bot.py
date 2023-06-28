import numpy as np
import pyglet
import random
import pickle
import atexit
import os
from pybird.game import Game


class Bot:
    def __init__(self, game):
        self.game = game
        # constants
        self.WINDOW_HEIGHT = Game.WINDOW_HEIGHT
        self.PIPE_WIDTH = Game.PIPE_WIDTH
        # this flag is used to make sure at most one tap during
        # every call of run()
        self.tapped = False

        self.game.play()

        # variables for plan
        self.Q = {}

        self.routine = 150
        self.alpha = 0.7
        self.gamma = 0.99
        self.explore = 0
        self.pre_s = (100, 100)
        self.pre_a = int(0)

        if os.path.isfile('dict_Q'):
            self.Q = pickle.load(open('dict_Q', 'rb'))
            print('read')
        else:
            for x in range(-11, 50):
                for y in range(-50, 50):
                    self.Q[(x, y)] = [0, 0]
            self.Q[self.pre_s] = [0, 0]
        # def do_at_exit():
        #     pickle.dump(self.Q, open('dict_Q', 'wb'))
        #     print('wirte to dict_Q')
        #
        # atexit.register(do_at_exit)

    # this method is auto called every 0.05s by the pyglet
    def run(self):
        if self.game.state == 'PLAY':
            self.tapped = False
            # call plan() to execute your plan
            self.plan(self.get_state())

        else:
            state = self.get_state()
            self.routine += 1
            print(self.routine)
            bird_state = list(state['bird'])
            bird_state[2] = 'dead'
            state['bird'] = bird_state
            # do NOT allow tap
            self.tapped = True
            self.plan(state)
            # restart game
            print('score:', self.game.record.get(), 'best: ', self.game.record.best_score)
            pickle.dump(self.Q, open('dict_Q', 'wb'))
            print('wirte to dict_Q')
            self.game.restart()
            self.game.play()

    # get the state that robot needed
    def get_state(self):
        state = {}
        # bird's position and status(dead or alive)
        state['bird'] = (int(round(self.game.bird.x)), int(round(self.game.bird.y)), 'alive')
        state['pipes'] = []
        # pipes' position
        for i in range(1, len(self.game.pipes), 2):
            p = self.game.pipes[i]
            if p.x < Game.WINDOW_WIDTH:
                # this pair of pipes shows on screen
                x = int(round(p.x))
                y = int(round(p.y))
                state['pipes'].append((x, y))
                state['pipes'].append((x, y - Game.PIPE_HEIGHT_INTERVAL))
        return state

    # simulate the click action, bird will fly higher when tapped
    # It can be called only once every time slice(every execution cycle of plan())
    def tap(self):
        if not self.tapped:
            self.tapped = True

    # That's where the robot actually works
    # NOTE Put your code here
    def plan(self, state):

        x_bird = state['bird'][0]
        y_bird = state['bird'][1]
        x_pipe = 0
        y_pipe_bot = 0
        if len(state['pipes']) > 0:
            (x1, y1) = state['pipes'][0]
            x2 = x1 + self.PIPE_WIDTH

            # if x2 <= x_bird:
            # 未导入的dict_Q的修改代码

            if x2 <= (x_bird - 10):
                (x_pipe, y_pipe_bot) = state['pipes'][3]
            else:
                (x_pipe, y_pipe_bot) = state['pipes'][1]

        # 将x/y分别变成原来的十分之一并取整，减少学习所需时间

        delta_x = int((x_pipe - x_bird) / 10)
        delta_y = int((y_pipe_bot - y_bird) / 10)

        s = (delta_x, delta_y)

        nothing = self.Q[s][0]
        jump = self.Q[s][1]
        if nothing >= jump:
            max_v = nothing
        else:
            max_v = jump

        if nothing >= jump:
            act = 0
        else:
            act = 1

        # 简单的防止落到地上的策略

        if y_bird < 150:
            act = 1

        # 以下为Qlearning算法，为防止学习过度而发散，当分数超过1000后减少学习率

        if state['bird'][2] == 'alive':
            r = 1
        else:
            r = -1000
        sco = self.game.record.get()
        beta = np.maximum(1, (sco - 1000))

        self.Q[self.pre_s][self.pre_a] += self.alpha * (r + self.gamma * max_v - self.Q[self.pre_s][self.pre_a]) / beta
        self.pre_a = act
        self.pre_s = s

        if act == 1:
            game.bird.jump()


if __name__ == '__main__':
    show_window = True
    enable_sound = False
    game = Game()
    game.set_sound(enable_sound)
    bot = Bot(game)


    def update(dt):
        game.update(dt)
        bot.run()


    pyglet.clock.schedule_interval(update, Game.TIME_INTERVAL)

    if show_window:
        window = pyglet.window.Window(Game.WINDOW_WIDTH, Game.WINDOW_HEIGHT, vsync=False)


        @window.event
        def on_draw():
            window.clear()
            game.draw()


        pyglet.app.run()
    else:
        pyglet.app.run()
