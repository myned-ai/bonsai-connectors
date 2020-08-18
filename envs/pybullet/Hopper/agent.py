import logging
import requests
from typing import Any, Dict
from hopper import Hopper


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
    log = logging.getLogger("hopper")
    log.setLevel(level='DEBUG')

    # we will use our environment (wrapper of OpenAI env)
    hopper = Hopper(iteration_limit=1000)

    # setting initial camera position
    hopper.initialize_camera(distance=2, yaw=10, pitch=-20)

    # setting initial camera position
    hopper.initialize_camera(distance=2, yaw=10, pitch=-20)

    # specify which agent you want to use,
    # BonsaiAgent that uses trained Brain or
    # RandomAgent that randomly selects next action
    agent = BonsaiAgent()

    # hopper._env.render()
    # hopper._env.reset()

    episode_count = 100

    try:
        for i in range(episode_count):
            # start a new episode and get the new state
            hopper.episode_start()
            state = hopper.get_state()

            while True:
                # get the action from the agent (based on the current state)
                action = agent.act(state)
                hopper._env.unwrapped.camera_adjust()

            # do the next step of the simulation and get the new state
                hopper.episode_step(action)
                state = hopper.get_state()

                if hopper.halted():
                    break

            hopper.episode_finish("")

    except KeyboardInterrupt:
        print("Stopped")
