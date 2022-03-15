import cv2

# font
font = cv2.FONT_HERSHEY_SIMPLEX
# Line thickness of 2 px
thickness = 2

class ImageDrawer(object):
    def __init__(self, ds_player):
        self.y = 480
        self.x = 640
        self.ds_player = ds_player

    def print_scores(self, img):
        # fontScale
        fontScale = 1

        color = (255, 0, 0)

        img = cv2.putText(img, 'Round: {}'.format(self.ds_player.round), (230, 30), font,
                            0.75, (0, 255, 0), thickness, cv2.LINE_AA)

        img = cv2.putText(img, 'Agent: {}'.format(self.ds_player.get_agent_score()), (30, 50), font,
                            fontScale, color, thickness, cv2.LINE_AA)

        img = cv2.putText(img, 'Player: {}'.format(self.ds_player.get_player_score()), (self.x - 250, 50), font,
                            fontScale, color, thickness, cv2.LINE_AA)

        return img

    def l2action(self, str):
        if str == 'P':
            return 'Papel'
        if str == 'S':
            return 'Tijeras'
        if str == 'R':
            return 'Piedra'

    def print_actions(self, img):
        # fontScale
        fontScale = 1

        color = (255, 0, 0)
        agent_action = self.l2action(self.ds_player.agent_actions[self.ds_player.round])
        player_action = self.l2action(self.ds_player.player_actions[self.ds_player.round])

        img = cv2.putText(img, 'Agent: {}'.format(agent_action), (30, 100), font,
                            fontScale, color, thickness, cv2.LINE_AA)

        img = cv2.putText(img, 'Player: {}'.format(player_action), (self.x - 250, 100), font,
                            fontScale, color, thickness, cv2.LINE_AA)

        print('Round: {}, Agent: {}, Player: {} - Score:({}, {})'.format(self.ds_player.round,
                                                                        agent_action, player_action,
                                                                        self.ds_player.get_agent_score(),
                                                                        self.ds_player.get_player_score()))

        return img

    def writeText(self, img, text, is_final=True):
        # fontScale
        fontScale = 0.75

        # color in BGR
        if is_final:
            color = (0, 255, 0)
        else:
            color = (255, 0, 0)

        # Using cv2.putText() method
        img = cv2.putText(img, text, (50, self.y - 50), font,
                            fontScale, color, thickness, cv2.LINE_AA)

        im = self.print_scores(img)

        return img
