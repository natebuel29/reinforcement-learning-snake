import random
import json
import dataclasses

@dataclasses.dataclass
class GameState:
    distance: tuple
    position: tuple
    surroundings: str
    direction: str
    apple_one: tuple
    apple_two: tuple

#MUST IMPLEMENT SECOND APPLE
class sarsaLearner(object):
    def __init__(self, window_width, window_height, block_size):
        #Game parameters
        self.window_width = window_width
        self.window_height = window_height
        self.block_size = block_size

        #Learning parameters
        self.epsilon = 0.7
        self.lr = 0.5
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

        self.directions = {
            "left": (-2*block_size,0),
            "right": (+2*block_size,0),
            "up" : (0,-2*block_size),
            "down":(0,2*block_size)
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

    def decrease_epsilon(self,decrease_value):
        if self.epsilon > 0.04: 
            self.epsilon = self.epsilon - decrease_value
        elif self.epsilon < 0.04:
            self.epsilon = 0.04
    
    def act(self,snake,direction,apple_one,apple_two):
        state = self.get_state(snake, direction, apple_one,apple_two)
        
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
                a1 = h['action']
                s0 = history[i+1]['state']   # previous state
                a0 = history[i+1]['action']  # action taken at previous state

                if s0.apple_one != s1.apple_one or s0.apple_two != s1.apple_two:  # Snake ate apple, positive reward
                    reward = 50
                else:
                    reward = 0         # Snake is further from apple, negative reward

                state_str = self.get_state_string(s0)
                new_state_str = self.get_state_string(s1)

                #Bellman Equation
                self.qvalues[state_str][a0] = self.qvalues[state_str][a0] + self.lr * (reward + self.qvalues[new_state_str][a1] - self.qvalues[state_str][a0] ) 

    def get_state(self, snake, direction, apple_one,apple_two):
        #Coordinates of snake head
        snake_head = snake[-1] 
        distanceX_one = apple_one[0] - snake_head[0]
        distanceY_one = apple_one[1] - snake_head[1]
        
        distanceX_two = apple_two[0] - snake_head[0]
        distanceY_two = apple_two[1] - snake_head[1]

        #Where is the apple in relation to the snake?
        if distanceX_one > 0:
            positionX_one = '1'     #Apple is to the right of the snake
        elif distanceX_one < 0:
            positionX_one = '0'     #Apple is to the left of the snake
        else:
            positionX_one = 'same'    #Apple and snake are on the same X file

        if distanceY_one > 0:
            positionY_one = '3'     #Apple is below snake
        elif distanceY_one < 0:
            positionY_one = '2'     #Apple is above snake
        else:
            positionY_one = 'same'    #Apple and snake are on the same Y file


        if distanceX_two > 0:
            positionX_two = '1'     #Apple is to the right of the snake
        elif distanceX_two < 0:
            positionX_two = '0'     #Apple is to the left of the snake
        else:
            positionX_two = 'same'    #Apple and snake are on the same X file

        if distanceY_two > 0:
            positionY_two = '3'     #Apple is below snake
        elif distanceY_two < 0:
            positionY_two = '2'     #Apple is above snake
        else:
            positionY_two = 'same'    #Apple and snake are on the same Y file


        surrounding_list = self.generate_surroundings(snake)
        surroundings = ''.join(surrounding_list)

        self.generate_surroundings(snake)

        #Return state
        return GameState(distance = (distanceX_one, distanceY_one,distanceX_two,distanceY_two), position = (positionX_one, positionY_one,positionX_two,positionY_two), direction=direction, surroundings = surroundings, apple_one = apple_one,apple_two =apple_two)


    def generate_surroundings(self,snake):
        snake_head = snake[-1]
        surroundings = []
        for direction,value in self.directions.items():
            direction_surroundings= []
            block = (snake_head[0] + value[0],snake_head[1]+value[1])
            if block[0] <= 0 or block[1] <= 0:
               direction_surroundings.append("1")
            else:
                direction_surroundings.append("0")
            if block[0] >= self.window_width or block[1] >=self.window_height:
                direction_surroundings.append("1")
            else:
                direction_surroundings.append("0")
            if block in snake[:-1]:
                direction_surroundings.append("1")
            else:
                direction_surroundings.append("0")
            
            surroundings.append(''.join(direction_surroundings))
        
        return surroundings      

    def get_state_string(self, state):
        return str((state.position[0], state.position[1],state.position[2],state.position[3],state.direction, state.surroundings))

