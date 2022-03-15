import random
from image_drawer import ImageDrawer
import time

#  R -> S -> P
actions = ['R', 'S', 'P']
start_actions = ['R', 'P']

NEW_ROUND = 0
FINISHING_ROUND = 1
FINISHED_ROUND = 2

MAX_FRAMES_LAG = 5

MILLIS_LAG = 500

def current_milli_time():
    return round(time.time() * 1000)

class PSR_DS_Player(object):

    def __init__(self):
        self.round = 1
        self.agent_score = 0
        self.player_score = 0

        self.agent_actions = [None for i in range(1000)]
        self.player_actions = [None for i in range(1000)]
        self.last_result = None

        self.current_state = NEW_ROUND
        self.frames_counter = 0

        self.im_drawer = ImageDrawer(self)
        self.last_image = None

        self.last_milis = 0

    def get_agent_score(self):
        return self.agent_score

    def get_player_score(self):
        return self.player_score

    def reset(self):
        self.round = 1

        self.agent_score = 0
        self.player_score = 0

        self.agent_actions = [None for i in range(1000)]
        self.player_actions = [None for i in range(1000)]
        self.last_result = None

        self.current_state = NEW_ROUND
        self.frames_counter = 0

        self.last_image = None

    def agent_add(self):
        self.agent_score += 1

    def player_add(self):
        self.player_score += 1

    def cycle_backward(self, psr):
        # R -> S -> P
        if psr == 'R':
            return 'S'
        if psr == 'S':
            return 'P'
        if psr == 'P':
            return 'R'

    def save_strategy(self, psr):
        # R -> S -> P
        if psr == 'R':
            return 'R'
        if psr == 'S':
            return 'S'
        if psr == 'P':
            return 'P'

    def manage_inputs(self, img, text, fingers):
        if True:
            if self.current_state == NEW_ROUND:
                if text is not None:
                    if 'era un dos tres' in text:
                        self.current_state = FINISHING_ROUND
                        self.calculate_action()
                        self.last_milis = current_milli_time()
                    if 'ya' in text:
                        self.current_state = FINISHING_ROUND
                        self.calculate_action()
                        self.last_milis = current_milli_time()
                    elif 'nuevo' in text:
                        self.reset()
                    elif 'juego' in text:
                        self.reset()
            elif self.current_state == FINISHING_ROUND:
                self.frames_counter += 1

                if self.frames_counter >= MAX_FRAMES_LAG:
                    self.frames_counter = 0

                    if sum(fingers) >= 4:
                        self.player_actions[self.round] = 'P'
                    elif sum(fingers) >= 2:
                        self.player_actions[self.round] = 'S'
                    else:
                        self.player_actions[self.round] = 'R'

                    self.process_result()

                    img = self.im_drawer.print_actions(img)
                    self.last_image = img.copy()

                    self.current_state = FINISHED_ROUND
            elif self.current_state == FINISHED_ROUND:
                img = self.last_image.copy()
                if text is not None:
                    if current_milli_time() >= self.last_milis + MILLIS_LAG:
                        if 'otra vez' in text:
                            self.current_state = NEW_ROUND
                            self.round += 1
                            self.last_image = None
                        elif 'nuevo' in text:
                            self.reset()
                        elif 'juego' in text:
                            self.reset()

        return img

    def calculate_action(self):
        # if self.round >= 3:
        #     if self.player_actions[self.round-1] == self.player_actions[self.round-2]:
        #         self.agent_actions[self.round] = self.save_strategy(self.player_actions[self.round-1])
        #         return

        if self.last_result is None:
            self.agent_actions[self.round] = start_actions[random.randrange(len(start_actions))]
        else:
            #  R -> S -> P
            if self.last_result == 'W':
                self.agent_actions[self.round] = self.cycle_backward(self.agent_actions[self.round-1])
            if self.last_result == 'L':
                self.agent_actions[self.round] = self.cycle_backward(self.agent_actions[self.round-1])

    def process_result(self):
        #  R -> S -> P
        if self.agent_actions[self.round] == self.player_actions[self.round]:
            self.last_result = None
        else:
            if self.player_actions[self.round] == 'R':
                if self.agent_actions[self.round] == 'P':
                    self.last_result = 'W'
                else:
                    self.last_result = 'L'
            if self.player_actions[self.round] == 'P':
                if self.agent_actions[self.round] == 'S':
                    self.last_result = 'W'
                else:
                    self.last_result = 'L'
            if self.player_actions[self.round] == 'S':
                if self.agent_actions[self.round] == 'R':
                    self.last_result = 'W'
                else:
                    self.last_result = 'L'

            if self.last_result == 'W':
                self.agent_add()
            elif self.last_result == 'L':
                self.player_add()
