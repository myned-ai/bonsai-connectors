import logging
import requests
from typing import Any, Dict
from mountain_car import MountainCar


class BonsaiAgent(object):
    """ The agent that gets the action from the trained brain exported as docker image and started locally
    """

    def act(self, state) -> Dict[str, Any]:
        action = self.predict(state)
        action["command"] = int(action["command"])
        return action

    def predict(self, state):
        #local endpoint when running trained brain locally in docker container
        url = "http://localhost:5000/v1/prediction"

        response = requests.get(url, json=state)
        action = response.json()

        return action


class RandomAgent(object):
    """The world's simplest agent!"""

    def __init__(self, action_space):
        self.action_space = action_space

    def act(self, observation, reward, done):
        return self.action_space.sample()


if __name__ == '__main__':
    logging.basicConfig()
    log = logging.getLogger("mountain-car")
    log.setLevel(level='INFO')

    # we will use our environment (wrapper of OpenAI env)
    mountain_car = MountainCar()

    # specify which agent you want to use, 
    # BonsaiAgent that uses trained Brain or
    # RandomAgent that randomly selects next action
    agent = BonsaiAgent()

    episode_count = 100

    try:
        for i in range(episode_count):
            #start a new episode and get the new state
            mountain_car.episode_start()
            state = mountain_car.get_state()

            while True:
                #get the action from the agent (based on the current state)
                action = agent.act(state)

                #do the next step of the simulation and get the new state
                mountain_car.episode_step(action)
                state = mountain_car.get_state()

                if mountain_car.halted():
                    break

            mountain_car.episode_finish("")

    except KeyboardInterrupt:
        print("Stopped")
