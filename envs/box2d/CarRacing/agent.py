import logging
from os import write
import requests
from typing import Any, Dict
from carracing import CarRacing


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
    log = logging.getLogger("carracing")
    log.setLevel(level='INFO')

    # we will use our environment (wrapper of OpenAI env)
    car_racing = CarRacing(iteration_limit=1000)

    # specify which agent you want to use,
    # BonsaiAgent that uses trained Brain or
    # RandomAgent that randomly selects next action
    agent = BonsaiAgent()

    # half_cheetah._env.render()
    # half_cheetah._env.reset()

    episode_count = 100
    iteration = 0
    try:
        for i in range(episode_count):
            iteration = 0
            # start a new episode and get the new state
            car_racing.episode_start()
            state = car_racing.get_state()

            while True:
                # get the action from the agent (based on the current state)
                action = agent.act(state)

            # do the next step of the simulation and get the new state
                car_racing.episode_step(action)
                state = car_racing.get_state()

                if car_racing.halted():
                    break
            print("iteration {}".format(iteration))
            iteration += 1
            
            car_racing.episode_finish("")

    except KeyboardInterrupt:
        print("Stopped")
        car_racing.unregister()