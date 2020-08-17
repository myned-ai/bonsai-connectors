import logging
import requests
from typing import Any, Dict
from reacher import Reacher


class BonsaiAgent(object):
    """ The agent that gets the action from the trained brain exported as docker image and started locally
    """

    def act(self, state) -> Dict[str, Any]:
        action = self.predict(state)

        return action

    def predict(self, state):
        # local endpoint when running trained brain locally in docker container
        url = "http://localhost:5000/v1/prediction"

        response = requests.get(url, json=state)
        action = response.json()

        return action


if __name__ == '__main__':
    logging.basicConfig()
    log = logging.getLogger("reacher")
    log.setLevel(level='DEBUG')

    # we will use our environment (wrapper of OpenAI env)
    reacher =Reacher(iteration_limit=200)

    # specify which agent you want to use,
    # BonsaiAgent that uses trained Brain or
    # RandomAgent that randomly selects next action
    agent = BonsaiAgent()


    episode_count = 100

    try:
        for i in range(episode_count):
            # start a new episode and get the new state
            reacher.episode_start()
            state = reacher.get_state()
            
            reacher.initialize_camera(distance=1, yaw=30, pitch=-40)

            while True:
                # get the action from the agent (based on the current state)
                action = agent.act(state)
               
            # do the next step of the simulation and get the new state
                reacher.episode_step(action)
                state = reacher.get_state()

                if reacher.halted():
                    break

            reacher.episode_finish("")

    except KeyboardInterrupt:
        print("Stopped")
