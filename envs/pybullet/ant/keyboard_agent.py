import logging
import requests
from typing import Any, Dict
from ant import Ant
from pynput.keyboard import Listener

class BonsaiAgent(object):
    """ The agent that gets the action from the trained brain exported as docker image and started locally
    """

    def act(self, state) -> Dict[str, Any]:
        action = self.predict(state)
       # action["command"] = int(action["command"])
        return action

    def predict(self, state):
        # local endpoint when running trained brain locally in docker container
        url = "http://localhost:5000/v1/prediction"

        response = requests.get(url, json=state)
        action = response.json()

        return action


class RandomAgent(object):
    """The world's simplest agent!"""

    def __init__(self, action_space):
        self.action_space = action_space

    def act(self):
        return self.action_space.sample()

def on_press(key):
    global j
    try:
        if key.char == ('e'):
            j[7] = 1.0
        elif key.char == ('d'):
            j[7] = -1.0

        elif key.char == ('w'):
            j[6] = 1.0
        elif key.char == ('s'):
            j[6] = -1.0  

        elif key.char == ('q'):
            j[5] = 1.0
        elif key.char == ('a'):
            j[5] = -1.0  

        elif key.char == ('9'):
            j[4] = 1.0
        elif key.char == ('0'):
            j[4] = -1.0  

        elif key.char == ('7'):
            j[3] = 1.0
        elif key.char == ('8'):
            j[3] = -1.0  

        elif key.char == ('5'):
            j[2] = 1.0
        elif key.char == ('6'):
            j[2] = -1.0  

        elif key.char == ('3'):
            j[1] = 1.0
        elif key.char == ('4'):
            j[1] = -1.0   
            
        elif key.char == ('1'):
            j[0] = 1.0
        elif key.char == ('2'):
            j[0] = -1.0                    
        else:
            return
    except:
       return
    global changed
    changed = True

    action = {"j1":j[0],"j2":j[1],"j3":j[2],"j4":j[3],"j5":j[4],"j6":j[5],"j7":j[6],"j8":j[7] }
    ant.episode_step(action)
    #state = ant.get_state()
    j = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    changed = False




if __name__ == '__main__':
    logging.basicConfig()
    log = logging.getLogger("ant")
    log.setLevel(level='INFO')

    # we will use our environment (wrapper of OpenAI env)
    ant = Ant()
    global changed
    global j
    j = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    # specify which agent you want to use,
    # BonsaiAgent that uses trained Brain or
    # RandomAgent that randomly selects next action
    agent = BonsaiAgent()

    ant._env.render()
    ant._env.reset()

    episode_count = 100

    changed = False
    # Collect events until released
    listener =  Listener(  on_press = on_press)   
    listener.start()
    try:
        for i in range(episode_count):
            # start a new episode and get the new state
            ant.episode_start()
            state = ant.get_state()

            while True:
                # get the action from the agent (based on the current state)
                
                if ant.halted():
                    break

            ant.episode_finish("")

    except KeyboardInterrupt:
        print("Stopped")
