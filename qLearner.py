import random
import json
import dataclasses

@dataclasses.dataclass
class GameState:
    distance: tuple
    position: tuple
    surroundings: str
    apple: tuple


class qLearner(object):
    def __init__(self, window_width, window_height, block_size):
        #Game parameters
        self.window_width = window_width
        self.window_height = window_height
        self.block_size = block_size

        #Learning parameters
        self.epsilon = 0.7
        self.lr = 0.7
        self.discount = .8

        self.decrease_value = 0.001

        #State/Action history
        self.qvalues = self.load_qvalues()
        self.history = []

        #List of actions
        self.actions = {
            0: 'left',
            1: 'right',
            2: 'up',
            3: 'down'
        }

    def reset(self):
        self.history = []

    def load_qvalues(self, path="qvalues.json"):
        with open(path, "r") as f:
            qvalues = json.load(f)
        return qvalues

    def save_qvalues(self, path="qvalues.json"):
        with open(path, "w") as f:
            json.dump(self.qvalues, f)

    def act(self, snake, apple):
        state = self.get_state(snake, apple)

        # Epsilon greedy
        rand = random.uniform(0, 1)
        if rand < self.epsilon:
            action_key = random.choices(list(self.actions.keys()))[0]
        else:
            state_scores = self.qvalues[self.get_state_string(state)]
            action_key = state_scores.index(max(state_scores))
        action_val = self.actions[action_key]

        #Remembering actions snake took at each state
        self.history.append({
            'state': state,
            'action': action_key
        })
        return action_val

    def update_qvalues(self, reason):
        history = self.history[::-1]
        for i, h in enumerate(history[:-1]):
            if reason:  # Snake Died -> Negative reward
                stateN = history[0]['state']
                actionN = history[0]['action']
                state_str = self.get_state_string(stateN)
                reward = -1

                # Bellman equation - there is no future state since game is over
                self.qvalues[state_str][actionN] = (1-self.lr) * self.qvalues[state_str][actionN] + self.lr * reward
                reason = None
            else:
                s1 = h['state']              # current state
                s0 = history[i+1]['state']   # previous state
                a0 = history[i+1]['action']  # action taken at previous state

                x1 = s0.distance[0]     # x distance at current state
                y1 = s0.distance[1]     # y distance at current state

                x2 = s1.distance[0]     # x distance at previous state
                y2 = s1.distance[1]     # y distance at previous state

                if s0.apple != s1.apple:  # Snake ate apple, positive reward
                    reward = 1
                elif (abs(x1) > abs(x2) or abs(y1) > abs(y2)):
                    reward = 1          #Snake is closer to the apple, positive reward
                else:
                    reward = -1         # Snake is further from apple, negative reward

                state_str = self.get_state_string(s0)
                new_state_str = self.get_state_string(s1)

                #Bellman Equation
                self.qvalues[state_str][a0] = (1-self.lr) * (self.qvalues[state_str][a0]) + self.lr * (reward + self.discount*max(self.qvalues[new_state_str])) 

    def get_state(self, snake, apple):
        #Coordinates of snake head
        snake_head = snake[-1] 
        distanceX = apple[0] - snake_head[0]
        distanceY = apple[1] - snake_head[1]

        #Where is the apple in relation to the snake?
        if distanceX > 0:
            positionX = '1'     #Apple is to the right of the snake
        elif distanceX < 0:
            positionX = '0'     #Apple is to the left of the snake
        else:
            positionX = 'NA'    #Apple and snake are on the same X file

        if distanceY > 0:
            positionY = '3'     #Apple is below snake
        elif distanceY < 0:
            positionY = '2'     #Apple is above snake
        else:
            positionY = 'NA'    #Apple and snake are on the same Y file

        ##***Not sure what's happening down here***

        sqs = [
            (snake_head[0]-self.block_size, snake_head[1]),
            (snake_head[0]+self.block_size, snake_head[1]),
            (snake_head[0],                 snake_head[1]-self.block_size),
            (snake_head[0],                 snake_head[1]+self.block_size),
        ]

        surrounding_list = []
        for sq in sqs:
            if sq[0] < 0 or sq[1] < 0:  # off screen left or top
                surrounding_list.append('1')
            # off screen right or bottom
            elif sq[0] >= self.window_width or sq[1] >= self.window_height:
                surrounding_list.append('1')
            elif sq in snake[:-1]:  # part of tail
                surrounding_list.append('1')
            else:
                surrounding_list.append('0')
        surroundings = ''.join(surrounding_list)

        #Return state
        return GameState(distance = (distanceX, distanceY), position = (positionX, positionY), surroundings = surroundings, apple = apple)

    def get_state_string(self, state):
        return str((state.position[0], state.position[1], state.surroundings))
